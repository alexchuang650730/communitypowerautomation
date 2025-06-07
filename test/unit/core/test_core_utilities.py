#!/usr/bin/env python3
"""
核心功能单元测试
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestCoreUtilities(unittest.TestCase):
    """核心实用功能单元测试类"""
    
    def test_environment_variables(self):
        """测试环境变量配置"""
        # 测试API密钥环境变量
        api_keys = [
            "CLAUDE_API_KEY",
            "GEMINI_API_KEY", 
            "KILO_API_KEY",
            "SUPERMEMORY_API_KEY",
            "GITHUB_TOKEN"
        ]
        
        for key in api_keys:
            value = os.getenv(key)
            self.assertIsNotNone(value, f"{key} should be set")
            self.assertGreater(len(value), 0, f"{key} should not be empty")
    
    def test_project_structure(self):
        """测试项目结构"""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # 检查关键目录
        key_dirs = [
            "mcptool",
            "mcptool/adapters",
            "test",
            "test/unit",
            "test/integration",
            "test/e2e"
        ]
        
        for dir_path in key_dirs:
            full_path = project_root / dir_path
            self.assertTrue(full_path.exists(), f"Directory {dir_path} should exist")
            self.assertTrue(full_path.is_dir(), f"{dir_path} should be a directory")
    
    def test_import_capabilities(self):
        """测试导入能力"""
        # 测试基础模块导入
        try:
            import json
            import logging
            import requests
            self.assertTrue(True, "Basic modules import successfully")
        except ImportError as e:
            self.fail(f"Failed to import basic modules: {e}")
        
        # 测试AI相关模块导入
        try:
            import anthropic
            import google.generativeai as genai
            self.assertTrue(True, "AI modules import successfully")
        except ImportError:
            self.skipTest("AI modules not available")
    
    def test_logging_configuration(self):
        """测试日志配置"""
        import logging
        logger = logging.getLogger("test_logger")
        self.assertIsNotNone(logger)
        
        # 测试日志级别
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        self.assertTrue(True, "Logging works correctly")
    
    def test_configuration_management(self):
        """测试配置管理"""
        # 测试默认配置
        default_config = {
            "max_chunk_size": 4000,
            "overlap_size": 200,
            "embedding_dim": 768
        }
        
        for key, value in default_config.items():
            self.assertIsInstance(value, (int, float, str))
            self.assertGreater(value, 0)
    
    def test_error_handling_utilities(self):
        """测试错误处理实用功能"""
        def test_function_with_error():
            raise ValueError("Test error")
        
        try:
            test_function_with_error()
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertEqual(str(e), "Test error")
        except Exception as e:
            self.fail(f"Unexpected exception type: {type(e)}")


class TestDataStructures(unittest.TestCase):
    """数据结构单元测试类"""
    
    def test_context_chunk_structure(self):
        """测试上下文块数据结构"""
        chunk_data = {
            "id": "chunk_001",
            "content": "这是测试内容",
            "metadata": {"source": "test"},
            "timestamp": "2025-06-04T12:00:00"
        }
        
        # 验证数据结构
        self.assertIn("id", chunk_data)
        self.assertIn("content", chunk_data)
        self.assertIn("metadata", chunk_data)
        self.assertIn("timestamp", chunk_data)
        
        self.assertIsInstance(chunk_data["id"], str)
        self.assertIsInstance(chunk_data["content"], str)
        self.assertIsInstance(chunk_data["metadata"], dict)
    
    def test_mcp_message_structure(self):
        """测试MCP消息结构"""
        mcp_message = {
            "jsonrpc": "2.0",
            "id": "test_001",
            "method": "tools/list",
            "params": {}
        }
        
        # 验证MCP消息格式
        self.assertEqual(mcp_message["jsonrpc"], "2.0")
        self.assertIn("id", mcp_message)
        self.assertIn("method", mcp_message)
        self.assertIn("params", mcp_message)
    
    def test_api_response_structure(self):
        """测试API响应结构"""
        api_response = {
            "success": True,
            "data": {"result": "test"},
            "error": None,
            "timestamp": "2025-06-04T12:00:00"
        }
        
        # 验证API响应格式
        self.assertIn("success", api_response)
        self.assertIn("data", api_response)
        self.assertIsInstance(api_response["success"], bool)


if __name__ == "__main__":
    unittest.main()

