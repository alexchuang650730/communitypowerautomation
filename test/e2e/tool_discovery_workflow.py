#!/usr/bin/env python3
"""
工具发现工作流端到端测试
测试完整的工具发现和执行流程
"""

import sys
import os
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.unified_smart_tool_engine_mcp_v2 import UnifiedSmartToolEngineMCP

class TestToolDiscoveryWorkflow(unittest.TestCase):
    """工具发现工作流测试"""
    
    def setUp(self):
        """测试初始化"""
        self.tool_engine = UnifiedSmartToolEngineMCP()
    
    def test_tool_discovery_flow(self):
        """测试工具发现流程"""
        # 模拟用户请求
        request = {
            "action": "discover_tools",
            "query": "calendar scheduling",
            "filters": {"platforms": ["aci.dev"]}
        }
        
        result = self.tool_engine.process(request)
        
        self.assertIsInstance(result, dict)
        self.assertIn("tools", result)
        self.assertIn("total_count", result)
    
    def test_end_to_end_execution(self):
        """测试端到端工具执行"""
        # 发现工具
        discovery_result = self.tool_engine.process({
            "action": "discover_tools",
            "query": "data analysis"
        })
        
        self.assertIsInstance(discovery_result, dict)
        
        # 如果找到工具，测试执行
        if discovery_result.get("tools"):
            tool = discovery_result["tools"][0]
            execution_result = self.tool_engine.process({
                "action": "execute_tool",
                "tool_name": tool.get("name", "test_tool"),
                "parameters": {"test": "data"}
            })
            
            self.assertIsInstance(execution_result, dict)

if __name__ == "__main__":
    unittest.main()

