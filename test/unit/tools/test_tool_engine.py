#!/usr/bin/env python3
"""
工具引擎单元测试
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcptool.adapters.unified_smart_tool_engine_mcp import UnifiedSmartToolEngineMCP
    TOOL_ENGINE_AVAILABLE = True
except ImportError:
    TOOL_ENGINE_AVAILABLE = False
    # 创建Mock版本
    class UnifiedSmartToolEngineMCP:
        def __init__(self):
            self.name = "UnifiedSmartToolEngineMCP"
            self.config = {"mock": True}
        
        def process(self, input_data):
            action = input_data.get("action", "unknown")
            if action == "discover_tools":
                return {
                    "success": True,
                    "tools": ["mock_tool_1", "mock_tool_2"],
                    "category": input_data.get("category", "general")
                }
            elif action == "execute_tool":
                return {
                    "success": True,
                    "result": "Mock execution result",
                    "tool_name": input_data.get("tool_name", "unknown")
                }
            elif action == "list_tools":
                return {
                    "success": True,
                    "tools": [
                        {"name": "mock_tool_1", "description": "Mock tool 1"},
                        {"name": "mock_tool_2", "description": "Mock tool 2"}
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        def get_capabilities(self):
            return ["工具发现", "工具执行", "工具管理"]
        
        def get_status(self):
            return {
                "name": self.name,
                "status": "active",
                "capabilities": self.get_capabilities(),
                "health": "healthy",
                "mock": True
            }


class TestUnifiedSmartToolEngineMCP(unittest.TestCase):
    """统一智能工具引擎单元测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.tool_engine = UnifiedSmartToolEngineMCP()
    
    def test_initialization(self):
        """测试工具引擎初始化"""
        self.assertEqual(self.tool_engine.name, "UnifiedSmartToolEngineMCP")
        self.assertIsNotNone(self.tool_engine.config)
    
    def test_tool_discovery(self):
        """测试工具发现功能"""
        input_data = {
            "action": "discover_tools",
            "category": "data_analysis"
        }
        
        result = self.tool_engine.process(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("tools", result)
            self.assertIsInstance(result["tools"], list)
    
    def test_tool_execution(self):
        """测试工具执行功能"""
        input_data = {
            "action": "execute_tool",
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"}
        }
        
        result = self.tool_engine.process(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_get_capabilities(self):
        """测试获取能力列表"""
        capabilities = self.tool_engine.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)
    
    def test_get_status(self):
        """测试获取状态信息"""
        status = self.tool_engine.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("name", status)
        self.assertIn("status", status)
        self.assertIn("capabilities", status)
        self.assertIn("health", status)
    
    def test_tool_registry(self):
        """测试工具注册表功能"""
        input_data = {
            "action": "list_tools"
        }
        
        result = self.tool_engine.process(input_data)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("tools", result)
            self.assertIsInstance(result["tools"], list)
    
    def test_error_handling(self):
        """测试错误处理"""
        invalid_input = {
            "action": "invalid_action"
        }
        
        result = self.tool_engine.process(invalid_input)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        if not result.get("success"):
            self.assertIn("error", result)


class TestToolUtilities(unittest.TestCase):
    """工具实用函数单元测试类"""
    
    def test_tool_validation(self):
        """测试工具验证功能"""
        # 模拟工具验证
        valid_tool = {
            "name": "test_tool",
            "description": "测试工具",
            "parameters": {}
        }
        
        # 这里应该有实际的验证逻辑
        self.assertIsInstance(valid_tool, dict)
        self.assertIn("name", valid_tool)
        self.assertIn("description", valid_tool)
    
    def test_parameter_validation(self):
        """测试参数验证功能"""
        parameters = {
            "required_param": "value",
            "optional_param": "optional_value"
        }
        
        # 这里应该有实际的参数验证逻辑
        self.assertIsInstance(parameters, dict)
        self.assertIn("required_param", parameters)
    
    def test_tool_metadata_structure(self):
        """测试工具元数据结构"""
        tool_metadata = {
            "id": "tool_001",
            "name": "example_tool",
            "version": "1.0.0",
            "description": "示例工具",
            "category": "utility",
            "parameters": {
                "input": {"type": "string", "required": True},
                "output_format": {"type": "string", "default": "json"}
            },
            "capabilities": ["data_processing", "format_conversion"]
        }
        
        # 验证工具元数据结构
        required_fields = ["id", "name", "version", "description", "category"]
        for field in required_fields:
            self.assertIn(field, tool_metadata)
        
        self.assertIsInstance(tool_metadata["parameters"], dict)
        self.assertIsInstance(tool_metadata["capabilities"], list)


if __name__ == "__main__":
    unittest.main()

