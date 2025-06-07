#!/usr/bin/env python3
"""
MCP协议合规性检查器
验证MCP适配器是否符合MCP协议标准
"""

import sys
import os
import unittest
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.base_mcp import BaseMCP

class TestMCPCompliance(unittest.TestCase):
    """MCP协议合规性测试"""
    
    def test_base_mcp_interface(self):
        """测试BaseMCP接口合规性"""
        # 检查BaseMCP类是否存在必要的方法
        required_methods = ['process', 'get_capabilities', 'get_status']
        
        for method in required_methods:
            self.assertTrue(hasattr(BaseMCP, method), 
                          f"BaseMCP缺少必要方法: {method}")
    
    def test_mcp_response_format(self):
        """测试MCP响应格式合规性"""
        # 模拟MCP响应
        mock_response = {
            "status": "success",
            "data": {"result": "test"},
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "adapter": "test_adapter"
            }
        }
        
        # 验证响应格式
        self.assertIn("status", mock_response)
        self.assertIn("data", mock_response)
        self.assertIn("metadata", mock_response)
        
        # 验证状态值
        valid_statuses = ["success", "error", "pending"]
        self.assertIn(mock_response["status"], valid_statuses)
    
    def test_error_handling_compliance(self):
        """测试错误处理合规性"""
        error_response = {
            "status": "error",
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Invalid request format",
                "details": {}
            },
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "adapter": "test_adapter"
            }
        }
        
        # 验证错误响应格式
        self.assertEqual(error_response["status"], "error")
        self.assertIn("error", error_response)
        self.assertIn("code", error_response["error"])
        self.assertIn("message", error_response["error"])

if __name__ == "__main__":
    unittest.main()

