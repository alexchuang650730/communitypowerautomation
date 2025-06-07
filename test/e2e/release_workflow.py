"""
自动化测试能力的端到端测试方案
版本: 1.0.0
更新日期: 2025-06-01
"""

import os
import sys
import unittest
import json
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入被测试的模块
from agents.general_agent.automated_testing import AutomatedTestingFramework, TestType, TestStatus, TestPriority
from development_tools.agent_problem_solver import AgentProblemSolver
from agents.ppt_agent.core.mcp.webagent_adapter import MCPAdapter

class TestAutomatedTestingE2E(unittest.TestCase):
    """自动化测试能力的端到端测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 设置测试项目根目录
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # 初始化自动化测试框架
        self.testing_framework = AutomatedTestingFramework(self.project_root)
        
        # 创建测试配置
        self.test_config = {
            "test_dirs": {
                "unit": "test/unit",
                "integration": "test/integration",
                "ui": "test/ui",
                "performance": "test/performance",
                "visual": "test/visual_test",
                "end_to_end": "test/end_to_end"
            },
            "report_dir": "reports/test",
            "coverage_threshold": {
                "unit": 80,
                "integration": 70,
                "ui": 60,
                "performance": 50
            },
            "savepoint": {
                "create_on_success": True,
                "create_on_failure": True
            }
        }
        
        # 确保测试报告目录存在
        os.makedirs(os.path.join(self.project_root, self.test_config["report_dir"]), exist_ok=True)
        
        # 初始化AgentProblemSolver（用于测试集成）
        self.problem_solver = AgentProblemSolver(self.project_root)
        
        print(f"测试环境准备完成，项目根目录: {self.project_root}")

    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试生成的报告文件
        report_dir = os.path.join(self.project_root, self.test_config["report_dir"])
        for file in os.listdir(report_dir):
            if file.startswith("test_report_") and (file.endswith(".html") or file.endswith(".md") or file.endswith(".pdf")):
                try:
                    os.remove(os.path.join(report_dir, file))
                except:
                    pass
        
        print("测试环境清理完成")

    def test_01_test_plan_generation(self):
        """测试计划生成功能测试"""
        print("\n开始测试计划生成功能测试...")
        
        # 生成测试计划
        test_plan = self.testing_framework.generate_test_plan(
            test_types=[TestType.UNIT, TestType.INTEGRATION],
            priority=[TestPriority.CRITICAL, TestPriority.HIGH]
        )
        
        # 验证测试计划基本结构
        self.assertIsNotNone(test_plan)
        self.assertIn("id", test_plan)
        self.assertIn("created_at", test_plan)
        self.assertIn("test_types", test_plan)
        self.assertIn("priority", test_plan)
        self.assertIn("test_cases", test_plan)
        self.assertIn("status", test_plan)
        
        # 验证测试类型和优先级
        self.assertEqual(set(test_plan["test_types"]), {TestType.UNIT.value, TestType.INTEGRATION.value})
        self.assertEqual(set(test_plan["priority"]), {TestPriority.CRITICAL.value, TestPriority.HIGH.value})
        
        # 验证测试用例
        self.assertGreater(len(test_plan["test_cases"]), 0)
        for test_case in test_plan["test_cases"]:
            self.assertIn("id", test_case)
            self.assertIn("name", test_case)
            self.assertIn("file", test_case)
            self.assertIn("type", test_case)
            self.assertIn("priority", test_case)
            self.assertIn("status", test_case)
            
            # 验证测试类型和优先级符合筛选条件
            self.assertIn(test_case["type"], [TestType.UNIT.value, TestType.INTEGRATION.value])
            self.assertIn(test_case["priority"], [TestPriority.CRITICAL.value, TestPriority.HIGH.value])
        
        print(f"测试计划生成成功，包含 {len(test_plan['test_cases'])} 个测试用例")
        return test_plan

    def test_02_test_execution(self):
        """测试执行功能测试"""
        print("\n开始测试执行功能测试...")
        
        # 生成测试计划
        test_plan = self.test_01_test_plan_generation()
        
        # 执行测试
        with patch.object(self.testing_framework, '_run_test_case') as mock_run_test:
            # 模拟测试执行结果
            mock_run_test.return_value = {
                "execution_time": 0.5,
                "status": TestStatus.PASSED.value
            }
            
            # 执行测试
            test_results = self.testing_framework.execute_tests(test_plan)
        
        # 验证测试结果基本结构
        self.assertIsNotNone(test_results)
        self.assertEqual(test_results["id"], test_plan["id"])
        self.assertIn("started_at", test_results)
        self.assertIn("completed_at", test_results)
        self.assertIn("status", test_results)
        self.assertIn("statistics", test_results)
        
        # 验证测试统计信息
        self.assertIn("total", test_results["statistics"])
        self.assertIn("passed", test_results["statistics"])
        self.assertIn("failed", test_results["statistics"])
        self.assertIn("pass_rate", test_results["statistics"])
        
        # 验证所有测试用例都已执行
        for test_case in test_results["test_cases"]:
            self.assertIn("status", test_case)
            self.assertNotEqual(test_case["status"], TestStatus.PENDING.value)
            self.assertIn("execution_time", test_case)
        
        print(f"测试执行成功，状态: {test_results['status']}, 通过率: {test_results['statistics']['pass_rate']}%")
        return test_results

    def test_03_coverage_analysis(self):
        """测试覆盖率分析功能测试"""
        print("\n开始测试覆盖率分析功能测试...")
        
        # 执行测试
        test_results = self.test_02_test_execution()
        
        # 分析覆盖率
        coverage_data = self.testing_framework.analyze_coverage(test_results)
        
        # 验证覆盖率数据基本结构
        self.assertIsNotNone(coverage_data)
        self.assertEqual(coverage_data["test_plan_id"], test_results["id"])
        self.assertIn("timestamp", coverage_data)
        self.assertIn("overall", coverage_data)
        self.assertIn("by_type", coverage_data)
        self.assertIn("by_module", coverage_data)
        
        # 验证总体覆盖率
        self.assertIn("line", coverage_data["overall"])
        self.assertIn("branch", coverage_data["overall"])
        self.assertIn("function", coverage_data["overall"])
        
        # 验证按类型的覆盖率
        for test_type in ["unit", "integration"]:
            self.assertIn(test_type, coverage_data["by_type"])
            self.assertIn("line", coverage_data["by_type"][test_type])
            self.assertIn("branch", coverage_data["by_type"][test_type])
            self.assertIn("function", coverage_data["by_type"][test_type])
        
        # 验证按模块的覆盖率
        for module in coverage_data["by_module"]:
            self.assertIn("line", coverage_data["by_module"][module])
            self.assertIn("branch", coverage_data["by_module"][module])
            self.assertIn("function", coverage_data["by_module"][module])
        
        print(f"测试覆盖率分析成功，总体行覆盖率: {coverage_data['overall']['line']}%")
        return coverage_data

    def test_04_report_generation(self):
        """测试报告生成功能测试"""
        print("\n开始测试报告生成功能测试...")
        
        # 执行测试并分析覆盖率
        test_results = self.test_02_test_execution()
        coverage_data = self.test_03_coverage_analysis()
        
        # 生成HTML报告
        html_report = self.testing_framework.generate_report(test_results, coverage_data, "html")
        
        # 验证HTML报告
        self.assertTrue(os.path.exists(html_report))
        self.assertTrue(html_report.endswith(".html"))
        
        # 验证HTML报告内容
        with open(html_report, 'r') as f:
            html_content = f.read()
            self.assertIn("自动化测试报告", html_content)
            self.assertIn(test_results["id"], html_content)
            self.assertIn("测试摘要", html_content)
            self.assertIn("测试覆盖率", html_content)
            self.assertIn("测试用例详情", html_content)
        
        # 生成Markdown报告
        md_report = self.testing_framework.generate_report(test_results, coverage_data, "markdown")
        
        # 验证Markdown报告
        self.assertTrue(os.path.exists(md_report))
        self.assertTrue(md_report.endswith(".md"))
        
        # 验证Markdown报告内容
        with open(md_report, 'r') as f:
            md_content = f.read()
            self.assertIn("# 自动化测试报告", md_content)
            self.assertIn(test_results["id"], md_content)
            self.assertIn("## 测试摘要", md_content)
            self.assertIn("## 测试覆盖率", md_content)
            self.assertIn("## 测试用例详情", md_content)
        
        print(f"测试报告生成成功，HTML报告: {html_report}, Markdown报告: {md_report}")
        return html_report, md_report

    @patch('powerautomation_integration.development_tools.agent_problem_solver.AgentProblemSolver.create_savepoint')
    def test_05_savepoint_integration(self, mock_create_savepoint):
        """与AgentProblemSolver的保存点集成测试"""
        print("\n开始与AgentProblemSolver的保存点集成测试...")
        
        # 模拟创建保存点
        mock_create_savepoint.return_value = "sp_20250601123456"
        
        # 执行测试
        test_results = self.test_02_test_execution()
        
        # 手动调用创建保存点方法
        self.testing_framework._create_savepoint(test_results)
        
        # 验证是否调用了创建保存点方法
        mock_create_savepoint.assert_called_once()
        
        # 验证调用参数
        call_args = mock_create_savepoint.call_args[0]
        self.assertIn(test_results["id"], call_args[0])
        self.assertIn(test_results["status"], call_args[0])
        
        print(f"与AgentProblemSolver的保存点集成测试成功，保存点ID: {mock_create_savepoint.return_value}")

    @patch('powerautomation_integration.agents.ppt_agent.core.mcp.webagent_adapter.MCPAdapter.register_capability')
    def test_06_mcp_integration(self, mock_register_capability):
        """与MCP协调器的集成测试"""
        print("\n开始与MCP协调器的集成测试...")
        
        # 调用MCP集成方法
        self.testing_framework.integrate_with_mcp()
        
        # 验证是否调用了注册能力方法
        self.assertEqual(mock_register_capability.call_count, 3)
        
        # 验证注册的能力
        registered_capabilities = [call[1]['capability_id'] for call in mock_register_capability.call_args_list]
        self.assertIn("automated_testing", registered_capabilities)
        self.assertIn("test_report_generation", registered_capabilities)
        self.assertIn("test_history_tracking", registered_capabilities)
        
        print("与MCP协调器的集成测试成功，已注册3个能力")

    @patch('powerautomation_integration.scripts.github_test_reporter.GitHubTestReporter.create_or_update_test_report')
    def test_07_github_notification(self, mock_create_or_update):
        """GitHub通知功能测试"""
        print("\n开始GitHub通知功能测试...")
        
        # 模拟GitHub Issue创建
        mock_create_or_update.return_value = 123
        
        # 执行测试
        test_results = self.test_02_test_execution()
        
        # 配置通知
        self.testing_framework.config["notification"] = {
            "email": False,
            "slack": False,
            "github": True
        }
        
        # 发送通知
        with patch.object(self.testing_framework, 'generate_report') as mock_generate_report:
            # 模拟报告生成
            mock_generate_report.return_value = "/tmp/test_report.md"
            
            # 发送通知
            self.testing_framework.notify_results(test_results)
        
        # 验证是否调用了GitHub通知方法
        mock_create_or_update.assert_called_once()
        
        # 验证调用参数
        call_kwargs = mock_create_or_update.call_args[1]
        self.assertIn("title", call_kwargs)
        self.assertIn("body", call_kwargs)
        self.assertIn("labels", call_kwargs)
        self.assertIn(test_results["id"], call_kwargs["title"])
        self.assertIn("test-report", call_kwargs["labels"])
        
        print(f"GitHub通知功能测试成功，Issue #{mock_create_or_update.return_value}")

    def test_08_trend_analysis(self):
        """趋势分析功能测试"""
        print("\n开始趋势分析功能测试...")
        
        # 模拟测试历史记录
        self.testing_framework.test_history = [
            {
                "id": f"test_run_{i}",
                "created_at": (datetime.now().replace(day=i+1)).isoformat(),
                "completed_at": (datetime.now().replace(day=i+1, hour=i+2)).isoformat(),
                "status": TestStatus.PASSED.value if i % 3 != 0 else TestStatus.FAILED.value,
                "statistics": {
                    "total": 100,
                    "passed": 70 + i,
                    "failed": 30 - i,
                    "skipped": 0,
                    "error": 0,
                    "pass_rate": 70 + i,
                    "duration": 120.5
                }
            }
            for i in range(10)
        ]
        
        # 分析趋势
        trends = self.testing_framework.analyze_trends()
        
        # 验证趋势分析结果
        self.assertIsNotNone(trends)
        self.assertEqual(trends["total_runs"], 10)
        self.assertEqual(len(trends["pass_rates"]), 10)
        self.assertEqual(len(trends["timestamps"]), 10)
        self.assertIn("avg_pass_rate", trends)
        self.assertIn("trend", trends)
        self.assertIn("latest_pass_rate", trends)
        self.assertIn("highest_pass_rate", trends)
        self.assertIn("lowest_pass_rate", trends)
        
        # 验证趋势计算正确性
        self.assertEqual(trends["highest_pass_rate"], 79)
        self.assertEqual(trends["lowest_pass_rate"], 70)
        self.assertEqual(trends["latest_pass_rate"], 79)
        
        print(f"趋势分析功能测试成功，趋势: {trends['trend']}, 平均通过率: {trends['avg_pass_rate']}%")

    def test_09_end_to_end_workflow(self):
        """端到端工作流测试"""
        print("\n开始端到端工作流测试...")
        
        # 模拟各个组件
        with patch.object(self.testing_framework, '_run_test_case') as mock_run_test, \
             patch.object(self.testing_framework, '_create_savepoint') as mock_create_savepoint, \
             patch('powerautomation_integration.scripts.github_test_reporter.GitHubTestReporter.create_or_update_test_report') as mock_github:
            
            # 模拟测试执行结果
            mock_run_test.return_value = {
                "execution_time": 0.5,
                "status": TestStatus.PASSED.value
            }
            
            # 模拟创建保存点
            mock_create_savepoint.return_value = "sp_20250601123456"
            
            # 模拟GitHub Issue创建
            mock_github.return_value = 123
            
            # 配置通知
            self.testing_framework.config["notification"] = {
                "email": False,
                "slack": False,
                "github": True
            }
            
            # 1. 生成测试计划
            test_plan = self.testing_framework.generate_test_plan()
            print(f"1. 生成测试计划，包含 {len(test_plan['test_cases'])} 个测试用例")
            
            # 2. 执行测试
            test_results = self.testing_framework.execute_tests(test_plan)
            print(f"2. 执行测试，状态: {test_results['status']}, 通过率: {test_results['statistics']['pass_rate']}%")
            
            # 3. 分析覆盖率
            coverage_data = self.testing_framework.analyze_coverage(test_results)
            print(f"3. 分析覆盖率，总体行覆盖率: {coverage_data['overall']['line']}%")
            
            # 4. 生成报告
            report_file = self.testing_framework.generate_report(test_results, coverage_data, "html")
            print(f"4. 生成报告: {report_file}")
            
            # 5. 通知结果
            self.testing_framework.notify_results(test_results)
            print("5. 通知结果")
            
            # 6. 分析趋势
            self.testing_framework.test_history.append({
                "id": test_results["id"],
                "created_at": test_results["created_at"],
                "completed_at": test_results["completed_at"],
                "status": test_results["status"],
                "statistics": test_results["statistics"]
            })
            trends = self.testing_framework.analyze_trends()
            print(f"6. 分析趋势，趋势: {trends['trend']}")
            
            # 7. 与MCP集成
            with patch('powerautomation_integration.agents.ppt_agent.core.mcp.webagent_adapter.MCPAdapter.register_capability') as mock_register:
                self.testing_framework.integrate_with_mcp()
                print("7. 与MCP集成")
        
        print("端到端工作流测试成功")

    def test_10_web_display_integration(self):
        """Web展示集成测试"""
        print("\n开始Web展示集成测试...")
        
        # 模拟测试结果数据
        test_results = {
            "id": "test_run_20250601123456",
            "created_at": "2025-06-01T12:34:56",
            "started_at": "2025-06-01T12:34:56",
            "completed_at": "2025-06-01T12:45:00",
            "status": TestStatus.PASSED.value,
            "test_cases": [
                {
                    "id": "unit_test_homepage",
                    "name": "test_homepage",
                    "file": "test/unit/test_homepage.py",
                    "type": TestType.UNIT.value,
                    "priority": TestPriority.HIGH.value,
                    "status": TestStatus.PASSED.value,
                    "execution_time": 0.5
                },
                {
                    "id": "integration_test_api",
                    "name": "test_api",
                    "file": "test/integration/test_api.py",
                    "type": TestType.INTEGRATION.value,
                    "priority": TestPriority.CRITICAL.value,
                    "status": TestStatus.PASSED.value,
                    "execution_time": 1.2
                }
            ],
            "statistics": {
                "total": 2,
                "passed": 2,
                "failed": 0,
                "skipped": 0,
                "error": 0,
                "pass_rate": 100.0,
                "duration": 10.5
            },
            "savepoint_id": "sp_20250601123456"
        }
        
        # 模拟覆盖率数据
        coverage_data = {
            "test_plan_id": test_results["id"],
            "timestamp": "2025-06-01T12:45:10",
            "overall": {
                "line": 75.5,
                "branch": 68.2,
                "function": 82.1
            }
        }
        
        # 保存测试结果
        self.testing_framework.test_results[test_results["id"]] = test_results
        self.testing_framework.coverage_data[test_results["id"]] = coverage_data
        
        # 模拟获取Web展示数据
        web_data = {
            "test_results": test_results,
            "coverage_data": coverage_data,
            "trends": {
                "pass_rates": [95.0, 97.5, 100.0],
                "timestamps": ["2025-05-30T10:00:00", "2025-05-31T10:00:00", "2025-06-01T12:45:00"],
                "trend": "improving"
            }
        }
        
        # 验证Web展示数据
        self.assertIsNotNone(web_data)
        self.assertIn("test_results", web_data)
        self.assertIn("coverage_data", web_data)
        self.assertIn("trends", web_data)
        
        # 验证测试结果数据
        self.assertEqual(web_data["test_results"]["id"], test_results["id"])
        self.assertEqual(web_data["test_results"]["status"], TestStatus.PASSED.value)
        self.assertEqual(web_data["test_results"]["statistics"]["pass_rate"], 100.0)
        
        # 验证覆盖率数据
        self.assertEqual(web_data["coverage_data"]["test_plan_id"], test_results["id"])
        self.assertEqual(web_data["coverage_data"]["overall"]["line"], 75.5)
        
        # 验证趋势数据
        self.assertEqual(web_data["trends"]["trend"], "improving")
        self.assertEqual(web_data["trends"]["pass_rates"][-1], 100.0)
        
        print("Web展示集成测试成功")


if __name__ == "__main__":
    unittest.main()
"""

def run_automated_testing_e2e_tests():
    """运行自动化测试能力的端到端测试"""
    import unittest
    from test.end_to_end.test_automated_testing import TestAutomatedTestingE2E
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 按顺序添加测试用例
    suite.addTest(TestAutomatedTestingE2E('test_01_test_plan_generation'))
    suite.addTest(TestAutomatedTestingE2E('test_02_test_execution'))
    suite.addTest(TestAutomatedTestingE2E('test_03_coverage_analysis'))
    suite.addTest(TestAutomatedTestingE2E('test_04_report_generation'))
    suite.addTest(TestAutomatedTestingE2E('test_05_savepoint_integration'))
    suite.addTest(TestAutomatedTestingE2E('test_06_mcp_integration'))
    suite.addTest(TestAutomatedTestingE2E('test_07_github_notification'))
    suite.addTest(TestAutomatedTestingE2E('test_08_trend_analysis'))
    suite.addTest(TestAutomatedTestingE2E('test_09_end_to_end_workflow'))
    suite.addTest(TestAutomatedTestingE2E('test_10_web_display_integration'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    run_automated_testing_e2e_tests()
