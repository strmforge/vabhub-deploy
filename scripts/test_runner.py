#!/usr/bin/env python3
"""
VabHub 多仓库测试运行器
统一管理所有测试套件的执行和报告生成
"""

import argparse
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class TestRunner:
    """测试运行器主类"""
    
    def __init__(self, config_path: str = "tests/config/test_config.yaml"):
        self.config_path = config_path
        self.results = {}
        self.start_time = None
        
    def load_config(self) -> Dict:
        """加载测试配置"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            print("警告: PyYAML 未安装，使用默认配置")
            return self.default_config()
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
            return self.default_config()
    
    def default_config(self) -> Dict:
        """默认测试配置"""
        return {
            'test_suites': {
                'unit': {
                    'description': '单元测试套件',
                    'patterns': ['tests/unit/test_*.py'],
                    'timeout': 300,
                    'parallel': True
                },
                'integration': {
                    'description': '集成测试套件',
                    'patterns': ['tests/integration/test_*.py'],
                    'requires': ['docker'],
                    'timeout': 600
                },
                'e2e': {
                    'description': '端到端测试套件',
                    'patterns': ['tests/e2e/test_*.py'],
                    'requires': ['selenium', 'test_environment'],
                    'timeout': 1200
                },
                'performance': {
                    'description': '性能测试套件',
                    'patterns': ['tests/performance/test_*.py'],
                    'requires': ['locust'],
                    'timeout': 1800
                }
            }
        }
    
    def check_requirements(self, suite_config: Dict) -> bool:
        """检查测试套件依赖"""
        requirements = suite_config.get('requires', [])
        
        for req in requirements:
            if req == 'docker':
                if not self.check_docker():
                    print(f"错误: Docker 不可用，无法运行测试")
                    return False
            elif req == 'selenium':
                if not self.check_selenium():
                    print(f"警告: Selenium 未安装，某些测试可能失败")
            elif req == 'locust':
                if not self.check_locust():
                    print(f"警告: Locust 未安装，性能测试不可用")
                    return False
            elif req == 'test_environment':
                if not self.check_test_environment():
                    print(f"错误: 测试环境未就绪")
                    return False
        
        return True
    
    def check_docker(self) -> bool:
        """检查 Docker 是否可用"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_selenium(self) -> bool:
        """检查 Selenium 是否安装"""
        try:
            import selenium
            return True
        except ImportError:
            return False
    
    def check_locust(self) -> bool:
        """检查 Locust 是否安装"""
        try:
            import locust
            return True
        except ImportError:
            return False
    
    def check_test_environment(self) -> bool:
        """检查测试环境"""
        # 检查测试环境是否运行
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=test', '--format', '{{.Names}}'],
                                 capture_output=True, text=True)
            return 'test' in result.stdout
        except:
            return False
    
    def run_test_suite(self, suite_name: str, suite_config: Dict) -> Dict:
        """运行单个测试套件"""
        print(f"\n🚀 开始运行 {suite_name} 测试套件")
        print(f"描述: {suite_config['description']}")
        
        # 检查依赖
        if not self.check_requirements(suite_config):
            return {
                'suite': suite_name,
                'status': 'skipped',
                'reason': '依赖检查失败',
                'duration': 0
            }
        
        # 构建测试命令
        patterns = suite_config['patterns']
        timeout = suite_config.get('timeout', 300)
        
        test_files = []
        for pattern in patterns:
            for path in Path('.').glob(pattern):
                if path.is_file():
                    test_files.append(str(path))
        
        if not test_files:
            print(f"⚠️  未找到测试文件: {patterns}")
            return {
                'suite': suite_name,
                'status': 'skipped',
                'reason': '无测试文件',
                'duration': 0
            }
        
        # 执行测试
        start_time = time.time()
        
        cmd = ['python', '-m', 'pytest'] + test_files + ['-v', '--tb=short']
        
        if suite_config.get('parallel', False):
            cmd.extend(['-n', 'auto'])
        
        try:
            result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
            duration = time.time() - start_time
            
            # 解析结果
            if result.returncode == 0:
                status = 'passed'
                print(f"✅ {suite_name} 测试通过")
            else:
                status = 'failed'
                print(f"❌ {suite_name} 测试失败")
                print(result.stdout)
                print(result.stderr)
            
            return {
                'suite': suite_name,
                'status': status,
                'duration': round(duration, 2),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ {suite_name} 测试超时")
            return {
                'suite': suite_name,
                'status': 'timeout',
                'duration': round(duration, 2)
            }
    
    def generate_report(self, results: List[Dict], output_format: str = 'text') -> str:
        """生成测试报告"""
        total_duration = sum(r['duration'] for r in results)
        passed = len([r for r in results if r['status'] == 'passed'])
        failed = len([r for r in results if r['status'] == 'failed'])
        skipped = len([r for r in results if r['status'] == 'skipped'])
        
        if output_format == 'html':
            return self.generate_html_report(results, total_duration, passed, failed, skipped)
        else:
            return self.generate_text_report(results, total_duration, passed, failed, skipped)
    
    def generate_text_report(self, results: List[Dict], total_duration: float, 
                           passed: int, failed: int, skipped: int) -> str:
        """生成文本报告"""
        report = f"""
📊 VabHub 测试报告
==================

执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总耗时: {total_duration:.2f} 秒

测试套件统计:
- ✅ 通过: {passed}
- ❌ 失败: {failed}
- ⚠️  跳过: {skipped}
- 📊 总计: {len(results)}

详细结果:
"""
        
        for result in results:
            status_icon = '✅' if result['status'] == 'passed' else '❌' if result['status'] == 'failed' else '⚠️'
            report += f"{status_icon} {result['suite']}: {result['status']} ({result['duration']}s)\n"
            if result.get('reason'):
                report += f"   原因: {result['reason']}\n"
        
        return report
    
    def generate_html_report(self, results: List[Dict], total_duration: float,
                           passed: int, failed: int, skipped: int) -> str:
        """生成 HTML 报告"""
        # 简化的 HTML 报告
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VabHub 测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
        .suite {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
    </style>
</head>
<body>
    <h1>VabHub 测试报告</h1>
    <div class="summary">
        <p><strong>执行时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>总耗时:</strong> {total_duration:.2f} 秒</p>
        <p><strong>测试套件统计:</strong></p>
        <ul>
            <li class="passed">通过: {passed}</li>
            <li class="failed">失败: {failed}</li>
            <li class="skipped">跳过: {skipped}</li>
            <li>总计: {len(results)}</li>
        </ul>
    </div>
    <h2>详细结果</h2>
"""
        
        for result in results:
            status_class = 'passed' if result['status'] == 'passed' else 'failed' if result['status'] == 'failed' else 'skipped'
            html += f"""
    <div class="suite {status_class}">
        <h3>{result['suite']}</h3>
        <p><strong>状态:</strong> {result['status']}</p>
        <p><strong>耗时:</strong> {result['duration']} 秒</p>
        {f'<p><strong>原因:</strong> {result["reason"]}</p>' if result.get('reason') else ''}
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def run(self, suites: List[str] = None, parallel: bool = False, 
           report_format: str = 'text') -> bool:
        """运行测试"""
        self.start_time = time.time()
        config = self.load_config()
        
        # 确定要运行的套件
        if suites is None or 'all' in suites:
            suites_to_run = list(config['test_suites'].keys())
        else:
            suites_to_run = [s for s in suites if s in config['test_suites']]
        
        if not suites_to_run:
            print("错误: 未找到指定的测试套件")
            return False
        
        print(f"🎯 准备运行 {len(suites_to_run)} 个测试套件")
        
        # 运行测试套件
        results = []
        for suite_name in suites_to_run:
            suite_config = config['test_suites'][suite_name]
            result = self.run_test_suite(suite_name, suite_config)
            results.append(result)
        
        # 生成报告
        report = self.generate_report(results, report_format)
        
        # 保存报告
        if report_format == 'html':
            report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        else:
            report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 测试报告已保存: {report_file}")
        print(report)
        
        # 返回总体结果
        all_passed = all(r['status'] == 'passed' for r in results if r['status'] != 'skipped')
        return all_passed

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='VabHub 多仓库测试运行器')
    parser.add_argument('--suite', nargs='+', help='要运行的测试套件名称')
    parser.add_argument('--all', action='store_true', help='运行所有测试套件')
    parser.add_argument('--parallel', action='store_true', help='并行运行测试')
    parser.add_argument('--report', action='store_true', help='生成测试报告')
    parser.add_argument('--format', choices=['text', 'html'], default='text', 
                       help='报告格式')
    parser.add_argument('--config', default='tests/config/test_config.yaml',
                       help='测试配置文件路径')
    
    args = parser.parse_args()
    
    # 确定测试套件
    if args.all:
        suites = ['all']
    elif args.suite:
        suites = args.suite
    else:
        suites = ['unit']  # 默认运行单元测试
    
    # 运行测试
    runner = TestRunner(args.config)
    success = runner.run(suites=suites, parallel=args.parallel, 
                        report_format=args.format)
    
    # 退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()