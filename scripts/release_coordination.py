#!/usr/bin/env python3
"""
VabHub 多仓库发布协调脚本
用于协调多个仓库的版本发布和依赖管理
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests
from datetime import datetime

class ReleaseCoordinator:
    """多仓库发布协调器"""
    
    def __init__(self, org_name: str = "vabhub"):
        self.org_name = org_name
        self.repos = [
            "vabhub-core",
            "vabhub-frontend", 
            "vabhub-plugins",
            "vabhub-resources",
            "vabhub-deploy"
        ]
        
        # 仓库依赖关系
        self.dependencies = {
            "vabhub-core": [],
            "vabhub-plugins": ["vabhub-core"],
            "vabhub-frontend": ["vabhub-core"],
            "vabhub-resources": [],
            "vabhub-deploy": ["vabhub-core", "vabhub-frontend", "vabhub-plugins"]
        }
        
    def get_latest_release(self, repo: str) -> Optional[str]:
        """获取仓库的最新发布版本"""
        try:
            url = f"https://api.github.com/repos/{self.org_name}/{repo}/releases/latest"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()["tag_name"]
        except Exception as e:
            print(f"获取 {repo} 最新版本失败: {e}")
        return None
    
    def check_dependency_compatibility(self, repo: str, target_version: str) -> bool:
        """检查依赖兼容性"""
        deps = self.dependencies.get(repo, [])
        
        for dep in deps:
            latest_version = self.get_latest_release(dep)
            if not latest_version:
                print(f"⚠️ 无法获取 {dep} 的最新版本")
                continue
                
            # 简单的版本兼容性检查（实际应该使用语义化版本比较）
            if latest_version.split('.')[0] != target_version.split('.')[0]:
                print(f"❌ {repo} 依赖的 {dep} 主版本不兼容")
                return False
                
        return True
    
    def generate_release_plan(self, version: str) -> Dict:
        """生成发布计划"""
        plan = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "repositories": {},
            "dependencies": {},
            "release_order": []
        }
        
        # 拓扑排序确定发布顺序
        released = set()
        
        while len(released) < len(self.repos):
            for repo in self.repos:
                if repo in released:
                    continue
                    
                # 检查依赖是否都已发布
                deps_ready = all(dep in released for dep in self.dependencies.get(repo, []))
                
                if deps_ready:
                    plan["release_order"].append(repo)
                    released.add(repo)
                    
                    # 记录依赖信息
                    plan["dependencies"][repo] = self.dependencies.get(repo, [])
                    plan["repositories"][repo] = {
                        "current_version": self.get_latest_release(repo),
                        "target_version": version,
                        "release_ready": self.check_dependency_compatibility(repo, version)
                    }
        
        return plan
    
    def validate_release_plan(self, plan: Dict) -> bool:
        """验证发布计划"""
        issues = []
        
        for repo, info in plan["repositories"].items():
            if not info["release_ready"]:
                issues.append(f"{repo} 依赖检查失败")
            
            # 检查版本格式
            if not self.is_valid_version(info["target_version"]):
                issues.append(f"{repo} 目标版本格式无效: {info['target_version']}")
        
        if issues:
            print("❌ 发布计划验证失败:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✅ 发布计划验证通过")
        return True
    
    def is_valid_version(self, version: str) -> bool:
        """检查版本号格式"""
        try:
            parts = version.split('.')
            if len(parts) != 3:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
            
            return True
        except:
            return False
    
    def execute_release_plan(self, plan: Dict, dry_run: bool = True):
        """执行发布计划"""
        if not self.validate_release_plan(plan):
            return False
        
        mode = "[DRY RUN]" if dry_run else "[EXECUTING]"
        print(f"\n🚀 {mode} 开始执行发布计划 v{plan['version']}")
        
        for repo in plan["release_order"]:
            repo_info = plan["repositories"][repo]
            
            print(f"\n📦 处理 {repo}")
            print(f"   当前版本: {repo_info['current_version'] or '无'}")
            print(f"   目标版本: {repo_info['target_version']}")
            
            if not dry_run:
                # 实际执行发布操作
                success = self.release_repository(repo, plan["version"])
                if not success:
                    print(f"❌ {repo} 发布失败")
                    return False
                print(f"✅ {repo} 发布成功")
            else:
                print(f"   {mode} 跳过实际发布操作")
        
        return True
    
    def release_repository(self, repo: str, version: str) -> bool:
        """发布单个仓库（模拟实现）"""
        # 这里应该实现实际的发布逻辑
        # 包括：创建标签、生成发布说明、发布到包管理器等
        
        print(f"   📝 为 {repo} 创建标签 v{version}")
        print(f"   📋 生成发布说明")
        print(f"   📦 发布到包管理器")
        
        # 模拟发布过程
        import time
        time.sleep(1)  # 模拟发布耗时
        
        return True
    
    def generate_changelog(self, version: str) -> str:
        """生成变更日志"""
        changelog = f"# VabHub v{version} 发布说明\n\n"
        changelog += f"**发布日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for repo in self.repos:
            changelog += f"## {repo}\n\n"
            changelog += "### 新功能\n- 功能1\n- 功能2\n\n"
            changelog += "### 修复\n- 修复1\n- 修复2\n\n"
            changelog += "### 改进\n- 改进1\n- 改进2\n\n"
        
        return changelog

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VabHub 多仓库发布协调工具")
    parser.add_argument("version", help="目标版本号 (格式: x.y.z)")
    parser.add_argument("--dry-run", action="store_true", help="干运行模式")
    parser.add_argument("--generate-changelog", action="store_true", help="生成变更日志")
    
    args = parser.parse_args()
    
    coordinator = ReleaseCoordinator()
    
    if args.generate_changelog:
        changelog = coordinator.generate_changelog(args.version)
        print(changelog)
        return
    
    # 生成发布计划
    plan = coordinator.generate_release_plan(args.version)
    
    # 打印发布计划
    print("📋 发布计划概览:")
    print(f"版本: v{plan['version']}")
    print(f"发布日期: {plan['timestamp']}")
    print(f"发布顺序: {' -> '.join(plan['release_order'])}")
    
    print("\n📊 仓库状态:")
    for repo, info in plan["repositories"].items():
        status = "✅" if info["release_ready"] else "❌"
        print(f"{status} {repo}: {info['current_version'] or '无'} -> v{info['target_version']}")
    
    # 执行发布计划
    coordinator.execute_release_plan(plan, dry_run=args.dry_run)

if __name__ == "__main__":
    main()