#!/usr/bin/env python3
"""
VabHub 多仓库同步工具
用于同步多个仓库的配置、版本和依赖关系
"""

import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests

class MultiRepoSync:
    """多仓库同步管理器"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.repos = [
            "vabhub-core",
            "vabhub-frontend", 
            "vabhub-plugins",
            "vabhub-resources",
            "vabhub-deploy"
        ]
        
        # 同步配置
        self.sync_config = {
            "version_files": ["package.json", "setup.py", "pyproject.toml"],
            "config_files": ["config.yaml", "config.json", ".env.example"],
            "ignore_patterns": ["node_modules", ".git", "__pycache__", "*.pyc"]
        }
    
    def clone_or_update_repos(self) -> bool:
        """克隆或更新所有仓库"""
        print("🔄 同步仓库...")
        
        for repo in self.repos:
            repo_path = self.base_dir / repo
            
            if repo_path.exists():
                print(f"  更新 {repo}...")
                try:
                    subprocess.run(["git", "pull"], cwd=repo_path, check=True)
                    print(f"  ✅ {repo} 更新成功")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ {repo} 更新失败: {e}")
                    return False
            else:
                print(f"  克隆 {repo}...")
                try:
                    subprocess.run([
                        "git", "clone", 
                        f"https://github.com/vabhub/{repo}.git",
                        str(repo_path)
                    ], check=True)
                    print(f"  ✅ {repo} 克隆成功")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ {repo} 克隆失败: {e}")
                    return False
        
        return True
    
    def sync_versions(self) -> Dict:
        """同步版本信息"""
        print("\n🔢 同步版本信息...")
        
        version_info = {}
        
        for repo in self.repos:
            repo_path = self.base_dir / repo
            version_info[repo] = self._get_repo_version(repo_path)
        
        return version_info
    
    def _get_repo_version(self, repo_path: Path) -> Dict:
        """获取仓库版本信息"""
        version_info = {
            "version": "未知",
            "version_file": None,
            "git_hash": "未知",
            "last_commit": "未知"
        }
        
        # 获取 Git 信息
        try:
            # 获取最新提交哈希
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            version_info["git_hash"] = result.stdout.strip()
            
            # 获取最后提交时间
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=short"],
                cwd=repo_path, capture_output=True, text=True, check=True
            )
            version_info["last_commit"] = result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
        
        # 查找版本文件
        for version_file in self.sync_config["version_files"]:
            file_path = repo_path / version_file
            if file_path.exists():
                version_info["version_file"] = version_file
                
                if version_file == "package.json":
                    # Node.js 项目
                    with open(file_path, 'r') as f:
                        package_info = json.load(f)
                    version_info["version"] = package_info.get("version", "未知")
                
                elif version_file == "setup.py":
                    # Python 项目 - 简化版本提取
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # 简单的版本提取
                    import re
                    version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
                    if version_match:
                        version_info["version"] = version_match.group(1)
                
                break
        
        return version_info
    
    def validate_dependencies(self) -> List[str]:
        """验证依赖关系"""
        print("\n🔗 验证依赖关系...")
        
        issues = []
        
        # 检查核心依赖
        core_version = self._get_repo_version(self.base_dir / "vabhub-core")["version"]
        
        for repo in ["vabhub-frontend", "vabhub-plugins"]:
            repo_path = self.base_dir / repo
            
            # 检查 package.json 或 requirements.txt 中的依赖
            package_json = repo_path / "package.json"
            requirements_txt = repo_path / "requirements.txt"
            
            if package_json.exists():
                with open(package_json, 'r') as f:
                    deps = json.load(f).get("dependencies", {})
                
                if "@vabhub/core" in deps:
                    # 检查版本兼容性
                    expected_version = f"^{core_version}"
                    if deps["@vabhub/core"] != expected_version:
                        issues.append(f"{repo} 的核心依赖版本不匹配")
            
            elif requirements_txt.exists():
                with open(requirements_txt, 'r') as f:
                    content = f.read()
                
                if "vabhub-core" in content:
                    # 简化检查
                    if core_version not in content:
                        issues.append(f"{repo} 的核心依赖版本不匹配")
        
        if not issues:
            print("  ✅ 所有依赖关系验证通过")
        else:
            print("  ⚠️ 发现依赖问题:")
            for issue in issues:
                print(f"    - {issue}")
        
        return issues
    
    def generate_sync_report(self) -> Dict:
        """生成同步报告"""
        print("\n📊 生成同步报告...")
        
        version_info = self.sync_versions()
        dependency_issues = self.validate_dependencies()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "sync_status": "成功" if not dependency_issues else "有警告",
            "repositories": version_info,
            "dependency_issues": dependency_issues,
            "summary": {
                "total_repos": len(self.repos),
                "synced_repos": len([v for v in version_info.values() if v["version"] != "未知"]),
                "issues_count": len(dependency_issues)
            }
        }
        
        return report
    
    def create_backup(self) -> bool:
        """创建配置备份"""
        print("\n💾 创建配置备份...")
        
        backup_dir = self.base_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            for repo in self.repos:
                repo_path = self.base_dir / repo
                
                # 备份配置文件
                for config_file in self.sync_config["config_files"]:
                    file_path = repo_path / config_file
                    if file_path.exists():
                        backup_path = backup_dir / repo / config_file
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        import shutil
                        shutil.copy2(file_path, backup_path)
                        print(f"  备份 {repo}/{config_file}")
            
            print(f"  ✅ 备份完成: {backup_dir}")
            return True
            
        except Exception as e:
            print(f"  ❌ 备份失败: {e}")
            return False
    
    def sync_configurations(self) -> bool:
        """同步配置文件"""
        print("\n⚙️ 同步配置文件...")
        
        # 这里可以实现配置文件的自动同步逻辑
        # 例如：将部署配置同步到各仓库
        
        print("  🔄 配置文件同步功能待实现")
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VabHub 多仓库同步工具")
    parser.add_argument("--sync", action="store_true", help="同步所有仓库")
    parser.add_argument("--report", action="store_true", help="生成同步报告")
    parser.add_argument("--backup", action="store_true", help="创建配置备份")
    parser.add_argument("--validate", action="store_true", help="验证依赖关系")
    parser.add_argument("--dir", default=".", help="工作目录路径")
    
    args = parser.parse_args()
    
    sync_manager = MultiRepoSync(Path(args.dir))
    
    if args.sync:
        # 完整同步流程
        if not sync_manager.clone_or_update_repos():
            return
        
        sync_manager.sync_versions()
        sync_manager.validate_dependencies()
        sync_manager.create_backup()
        sync_manager.sync_configurations()
        
        report = sync_manager.generate_sync_report()
        print("\n" + "="*50)
        print("✅ 同步完成")
        print(f"📊 总结: 同步了 {report['summary']['total_repos']} 个仓库")
        print(f"📈 状态: {report['sync_status']}")
    
    elif args.report:
        report = sync_manager.generate_sync_report()
        
        print("📋 同步报告")
        print("="*50)
        
        for repo, info in report["repositories"].items():
            status = "✅" if info["version"] != "未知" else "❌"
            print(f"{status} {repo}: {info['version']} ({info['last_commit']})")
        
        print(f"\n📊 总结: {report['summary']['synced_repos']}/{report['summary']['total_repos']} 个仓库已同步")
        print(f"📈 状态: {report['sync_status']}")
    
    elif args.backup:
        sync_manager.create_backup()
    
    elif args.validate:
        issues = sync_manager.validate_dependencies()
        
        if not issues:
            print("✅ 所有依赖关系验证通过")
        else:
            print("❌ 发现依赖问题:")
            for issue in issues:
                print(f"  - {issue}")
    
    else:
        # 默认显示简要状态
        sync_manager.clone_or_update_repos()
        report = sync_manager.generate_sync_report()
        
        print("🔍 VabHub 多仓库状态")
        print("="*50)
        
        for repo, info in report["repositories"].items():
            status = "✅" if info["version"] != "未知" else "❌"
            print(f"{status} {repo}: {info['version']}")
        
        print(f"\n📊 同步状态: {report['sync_status']}")

if __name__ == "__main__":
    main()