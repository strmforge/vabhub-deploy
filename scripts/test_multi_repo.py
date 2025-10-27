#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VabHub 多仓库部署测试脚本
测试多仓库架构和部署功能
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_docker_config():
    """测试 Docker 配置"""
    print("🐳 测试 Docker 配置...")
    
    # 检查 Docker Compose 文件
    compose_files = [
        "docker-compose.multi-repo.yml",
        "docker-compose.yml"
    ]
    
    for compose_file in compose_files:
        if Path(compose_file).exists():
            print(f"✅ Docker Compose 文件存在: {compose_file}")
        else:
            print(f"❌ Docker Compose 文件缺失: {compose_file}")
            return False
    
    # 检查 Dockerfile
    dockerfiles = [
        "docker/Dockerfile.core",
        "Dockerfile"
    ]
    
    for dockerfile in dockerfiles:
        if Path(dockerfile).exists():
            print(f"✅ Dockerfile 存在: {dockerfile}")
        else:
            print(f"❌ Dockerfile 缺失: {dockerfile}")
            return False
    
    return True

def test_deployment_scripts():
    """测试部署脚本"""
    print("\n📦 测试部署脚本...")
    
    scripts = [
        "scripts/deploy_multi_repo.sh",
        "scripts/deploy_lightweight.sh"
    ]
    
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"✅ 部署脚本存在: {script}")
            
            # 检查脚本权限
            if os.access(script_path, os.X_OK):
                print(f"✅ 脚本有执行权限: {script}")
            else:
                print(f"⚠️ 脚本需要执行权限: {script}")
        else:
            print(f"❌ 部署脚本缺失: {script}")
            return False
    
    return True

def test_plugin_system():
    """测试插件系统"""
    print("\n🔌 测试插件系统...")
    
    try:
        from app.core.plugin_manager import PluginManager
        
        # 创建插件管理器
        manager = PluginManager()
        print("✅ 插件管理器创建成功")
        
        # 检测插件
        plugins = manager.detect_plugins()
        print(f"📊 检测到 {len(plugins)} 个插件")
        
        # 获取插件统计
        stats = manager.get_plugin_stats()
        print(f"📈 插件统计: {stats}")
        
        # 检查插件目录
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            print("✅ 插件目录存在")
            
            # 检查示例插件
            example_plugin = plugins_dir / "example.py"
            if example_plugin.exists():
                print("✅ 示例插件存在")
            else:
                print("⚠️ 示例插件缺失")
        else:
            print("❌ 插件目录缺失")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 插件系统测试失败: {e}")
        return False

def test_config_files():
    """测试配置文件"""
    print("\n⚙️ 测试配置文件...")
    
    config_files = [
        "config/config.yaml",
        "config/libraries.yaml",
        "config/categories.yaml"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ 配置文件存在: {config_file}")
        else:
            print(f"❌ 配置文件缺失: {config_file}")
            return False
    
    return True

def test_docker_commands():
    """测试 Docker 命令"""
    print("\n🔧 测试 Docker 命令...")
    
    try:
        # 检查 Docker 是否可用
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker 命令可用")
        else:
            print("❌ Docker 命令不可用")
            return False
        
        # 检查 Docker Compose
        result = subprocess.run(["docker-compose", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose 命令可用")
        else:
            print("❌ Docker Compose 命令不可用")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Docker 命令测试失败: {e}")
        return False

def test_multi_repo_structure():
    """测试多仓库结构"""
    print("\n🏗️ 测试多仓库结构...")
    
    # 检查多仓库文档
    if Path("MULTI_REPO_ARCHITECTURE.md").exists():
        print("✅ 多仓库架构文档存在")
    else:
        print("❌ 多仓库架构文档缺失")
        return False
    
    # 检查部署指南
    if Path("README_MULTI_REPO.md").exists():
        print("✅ 多仓库部署指南存在")
    else:
        print("❌ 多仓库部署指南缺失")
        return False
    
    # 检查核心目录结构
    core_dirs = ["app", "config", "docker", "scripts", "plugins"]
    for dir_name in core_dirs:
        if Path(dir_name).exists():
            print(f"✅ 核心目录存在: {dir_name}")
        else:
            print(f"❌ 核心目录缺失: {dir_name}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("🎯 VabHub 多仓库部署系统测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_multi_repo_structure,
        test_docker_config,
        test_deployment_scripts,
        test_plugin_system,
        test_config_files,
        test_docker_commands
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 统计测试结果
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！多仓库部署系统准备就绪")
        print("\n🚀 下一步操作:")
        print("1. 初始化部署: ./scripts/deploy_multi_repo.sh init")
        print("2. 启动服务: ./scripts/deploy_multi_repo.sh start")
        print("3. 访问系统: http://localhost:8090")
        print("4. 查看文档: README_MULTI_REPO.md")
    else:
        print("⚠️ 部分测试失败，请检查系统配置")
        print("\n🔧 建议操作:")
        print("1. 检查 Docker 和 Docker Compose 安装")
        print("2. 检查项目目录结构")
        print("3. 查看具体错误信息")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)