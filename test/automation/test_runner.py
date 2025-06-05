"""
端到端视觉自动化测试：测试入口
"""
import os
import sys
import argparse
import pytest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def main():
    """测试入口主函数"""
    parser = argparse.ArgumentParser(description='运行端到端视觉自动化测试')
    parser.add_argument('--test', help='指定要运行的测试名称')
    parser.add_argument('--headless', action='store_true', help='是否以无头模式运行')
    parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'], help='指定浏览器')
    args = parser.parse_args()
    
    # 创建报告目录
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # 创建截图目录
    screenshots_dir = os.path.join(reports_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # 创建差异目录
    diff_dir = os.path.join(reports_dir, 'diff')
    os.makedirs(diff_dir, exist_ok=True)
    
    # 构建pytest参数
    pytest_args = [
        '--browser', args.browser,
        '--headed', '' if args.headless else 'true',
        '--screenshot', 'on',
        '--video', 'on',
        '--output', reports_dir,
        '--html', os.path.join(reports_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    ]
    
    # 如果指定了测试名称，则只运行该测试
    if args.test:
        pytest_args.append(f'scenarios/test_{args.test}.py')
    else:
        pytest_args.append('scenarios/')
    
    # 运行测试
    return pytest.main(pytest_args)

if __name__ == '__main__':
    sys.exit(main())
