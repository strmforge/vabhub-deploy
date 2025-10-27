#!/usr/bin/env python3
"""
VabHub 多仓库版本管理工具
用于统一管理多个仓库的版本号和发布流程
"""

import json
import yaml
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
import argparse

class VersionManager:
    """多仓库版本管理器"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.repos = {
            "vabhub-core": {
                "path": base_dir / "vabhub-core",
                "type": "python",
                "version_file": "setup.py",
                "dependencies": []
            },
            "vabhub-frontend": {
                "path": base_dir / "vabhub-frontend", 
                "type": "javascript",
                "version_file": "package.json",
                "dependencies": ["vabhub-core"]
            },
            "vabhub-plugins": {
                "path": base_dir / "vabhub-plugins",
                "type": "python", 
                "version_file": "setup.py",
                "dependencies": ["vabhub-core"]
            },
            "vabhub-resources": {
                "path": base_dir / "vabhub-resources",
                "type": "resources",
                "version_file": "VERSION",
                "dependencies": []
            },
            "vabhub-deploy": {
                "path": base_dir / "vabhub-deploy",
                "type": "deploy",
                "version_file": "VERSION",
                "dependencies": ["vabhub-core", "vabhub-frontend", "vabhub-plugins"]
            }
        }
    
    def get_current_version(self, repo: str) -> Optional[str]:
        """获取仓库当前版本号"""
        repo_info = self.repos.get(repo)
        if not repo_info or not repo_info["path"].exists():
            return None
        
        version_file = repo_info["path"] / repo_info["version_file"]
        
        if not version_file.exists():
            return None
        
        if repo_info["type"] == "python":
            # 解析 setup.py
            with open(version_file, 'r') as f:
                content = f.read()
            
            version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
            if version_match:
                return version_match.group(1)
        
        elif repo_info["type"] == "javascript":
            # 解析 package.json
            with open(version_file, 'r') as f:
                package_info = json.load(f)
            
            return package_info.get("version")
        
        elif repo_info["type"] in ["resources", "deploy"]:
            # 解析 VERSION 文件
            with open(version_file, 'r') as f:
                return f.read().strip()
        
        return None
    
    def set_version(self, repo: str, new_version: str) -> bool:
        """设置仓库版本号"""
        repo_info = self.repos.get(repo)
        if not repo_info or not repo_info["path"].exists():
            print(f"❌ 仓库不存在: {repo}")
            return False
        
        version_file = repo_info["path"] / repo_info["version_file"]
        
        if repo_info["type"] == "python":
            # 更新 setup.py
            with open(version_file, 'r') as f:
                content = f.read()
            
            # 替换版本号
            new_content = re.sub(
                r"version=['\"]([^'\"]+)['\"]", 
                f"version='{new_version}'", 
                content
            )
            
            with open(version_file, 'w') as f:
                f.write(new_content)
        
        elif repo_info["type"] == "javascript":
            # 更新 package.json
            with open(version_file, 'r') as f:
                package_info = json.load(f)
            
            package_info["version"] = new_version
            
            with open(version_file, 'w') as f:
                json.dump(package_info, f, indent=2)
        
        elif repo_info["type"] in ["resources", "deploy"]:
            # 更新 VERSION 文件
            with open(version_file, 'w') as f:
                f.write(new_version + "\n")
        
        print(f"✅ {repo} 版本更新为: {new_version}")
        return True
    
    def validate_version_format(self, version: str) -> bool:
        """验证版本号格式"""
        # 语义化版本格式: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
        pattern = r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        return re.match(pattern, version) is not None
    
    def check_dependency_compatibility(self, repo: str, target_version: str) -> Dict:
        """检查依赖兼容性"""
        repo_info = self.repos.get(repo)
        if not repo_info:
            return {"compatible": False, "issues": [f"未知仓库: {repo}"]}
        
        issues = []
        
        for dep_repo in repo_info["dependencies"]:
            dep_version = self.get_current_version(dep_repo)
            if not dep_version:
                issues.append(f"无法获取 {dep_repo} 的版本号")
                continue
            
            # 简单的版本兼容性检查
            current_major = dep_version.split('.')[0]
            target_major = target_version.split('.')[0]
            
            if current_major != target_major:
                issues.append(
                    f"{dep_repo} 主版本不兼容: "
                    f"当前 {dep_version}, 目标 {target_version}"
                )
        
        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "dependencies": repo_info["dependencies"]
        }
    
    def generate_version_report(self) -> Dict:
        """生成版本报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "repositories": {},
            "compatibility_issues": [],
            "summary": {
                "total_repos": len(self.repos),
                "versioned_repos": 0,
                "compatible_repos": 0
            }
        }
        
        for repo in self.repos:
            current_version = self.get_current_version(repo)
            
            if current_version:
                report["summary"]["versioned_repos"] += 1
                
                # 检查兼容性
                compatibility = self.check_dependency_compatibility(repo, current_version)
                
                if compatibility["compatible"]:
                    report["summary"]["compatible_repos"] += 1
                else:
                    report["compatibility_issues"].extend(compatibility["issues"])
            
            report["repositories"][repo] = {
                "current_version": current_version,
                "type": self.repos[repo]["type"],
                "dependencies": self.repos[repo]["dependencies"]
            }
        
        return report
    
    def create_git_tag(self, repo: str, version: str) -> bool:
        """创建 Git 标签"""
        repo_info = self.repos.get(repo)
        if not repo_info or not repo_info["path"].exists():
            return False
        
        try:
            # 提交版本变更
            subprocess.run(["git", "add", repo_info["version_file"]], 
                         cwd=repo_info["path"], check=True)
            
            subprocess.run(["git", "commit", "-m", f"chore: bump version to {version}"], 
                         cwd=repo_info["path"], check=True)
            
            # 创建标签
            tag_name = f"v{version}"
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Version {version}"], 
                         cwd=repo_info["path"], check=True)
            
            print(f"✅ {repo} 标签创建成功: {tag_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {repo} 标签创建失败: {e}")
            return False
    
    def update_all_versions(self, new_version: str, create_tags: bool = False) -> bool:
        """更新所有仓库版本号"""
        if not self.validate_version_format(new_version):
            print(f"❌ 版本号格式无效: {new_version}")
            return False
        
        print(f"🚀 开始更新所有仓库版本为: {new_version}")
        
        # 按依赖顺序更新
        release_order = self._get_release_order()
        
        success_count = 0
        
        for repo in release_order:
            # 检查依赖兼容性
            compatibility = self.check_dependency_compatibility(repo, new_version)
            
            if not compatibility["compatible"]:
                print(f"⚠️  {repo} 依赖检查失败:")
                for issue in compatibility["issues"]:
                    print(f"    - {issue}")
                continue
            
            # 更新版本号
            if self.set_version(repo, new_version):
                success_count += 1
                
                # 创建 Git 标签
                if create_tags:
                    self.create_git_tag(repo, new_version)
        
        print(f"\n📊 版本更新完成: {success_count}/{len(self.repos)} 个仓库更新成功")
        return success_count == len(self.repos)
    
    def _get_release_order(self) -> List[str]:
        """获取发布顺序（拓扑排序）"""
        # 简单的拓扑排序实现
        released = set()
        order = []
        
        while len(released) < len(self.repos):
            for repo, info in self.repos.items():
                if repo in released:
                    continue
                
                # 检查依赖是否都已发布
                deps_ready = all(dep in released for dep in info["dependencies"])
                
                if deps_ready:
                    order.append(repo)
                    released.add(repo)
        
        return order
    
    def generate_changelog(self, version: str, since_version: Optional[str] = None) -> str:
        """生成变更日志"""
        changelog = f"# VabHub v{version} 发布说明\n\n"
        changelog += f"**发布日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if since_version:
            changelog += f"**变更范围**: v{since_version} → v{version}\n\n"
        
        for repo in self.repos:
            current_version = self.get_current_version(repo)
            
            changelog += f"## {repo}\n\n"
            changelog += f"**版本**: {current_version or '未知'}\n\n"
            
            # 这里可以集成 git log 分析来生成实际的变更内容
            changelog += "### 新功能\n- 功能1\n- 功能2\n\n"
            changelog += "### 修复\n- 修复1\n- 修复2\n\n"
            changelog += "### 改进\n- 改进1\n- 改进2\n\n"
        
        return changelog

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="VabHub 多仓库版本管理工具")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="显示版本状态")
    status_parser.add_argument("--detailed", action="store_true", help="详细输出")
    
    # update 命令
    update_parser = subparsers.add_parser("update", help="更新版本号")
    update_parser.add_argument("version", help="新版本号")
    update_parser.add_argument("--repo", default="all", help="指定仓库（默认：所有仓库）")
    update_parser.add_argument("--tag", action="store_true", help="创建 Git 标签")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证版本兼容性")
    
    # changelog 命令
    changelog_parser = subparsers.add_parser("changelog", help="生成变更日志")
    changelog_parser.add_argument("version", help="目标版本号")
    changelog_parser.add_argument("--since", help="起始版本号")
    
    # tag 命令
    tag_parser = subparsers.add_parser("tag", help="创建 Git 标签")
    tag_parser.add_argument("version", help="版本号")
    tag_parser.add_argument("--repo", default="all", help="指定仓库")
    
    # dashboard 命令
    dashboard_parser = subparsers.add_parser("dashboard", help="显示版本仪表板")
    
    args = parser.parse_args()
    
    manager = VersionManager(Path(".."))  # 从 VabHub-Deploy 目录向上查找
    
    if args.command == "status":
        report = manager.generate_version_report()
        
        if args.detailed:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print("📋 版本状态报告")
            print("=" * 50)
            
            for repo, info in report["repositories"].items():
                status = "✅" if info["current_version"] else "❌"
                print(f"{status} {repo}: {info['current_version'] or '无版本'}")
            
            print(f"\n📊 总结: {report['summary']['versioned_repos']}/{report['summary']['total_repos']} 个仓库有版本号")
            
            if report["compatibility_issues"]:
                print("\n🚨 兼容性问题:")
                for issue in report["compatibility_issues"]:
                    print(f"  - {issue}")
    
    elif args.command == "update":
        if args.repo == "all":
            success = manager.update_all_versions(args.version, args.tag)
            if not success:
                sys.exit(1)
        else:
            if args.repo not in manager.repos:
                print(f"❌ 未知仓库: {args.repo}")
                sys.exit(1)
            
            if manager.set_version(args.repo, args.version):
                if args.tag:
                    manager.create_git_tag(args.repo, args.version)
    
    elif args.command == "validate":
        report = manager.generate_version_report()
        
        if report["compatibility_issues"]:
            print("❌ 版本兼容性检查失败:")
            for issue in report["compatibility_issues"]:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✅ 所有版本兼容性检查通过")
    
    elif args.command == "changelog":
        changelog = manager.generate_changelog(args.version, args.since)
        print(changelog)
    
    elif args.command == "tag":
        if args.repo == "all":
            for repo in manager.repos:
                manager.create_git_tag(repo, args.version)
        else:
            if args.repo not in manager.repos:
                print(f"❌ 未知仓库: {args.repo}")
                sys.exit(1)
            
            manager.create_git_tag(args.repo, args.version)
    
    elif args.command == "dashboard":
        report = manager.generate_version_report()
        
        print("📊 VabHub 版本状态仪表板"
        print("=" * 50)
        
        for repo, info in report["repositories"].items():
            current_version = info["current_version"]
            
            if current_version:
                compatibility = manager.check_dependency_compatibility(repo, current_version)
                status = "✅" if compatibility["compatible"] else "❌"
                print(f"{status} {repo}: v{current_version}")
            else:
                print(f"❌ {repo}: 无版本号")
        
        print(f"\n📈 发布状态: {report['summary']['versioned_repos']}/{report['summary']['total_repos']} 个仓库有版本号")
        print(f"🔗 依赖状态: {'✅ 正常' if not report['compatibility_issues'] else '❌ 有问题'}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()