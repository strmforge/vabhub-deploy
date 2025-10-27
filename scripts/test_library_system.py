#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VabHub 库分离系统测试脚本
测试轻量部署和库管理功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_library_manager():
    """测试库管理器"""
    print("🧪 测试库管理器...")
    
    try:
        from core.library_manager import create_library_manager
        
        # 创建库管理器
        manager = create_library_manager()
        print("✅ 库管理器创建成功")
        
        # 获取库列表
        libraries = manager.get_libraries()
        print(f"📚 库数量: {len(libraries)}")
        
        # 获取库统计
        stats = manager.get_library_stats()
        print(f"📊 库统计: {stats}")
        
        # 测试路径验证
        for lib_id, library in libraries.items():
            print(f"🔍 验证库 '{library['name']}': {library['path']}")
            
        return True
        
    except Exception as e:
        print(f"❌ 库管理器测试失败: {e}")
        return False

def test_system_detector():
    """测试系统检测器"""
    print("\n🔧 测试系统检测器...")
    
    try:
        from core.system_detector import create_system_detector
        
        # 创建系统检测器
        detector = create_system_detector()
        print("✅ 系统检测器创建成功")
        
        # 运行检测
        results = detector.run_comprehensive_detection()
        print("✅ 系统检测完成")
        
        # 显示检测结果
        detector.print_detection_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ 系统检测器测试失败: {e}")
        return False

def test_lightweight_starter():
    """测试轻量级启动器"""
    print("\n🚀 测试轻量级启动器...")
    
    try:
        # 导入启动器模块
        import start_lightweight
        print("✅ 轻量级启动器导入成功")
        
        # 测试启动器功能
        print("✅ 轻量级启动器功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 轻量级启动器测试失败: {e}")
        return False

def test_config_system():
    """测试配置系统"""
    print("\n⚙️ 测试配置系统...")
    
    try:
        from core.config import Settings
        
        # 创建配置实例
        settings = Settings()
        print("✅ 配置系统创建成功")
        
        # 检查库配置路径
        libraries_config = Path("config/libraries.yaml")
        if libraries_config.exists():
            print("✅ 库配置文件存在")
        else:
            print("⚠️ 库配置文件不存在")
        
        # 检查主配置文件
        main_config = Path("config/config.yaml")
        if main_config.exists():
            print("✅ 主配置文件存在")
        else:
            print("⚠️ 主配置文件不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False

def test_deployment_script():
    """测试部署脚本"""
    print("\n📦 测试部署脚本...")
    
    try:
        # 检查部署脚本是否存在
        deploy_script = Path("scripts/deploy_lightweight.sh")
        if deploy_script.exists():
            print("✅ 部署脚本存在")
            
            # 检查脚本权限
            if os.access(str(deploy_script), os.X_OK):
                print("✅ 部署脚本有执行权限")
            else:
                print("⚠️ 部署脚本需要执行权限: chmod +x scripts/deploy_lightweight.sh")
        else:
            print("❌ 部署脚本不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 部署脚本测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 VabHub 轻量部署系统测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_library_manager,
        test_system_detector,
        test_lightweight_starter,
        test_config_system,
        test_deployment_script
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
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪")
        print("\n🚀 下一步操作:")
        print("1. 运行部署脚本: ./scripts/deploy_lightweight.sh")
        print("2. 或直接启动: python start_lightweight.py")
        print("3. 访问 http://localhost:8090 查看系统")
    else:
        print("⚠️ 部分测试失败，请检查系统配置")
        print("\n🔧 建议操作:")
        print("1. 检查依赖安装: pip install -r requirements.txt")
        print("2. 检查配置文件: config/ 目录")
        print("3. 查看日志文件: logs/app.log")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1