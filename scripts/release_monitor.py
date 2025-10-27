#!/usr/bin/env python3
"""
VabHub 发布监控工具

功能：
- 实时监控发布状态
- 发布健康检查
- 发布指标统计
- 问题检测和告警
"""

import argparse
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加脚本目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from release_coordination import ReleaseCoordinator
from version_manager import VersionManager

class ReleaseMonitor:
    """发布监控工具"""
    
    def __init__(self):
        self.coordinator = ReleaseCoordinator()
        self.version_manager = VersionManager()
        
        # 监控配置
        self.monitor_intervals = {
            'high': 10,      # 10秒间隔（关键阶段）
            'medium': 30,    # 30秒间隔（常规监控）
            'low': 60        # 60秒间隔（稳定阶段）
        }
    
    def get_release_status(self, version: str) -> Dict:
        """获取发布状态"""
        status = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'repositories': {},
            'overall_status': 'unknown',
            'health_indicators': {}
        }
        
        # 检查各仓库状态
        for repo in self.coordinator.repos:
            repo_status = self.get_repository_status(repo, version)
            status['repositories'][repo] = repo_status
        
        # 计算整体状态
        status['overall_status'] = self.calculate_overall_status(status['repositories'])
        
        # 收集健康指标
        status['health_indicators'] = self.collect_health_indicators(status)
        
        return status
    
    def get_repository_status(self, repo: str, version: str) -> Dict:
        """获取单个仓库状态"""
        status = {
            'name': repo,
            'version': version,
            'build_status': self.check_build_status(repo, version),
            'test_status': self.check_test_status(repo, version),
            'deployment_status': self.check_deployment_status(repo, version),
            'health_score': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        # 计算健康分数
        status['health_score'] = self.calculate_health_score(status)
        
        return status
    
    def check_build_status(self, repo: str, version: str) -> str:
        """检查构建状态"""
        # 这里可以集成实际的构建状态检查
        # 例如：检查 CI/CD 流水线状态
        return 'success'  # 模拟成功状态
    
    def check_test_status(self, repo: str, version: str) -> str:
        """检查测试状态"""
        # 这里可以集成实际的测试状态检查
        return 'success'
    
    def check_deployment_status(self, repo: str, version: str) -> str:
        """检查部署状态"""
        # 这里可以集成实际的部署状态检查
        return 'success'
    
    def calculate_health_score(self, repo_status: Dict) -> int:
        """计算健康分数"""
        score = 100
        
        # 构建状态扣分
        if repo_status['build_status'] != 'success':
            score -= 30
        
        # 测试状态扣分
        if repo_status['test_status'] != 'success':
            score -= 30
        
        # 部署状态扣分
        if repo_status['deployment_status'] != 'success':
            score -= 40
        
        return max(0, score)
    
    def calculate_overall_status(self, repositories: Dict) -> str:
        """计算整体状态"""
        status_counts = {'success': 0, 'warning': 0, 'error': 0}
        
        for repo_status in repositories.values():
            health_score = repo_status['health_score']
            if health_score >= 80:
                status_counts['success'] += 1
            elif health_score >= 60:
                status_counts['warning'] += 1
            else:
                status_counts['error'] += 1
        
        total = len(repositories)
        if status_counts['error'] > 0:
            return 'error'
        elif status_counts['warning'] > 0:
            return 'warning'
        else:
            return 'success'
    
    def collect_health_indicators(self, status: Dict) -> Dict:
        """收集健康指标"""
        indicators = {
            'average_health_score': 0,
            'success_rate': 0,
            'problem_repositories': [],
            'performance_metrics': {},
            'resource_usage': {}
        }
        
        # 计算平均健康分数
        total_score = 0
        success_count = 0
        
        for repo, repo_status in status['repositories'].items():
            total_score += repo_status['health_score']
            
            if repo_status['health_score'] >= 80:
                success_count += 1
            else:
                indicators['problem_repositories'].append({
                    'name': repo,
                    'health_score': repo_status['health_score'],
                    'issues': self.identify_issues(repo_status)
                })
        
        indicators['average_health_score'] = total_score / len(status['repositories'])
        indicators['success_rate'] = success_count / len(status['repositories']) * 100
        
        return indicators
    
    def identify_issues(self, repo_status: Dict) -> List[str]:
        """识别具体问题"""
        issues = []
        
        if repo_status['build_status'] != 'success':
            issues.append('构建失败')
        
        if repo_status['test_status'] != 'success':
            issues.append('测试失败')
        
        if repo_status['deployment_status'] != 'success':
            issues.append('部署失败')
        
        return issues
    
    def real_time_monitor(self, version: str, duration: int = 3600):
        """实时监控"""
        print(f"🔍 开始实时监控版本 {version}")
        print(f"⏰ 监控时长: {duration} 秒")
        print("-" * 50)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration)
        
        iteration = 0
        
        while datetime.now() < end_time:
            iteration += 1
            
            # 获取当前状态
            status = self.get_release_status(version)
            
            # 显示状态信息
            self.display_status(status, iteration)
            
            # 检查是否需要告警
            self.check_alerts(status)
            
            # 确定监控间隔
            interval = self.determine_monitor_interval(status)
            
            # 等待下一次检查
            time.sleep(interval)
        
        print(f"\n✅ 监控完成")
        
        # 生成最终报告
        final_report = self.generate_final_report(version, start_time)
        self.display_final_report(final_report)
    
    def determine_monitor_interval(self, status: Dict) -> int:
        """确定监控间隔"""
        overall_status = status['overall_status']
        
        if overall_status == 'error':
            return self.monitor_intervals['high']
        elif overall_status == 'warning':
            return self.monitor_intervals['medium']
        else:
            return self.monitor_intervals['low']
    
    def display_status(self, status: Dict, iteration: int):
        """显示状态信息"""
        print(f"\n📊 监控周期 #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
        
        # 整体状态
        status_emoji = {'success': '✅', 'warning': '⚠️', 'error': '❌'}
        emoji = status_emoji.get(status['overall_status'], '❓')
        print(f"{emoji} 整体状态: {status['overall_status']}")
        
        # 各仓库状态
        for repo, repo_status in status['repositories'].items():
            health_emoji = '✅' if repo_status['health_score'] >= 80 else '⚠️' if repo_status['health_score'] >= 60 else '❌'
            print(f"  {health_emoji} {repo}: {repo_status['health_score']}分")
        
        # 健康指标
        indicators = status['health_indicators']
        print(f"📈 平均健康分数: {indicators['average_health_score']:.1f}")
        print(f"🎯 成功率: {indicators['success_rate']:.1f}%")
        
        # 问题仓库
        if indicators['problem_repositories']:
            print("🚨 问题仓库:")
            for problem in indicators['problem_repositories']:
                print(f"   - {problem['name']}: {problem['health_score']}分")
                for issue in problem['issues']:
                    print(f"     • {issue}")
    
    def check_alerts(self, status: Dict):
        """检查告警"""
        # 严重问题告警
        if status['overall_status'] == 'error':
            print("🚨 严重告警: 检测到严重问题!")
        
        # 健康分数过低告警
        indicators = status['health_indicators']
        if indicators['average_health_score'] < 70:
            print("⚠️ 警告: 平均健康分数过低")
    
    def generate_final_report(self, version: str, start_time: datetime) -> Dict:
        """生成最终报告"""
        final_status = self.get_release_status(version)
        
        report = {
            'version': version,
            'monitoring_period': {
                'start': start_time.isoformat(),
                'end': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - start_time).total_seconds() / 60
            },
            'final_status': final_status,
            'summary': self.generate_summary(final_status)
        }
        
        return report
    
    def generate_summary(self, status: Dict) -> Dict:
        """生成摘要"""
        indicators = status['health_indicators']
        
        summary = {
            'overall_health': status['overall_status'],
            'average_score': indicators['average_health_score'],
            'success_rate': indicators['success_rate'],
            'problem_count': len(indicators['problem_repositories']),
            'recommendations': self.generate_recommendations(status)
        }
        
        return summary
    
    def generate_recommendations(self, status: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if status['overall_status'] == 'error':
            recommendations.append("立即检查问题仓库并修复")
        
        indicators = status['health_indicators']
        if indicators['average_health_score'] < 80:
            recommendations.append("优化构建和测试流程")
        
        if indicators['problem_repositories']:
            recommendations.append("重点关注问题仓库的健康状况")
        
        return recommendations
    
    def display_final_report(self, report: Dict):
        """显示最终报告"""
        print("\n" + "=" * 50)
        print("📋 监控最终报告")
        print("=" * 50)
        
        summary = report['summary']
        period = report['monitoring_period']
        
        print(f"📦 版本: {report['version']}")
        print(f"⏱️ 监控时长: {period['duration_minutes']:.1f} 分钟")
        print(f"🏥 最终健康状态: {summary['overall_health']}")
        print(f"📊 平均分数: {summary['average_score']:.1f}")
        print(f"🎯 成功率: {summary['success_rate']:.1f}%")
        print(f"🚨 问题数量: {summary['problem_count']}")
        
        if summary['recommendations']:
            print("\n💡 建议:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")
    
    def health_check(self, version: str):
        """健康检查"""
        print(f"🔍 执行健康检查 - 版本 {version}")
        
        status = self.get_release_status(version)
        
        # 检查各项指标
        checks = [
            ('整体状态', status['overall_status'] == 'success'),
            ('平均健康分数', status['health_indicators']['average_health_score'] >= 80),
            ('成功率', status['health_indicators']['success_rate'] >= 90),
            ('问题仓库', len(status['health_indicators']['problem_repositories']) == 0)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status_emoji = '✅' if passed else '❌'
            print(f"{status_emoji} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ 健康检查通过")
        else:
            print("\n❌ 健康检查失败")
        
        return all_passed
    
    def metrics_report(self, version: str):
        """指标报告"""
        print(f"📈 生成指标报告 - 版本 {version}")
        
        status = self.get_release_status(version)
        indicators = status['health_indicators']
        
        print("\n📊 发布指标:")
        print(f"  • 平均健康分数: {indicators['average_health_score']:.1f}")
        print(f"  • 成功率: {indicators['success_rate']:.1f}%")
        print(f"  • 问题仓库数量: {len(indicators['problem_repositories'])}")
        
        if indicators['problem_repositories']:
            print("\n🚨 问题仓库详情:")
            for problem in indicators['problem_repositories']:
                print(f"  • {problem['name']}: {problem['health_score']}分")
                for issue in problem['issues']:
                    print(f"    - {issue}")

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='VabHub 发布监控工具')
    parser.add_argument('--version', required=True, help='监控的版本号')
    parser.add_argument('--monitor', action='store_true', help='实时监控模式')
    parser.add_argument('--duration', type=int, default=3600, help='监控时长（秒）')
    parser.add_argument('--health-check', action='store_true', help='执行健康检查')
    parser.add_argument('--metrics', action='store_true', help='生成指标报告')
    
    args = parser.parse_args()
    
    monitor = ReleaseMonitor()
    
    if args.monitor:
        monitor.real_time_monitor(args.version, args.duration)
    elif args.health_check:
        monitor.health_check(args.version)
    elif args.metrics:
        monitor.metrics_report(args.version)
    else:
        # 默认显示当前状态
        status = monitor.get_release_status(args.version)
        monitor.display_status(status, 1)

if __name__ == '__main__':
    main()