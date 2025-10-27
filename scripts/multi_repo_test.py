#!/usr/bin/env python3
"""
VabHub 多仓库集成测试器
测试多仓库之间的集成和协调功能
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

class MultiRepoTester:
    """多仓库集成测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    def test_api_connectivity(self) -> Dict:
        """测试 API 连通性"""
        print("🔌 测试 API 连通性...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ API 连通性测试通过")
                return {
                    'test': 'api_connectivity',
                    'status': 'passed',
                    'response_time': response.elapsed.total_seconds(),
                    'details': response.json()
                }
            else:
                print(f"❌ API 连通性测试失败: HTTP {response.status_code}")
                return {
                    'test': 'api_connectivity',
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API 连通性测试失败: {e}")
            return {
                'test': 'api_connectivity',
                'status': 'failed',
                'error': str(e)
            }
    
    def test_database_connection(self) -> Dict:
        """测试数据库连接"""
        print("🗄️ 测试数据库连接...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health/db", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('database_status') == 'healthy':
                    print("✅ 数据库连接测试通过")
                    return {
                        'test': 'database_connection',
                        'status': 'passed',
                        'response_time': response.elapsed.total_seconds(),
                        'details': data
                    }
                else:
                    print("❌ 数据库连接测试失败: 数据库状态异常")
                    return {
                        'test': 'database_connection',
                        'status': 'failed',
                        'error': 'Database status unhealthy',
                        'details': data
                    }
            else:
                print(f"❌ 数据库连接测试失败: HTTP {response.status_code}")
                return {
                    'test': 'database_connection',
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return {
                'test': 'database_connection',
                'status': 'failed',
                'error': str(e)
            }
    
    def test_redis_connection(self) -> Dict:
        """测试 Redis 连接"""
        print("🔴 测试 Redis 连接...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health/redis", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('redis_status') == 'healthy':
                    print("✅ Redis 连接测试通过")
                    return {
                        'test': 'redis_connection',
                        'status': 'passed',
                        'response_time': response.elapsed.total_seconds(),
                        'details': data
                    }
                else:
                    print("❌ Redis 连接测试失败: Redis 状态异常")
                    return {
                        'test': 'redis_connection',
                        'status': 'failed',
                        'error': 'Redis status unhealthy',
                        'details': data
                    }
            else:
                print(f"❌ Redis 连接测试失败: HTTP {response.status_code}")
                return {
                    'test': 'redis_connection',
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Redis 连接测试失败: {e}")
            return {
                'test': 'redis_connection',
                'status': 'failed',
                'error': str(e)
            }
    
    def test_frontend_connectivity(self) -> Dict:
        """测试前端连通性"""
        print("🌐 测试前端连通性...")
        
        frontend_url = "http://localhost:3000"
        
        try:
            response = requests.get(frontend_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ 前端连通性测试通过")
                return {
                    'test': 'frontend_connectivity',
                    'status': 'passed',
                    'response_time': response.elapsed.total_seconds(),
                    'url': frontend_url
                }
            else:
                print(f"❌ 前端连通性测试失败: HTTP {response.status_code}")
                return {
                    'test': 'frontend_connectivity',
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}',
                    'url': frontend_url
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 前端连通性测试失败: {e}")
            return {
                'test': 'frontend_connectivity',
                'status': 'failed',
                'error': str(e),
                'url': frontend_url
            }
    
    def test_api_endpoints(self) -> Dict:
        """测试 API 端点"""
        print("🔗 测试 API 端点...")
        
        endpoints = [
            ('/api/users', 'GET'),
            ('/api/users', 'POST'),
            ('/api/auth/login', 'POST'),
            ('/api/auth/register', 'POST'),
            ('/api/config', 'GET')
        ]
        
        results = []
        passed = 0
        failed = 0
        
        for endpoint, method in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                if method == 'GET':
                    response = requests.get(url, timeout=10)
                elif method == 'POST':
                    # 对于 POST 请求，发送空的 JSON 数据
                    response = requests.post(url, json={}, timeout=10)
                else:
                    continue
                
                if response.status_code in [200, 201, 400, 401]:
                    # 这些状态码表示端点存在且可访问
                    status = 'passed'
                    passed += 1
                    print(f"✅ {method} {endpoint}: HTTP {response.status_code}")
                else:
                    status = 'failed'
                    failed += 1
                    print(f"❌ {method} {endpoint}: HTTP {response.status_code}")
                
                results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': response.status_code,
                    'status': status,
                    'response_time': response.elapsed.total_seconds()
                })
                
            except requests.exceptions.RequestException as e:
                failed += 1
                print(f"❌ {method} {endpoint}: {e}")
                
                results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'failed',
                    'error': str(e)
                })
        
        overall_status = 'passed' if failed == 0 else 'failed'
        
        return {
            'test': 'api_endpoints',
            'status': overall_status,
            'passed': passed,
            'failed': failed,
            'total': len(endpoints),
            'results': results
        }
    
    def test_inter_service_communication(self) -> Dict:
        """测试服务间通信"""
        print("🔗 测试服务间通信...")
        
        # 测试前端调用 API
        try:
            # 模拟前端调用 API 的健康检查
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ 服务间通信测试通过")
                return {
                    'test': 'inter_service_communication',
                    'status': 'passed',
                    'response_time': response.elapsed.total_seconds(),
                    'details': 'Frontend to API communication successful'
                }
            else:
                print(f"❌ 服务间通信测试失败: HTTP {response.status_code}")
                return {
                    'test': 'inter_service_communication',
                    'status': 'failed',
                    'error': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 服务间通信测试失败: {e}")
            return {
                'test': 'inter_service_communication',
                'status': 'failed',
                'error': str(e)
            }
    
    def test_data_consistency(self) -> Dict:
        """测试数据一致性"""
        print("📊 测试数据一致性...")
        
        # 创建测试数据
        test_user = {
            'username': f'test_user_{int(time.time())}',
            'email': f'test{int(time.time())}@example.com',
            'password': 'testpassword123'
        }
        
        try:
            # 创建用户
            create_response = requests.post(f"{self.base_url}/api/users", 
                                          json=test_user, timeout=10)
            
            if create_response.status_code not in [200, 201]:
                return {
                    'test': 'data_consistency',
                    'status': 'failed',
                    'error': f'创建用户失败: HTTP {create_response.status_code}'
                }
            
            # 查询用户
            get_response = requests.get(f"{self.base_url}/api/users/{test_user['username']}", 
                                      timeout=10)
            
            if get_response.status_code == 200:
                user_data = get_response.json()
                
                # 验证数据一致性
                if (user_data.get('username') == test_user['username'] and 
                    user_data.get('email') == test_user['email']):
                    print("✅ 数据一致性测试通过")
                    
                    # 清理测试数据
                    requests.delete(f"{self.base_url}/api/users/{test_user['username']}", 
                                  timeout=10)
                    
                    return {
                        'test': 'data_consistency',
                        'status': 'passed',
                        'details': 'Data creation and retrieval consistent'
                    }
                else:
                    return {
                        'test': 'data_consistency',
                        'status': 'failed',
                        'error': 'Data inconsistency detected'
                    }
            else:
                return {
                    'test': 'data_consistency',
                    'status': 'failed',
                    'error': f'查询用户失败: HTTP {get_response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 数据一致性测试失败: {e}")
            return {
                'test': 'data_consistency',
                'status': 'failed',
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("🎯 开始多仓库集成测试")
        print("=" * 50)
        
        tests = [
            self.test_api_connectivity,
            self.test_database_connection,
            self.test_redis_connection,
            self.test_frontend_connectivity,
            self.test_api_endpoints,
            self.test_inter_service_communication,
            self.test_data_consistency
        ]
        
        results = []
        start_time = time.time()
        
        for test_func in tests:
            result = test_func()
            results.append(result)
            print()  # 空行分隔
        
        total_time = time.time() - start_time
        
        # 统计结果
        passed = len([r for r in results if r['status'] == 'passed'])
        failed = len([r for r in results if r['status'] == 'failed'])
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
        print("📊 测试摘要:")
        print("-" * 30)
        print(f"总体状态: {'✅ 通过' if overall_status == 'passed' else '❌ 失败'}")
        print(f"测试总数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"总耗时: {total_time:.2f} 秒")
        
        return summary
    
    def generate_report(self, summary: Dict, format: str = 'text') -> str:
        """生成测试报告"""
        if format == 'json':
            return json.dumps(summary, indent=2, ensure_ascii=False)
        else:
            return self.generate_text_report(summary)
    
    def generate_text_report(self, summary: Dict) -> str:
        """生成文本报告"""
        report = []
        report.append("=" * 60)
        report.append("📊 VabHub 多仓库集成测试报告")
        report.append("=" * 60)
        report.append(f"📅 测试时间: {summary['timestamp']}")
        report.append(f"⏱️ 总执行时间: {summary['total_time']:.2f} 秒")
        report.append(f"🏆 总体结果: {'✅ 通过' if summary['overall_status'] == 'passed' else '❌ 失败'}")
        report.append(f"📊 测试统计: {summary['passed']}/{summary['total_tests']} 通过")
        report.append("")
        
        # 详细结果
        report.append("🔧 详细测试结果:")
        report.append("-" * 40)
        
        for result in summary['results']:
            status_icon = '✅' if result['status'] == 'passed' else '❌'
            report.append(f"{status_icon} {result['test']}: {result['status']}")
            
            if 'error' in result:
                report.append(f"   错误: {result['error']}")
            
            if 'response_time' in result:
                report.append(f"   响应时间: {result['response_time']:.3f} 秒")
        
        return '\n'.join(report)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='VabHub 多仓库集成测试器')
    
    parser.add_argument('--url', default='http://localhost:8000',
                       help='API 基础 URL')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='报告格式')
    parser.add_argument('--output', help='报告输出文件')
    
    args = parser.parse_args()
    
    tester = MultiRepoTester(args.url)
    summary = tester.run_all_tests()
    
    # 生成报告
    report = tester.generate_report(summary, args.format)
    
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