#!/usr/bin/env python3
"""
VabHub 多仓库依赖管理工具
用于管理和验证跨仓库的依赖关系
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
import requests

class DependencyManager:
    """多仓库依赖管理器"""
    
    def __init__(self, org_name: str = "vabhub"):
        self.org_name = org_name
        self.repositories = {
            "vabhub-core": {
                "language": "python",
                "package_name": "vabhub-core",
                "dependencies": []
            },
            "vabhub-frontend": {
                "language": "javascript",
                "package_name": "@vabhub/frontend",
                "dependencies": ["vabhub-core"]
            },
            "vabhub-plugins": {
                "language": "python",
                "package_name": "vabhub-plugins",
                "dependencies": ["vabhub-core"]
            },
            "vabhub-resources": {
                "language": "none",
                "package_name": "vabhub-resources",
                "dependencies": []
            },
            "vabhub-deploy": {
                "language": "yaml",
                "package_name": "vabhub-deploy",
                "dependencies": ["vabhub-core", "vabhub-frontend", "vabhub-plugins"]
            }
        }
    
    def get_package_info(self, repo: str, version: str = "latest") -> Optional[Dict]:
        """获取包信息"""
        repo_info = self.repositories.get(repo)
        if not repo_info:
            return None
        
        if repo_info["language"] == "python":
            return self._get_pypi_package_info(repo_info["package_name"], version)
        elif repo_info["language"] == "javascript":
            return self._get_npm_package_info(repo_info["package_name"], version)
        else:
            return {"name": repo_info["package_name"], "version": version}
    
    def _get_pypi_package_info(self, package_name: str, version: str) -> Optional[Dict]:
        """从 PyPI 获取包信息"""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                if version == "latest":
                    version = data["info"]["version"]
                
                return {
                    "name": package_name,
                    "version": version,
                    "latest_version": data["info"]["version"],
                    "summary": data["info"]["summary"],
                    "requires_dist": data["info"].get("requires_dist", [])
                }
        except Exception as e:
            print(f"获取 PyPI 包信息失败: {e}")
        
        return None
    
    def _get_npm_package_info(self, package_name: str, version: str) -> Optional[Dict]:
        """从 NPM 获取包信息"""
        try:
            url = f"https://registry.npmjs.org/{package_name}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                
                if version == "latest":
                    version = data["dist-tags"]["latest"]
                
                version_info = data["versions"].get(version)
                if version_info:
                    return {
                        "name": package_name,
                        "version": version,
                        "latest_version": data["dist-tags"]["latest"],
                        "description": version_info.get("description", ""),
                        "dependencies": version_info.get("dependencies", {})
                    }
        except Exception as e:
            print(f"获取 NPM 包信息失败: {e}")
        
        return None
    
    def check_dependency_compatibility(self, repo: str, target_version: str) -> Dict:
        """检查依赖兼容性"""
        repo_info = self.repositories.get(repo)
        if not repo_info:
            return {"compatible": False, "issues": [f"未知仓库: {repo}"]}
        
        issues = []
        
        for dep_repo in repo_info["dependencies"]:
            dep_info = self.get_package_info(dep_repo)
            if not dep_info:
                issues.append(f"无法获取 {dep_repo} 的包信息")
                continue
            
            # 简单的版本兼容性检查
            current_major = dep_info["version"].split('.')[0]
            target_major = target_version.split('.')[0]
            
            if current_major != target_major:
                issues.append(
                    f"{dep_repo} 主版本不兼容: "
                    f"当前 {dep_info['version']}, 目标 {target_version}"
                )
        
        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "dependencies": [
                {
                    "repo": dep,
                    "current_version": self.get_package_info(dep)["version"] if self.get_package_info(dep) else "未知",
                    "compatible": True  # 简化检查
                }
                for dep in repo_info["dependencies"]
            ]
        }
    
    def generate_dependency_report(self) -> Dict:
        """生成依赖关系报告"""
        report = {
            "timestamp": "2025-10-26T00:00:00Z",
            "repositories": {},
            "dependency_graph": {},
            "compatibility_issues": []
        }
        
        # 收集各仓库信息
        for repo, info in self.repositories.items():
            package_info = self.get_package_info(repo)
            
            report["repositories"][repo] = {
                "language": info["language"],
                "package_name": info["package_name"],
                "current_version": package_info["version"] if package_info else "未知",
                "latest_version": package_info["latest_version"] if package_info else "未知",
                "dependencies": info["dependencies"]
            }
        
        # 构建依赖图
        for repo, info in self.repositories.items():
            report["dependency_graph"][repo] = {
                "dependencies": info["dependencies"],
                "dependents": [
                    dependent for dependent, dep_info in self.repositories.items()
                    if repo in dep_info["dependencies"]
                ]
            }
        
        # 检查兼容性问题
        for repo in self.repositories:
            compatibility = self.check_dependency_compatibility(repo, "1.0.0")
            if not compatibility["compatible"]:
                report["compatibility_issues"].extend(compatibility["issues"])
        
        return report
    
    def validate_docker_compose(self, compose_file: Path) -> bool:
        """验证 Docker Compose 文件中的依赖关系"""
        try:
            with open(compose_file, 'r') as f:
                compose_config = yaml.safe_load(f)
            
            services = compose_config.get('services', {})
            issues = []
            
            # 检查服务依赖
            for service_name, service_config in services.items():
                depends_on = service_config.get('depends_on', [])
                
                # 验证依赖服务是否存在
                for dependency in depends_on:
                    if dependency not in services:
                        issues.append(f"服务 {service_name} 依赖未知服务: {dependency}")
            
            if issues:
                print("Docker Compose 依赖问题:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            
            return True
            
        except Exception as e:
            print(f"验证 Docker Compose 文件失败: {e}")
            return False
    
    def generate_dependency_diagram(self) -> str:
        """生成依赖关系图（Mermaid 格式）"""
        diagram = "graph TD\n"
        
        for repo, info in self.repositories.items():
            for dependency in info["dependencies"]:
                diagram += f"    {dependency} --> {repo}\n"
        
        return diagram

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VabHub 多仓库依赖管理工具")
    parser.add_argument("--report", action="store_true", help="生成依赖报告")
    parser.add_argument("--check", metavar="REPO", help="检查指定仓库的依赖兼容性")
    parser.add_argument("--diagram", action="store_true", help="生成依赖关系图")
    parser.add_argument("--validate-compose", metavar="FILE", help="验证 Docker Compose 文件")
    
    args = parser.parse_args()
    
    manager = DependencyManager()
    
    if args.report:
        report = manager.generate_dependency_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.check:
        compatibility = manager.check_dependency_compatibility(args.check, "1.0.0")
        print(f"{args.check} 依赖兼容性检查:")
        print(f"兼容性: {'✅ 通过' if compatibility['compatible'] else '❌ 失败'}")
        
        if compatibility["issues"]:
            print("问题:")
            for issue in compatibility["issues"]:
                print(f"  - {issue}")
    
    elif args.diagram:
        diagram = manager.generate_dependency_diagram()
        print("依赖关系图 (Mermaid):")
        print(diagram)
    
    elif args.validate_compose:
        compose_file = Path(args.validate_compose)
        if manager.validate_docker_compose(compose_file):
            print("✅ Docker Compose 文件验证通过")
        else:
            print("❌ Docker Compose 文件验证失败")
    
    else:
        # 默认显示简要报告
        report = manager.generate_dependency_report()
        
        print("📊 VabHub 多仓库依赖状态")
        print("=" * 50)
        
        for repo, info in report["repositories"].items():
            status = "✅" if info["current_version"] == info["latest_version"] else "⚠️"
            print(f"{status} {repo} ({info['language']})")
            print(f"   版本: {info['current_version']} (最新: {info['latest_version']})")
            
            if info["dependencies"]:
                print(f"   依赖: {', '.join(info['dependencies'])}")
            print()
        
        if report["compatibility_issues"]:
            print("🚨 兼容性问题:")
            for issue in report["compatibility_issues"]:
                print(f"  - {issue}")

if __name__ == "__main__":
    main()