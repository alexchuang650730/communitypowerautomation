#!/usr/bin/env python3
"""
BaseMCP适配器单元测试
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.base_mcp import BaseMCP


class TestBaseMCP(unittest.TestCase):
    """BaseMCP适配器单元测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = BaseMCP("TestAdapter")
    
    def test_initialization(self):
        """测试适配器初始化"""
        self.assertEqual(self.adapter.name, "TestAdapter")
        self.assertIsNotNone(self.adapter.logger)
    
    def test_process_method(self):
        """测试process方法"""
        input_data = {"test": "data"}
        result = self.adapter.process(input_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        # 更新期望：BaseMCP现在返回success状态，因为它有默认的_process_implementation
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("metadata", result)
    
    def test_validate_input_method(self):
        """测试validate_input方法"""
        input_data = {"test": "data"}
        result = self.adapter.validate_input(input_data)
        
        self.assertIsInstance(result, bool)
        self.assertTrue(result)  # 默认返回True
    
    def test_get_capabilities_method(self):
        """测试get_capabilities方法"""
        capabilities = self.adapter.get_capabilities()
        
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)
        self.assertIn("基础MCP适配功能", capabilities)
    
    def test_get_status_method(self):
        """测试get_status方法"""
        status = self.adapter.get_status()
        
        self.assertIsInstance(status, dict)
        # 更新期望字段名：新的接口使用module_name而不是name
        self.assertIn("module_name", status)
        self.assertIn("status", status)
        self.assertIn("capabilities", status)
        self.assertIn("health_status", status)  # 更新字段名
        
        self.assertEqual(status["module_name"], "TestAdapter")
        self.assertEqual(status["status"], "active")
        self.assertEqual(status["health_status"], "ready")  # 更新期望值
        self.assertIsInstance(status["capabilities"], list)
    
    def test_inheritance_compatibility(self):
        """测试继承兼容性"""
        class TestChildAdapter(BaseMCP):
            def __init__(self):
                super().__init__("ChildAdapter")
            
            def process(self, input_data):
                return {"status": "success", "data": input_data}
        
        child_adapter = TestChildAdapter()
        self.assertEqual(child_adapter.name, "ChildAdapter")
        
        result = child_adapter.process({"test": "data"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], {"test": "data"})


if __name__ == "__main__":
    unittest.main()

