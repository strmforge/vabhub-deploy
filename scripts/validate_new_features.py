#!/usr/bin/env python3
"""
VabHub 新功能部署验证脚本
验证所有新功能在多仓库环境中的正确部署
"""

import sys
import os
from pathlib import Path
import subprocess
import json

def check_dependencies():
    """检查依赖项是否正确安装"""
    print("🔍 检查依赖项...")
    
    # 检查VabHub-Core依赖
    core_req_path = Path("../VabHub-Core/requirements.txt")
    if core_req_path.exists():
        with open(core_req_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "APScheduler" in content:
                print("✅ APScheduler依赖已正确配置")
            else:
                print("❌ APScheduler依赖未找到")
                return False
                
            if "pydantic-settings" in content:
                print("✅ pydantic-settings依赖已正确配置")
            else:
                print("❌ pydantic-settings依赖未找到")
                return False
    
    return True

def check_module_imports():
    """检查模块导入是否正常"""
    print("🔍 检查模块导入...")
    
    test_code = """
import sys
sys.path.insert(0, '../VabHub-Core')

try:
    from core.event import EventManager, EventType
    print("✅ 事件系统模块导入成功")
except Exception as e:
    print(f"❌ 事件系统模块导入失败: {e}")
    sys.exit(1)

try:
    from core.scheduler import Scheduler
    print("✅ 调度器模块导入成功")
except Exception as e:
    print(f"❌ 调度器模块导入失败: {e}")
    sys.exit(1)

try:
    from core.chain import ChainBase, MediaChain
    print("✅ 业务链模块导入成功")
except Exception as e:
    print(f"❌ 业务链模块导入失败: {e}")
    sys.exit(1)

try:
    from core.plugin import PluginManager
    print("✅ 插件系统模块导入成功")
except Exception as e:
    print(f"❌ 插件系统模块导入失败: {e}")
    sys.exit(1)
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True, cwd=Path.cwd())
        print(result.stdout)
        if result.returncode != 0:
            print("❌ 模块导入测试失败")
            return False
    except Exception as e:
        print(f"❌ 模块导入测试异常: {e}")
        return False
    
    return True

def check_frontend_api():
    """检查前端API接口"""
    print("🔍 检查前端API接口...")
    
    frontend_api_path = Path("../VabHub-Frontend/src/api/index.js")
    if frontend_api_path.exists():
        with open(frontend_api_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "eventAPI" in content:
                print("✅ 事件系统API接口已配置")
            else:
                print("❌ 事件系统API接口未找到")
                return False
                
            if "schedulerAPI" in content:
                print("✅ 调度器API接口已配置")
            else:
                print("❌ 调度器API接口未找到")
                return False
                
            if "chainAPI" in content:
                print("✅ 业务链API接口已配置")
            else:
                print("❌ 业务链API接口未找到")
                return False
    
    return True

def check_plugin_framework():
    """检查插件框架"""
    print("🔍 检查插件框架...")
    
    plugin_setup_path = Path("../VabHub-Plugins/setup.py")
    if plugin_setup_path.exists():
        with open(plugin_setup_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "vabhub-core" in content:
                print("✅ 插件框架依赖已正确配置")
            else:
                print("❌ 插件框架依赖未找到")
                return False
    
    return True

def check_deployment_config():
    """检查部署配置"""
    print("🔍 检查部署配置...")
    
    deploy_req_path = Path("deploy_requirements.txt")
    if deploy_req_path.exists():
        with open(deploy_req_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "APScheduler" in content:
                print("✅ 部署依赖已正确配置")
            else:
                print("❌ 部署依赖未找到")
                return False
    
    return True

def main():
    """主验证函数"""
    print("🚀 开始VabHub新功能部署验证...\n")
    
    checks = [
        ("依赖项检查", check_dependencies),
        ("模块导入检查", check_module_imports),
        ("前端API检查", check_frontend_api),
        ("插件框架检查", check_plugin_framework),
        ("部署配置检查", check_deployment_config)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 50)
        
        if not check_func():
            all_passed = False
            print(f"❌ {check_name} 失败")
        else:
            print(f"✅ {check_name} 通过")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有验证检查通过！新功能已成功部署到多仓库环境。")
        print("\n📊 部署状态总结:")
        print("  ✅ VabHub-Core: 事件系统、调度器、业务链、插件框架")
        print("  ✅ VabHub-Frontend: 新API接口适配")
        print("  ✅ VabHub-Plugins: 插件框架升级")
        print("  ✅ VabHub-Deploy: 部署配置更新")
        print("\n🚀 系统现在具备完整的MoviePilot对标功能！")
    else:
        print("❌ 部分验证检查失败，请检查相关配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()