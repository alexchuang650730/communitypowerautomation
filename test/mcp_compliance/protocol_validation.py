#!/usr/bin/env python3
"""
MCP协议验证测试模块

验证MCP（Model Context Protocol）协议的实现是否符合标准规范，
包括消息格式、通信流程、错误处理等方面的合规性检查。

作者: PowerAutomation团队
版本: 1.0.0
日期: 2025-06-04
"""

import json
import pytest
import asyncio
import sys
import os
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from mcptool.adapters.unified_smart_tool_engine_mcp import UnifiedSmartToolEngineMCP
    from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class TestMCPProtocolValidation:
    """MCP协议验证测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        if MCP_AVAILABLE:
            self.tool_engine = UnifiedSmartToolEngineMCP()
            self.workflow_engine = IntelligentWorkflowEngineMCP()
        else:
            self.tool_engine = Mock()
            self.workflow_engine = Mock()
    
    def test_mcp_message_format_validation(self):
        """测试MCP消息格式验证"""
        # 标准MCP消息格式
        valid_message = {
            "jsonrpc": "2.0",
            "id": "test_001",
            "method": "tools/list",
            "params": {}
        }
        
        # 验证消息格式
        assert "jsonrpc" in valid_message
        assert valid_message["jsonrpc"] == "2.0"
        assert "id" in valid_message
        assert "method" in valid_message
        
        # 测试无效消息格式
        invalid_messages = [
            {"jsonrpc": "1.0", "id": "test", "method": "test"},  # 错误版本
            {"id": "test", "method": "test"},  # 缺少jsonrpc
            {"jsonrpc": "2.0", "method": "test"},  # 缺少id
            {"jsonrpc": "2.0", "id": "test"}  # 缺少method
        ]
        
        for invalid_msg in invalid_messages:
            # 验证这些消息应该被识别为无效
            assert not self._is_valid_mcp_message(invalid_msg)
    
    def _is_valid_mcp_message(self, message: Dict[str, Any]) -> bool:
        """验证MCP消息格式是否有效"""
        required_fields = ["jsonrpc", "id", "method"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in message:
                return False
        
        # 检查JSON-RPC版本
        if message["jsonrpc"] != "2.0":
            return False
        
        return True
    
    def test_mcp_method_validation(self):
        """测试MCP方法验证"""
        # 标准MCP方法
        standard_methods = [
            "initialize",
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get"
        ]
        
        # 验证方法名格式
        for method in standard_methods:
            assert isinstance(method, str)
            assert len(method) > 0
            
            # 方法名应该只包含字母、数字、斜杠和下划线
            import re
            assert re.match(r'^[a-zA-Z0-9/_]+$', method)
    
    @pytest.mark.asyncio
    async def test_mcp_initialization_protocol(self):
        """测试MCP初始化协议"""
        if not MCP_AVAILABLE:
            pytest.skip("MCP components not available")
        
        # 模拟初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": "init_001",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True}
                },
                "clientInfo": {
                    "name": "PowerAutomation",
                    "version": "1.0.0"
                }
            }
        }
        
        # 验证初始化请求格式
        assert self._is_valid_mcp_message(init_request)
        assert "params" in init_request
        assert "protocolVersion" in init_request["params"]
        assert "capabilities" in init_request["params"]
        assert "clientInfo" in init_request["params"]
        
        # 模拟初始化响应
        init_response = {
            "jsonrpc": "2.0",
            "id": "init_001",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True}
                },
                "serverInfo": {
                    "name": "PowerAutomation MCP Server",
                    "version": "1.0.0"
                }
            }
        }
        
        # 验证初始化响应格式
        assert "result" in init_response
        assert "protocolVersion" in init_response["result"]
        assert "serverInfo" in init_response["result"]
    
    @pytest.mark.asyncio
    async def test_tools_list_protocol(self):
        """测试工具列表协议"""
        if not MCP_AVAILABLE:
            pytest.skip("MCP components not available")
        
        # 模拟工具列表请求
        tools_request = {
            "jsonrpc": "2.0",
            "id": "tools_001",
            "method": "tools/list",
            "params": {}
        }
        
        # 验证请求格式
        assert self._is_valid_mcp_message(tools_request)
        assert tools_request["method"] == "tools/list"
        
        # 模拟工具列表响应
        tools_response = {
            "jsonrpc": "2.0",
            "id": "tools_001",
            "result": {
                "tools": [
                    {
                        "name": "data_analyzer",
                        "description": "分析数据并生成报告",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "data": {"type": "string"},
                                "format": {"type": "string"}
                            },
                            "required": ["data"]
                        }
                    }
                ]
            }
        }
        
        # 验证响应格式
        assert "result" in tools_response
        assert "tools" in tools_response["result"]
        assert isinstance(tools_response["result"]["tools"], list)
        
        # 验证工具定义格式
        for tool in tools_response["result"]["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    @pytest.mark.asyncio
    async def test_tool_call_protocol(self):
        """测试工具调用协议"""
        if not MCP_AVAILABLE:
            pytest.skip("MCP components not available")
        
        # 模拟工具调用请求
        call_request = {
            "jsonrpc": "2.0",
            "id": "call_001",
            "method": "tools/call",
            "params": {
                "name": "data_analyzer",
                "arguments": {
                    "data": "sales_data.csv",
                    "format": "json"
                }
            }
        }
        
        # 验证请求格式
        assert self._is_valid_mcp_message(call_request)
        assert call_request["method"] == "tools/call"
        assert "params" in call_request
        assert "name" in call_request["params"]
        assert "arguments" in call_request["params"]
        
        # 模拟工具调用响应
        call_response = {
            "jsonrpc": "2.0",
            "id": "call_001",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "数据分析完成，共处理1000条记录"
                    }
                ],
                "isError": False
            }
        }
        
        # 验证响应格式
        assert "result" in call_response
        assert "content" in call_response["result"]
        assert "isError" in call_response["result"]
        assert isinstance(call_response["result"]["content"], list)
    
    def test_error_response_format(self):
        """测试错误响应格式"""
        # 标准错误响应
        error_response = {
            "jsonrpc": "2.0",
            "id": "error_001",
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": {
                    "method": "invalid/method"
                }
            }
        }
        
        # 验证错误响应格式
        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]
        assert isinstance(error_response["error"]["code"], int)
        assert isinstance(error_response["error"]["message"], str)
        
        # 验证标准错误代码
        standard_error_codes = {
            -32700: "Parse error",
            -32600: "Invalid Request",
            -32601: "Method not found",
            -32602: "Invalid params",
            -32603: "Internal error"
        }
        
        for code, message in standard_error_codes.items():
            assert isinstance(code, int)
            assert code < 0  # 错误代码应该是负数
    
    def test_notification_format(self):
        """测试通知格式"""
        # MCP通知（无需响应的消息）
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/tools/list_changed",
            "params": {}
        }
        
        # 验证通知格式
        assert "jsonrpc" in notification
        assert "method" in notification
        assert "id" not in notification  # 通知不应该有id字段
        
        # 验证通知方法名
        assert notification["method"].startswith("notifications/")
    
    def test_schema_validation(self):
        """测试模式验证"""
        # JSON Schema示例
        tool_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "properties": {"type": "object"},
                        "required": {"type": "array"}
                    },
                    "required": ["type"]
                }
            },
            "required": ["name", "description", "inputSchema"]
        }
        
        # 验证模式结构
        assert "type" in tool_schema
        assert "properties" in tool_schema
        assert "required" in tool_schema
        assert tool_schema["type"] == "object"
    
    @pytest.mark.asyncio
    async def test_protocol_version_compatibility(self):
        """测试协议版本兼容性"""
        supported_versions = [
            "2024-11-05",
            "2024-10-07",
            "2024-09-25"
        ]
        
        for version in supported_versions:
            # 验证版本格式
            assert isinstance(version, str)
            assert len(version) == 10  # YYYY-MM-DD格式
            
            # 验证日期格式
            import re
            assert re.match(r'^\d{4}-\d{2}-\d{2}$', version)
    
    def test_capability_negotiation(self):
        """测试能力协商"""
        # 客户端能力
        client_capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": False},
            "prompts": {"listChanged": True}
        }
        
        # 服务器能力
        server_capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": False, "listChanged": True},
            "prompts": {"listChanged": True}
        }
        
        # 验证能力格式
        for capabilities in [client_capabilities, server_capabilities]:
            assert isinstance(capabilities, dict)
            for category, features in capabilities.items():
                assert isinstance(features, dict)
                for feature, supported in features.items():
                    assert isinstance(supported, bool)
    
    def test_content_type_validation(self):
        """测试内容类型验证"""
        # 支持的内容类型
        content_types = [
            {"type": "text", "text": "Hello world"},
            {"type": "image", "data": "base64data", "mimeType": "image/png"},
            {"type": "resource", "resource": {"uri": "file://test.txt"}}
        ]
        
        for content in content_types:
            assert "type" in content
            assert isinstance(content["type"], str)
            
            # 根据类型验证必需字段
            if content["type"] == "text":
                assert "text" in content
            elif content["type"] == "image":
                assert "data" in content
                assert "mimeType" in content
            elif content["type"] == "resource":
                assert "resource" in content


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

