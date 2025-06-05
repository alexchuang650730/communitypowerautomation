#!/usr/bin/env python3
"""
MCPTool与Kilocode集成测试
测试MCPTool与Kilocode API的集成功能
"""

import sys
import os
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.infinite_context_adapter_mcp import InfiniteContextAdapterMCP

class TestMCPToolKilocodeIntegration(unittest.TestCase):
    """MCPTool与Kilocode集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.adapter = InfiniteContextAdapterMCP()
    
    def test_kilo_api_connection(self):
        """测试Kilo API连接"""
        # 检查API密钥配置
        self.assertIsNotNone(self.adapter.kilo_api_key, "KILO_API_KEY未配置")
    
    def test_code_analysis_integration(self):
        """测试代码分析集成"""
        test_code = """
def hello_world():
    print("Hello, World!")
    return "success"
        """
        
        result = self.adapter.process({
            "action": "analyze_context",
            "content": test_code,
            "context_type": "code"
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn("analysis", result)

if __name__ == "__main__":
    unittest.main()

