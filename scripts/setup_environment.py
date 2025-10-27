#!/usr/bin/env python3
"""
环境设置脚本
用于设置开发、测试和生产环境
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any


class EnvironmentSetup:
    """环境设置类"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        
    def setup_environment(self):
        """设置环境"""
        print(f"设置 {self.environment} 环境...")
        
        # 创建必要的目录
        self._create_directories()
        
        # 创建配置文件
        self._create_config_files()
        
        # 设置权限
        self._set_permissions()
        
        print(f"{self.environment} 环境设置完成")
        
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.project_root / "logs",
            self.project_root / "data",
            self.project_root / "backups",
            self.project_root / "uploads",
            self.config_dir
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"创建目录: {directory}")
            
    def _create_config_files(self):
        """创建配置文件"""
        
        # 基础配置文件
        base_config = {
            "environment": self.environment,
            "debug": self.environment == "development",
            "log_level": "INFO" if self.environment == "production" else "DEBUG",
            "api_keys": {
                "musicbrainz": "",
                "acoustid": "",
                "aws_access_key": "",
                "aws_secret_key": "",
                "aliyun_access_key": "",
                "aliyun_secret_key": "",
                "tencent_secret_id": "",
                "tencent_secret_key": ""
            },
            "database": {
                "redis_url": "redis://localhost:6379/0",
                "cache_ttl": 3600
            },
            "web": {
                "host": "0.0.0.0",
                "port": 8090,
                "cors_origins": ["*"] if self.environment == "development" else []
            },
            "plugins": {
                "enabled": ["music_scraper", "file_organizer", "cloud_storage"],
                "auto_reload": self.environment == "development"
            }
        }
        
        # 根据环境调整配置
        if self.environment == "production":
            base_config["web"]["cors_origins"] = ["https://your-domain.com"]
            base_config["plugins"]["auto_reload"] = False
            
        elif self.environment == "testing":
            base_config["database"]["redis_url"] = "redis://localhost:6380/0"
            base_config["web"]["port"] = 8091
            
        # 写入配置文件
        config_file = self.config_dir / f"config.{self.environment}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(base_config, f, indent=2, ensure_ascii=False)
            
        print(f"创建配置文件: {config_file}")
        
        # 创建环境变量文件
        self._create_env_file()
        
    def _create_env_file(self):
        """创建环境变量文件"""
        env_content = f"""
# 媒体管理平台环境配置
ENVIRONMENT={self.environment}
DEBUG={'true' if self.environment == 'development' else 'false'}
LOG_LEVEL={'DEBUG' if self.environment == 'development' else 'INFO'}

# 数据库配置
REDIS_URL={'redis://localhost:6379/0' if self.environment != 'testing' else 'redis://localhost:6380/0'}

# Web服务配置
HOST=0.0.0.0
PORT={'8090' if self.environment != 'testing' else '8091'}

# API密钥配置（请根据实际情况填写）
MUSICBRAINZ_API_KEY=
ACOUSTID_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
TENCENT_SECRET_ID=
TENCENT_SECRET_KEY=
"""
        
        env_file = self.project_root / f".env.{self.environment}"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content.strip())
            
        print(f"创建环境文件: {env_file}")
        
    def _set_permissions(self):
        """设置文件权限"""
        if self.environment == "production":
            # 在生产环境中设置更严格的权限
            sensitive_dirs = [
                self.project_root / "config",
                self.project_root / "logs",
                self.project_root / "data"
            ]
            
            for directory in sensitive_dirs:
                if directory.exists():
                    # 设置目录权限为750
                    directory.chmod(0o750)
                    print(f"设置权限: {directory}")
                    
    def cleanup(self):
        """清理环境"""
        print(f"清理 {self.environment} 环境..."
        
        # 删除临时文件
        temp_files = [
            self.project_root / "__pycache__",
            self.project_root / "*.pyc",
            self.project_root / "*.log"
        ]
        
        for pattern in temp_files:
            for file_path in self.project_root.glob(pattern.name if hasattr(pattern, 'name') else pattern):
                if file_path.is_file():
                    file_path.unlink()
                    print(f"删除文件: {file_path}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"删除目录: {file_path}")
                    
        print(f"{self.environment} 环境清理完成")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python setup_environment.py [environment]")
        print("环境选项: development, testing, production")
        sys.exit(1)
        
    environment = sys.argv[1].lower()
    
    if environment not in ["development", "testing", "production"]:
        print("错误: 环境必须是 development, testing 或 production")
        sys.exit(1)
        
    setup = EnvironmentSetup(environment)
    
    if len(sys.argv) > 2 and sys.argv[2] == "cleanup":
        setup.cleanup()
    else:
        setup.setup_environment()


if __name__ == "__main__":
    main()