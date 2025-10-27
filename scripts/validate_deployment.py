#!/usr/bin/env python3
"""
VabHub 多仓库部署验证器
验证多仓库部署的完整性和正确性
"""

import argparse
import subprocess
import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DeploymentValidator:
    """部署验证器"""
    
    def __init__(self, config_path: str = "tests/config/deployment_config.yaml"):
        self.config_path = config_path
        self.validation_results = {}
        
    def load_config(self) -> Dict:
        """加载部署配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
            return self.default_config()
        except json.JSONDecodeError:
            print(f"错误: 配置文件 {self.config_path} 格式错误")
            return self.default_config()
    
    def default_config(self) -> Dict:
        """默认部署配置"""
        return {
            'services': {
                'api': {
                    'port': 8000,
                    'health_endpoint': '/health',
                    'expected_status': 200
                },
                'frontend': {
                    'port': 3000,
                    'health_endpoint': '/',
                    'expected_status': 200
                },
                'database': {
                    'port': 5432,
                    'health_check': 'pg_isready'
                },
                'redis': {
                    'port': 6379,
                    'health_check': 'redis-cli ping'
                }
            },
            'validation_timeout': 300,
            'retry_interval': 5
        }
    
    def validate_service_health(self, service_name: str, service_config: Dict) -> Dict:
        """验证服务健康状态"""
        print(f"🔍 验证 {service_name} 服务健康状态...")
        
        try:
            if 'health_endpoint' in service_config:
                # HTTP 服务健康检查
                url = f"http://localhost:{service_config['port']}{service_config['health_endpoint']}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == service_config['expected_status']:
                    print(f"✅ {service_name} 健康检查通过")
                    return {
                        'service': service_name,
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds(),
                        'details': response.json() if response.headers.get('content-type') == 'application/json' else {}
                    }
                else:
                    print(f"❌ {service_name} 健康检查失败: HTTP {response.status_code}")
                    return {
                        'service': service_name,
                        'status': 'unhealthy',
                        'error': f'HTTP {response.status_code}',
                        'response_time': response.elapsed.total_seconds()
                    }
                    
            elif 'health_check' in service_config:
                # 命令行健康检查
                health_check = service_config['health_check']
                
                try:
                    result = subprocess.run(health_check.split(), 
                                         capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        print(f"✅ {service_name} 健康检查通过")
                        return {
                            'service': service_name,
                            'status': 'healthy',
                            'details': {'output': result.stdout.strip()}
                        }
                    else:
                        print(f"❌ {service_name} 健康检查失败: {result.stderr}")
                        return {
                            'service': service_name,
                            'status': 'unhealthy',
                            'error': result.stderr.strip()
                        }
                        
                except subprocess.TimeoutExpired:
                    print(f"❌ {service_name} 健康检查超时")
                    return {
                        'service': service_name,
                        'status': 'unhealthy',
                        'error': 'Health check timeout'
                    }
                    
        except Exception as e:
            print(f"❌ {service_name} 健康检查异常: {e}")
            return {
                'service': service_name,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def validate_service_connectivity(self, service_name: str, service_config: Dict) -> Dict:
        """验证服务连通性"""
        print(f"🔗 验证 {service_name} 服务连通性...")
        
        try:
            # 检查端口是否开放
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            result = sock.connect_ex(('localhost', service_config['port']))
            sock.close()
            
            if result == 0:
                print(f"✅ {service_name} 端口 {service_config['port']} 连通性正常")
                return {
                    'service': service_name,
                    'status': 'connected',
                    'port': service_config['port']
                }
            else:
                print(f"❌ {service_name} 端口 {service_config['port']} 无法连接")
                return {
                    'service': service_name,
                    'status': 'disconnected',
                    'port': service_config['port'],
                    'error': f'Port {service_config["port"]} not accessible'
                }
                
        except Exception as e:
            print(f"❌ {service_name} 连通性检查异常: {e}")
            return {
                'service': service_name,
                'status': 'error',
                'error': str(e)
            }
    
    def validate_inter_service_communication(self) -> Dict:
        """验证服务间通信"""
        print("🔗 验证服务间通信...")
        
        try:
            # 测试前端调用 API
            api_response = requests.get("http://localhost:8000/health", timeout=10)
            frontend_response = requests.get("http://localhost:3000", timeout=10)
            
            if api_response.status_code == 200 and frontend_response.status_code == 200:
                print("✅ 服务间通信正常")
                return {
                    'test': 'inter_service_communication',
                    'status': 'passed',
                    'details': {
                        'api_to_frontend': 'healthy',
                        'frontend_to_api': 'healthy'
                    }
                }
            else:
                print("❌ 服务间通信异常")
                return {
                    'test': 'inter_service_communication',
                    'status': 'failed',
                    'error': f'API: {api_response.status_code}, Frontend: {frontend_response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ 服务间通信检查异常: {e}")
            return {
                'test': 'inter_service_communication',
                'status': 'failed',
                'error': str(e)
            }
    
    def validate_data_persistence(self) -> Dict:
        """验证数据持久性"""
        print("💾 验证数据持久性...")
        
        try:
            # 创建测试数据
            test_data = {
                'username': f'validation_test_{int(time.time())}',
                'email': f'validation{int(time.time())}@example.com',
                'password': 'validation_password'
            }
            
            # 创建用户
            create_response = requests.post("http://localhost:8000/api/users", 
                                           json=test_data, timeout=10)
            
            if create_response.status_code not in [200, 201]:
                return {
                    'test': 'data_persistence',
                    'status': 'failed',
                    'error': f'创建数据失败: HTTP {create_response.status_code}'
                }
            
            # 查询用户
            get_response = requests.get(f"http://localhost:8000/api/users/{test_data['username']}", 
                                      timeout=10)
            
            if get_response.status_code == 200:
                user_data = get_response.json()
                
                # 验证数据正确性
                if (user_data.get('username') == test_data['username'] and 
                    user_data.get('email') == test_data['email']):
                    
                    # 清理测试数据
                    requests.delete(f"http://localhost:8000/api/users/{test_data['username']}", 
                                  timeout=10)
                    
                    print("✅ 数据持久性验证通过")
                    return {
                        'test': 'data_persistence',
                        'status': 'passed',
                        'details': 'Data creation, retrieval, and deletion successful'
                    }
                else:
                    return {
                        'test': 'data_persistence',
                        'status': 'failed',
                        'error': 'Data inconsistency detected'
                    }
            else:
                return {
                    'test': 'data_persistence',
                    'status': 'failed',
                    'error': f'查询数据失败: HTTP {get_response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ 数据持久性验证异常: {e}")
            return {
                'test': 'data_persistence',
                'status': 'failed',
                'error': str(e)
            }
    
    def validate_deployment_completeness(self) -> Dict:
        """验证部署完整性"""
        print("📋 验证部署完整性...")
        
        config = self.load_config()
        services = config.get('services', {})
        
        missing_services = []
        deployed_services = []
        
        for service_name, service_config in services.items():
            # 检查服务是否部署
            connectivity_result = self.validate_service_connectivity(service_name, service_config)
            
            if connectivity_result['status'] == 'connected':
                deployed_services.append(service_name)
            else:
                missing_services.append(service_name)
        
        if not missing_services:
            print("✅ 部署完整性验证通过")
            return {
                'test': 'deployment_completeness',
                'status': 'passed',
                'deployed_services': deployed_services,
                'missing_services': missing_services
            }
        else:
            print(f"❌ 部署不完整，缺失服务: {missing_services}")
            return {
                'test': 'deployment_completeness',
                'status': 'failed',
                'deployed_services': deployed_services,
                'missing_services': missing_services,
                'error': f'Missing services: {missing_services}'
            }
    
    def wait_for_services_ready(self, timeout: int = 300) -> bool:
        """等待服务就绪"""
        print(f"⏳ 等待服务就绪 (超时: {timeout}秒)...")
        
        config = self.load_config()
        services = config.get('services', {})
        retry_interval = config.get('retry_interval', 5)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_ready = True
            
            for service_name, service_config in services.items():
                health_result = self.validate_service_health(service_name, service_config)
                
                if health_result['status'] != 'healthy':
                    all_ready = False
                    print(f"⚠️ {service_name} 尚未就绪，等待重试...")
                    break
            
            if all_ready:
                print("✅ 所有服务已就绪")
                return True
            
            time.sleep(retry_interval)
        
        print("❌ 服务启动超时")
        return False
    
    def run_full_validation(self) -> Dict:
        """运行完整验证"""
        print("🎯 开始部署完整性验证")
        print("=" * 50)
        
        start_time = time.time()
        
        # 等待服务就绪
        config = self.load_config()
        timeout = config.get('validation_timeout', 300)
        
        if not self.wait_for_services_ready(timeout):
            return {
                'overall_status': 'failed',
                'error': 'Services not ready within timeout',
                'timestamp': datetime.now().isoformat()
            }
        
        # 运行各项验证
        validation_tests = [
            self.validate_deployment_completeness,
            self.validate_inter_service_communication,
            self.validate_data_persistence
        ]
        
        results = []
        
        for test_func in validation_tests:
            result = test_func()
            results.append(result)
            print()  # 空行分隔
        
        # 验证各服务健康状态
        config = self.load_config()
        services = config.get('services', {})
        
        for service_name, service_config in services.items():
            health_result = self.validate_service_health(service_name, service_config)
            results.append(health_result)
            print()
        
        total_time = time.time() - start_time
        
        # 统计结果
        passed = len([r for r in results if r.get('status') in ['passed', 'healthy', 'connected']])
        failed = len([r for r in results if r.get('status') in ['failed', 'unhealthy', 'disconnected']])
        total = len(results)
        
        overall_status = 'passed' if failed == 0 else 'failed'
        
        summary = {
            'overall_status': overall_status,
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'total_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        # 输出摘要
        print("📊 验证摘要:")
        print("-" * 30)
        print(f"总体状态: {'✅ 通过' if overall_status == 'passed' else '❌ 失败'}")
        print(f"验证总数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"总耗时: {total_time:.2f} 秒")
        
        return summary
    
    def generate_report(self, summary: Dict, format: str = 'text') -> str:
        """生成验证报告"""
        if format == 'json':
            return json.dumps(summary, indent=2, ensure_ascii=False)
        else:
            return self.generate_text_report(summary)
    
    def generate_text_report(self, summary: Dict) -> str:
        """生成文本报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 VabHub 部署验证报告")
        report.append("=" * 60)
        report.append(f"📅 验证时间: {summary['timestamp']}")
        report.append(f"⏱️ 总执行时间: {summary['total_time']:.2f} 秒")
        report.append(f"🏆 总体结果: {'✅ 通过' if summary['overall_status'] == 'passed' else '❌ 失败'}")
        report.append(f"📊 验证统计: {summary['passed']}/{summary['total_tests']} 通过")
        report.append("")
        
        # 详细结果
        report.append("🔧 详细验证结果:")
        report.append("-" * 40)
        
        for result in summary['results']:
            if 'test' in result:
                # 测试结果
                status_icon = '✅' if result['status'] == 'passed' else '❌'
                report.append(f"{status_icon} {result['test']}: {result['status']}")
            elif 'service' in result:
                # 服务结果
                status_icon = '✅' if result['status'] in ['healthy', 'connected'] else '❌'
                report.append(f"{status_icon} {result['service']}: {result['status']}")
            
            if 'error' in result:
                report.append(f"   错误: {result['error']}")
            
            if 'response_time' in result:
                report.append(f"   响应时间: {result['response_time']:.3f} 秒")
        
        return '\n'.join(report)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='VabHub 部署验证器')
    
    parser.add_argument('--config', default='tests/config/deployment_config.yaml',
                       help='部署配置文件路径')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='报告格式')
    parser.add_argument('--output', help='报告输出文件')
    parser.add_argument('--timeout', type=int, default=300,
                       help='验证超时时间（秒）')
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.config)
    summary = validator.run_full_validation()
    
    # 生成报告
    report = validator.generate_report(summary, args.format)
    
    # 输出报告
    if args.format == 'text':
        print("\n" + report)
    else:
        print(report)
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {args.output}")
    
    # 返回退出码
    sys.exit(0 if summary['overall_status'] == 'passed' else 1)

if __name__ == '__main__':
    main()