#!/usr/bin/env python3
"""
VabHub 测试环境部署器
用于部署和管理多仓库测试环境
"""

import argparse
import subprocess
import sys
import os
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class TestEnvironmentDeployer:
    """测试环境部署器"""
    
    def __init__(self, config_path: str = "tests/config/environment_config.yaml"):
        self.config_path = config_path
        self.environments = {}
        self.current_environment = None
        
    def load_config(self) -> Dict:
        """加载环境配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
            return self.default_config()
    
    def default_config(self) -> Dict:
        """默认环境配置"""
        return {
            'environments': {
                'unit': {
                    'description': '单元测试环境',
                    'services': ['database', 'redis'],
                    'docker_compose': 'docker-compose.unit.yml',
                    'timeout': 300
                },
                'integration': {
                    'description': '集成测试环境',
                    'services': ['database', 'redis', 'api', 'frontend'],
                    'docker_compose': 'docker-compose.integration.yml',
                    'timeout': 600
                },
                'e2e': {
                    'description': '端到端测试环境',
                    'services': ['database', 'redis', 'api', 'frontend', 'test-browser'],
                    'docker_compose': 'docker-compose.e2e.yml',
                    'timeout': 900
                }
            }
        }
    
    def check_docker(self) -> bool:
        """检查 Docker 是否可用"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_docker_compose(self) -> bool:
        """检查 Docker Compose 是否可用"""
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def create_docker_compose_file(self, environment: str, services_config: Dict) -> bool:
        """创建 Docker Compose 文件"""
        docker_compose_content = self.generate_docker_compose(services_config)
        
        compose_file = f"docker-compose.{environment}.yml"
        
        try:
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(docker_compose_content)
            
            print(f"✅ 已创建 Docker Compose 文件: {compose_file}")
            return True
            
        except Exception as e:
            print(f"❌ 创建 Docker Compose 文件失败: {e}")
            return False
    
    def generate_docker_compose(self, services_config: Dict) -> str:
        """生成 Docker Compose 配置"""
        return f"""version: '3.8'

services:
  database:
    image: postgres:13
    environment:
      POSTGRES_DB: vabhub_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d vabhub_test"]
      interval: 10s
      timeout: 5s
      retries: 3

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  api:
    build:
      context: ../VabHub-Core
      dockerfile: Dockerfile.test
    environment:
      DATABASE_URL: postgresql://test_user:test_password@database:5432/vabhub_test
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: test
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../VabHub-Frontend
      dockerfile: Dockerfile.test
    environment:
      API_URL: http://api:8000
    ports:
      - "3000:3000"
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  test-browser:
    image: selenium/standalone-chrome:latest
    ports:
      - "4444:4444"
      - "7900:7900"
    environment:
      SE_NODE_MAX_SESSIONS: 5
      SE_NODE_OVERRIDE_MAX_SESSIONS: true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4444/wd/hub/status"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    driver: bridge
"""
    
    def deploy_environment(self, environment: str, rebuild: bool = False) -> bool:
        """部署测试环境"""
        config = self.load_config()
        env_config = config['environments'].get(environment)
        
        if not env_config:
            print(f"❌ 未知环境: {environment}")
            return False
        
        print(f"🚀 开始部署 {environment} 测试环境")
        print(f"📋 描述: {env_config['description']}")
        
        # 检查 Docker 环境
        if not self.check_docker():
            print("❌ Docker 不可用")
            return False
        
        if not self.check_docker_compose():
            print("❌ Docker Compose 不可用")
            return False
        
        # 创建 Docker Compose 文件
        compose_file = env_config['docker_compose']
        if not Path(compose_file).exists():
            if not self.create_docker_compose_file(environment, env_config):
                return False
        
        # 构建服务
        if rebuild:
            print("🔨 重新构建服务...")
            try:
                subprocess.run(['docker-compose', '-f', compose_file, 'build'], 
                            check=True)
                print("✅ 服务构建完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 服务构建失败: {e}")
                return False
        
        # 启动服务
        print("🚀 启动测试环境...")
        try:
            subprocess.run(['docker-compose', '-f', compose_file, 'up', '-d'], 
                        check=True)
            print("✅ 服务启动完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 服务启动失败: {e}")
            return False
        
        # 等待服务就绪
        print("⏳ 等待服务就绪...")
        if not self.wait_for_services_ready(environment, env_config['timeout']):
            print("❌ 服务启动超时")
            return False
        
        self.current_environment = environment
        print(f"✅ {environment} 测试环境部署完成")
        return True
    
    def wait_for_services_ready(self, environment: str, timeout: int) -> bool:
        """等待服务就绪"""
        start_time = time.time()
        compose_file = f"docker-compose.{environment}.yml"
        
        while time.time() - start_time < timeout:
            try:
                # 检查服务状态
                result = subprocess.run(['docker-compose', '-f', compose_file, 'ps'], 
                                    capture_output=True, text=True)
                
                # 解析服务状态
                lines = result.stdout.strip().split('\n')
                services_running = 0
                services_total = len(self.get_services_for_environment(environment))
                
                for line in lines[2:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4 and parts[3] == 'Up':
                            services_running += 1
                
                print(f"📊 服务状态: {services_running}/{services_total} 运行中")
                
                if services_running == services_total:
                    print("✅ 所有服务已就绪")
                    return True
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ 检查服务状态时出错: {e}")
                time.sleep(5)
        
        return False
    
    def get_services_for_environment(self, environment: str) -> List[str]:
        """获取环境对应的服务列表"""
        config = self.load_config()
        env_config = config['environments'].get(environment, {})
        return env_config.get('services', [])
    
    def stop_environment(self, environment: str) -> bool:
        """停止测试环境"""
        compose_file = f"docker-compose.{environment}.yml"
        
        if not Path(compose_file).exists():
            print(f"⚠️ 环境 {environment} 未部署")
            return True
        
        print(f"🛑 停止 {environment} 测试环境...")
        
        try:
            subprocess.run(['docker-compose', '-f', compose_file, 'down'], 
                        check=True)
            print(f"✅ {environment} 测试环境已停止")
            
            if self.current_environment == environment:
                self.current_environment = None
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 停止环境失败: {e}")
            return False
    
    def cleanup_environment(self, environment: str) -> bool:
        """清理测试环境"""
        print(f"🧹 清理 {environment} 测试环境...")
        
        # 停止环境
        if not self.stop_environment(environment):
            return False
        
        # 清理 Docker 资源
        try:
            # 清理未使用的镜像、容器、网络
            subprocess.run(['docker', 'system', 'prune', '-f'], 
                        capture_output=True)
            print("✅ Docker 资源清理完成")
            
            # 删除 Docker Compose 文件
            compose_file = f"docker-compose.{environment}.yml"
            if Path(compose_file).exists():
                os.remove(compose_file)
                print(f"✅ 已删除 {compose_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 清理环境失败: {e}")
            return False
    
    def get_environment_status(self, environment: str) -> Dict:
        """获取环境状态"""
        compose_file = f"docker-compose.{environment}.yml"
        
        if not Path(compose_file).exists():
            return {'status': 'not_deployed', 'services': []}
        
        try:
            result = subprocess.run(['docker-compose', '-f', compose_file, 'ps'], 
                                capture_output=True, text=True)
            
            services = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines[2:]:  # 跳过标题行
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        service_name = parts[0]
                        status = parts[3]
                        services.append({'name': service_name, 'status': status})
            
            return {
                'status': 'running' if any(s['status'] == 'Up' for s in services) else 'stopped',
                'services': services
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def list_environments(self) -> Dict:
        """列出所有环境状态"""
        config = self.load_config()
        environments_status = {}
        
        for env_name in config['environments']:
            status = self.get_environment_status(env_name)
            environments_status[env_name] = status
        
        return environments_status

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='VabHub 测试环境部署器')
    
    # 操作命令
    parser.add_argument('action', choices=['deploy', 'stop', 'cleanup', 'status', 'list'],
                       help='要执行的操作')
    parser.add_argument('environment', nargs='?', 
                       help='目标环境名称 (unit, integration, e2e)')
    parser.add_argument('--rebuild', action='store_true', 
                       help='重新构建服务镜像')
    parser.add_argument('--config', default='tests/config/environment_config.yaml',
                       help='环境配置文件路径')
    
    args = parser.parse_args()
    
    deployer = TestEnvironmentDeployer(args.config)
    
    if args.action == 'deploy':
        if not args.environment:
            print("❌ 请指定要部署的环境")
            sys.exit(1)
        
        success = deployer.deploy_environment(args.environment, args.rebuild)
        sys.exit(0 if success else 1)
    
    elif args.action == 'stop':
        if not args.environment:
            print("❌ 请指定要停止的环境")
            sys.exit(1)
        
        success = deployer.stop_environment(args.environment)
        sys.exit(0 if success else 1)
    
    elif args.action == 'cleanup':
        if not args.environment:
            print("❌ 请指定要清理的环境")
            sys.exit(1)
        
        success = deployer.cleanup_environment(args.environment)
        sys.exit(0 if success else 1)
    
    elif args.action == 'status':
        if not args.environment:
            print("❌ 请指定要查询的环境")
            sys.exit(1)
        
        status = deployer.get_environment_status(args.environment)
        print(f"📊 {args.environment} 环境状态:")
        print(f"   状态: {status['status']}")
        if 'services' in status:
            for service in status['services']:
                print(f"   {service['name']}: {service['status']}")
    
    elif args.action == 'list':
        environments = deployer.list_environments()
        print("📋 可用测试环境:")
        
        config = deployer.load_config()
        for env_name, env_config in config['environments'].items():
            status = environments[env_name]
            status_icon = '🟢' if status['status'] == 'running' else '🔴' if status['status'] == 'stopped' else '⚪'
            print(f"{status_icon} {env_name}: {env_config['description']}")

if __name__ == '__main__':
    main()