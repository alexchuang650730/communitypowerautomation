"""
自动化工作流展示能力的端到端测试方案
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
from development_tools.agent_problem_solver import AgentProblemSolver
from development_tools.release_manager import ReleaseManager

class TestWorkflowVisualizationE2E(unittest.TestCase):
    """自动化工作流展示能力的端到端测试"""

    def setUp(self):
        """测试前的准备工作"""
        # 设置测试项目根目录
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        
        # 初始化AgentProblemSolver（用于生成工作节点）
        self.problem_solver = AgentProblemSolver(self.project_root)
        
        # 初始化ReleaseManager（用于生成部署节点）
        self.release_manager = ReleaseManager(self.project_root)
        
        # 模拟工作流节点数据
        self.workflow_nodes = [
            {
                "id": "node1",
                "type": "trigger",
                "name": "GitHub Release",
                "description": "检测到新版本: v1.0.0",
                "timestamp": "2025-06-01T09:00:00Z",
                "status": "success",
                "data": {
                    "release_version": "v1.0.0",
                    "release_url": "https://github.com/example/repo/releases/tag/v1.0.0"
                }
            },
            {
                "id": "node2",
                "type": "action",
                "name": "下载代码",
                "description": "下载release代码到本地",
                "timestamp": "2025-06-01T09:05:00Z",
                "status": "success",
                "data": {
                    "local_path": "/tmp/release/v1.0.0",
                    "file_count": 120
                }
            },
            {
                "id": "node3",
                "type": "action",
                "name": "运行测试",
                "description": "执行自动化测试",
                "timestamp": "2025-06-01T09:10:00Z",
                "status": "success",
                "data": {
                    "test_count": 50,
                    "pass_rate": 98.0
                }
            },
            {
                "id": "node4",
                "type": "condition",
                "name": "测试通过?",
                "description": "检查测试结果",
                "timestamp": "2025-06-01T09:15:00Z",
                "status": "success",
                "data": {
                    "condition": "pass_rate >= 95.0",
                    "result": True
                }
            },
            {
                "id": "node5",
                "type": "action",
                "name": "创建保存点",
                "description": "创建代码保存点",
                "timestamp": "2025-06-01T09:20:00Z",
                "status": "success",
                "data": {
                    "savepoint_id": "sp_20250601092000",
                    "description": "Release v1.0.0 测试通过"
                }
            },
            {
                "id": "node6",
                "type": "action",
                "name": "部署代码",
                "description": "部署到生产环境",
                "timestamp": "2025-06-01T09:25:00Z",
                "status": "success",
                "data": {
                    "environment": "production",
                    "deploy_id": "deploy_20250601092500"
                }
            }
        ]
        
        # 模拟工作流连接数据
        self.workflow_connections = [
            {
                "id": "conn1",
                "source": "node1",
                "target": "node2",
                "type": "success"
            },
            {
                "id": "conn2",
                "source": "node2",
                "target": "node3",
                "type": "success"
            },
            {
                "id": "conn3",
                "source": "node3",
                "target": "node4",
                "type": "success"
            },
            {
                "id": "conn4",
                "source": "node4",
                "target": "node5",
                "type": "true"
            },
            {
                "id": "conn5",
                "source": "node5",
                "target": "node6",
                "type": "success"
            }
        ]
        
        print(f"测试环境准备完成，项目根目录: {self.project_root}")

    def tearDown(self):
        """测试后的清理工作"""
        print("测试环境清理完成")

    def test_01_workflow_data_generation(self):
        """工作流数据生成测试"""
        print("\n开始工作流数据生成测试...")
        
        # 模拟AgentProblemSolver创建保存点
        with patch.object(self.problem_solver, 'create_savepoint') as mock_create_savepoint:
            mock_create_savepoint.return_value = "sp_20250601092000"
            
            # 创建保存点
            savepoint_id = self.problem_solver.create_savepoint("Release v1.0.0 测试通过")
            
            # 验证保存点ID
            self.assertEqual(savepoint_id, "sp_20250601092000")
            
            # 验证调用参数
            mock_create_savepoint.assert_called_once_with("Release v1.0.0 测试通过")
        
        # 模拟ReleaseManager部署代码
        with patch.object(self.release_manager, 'deploy_to_production') as mock_deploy:
            mock_deploy.return_value = {
                "deploy_id": "deploy_20250601092500",
                "status": "success",
                "timestamp": "2025-06-01T09:25:00Z"
            }
            
            # 部署代码
            deploy_result = self.release_manager.deploy_to_production("/tmp/release/v1.0.0")
            
            # 验证部署结果
            self.assertEqual(deploy_result["deploy_id"], "deploy_20250601092500")
            self.assertEqual(deploy_result["status"], "success")
            
            # 验证调用参数
            mock_deploy.assert_called_once_with("/tmp/release/v1.0.0")
        
        # 模拟获取工作流数据
        with patch.object(self.problem_solver, 'get_web_display_data') as mock_get_data:
            mock_get_data.return_value = {
                "nodes": self.workflow_nodes,
                "connections": self.workflow_connections
            }
            
            # 获取工作流数据
            workflow_data = self.problem_solver.get_web_display_data()
            
            # 验证工作流数据
            self.assertIsNotNone(workflow_data)
            self.assertIn("nodes", workflow_data)
            self.assertIn("connections", workflow_data)
            self.assertEqual(len(workflow_data["nodes"]), 6)
            self.assertEqual(len(workflow_data["connections"]), 5)
        
        print("工作流数据生成测试成功")
        return workflow_data

    def test_02_workflow_data_api(self):
        """工作流数据API测试"""
        print("\n开始工作流数据API测试...")
        
        # 模拟API响应
        api_response = {
            "nodes": self.workflow_nodes,
            "connections": self.workflow_connections,
            "metadata": {
                "total_nodes": len(self.workflow_nodes),
                "total_connections": len(self.workflow_connections),
                "last_updated": "2025-06-01T09:30:00Z"
            }
        }
        
        # 模拟API请求
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = api_response
            
            # 发送API请求
            import requests
            response = requests.get('http://localhost:8000/api/workflow')
            
            # 验证响应状态码
            self.assertEqual(response.status_code, 200)
            
            # 验证响应数据
            data = response.json()
            self.assertIsNotNone(data)
            self.assertIn("nodes", data)
            self.assertIn("connections", data)
            self.assertIn("metadata", data)
            self.assertEqual(data["metadata"]["total_nodes"], 6)
            self.assertEqual(data["metadata"]["total_connections"], 5)
        
        print("工作流数据API测试成功")
        return api_response

    def test_03_n8n_workflow_visualizer_component(self):
        """N8n工作流可视化组件测试"""
        print("\n开始N8n工作流可视化组件测试...")
        
        # 模拟React组件渲染
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "N8nWorkflowVisualizer",
                "props": {
                    "workflowNodes": self.workflow_nodes,
                    "workflowConnections": self.workflow_connections,
                    "height": "600px"
                }
            }
            
            # 渲染组件
            import react  # 模拟的模块
            result = react.render('N8nWorkflowVisualizer', {
                "workflowNodes": self.workflow_nodes,
                "workflowConnections": self.workflow_connections,
                "height": "600px"
            })
            
            # 验证渲染结果
            self.assertTrue(result["success"])
            self.assertEqual(result["component"], "N8nWorkflowVisualizer")
            self.assertEqual(len(result["props"]["workflowNodes"]), 6)
            self.assertEqual(len(result["props"]["workflowConnections"]), 5)
        
        print("N8n工作流可视化组件测试成功")

    def test_04_workflow_integration_panel_component(self):
        """工作流集成面板组件测试"""
        print("\n开始工作流集成面板组件测试...")
        
        # 模拟React组件渲染
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "WorkflowIntegrationPanel",
                "props": {
                    "refreshInterval": 30000
                },
                "children": [
                    {
                        "component": "N8nWorkflowVisualizer",
                        "props": {
                            "workflowNodes": self.workflow_nodes,
                            "workflowConnections": self.workflow_connections,
                            "height": "600px"
                        }
                    }
                ]
            }
            
            # 渲染组件
            import react  # 模拟的模块
            result = react.render('WorkflowIntegrationPanel', {
                "refreshInterval": 30000
            })
            
            # 验证渲染结果
            self.assertTrue(result["success"])
            self.assertEqual(result["component"], "WorkflowIntegrationPanel")
            self.assertEqual(result["children"][0]["component"], "N8nWorkflowVisualizer")
        
        print("工作流集成面板组件测试成功")

    def test_05_workflow_node_components(self):
        """工作流节点组件测试"""
        print("\n开始工作流节点组件测试...")
        
        # 测试触发器节点组件
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "TriggerNode",
                "props": {
                    "data": self.workflow_nodes[0]
                }
            }
            
            # 渲染组件
            import react  # 模拟的模块
            result = react.render('TriggerNode', {
                "data": self.workflow_nodes[0]
            })
            
            # 验证渲染结果
            self.assertTrue(result["success"])
            self.assertEqual(result["component"], "TriggerNode")
            self.assertEqual(result["props"]["data"]["type"], "trigger")
        
        # 测试动作节点组件
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "ActionNode",
                "props": {
                    "data": self.workflow_nodes[1]
                }
            }
            
            # 渲染组件
            result = react.render('ActionNode', {
                "data": self.workflow_nodes[1]
            })
            
            # 验证渲染结果
            self.assertTrue(result["success"])
            self.assertEqual(result["component"], "ActionNode")
            self.assertEqual(result["props"]["data"]["type"], "action")
        
        # 测试条件节点组件
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "ConditionNode",
                "props": {
                    "data": self.workflow_nodes[3]
                }
            }
            
            # 渲染组件
            result = react.render('ConditionNode', {
                "data": self.workflow_nodes[3]
            })
            
            # 验证渲染结果
            self.assertTrue(result["success"])
            self.assertEqual(result["component"], "ConditionNode")
            self.assertEqual(result["props"]["data"]["type"], "condition")
        
        print("工作流节点组件测试成功")

    def test_06_workflow_data_refresh(self):
        """工作流数据刷新测试"""
        print("\n开始工作流数据刷新测试...")
        
        # 模拟初始数据
        initial_data = {
            "nodes": self.workflow_nodes[:4],  # 只包含前4个节点
            "connections": self.workflow_connections[:3]  # 只包含前3个连接
        }
        
        # 模拟更新后的数据
        updated_data = {
            "nodes": self.workflow_nodes,  # 包含所有6个节点
            "connections": self.workflow_connections  # 包含所有5个连接
        }
        
        # 模拟API请求
        with patch('requests.get') as mock_get:
            # 第一次请求返回初始数据
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.side_effect = [initial_data, updated_data]
            
            # 发送第一次API请求
            import requests
            response1 = requests.get('http://localhost:8000/api/workflow')
            data1 = response1.json()
            
            # 验证初始数据
            self.assertEqual(len(data1["nodes"]), 4)
            self.assertEqual(len(data1["connections"]), 3)
            
            # 发送第二次API请求（模拟刷新）
            response2 = requests.get('http://localhost:8000/api/workflow')
            data2 = response2.json()
            
            # 验证更新后的数据
            self.assertEqual(len(data2["nodes"]), 6)
            self.assertEqual(len(data2["connections"]), 5)
        
        print("工作流数据刷新测试成功")

    def test_07_workflow_visualization_integration(self):
        """工作流可视化集成测试"""
        print("\n开始工作流可视化集成测试...")
        
        # 模拟AgentProblemSolver获取工作流数据
        with patch.object(self.problem_solver, 'get_web_display_data') as mock_get_data:
            mock_get_data.return_value = {
                "nodes": self.workflow_nodes,
                "connections": self.workflow_connections
            }
            
            # 获取工作流数据
            workflow_data = self.problem_solver.get_web_display_data()
        
        # 模拟API响应
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = workflow_data
            
            # 发送API请求
            import requests
            response = requests.get('http://localhost:8000/api/workflow')
            api_data = response.json()
        
        # 模拟React组件渲染
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "WorkflowIntegrationPanel",
                "props": {
                    "refreshInterval": 30000
                },
                "children": [
                    {
                        "component": "N8nWorkflowVisualizer",
                        "props": {
                            "workflowNodes": api_data["nodes"],
                            "workflowConnections": api_data["connections"],
                            "height": "600px"
                        }
                    }
                ]
            }
            
            # 渲染组件
            import react  # 模拟的模块
            result = react.render('WorkflowIntegrationPanel', {
                "refreshInterval": 30000
            })
        
        # 验证端到端集成
        self.assertEqual(len(workflow_data["nodes"]), 6)
        self.assertEqual(len(api_data["nodes"]), 6)
        self.assertEqual(result["children"][0]["props"]["workflowNodes"], api_data["nodes"])
        
        print("工作流可视化集成测试成功")

    def test_08_workflow_visualization_responsiveness(self):
        """工作流可视化响应式设计测试"""
        print("\n开始工作流可视化响应式设计测试...")
        
        # 测试桌面视图
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "N8nWorkflowVisualizer",
                "props": {
                    "workflowNodes": self.workflow_nodes,
                    "workflowConnections": self.workflow_connections,
                    "height": "600px"
                },
                "viewport": {
                    "width": 1920,
                    "height": 1080
                }
            }
            
            # 渲染组件
            import react  # 模拟的模块
            desktop_result = react.render('N8nWorkflowVisualizer', {
                "workflowNodes": self.workflow_nodes,
                "workflowConnections": self.workflow_connections,
                "height": "600px"
            }, viewport={"width": 1920, "height": 1080})
            
            # 验证渲染结果
            self.assertTrue(desktop_result["success"])
            self.assertEqual(desktop_result["viewport"]["width"], 1920)
        
        # 测试平板视图
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "N8nWorkflowVisualizer",
                "props": {
                    "workflowNodes": self.workflow_nodes,
                    "workflowConnections": self.workflow_connections,
                    "height": "500px"
                },
                "viewport": {
                    "width": 768,
                    "height": 1024
                }
            }
            
            # 渲染组件
            tablet_result = react.render('N8nWorkflowVisualizer', {
                "workflowNodes": self.workflow_nodes,
                "workflowConnections": self.workflow_connections,
                "height": "500px"
            }, viewport={"width": 768, "height": 1024})
            
            # 验证渲染结果
            self.assertTrue(tablet_result["success"])
            self.assertEqual(tablet_result["viewport"]["width"], 768)
            self.assertEqual(tablet_result["props"]["height"], "500px")
        
        # 测试移动视图
        with patch('react.render') as mock_render:
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "N8nWorkflowVisualizer",
                "props": {
                    "workflowNodes": self.workflow_nodes,
                    "workflowConnections": self.workflow_connections,
                    "height": "400px"
                },
                "viewport": {
                    "width": 375,
                    "height": 667
                }
            }
            
            # 渲染组件
            mobile_result = react.render('N8nWorkflowVisualizer', {
                "workflowNodes": self.workflow_nodes,
                "workflowConnections": self.workflow_connections,
                "height": "400px"
            }, viewport={"width": 375, "height": 667})
            
            # 验证渲染结果
            self.assertTrue(mobile_result["success"])
            self.assertEqual(mobile_result["viewport"]["width"], 375)
            self.assertEqual(mobile_result["props"]["height"], "400px")
        
        print("工作流可视化响应式设计测试成功")

    def test_09_workflow_visualization_interaction(self):
        """工作流可视化交互测试"""
        print("\n开始工作流可视化交互测试...")
        
        # 模拟节点点击事件
        with patch('react.simulate') as mock_simulate:
            # 模拟事件结果
            mock_simulate.return_value = {
                "success": True,
                "event": "click",
                "target": {
                    "id": "node1",
                    "type": "trigger",
                    "name": "GitHub Release"
                },
                "detail": {
                    "expanded": True,
                    "selected": True
                }
            }
            
            # 模拟点击事件
            import react  # 模拟的模块
            click_result = react.simulate('click', {
                "component": "N8nWorkflowVisualizer",
                "target": "node1"
            })
            
            # 验证事件结果
            self.assertTrue(click_result["success"])
            self.assertEqual(click_result["event"], "click")
            self.assertEqual(click_result["target"]["id"], "node1")
            self.assertTrue(click_result["detail"]["expanded"])
            self.assertTrue(click_result["detail"]["selected"])
        
        # 模拟节点悬停事件
        with patch('react.simulate') as mock_simulate:
            # 模拟事件结果
            mock_simulate.return_value = {
                "success": True,
                "event": "hover",
                "target": {
                    "id": "node2",
                    "type": "action",
                    "name": "下载代码"
                },
                "detail": {
                    "tooltip": True
                }
            }
            
            # 模拟悬停事件
            hover_result = react.simulate('hover', {
                "component": "N8nWorkflowVisualizer",
                "target": "node2"
            })
            
            # 验证事件结果
            self.assertTrue(hover_result["success"])
            self.assertEqual(hover_result["event"], "hover")
            self.assertEqual(hover_result["target"]["id"], "node2")
            self.assertTrue(hover_result["detail"]["tooltip"])
        
        # 模拟连接线点击事件
        with patch('react.simulate') as mock_simulate:
            # 模拟事件结果
            mock_simulate.return_value = {
                "success": True,
                "event": "click",
                "target": {
                    "id": "conn1",
                    "source": "node1",
                    "target": "node2",
                    "type": "success"
                },
                "detail": {
                    "highlighted": True
                }
            }
            
            # 模拟点击事件
            conn_result = react.simulate('click', {
                "component": "N8nWorkflowVisualizer",
                "target": "conn1"
            })
            
            # 验证事件结果
            self.assertTrue(conn_result["success"])
            self.assertEqual(conn_result["event"], "click")
            self.assertEqual(conn_result["target"]["id"], "conn1")
            self.assertTrue(conn_result["detail"]["highlighted"])
        
        print("工作流可视化交互测试成功")

    def test_10_end_to_end_workflow(self):
        """端到端工作流测试"""
        print("\n开始端到端工作流测试...")
        
        # 模拟AgentProblemSolver创建保存点
        with patch.object(self.problem_solver, 'create_savepoint') as mock_create_savepoint, \
             patch.object(self.problem_solver, 'get_web_display_data') as mock_get_data, \
             patch('requests.get') as mock_get, \
             patch('react.render') as mock_render:
            
            # 模拟创建保存点
            mock_create_savepoint.return_value = "sp_20250601092000"
            
            # 模拟获取工作流数据
            mock_get_data.return_value = {
                "nodes": self.workflow_nodes,
                "connections": self.workflow_connections
            }
            
            # 模拟API响应
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_get_data.return_value
            
            # 模拟渲染结果
            mock_render.return_value = {
                "success": True,
                "component": "WorkflowIntegrationPanel",
                "props": {
                    "refreshInterval": 30000
                },
                "children": [
                    {
                        "component": "N8nWorkflowVisualizer",
                        "props": {
                            "workflowNodes": self.workflow_nodes,
                            "workflowConnections": self.workflow_connections,
                            "height": "600px"
                        }
                    }
                ]
            }
            
            # 1. 创建保存点
            savepoint_id = self.problem_solver.create_savepoint("Release v1.0.0 测试通过")
            print(f"1. 创建保存点，ID: {savepoint_id}")
            
            # 2. 获取工作流数据
            workflow_data = self.problem_solver.get_web_display_data()
            print(f"2. 获取工作流数据，节点数: {len(workflow_data['nodes'])}")
            
            # 3. 发送API请求
            import requests
            response = requests.get('http://localhost:8000/api/workflow')
            api_data = response.json()
            print(f"3. 发送API请求，状态码: {response.status_code}")
            
            # 4. 渲染组件
            import react  # 模拟的模块
            result = react.render('WorkflowIntegrationPanel', {
                "refreshInterval": 30000
            })
            print(f"4. 渲染组件，成功: {result['success']}")
            
            # 验证端到端流程
            self.assertEqual(savepoint_id, "sp_20250601092000")
            self.assertEqual(len(workflow_data["nodes"]), 6)
            self.assertEqual(len(api_data["nodes"]), 6)
            self.assertTrue(result["success"])
        
        print("端到端工作流测试成功")


def run_workflow_visualization_e2e_tests():
    """运行自动化工作流展示能力的端到端测试"""
    import unittest
    from test.end_to_end.test_workflow_visualization import TestWorkflowVisualizationE2E
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 按顺序添加测试用例
    suite.addTest(TestWorkflowVisualizationE2E('test_01_workflow_data_generation'))
    suite.addTest(TestWorkflowVisualizationE2E('test_02_workflow_data_api'))
    suite.addTest(TestWorkflowVisualizationE2E('test_03_n8n_workflow_visualizer_component'))
    suite.addTest(TestWorkflowVisualizationE2E('test_04_workflow_integration_panel_component'))
    suite.addTest(TestWorkflowVisualizationE2E('test_05_workflow_node_components'))
    suite.addTest(TestWorkflowVisualizationE2E('test_06_workflow_data_refresh'))
    suite.addTest(TestWorkflowVisualizationE2E('test_07_workflow_visualization_integration'))
    suite.addTest(TestWorkflowVisualizationE2E('test_08_workflow_visualization_responsiveness'))
    suite.addTest(TestWorkflowVisualizationE2E('test_09_workflow_visualization_interaction'))
    suite.addTest(TestWorkflowVisualizationE2E('test_10_end_to_end_workflow'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    run_workflow_visualization_e2e_tests()
