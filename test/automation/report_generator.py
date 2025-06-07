#!/usr/bin/env python3
"""
自动化测试报告生成器
生成详细的测试执行报告
"""

import sys
import os
import json
import time
import unittest
from pathlib import Path
from datetime import datetime
from io import StringIO

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, output_dir="test_reports"):
        """初始化报告生成器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, test_modules):
        """运行测试套件并生成报告"""
        self.start_time = datetime.now()
        
        for module_name in test_modules:
            print(f"运行测试模块: {module_name}")
            result = self._run_single_test(module_name)
            self.test_results.append(result)
        
        self.end_time = datetime.now()
        
        # 生成报告
        self._generate_html_report()
        self._generate_json_report()
        self._generate_summary_report()
    
    def _run_single_test(self, module_name):
        """运行单个测试模块"""
        try:
            # 动态导入测试模块
            module = __import__(module_name, fromlist=[''])
            
            # 创建测试套件
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # 运行测试
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            test_result = runner.run(suite)
            
            return {
                "module": module_name,
                "tests_run": test_result.testsRun,
                "failures": len(test_result.failures),
                "errors": len(test_result.errors),
                "success_rate": (test_result.testsRun - len(test_result.failures) - len(test_result.errors)) / test_result.testsRun if test_result.testsRun > 0 else 0,
                "output": stream.getvalue(),
                "failure_details": [str(f) for f in test_result.failures],
                "error_details": [str(e) for e in test_result.errors]
            }
        except Exception as e:
            return {
                "module": module_name,
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "success_rate": 0,
                "output": f"模块导入失败: {str(e)}",
                "failure_details": [],
                "error_details": [str(e)]
            }
    
    def _generate_html_report(self):
        """生成HTML格式报告"""
        total_tests = sum(r["tests_run"] for r in self.test_results)
        total_failures = sum(r["failures"] for r in self.test_results)
        total_errors = sum(r["errors"] for r in self.test_results)
        overall_success_rate = (total_tests - total_failures - total_errors) / total_tests if total_tests > 0 else 0
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PowerAutomation 测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .module {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ background-color: #d4edda; }}
        .failure {{ background-color: #f8d7da; }}
        .error {{ background-color: #fff3cd; }}
        .details {{ margin-top: 10px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PowerAutomation 测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试持续时间: {self.end_time - self.start_time if self.end_time and self.start_time else 'N/A'}</p>
    </div>
    
    <div class="summary">
        <h2>测试总结</h2>
        <p>总测试数: {total_tests}</p>
        <p>成功率: {overall_success_rate:.2%}</p>
        <p>失败数: {total_failures}</p>
        <p>错误数: {total_errors}</p>
    </div>
    
    <div class="modules">
        <h2>模块详情</h2>
"""
        
        for result in self.test_results:
            status_class = "success" if result["success_rate"] == 1.0 else ("failure" if result["failures"] > 0 else "error")
            html_content += f"""
        <div class="module {status_class}">
            <h3>{result["module"]}</h3>
            <p>测试数: {result["tests_run"]}, 成功率: {result["success_rate"]:.2%}</p>
            <p>失败: {result["failures"]}, 错误: {result["errors"]}</p>
            <div class="details">
                <pre>{result["output"]}</pre>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(self.output_dir / "test_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def _generate_json_report(self):
        """生成JSON格式报告"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "duration": str(self.end_time - self.start_time) if self.end_time and self.start_time else None,
            "summary": {
                "total_tests": sum(r["tests_run"] for r in self.test_results),
                "total_failures": sum(r["failures"] for r in self.test_results),
                "total_errors": sum(r["errors"] for r in self.test_results),
                "overall_success_rate": sum(r["success_rate"] * r["tests_run"] for r in self.test_results) / sum(r["tests_run"] for r in self.test_results) if sum(r["tests_run"] for r in self.test_results) > 0 else 0
            },
            "modules": self.test_results
        }
        
        with open(self.output_dir / "test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def _generate_summary_report(self):
        """生成简要文本报告"""
        total_tests = sum(r["tests_run"] for r in self.test_results)
        total_failures = sum(r["failures"] for r in self.test_results)
        total_errors = sum(r["errors"] for r in self.test_results)
        overall_success_rate = (total_tests - total_failures - total_errors) / total_tests if total_tests > 0 else 0
        
        summary = f"""
PowerAutomation 测试报告摘要
================================

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试持续时间: {self.end_time - self.start_time if self.end_time and self.start_time else 'N/A'}

总体统计:
- 总测试数: {total_tests}
- 成功率: {overall_success_rate:.2%}
- 失败数: {total_failures}
- 错误数: {total_errors}

模块详情:
"""
        
        for result in self.test_results:
            summary += f"""
- {result["module"]}:
  测试数: {result["tests_run"]}, 成功率: {result["success_rate"]:.2%}
  失败: {result["failures"]}, 错误: {result["errors"]}
"""
        
        with open(self.output_dir / "test_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(summary)

if __name__ == "__main__":
    # 示例用法
    generator = TestReportGenerator()
    
    # 定义要测试的模块
    test_modules = [
        "test.integration.multi_model_synergy",
        "test.integration.mcptool_kilocode_integration", 
        "test.e2e.tool_discovery_workflow",
        "test.mcp_compliance.compliance_checker",
        "test.performance.load_testing"
    ]
    
    generator.run_test_suite(test_modules)
    print("测试报告已生成到 test_reports/ 目录")

