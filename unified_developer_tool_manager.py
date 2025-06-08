#!/usr/bin/env python3
"""
PowerAutomation v0.2 統一開發工具管理器
整合所有開發工具MCP適配器，提供統一的開發工具接口
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

# 導入標準化日誌系統
from standardized_logging_system import get_logger, log_info, log_error, LogCategory, performance_monitor

# 導入開發工具組件
try:
    from mcptool.core.development_tools.release_manager import ReleaseManager
    from mcptool.adapters.kilocode_adapter.kilocode_mcp import KiloCodeAdapter
    from mcptool.adapters.unified_smart_tool_engine_mcp import UnifiedSmartToolEngine
except ImportError as e:
    log_error(LogCategory.SYSTEM, f"開發工具導入失敗: {e}")

class DeveloperToolType(Enum):
    """開發工具類型"""
    CODE_GENERATION = "code_generation"
    RELEASE_MANAGEMENT = "release_management"
    PROBLEM_SOLVING = "problem_solving"
    TOOL_SELECTION = "tool_selection"
    THOUGHT_RECORDING = "thought_recording"

@dataclass
class DeveloperToolInfo:
    """開發工具信息"""
    name: str
    type: DeveloperToolType
    description: str
    version: str
    status: str
    capabilities: List[str]
    mcp_adapter: Optional[Any] = None

class UnifiedDeveloperToolManager:
    """統一開發工具管理器"""
    
    def __init__(self, project_dir: str = "/home/ubuntu/projects/communitypowerautomation"):
        self.project_dir = Path(project_dir)
        self.logger = get_logger()
        self.tools = {}
        self.active_tools = {}
        
        # 初始化開發工具
        self._initialize_tools()
        
        log_info(LogCategory.SYSTEM, "統一開發工具管理器初始化完成", {
            'project_dir': str(self.project_dir),
            'tools_count': len(self.tools)
        })
    
    def _initialize_tools(self):
        """初始化所有開發工具"""
        
        # 1. KiloCode代碼生成工具
        try:
            kilocode_adapter = KiloCodeAdapter()
            self.tools['kilocode'] = DeveloperToolInfo(
                name="KiloCode",
                type=DeveloperToolType.CODE_GENERATION,
                description="智能代碼生成和優化工具",
                version="v1.0",
                status="active",
                capabilities=["code_generation", "code_optimization", "code_explanation"],
                mcp_adapter=kilocode_adapter
            )
            log_info(LogCategory.MCP, "KiloCode適配器初始化成功")
        except Exception as e:
            log_error(LogCategory.MCP, "KiloCode適配器初始化失敗", exception=e)
        
        # 2. Release Manager發布管理工具
        try:
            release_manager = ReleaseManager(str(self.project_dir))
            self.tools['release_manager'] = DeveloperToolInfo(
                name="Release Manager",
                type=DeveloperToolType.RELEASE_MANAGEMENT,
                description="智能發布管理和版本控制工具",
                version="v1.0",
                status="active",
                capabilities=["version_management", "release_automation", "deployment"],
                mcp_adapter=release_manager
            )
            log_info(LogCategory.SYSTEM, "Release Manager初始化成功")
        except Exception as e:
            log_error(LogCategory.SYSTEM, "Release Manager初始化失敗", exception=e)
        
        # 3. 統一智能工具引擎
        try:
            tool_engine = UnifiedSmartToolEngine()
            self.tools['tool_engine'] = DeveloperToolInfo(
                name="Unified Tool Engine",
                type=DeveloperToolType.TOOL_SELECTION,
                description="統一智能工具選擇和管理引擎",
                version="v1.0",
                status="active",
                capabilities=["tool_selection", "tool_classification", "intelligent_routing"],
                mcp_adapter=tool_engine
            )
            log_info(LogCategory.MCP, "統一工具引擎初始化成功")
        except Exception as e:
            log_error(LogCategory.MCP, "統一工具引擎初始化失敗", exception=e)
    
    @performance_monitor("get_tool_info")
    def get_tool_info(self, tool_name: str) -> Optional[DeveloperToolInfo]:
        """獲取工具信息"""
        return self.tools.get(tool_name)
    
    @performance_monitor("list_tools")
    def list_tools(self, tool_type: Optional[DeveloperToolType] = None) -> List[DeveloperToolInfo]:
        """列出所有工具"""
        if tool_type:
            return [tool for tool in self.tools.values() if tool.type == tool_type]
        return list(self.tools.values())
    
    @performance_monitor("execute_kilocode_generation")
    def execute_kilocode_generation(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """執行KiloCode代碼生成"""
        try:
            kilocode_tool = self.tools.get('kilocode')
            if not kilocode_tool or not kilocode_tool.mcp_adapter:
                raise ValueError("KiloCode工具不可用")
            
            log_info(LogCategory.MCP, "開始KiloCode代碼生成", {
                'prompt_length': len(prompt),
                'language': language
            })
            
            # 調用KiloCode適配器
            result = kilocode_tool.mcp_adapter.generate_code(prompt, language)
            
            log_info(LogCategory.MCP, "KiloCode代碼生成完成", {
                'success': True,
                'result_length': len(str(result))
            })
            
            return {
                'success': True,
                'result': result,
                'tool': 'kilocode',
                'language': language
            }
            
        except Exception as e:
            log_error(LogCategory.MCP, "KiloCode代碼生成失敗", {'prompt': prompt[:100]}, e)
            return {
                'success': False,
                'error': str(e),
                'tool': 'kilocode'
            }
    
    @performance_monitor("execute_release_management")
    def execute_release_management(self, action: str, **kwargs) -> Dict[str, Any]:
        """執行Release Manager操作"""
        try:
            release_tool = self.tools.get('release_manager')
            if not release_tool or not release_tool.mcp_adapter:
                raise ValueError("Release Manager工具不可用")
            
            log_info(LogCategory.SYSTEM, f"開始Release Manager操作: {action}", kwargs)
            
            # 根據操作類型調用相應方法
            release_manager = release_tool.mcp_adapter
            
            if action == "create_release":
                result = release_manager.create_release(**kwargs)
            elif action == "deploy_release":
                result = release_manager.deploy_release(**kwargs)
            elif action == "get_release_status":
                result = release_manager.get_release_status(**kwargs)
            else:
                raise ValueError(f"不支持的操作: {action}")
            
            log_info(LogCategory.SYSTEM, f"Release Manager操作完成: {action}", {
                'success': True,
                'result_type': type(result).__name__
            })
            
            return {
                'success': True,
                'result': result,
                'tool': 'release_manager',
                'action': action
            }
            
        except Exception as e:
            log_error(LogCategory.SYSTEM, f"Release Manager操作失敗: {action}", kwargs, e)
            return {
                'success': False,
                'error': str(e),
                'tool': 'release_manager',
                'action': action
            }
    
    @performance_monitor("execute_development_workflow")
    def execute_development_workflow(self, 
                                   requirement: str,
                                   language: str = "python",
                                   auto_deploy: bool = False) -> Dict[str, Any]:
        """執行完整的開發工作流程"""
        try:
            log_info(LogCategory.SYSTEM, "開始執行開發工作流程", {
                'requirement_length': len(requirement),
                'language': language,
                'auto_deploy': auto_deploy
            })
            
            workflow_results = {
                'steps': [],
                'success': True,
                'final_result': None
            }
            
            # 步驟1: 使用KiloCode生成代碼
            log_info(LogCategory.SYSTEM, "工作流程步驟1: 代碼生成")
            code_result = self.execute_kilocode_generation(requirement, language)
            workflow_results['steps'].append({
                'step': 'code_generation',
                'result': code_result
            })
            
            if not code_result['success']:
                workflow_results['success'] = False
                return workflow_results
            
            # 步驟2: 如果啟用自動部署，使用Release Manager
            if auto_deploy:
                log_info(LogCategory.SYSTEM, "工作流程步驟2: 自動部署")
                deploy_result = self.execute_release_management(
                    "create_release",
                    version="auto",
                    description=f"自動生成的發布: {requirement[:50]}..."
                )
                workflow_results['steps'].append({
                    'step': 'auto_deploy',
                    'result': deploy_result
                })
                
                if not deploy_result['success']:
                    workflow_results['success'] = False
                    return workflow_results
            
            workflow_results['final_result'] = "開發工作流程執行成功"
            
            log_info(LogCategory.SYSTEM, "開發工作流程執行完成", {
                'success': True,
                'steps_count': len(workflow_results['steps'])
            })
            
            return workflow_results
            
        except Exception as e:
            log_error(LogCategory.SYSTEM, "開發工作流程執行失敗", {
                'requirement': requirement[:100],
                'language': language
            }, e)
            return {
                'success': False,
                'error': str(e),
                'steps': workflow_results.get('steps', [])
            }
    
    def get_tool_status(self) -> Dict[str, Any]:
        """獲取所有工具狀態"""
        status = {
            'total_tools': len(self.tools),
            'active_tools': len([t for t in self.tools.values() if t.status == 'active']),
            'tools': {}
        }
        
        for name, tool in self.tools.items():
            status['tools'][name] = {
                'name': tool.name,
                'type': tool.type.value,
                'status': tool.status,
                'capabilities': tool.capabilities,
                'version': tool.version
            }
        
        return status
    
    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        health_status = {
            'overall_health': 'healthy',
            'tools_health': {},
            'issues': []
        }
        
        for name, tool in self.tools.items():
            try:
                # 簡單的健康檢查
                if tool.mcp_adapter:
                    health_status['tools_health'][name] = 'healthy'
                else:
                    health_status['tools_health'][name] = 'no_adapter'
                    health_status['issues'].append(f"{name}: 缺少MCP適配器")
            except Exception as e:
                health_status['tools_health'][name] = 'error'
                health_status['issues'].append(f"{name}: {str(e)}")
        
        if health_status['issues']:
            health_status['overall_health'] = 'degraded'
        
        return health_status

# 全局開發工具管理器實例
_global_dev_tool_manager = None

def get_developer_tool_manager() -> UnifiedDeveloperToolManager:
    """獲取全局開發工具管理器實例"""
    global _global_dev_tool_manager
    if _global_dev_tool_manager is None:
        _global_dev_tool_manager = UnifiedDeveloperToolManager()
    return _global_dev_tool_manager

# 便捷函數
def generate_code(prompt: str, language: str = "python") -> Dict[str, Any]:
    """便捷的代碼生成函數"""
    return get_developer_tool_manager().execute_kilocode_generation(prompt, language)

def manage_release(action: str, **kwargs) -> Dict[str, Any]:
    """便捷的發布管理函數"""
    return get_developer_tool_manager().execute_release_management(action, **kwargs)

def run_development_workflow(requirement: str, language: str = "python", auto_deploy: bool = False) -> Dict[str, Any]:
    """便捷的開發工作流程函數"""
    return get_developer_tool_manager().execute_development_workflow(requirement, language, auto_deploy)

if __name__ == "__main__":
    # 測試統一開發工具管理器
    manager = UnifiedDeveloperToolManager()
    
    # 測試工具列表
    print("=== 開發工具列表 ===")
    tools = manager.list_tools()
    for tool in tools:
        print(f"- {tool.name} ({tool.type.value}): {tool.description}")
    
    # 測試工具狀態
    print("\n=== 工具狀態 ===")
    status = manager.get_tool_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 測試健康檢查
    print("\n=== 健康檢查 ===")
    health = manager.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    
    # 測試代碼生成（如果KiloCode可用）
    print("\n=== 測試代碼生成 ===")
    code_result = manager.execute_kilocode_generation("創建一個計算斐波那契數列的函數", "python")
    print(f"代碼生成結果: {code_result['success']}")
    
    # 測試開發工作流程
    print("\n=== 測試開發工作流程 ===")
    workflow_result = manager.execute_development_workflow(
        "創建一個簡單的Web API",
        language="python",
        auto_deploy=False
    )
    print(f"工作流程結果: {workflow_result['success']}")
    print(f"執行步驟數: {len(workflow_result['steps'])}")

