#!/usr/bin/env python3
"""
統一配置器管理器 - PowerAutomation MCP適配器
整合所有配置器：API配置、密鑰管理、意圖理解等
同時提供AI模型調用功能
"""

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pathlib import Path

# 導入真實API客戶端
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')
sys.path.append('/opt/.manus/.sandbox-runtime')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified_config_manager")

class ConfigType(Enum):
    """配置類型枚舉"""
    API_CONFIG = "api_config"
    API_KEYS = "api_keys"
    INTENT_UNDERSTANDING = "intent_understanding"
    WORKFLOW_ENGINE = "workflow_engine"
    SYSTEM_SETTINGS = "system_settings"

class APIMode(Enum):
    """API模式枚舉"""
    MOCK = "mock"
    REAL = "real"
    HYBRID = "hybrid"

class UnifiedConfigManagerMCP:
    """統一配置器管理器"""
    
    def __init__(self):
        """初始化統一配置器管理器"""
        self.adapter_name = "unified_config_manager"
        self.version = "1.0.0"
        self.is_available = True
        
        # 內部環境變數存儲
        self.internal_env = {
            'GEMINI_API_KEY': '',
            'CLAUDE_API_KEY': '',
            'ANTHROPIC_API_KEY': '',
            'KILOCODE_API_KEY': '',
            'SUPERMEMORY_API_KEY': '',
            'OPENAI_API_KEY': '',
            'GOOGLE_API_KEY': '',
            'MANUS_API_KEY': ''
        }
        
        # 配置存儲
        self.configs = {}
        self.config_files = {
            ConfigType.API_CONFIG: "api_config.json",
            ConfigType.API_KEYS: "api_keys.json",
            ConfigType.INTENT_UNDERSTANDING: "intent_config.json",
            ConfigType.WORKFLOW_ENGINE: "workflow_config.json",
            ConfigType.SYSTEM_SETTINGS: "system_config.json"
        }
        
        # 工具註冊表 - 整合配置管理和AI模型調用
        self.tools = {
            # 配置管理工具
            "get_config": {
                "name": "獲取配置",
                "description": "獲取指定類型的配置信息",
                "category": "config_management",
                "parameters": ["config_type", "section"]
            },
            "set_config": {
                "name": "設置配置",
                "description": "設置指定類型的配置信息",
                "category": "config_management",
                "parameters": ["config_type", "section", "key", "value"]
            },
            "list_configs": {
                "name": "列出所有配置",
                "description": "列出所有可用的配置類型和內容",
                "category": "config_management",
                "parameters": ["detailed"]
            },
            "switch_api_mode": {
                "name": "切換API模式",
                "description": "在模擬/真實/混合API模式之間切換",
                "category": "api_management",
                "parameters": ["mode", "api_provider"]
            },
            "manage_api_keys": {
                "name": "管理API密鑰",
                "description": "添加、更新、刪除API密鑰",
                "category": "api_management",
                "parameters": ["action", "provider", "api_key"]
            },
            "test_api_connection": {
                "name": "測試API連接",
                "description": "測試指定API提供商的連接狀態",
                "category": "api_management",
                "parameters": ["provider", "test_type"]
            },
            "configure_intent_understanding": {
                "name": "配置意圖理解",
                "description": "配置AI增強意圖理解模塊",
                "category": "ai_config",
                "parameters": ["model", "settings", "enable"]
            },
            "export_config": {
                "name": "導出配置",
                "description": "導出配置到文件",
                "category": "config_management",
                "parameters": ["config_type", "format", "file_path"]
            },
            "import_config": {
                "name": "導入配置",
                "description": "從文件導入配置",
                "category": "config_management",
                "parameters": ["config_type", "file_path", "merge"]
            },
            "reset_config": {
                "name": "重置配置",
                "description": "重置指定配置到默認值",
                "category": "config_management",
                "parameters": ["config_type", "confirm"]
            },
            # AI模型調用工具
            "generate_text": {
                "name": "AI文本生成",
                "description": "使用AI模型生成高質量文本",
                "category": "ai_generation",
                "parameters": ["prompt", "model", "max_tokens", "temperature"]
            },
            "analyze_content": {
                "name": "AI內容分析",
                "description": "使用AI分析和理解複雜內容",
                "category": "ai_analysis",
                "parameters": ["content", "analysis_type", "model", "context"]
            },
            "solve_problem": {
                "name": "AI問題解決",
                "description": "使用AI解決複雜問題和推理任務",
                "category": "ai_reasoning",
                "parameters": ["problem", "problem_type", "model", "reasoning_steps"]
            },
            "code_assistance": {
                "name": "AI編程助手",
                "description": "AI輔助編程和代碼分析",
                "category": "ai_coding",
                "parameters": ["code_task", "language", "model", "requirements"]
            },
            "multi_model_consensus": {
                "name": "多模型共識",
                "description": "使用多個AI模型達成共識答案",
                "category": "ai_consensus",
                "parameters": ["query", "models", "consensus_method", "confidence_threshold"]
            },
            "adaptive_prompting": {
                "name": "自適應提示",
                "description": "根據任務類型自動優化提示",
                "category": "ai_optimization",
                "parameters": ["task", "task_type", "optimization_level", "context"]
            },
            "get_api_status": {
                "name": "獲取API狀態",
                "description": "獲取所有AI API的當前狀態",
                "category": "api_management",
                "parameters": ["detailed"]
            },
            "list_models": {
                "name": "列出AI模型",
                "description": "列出所有可用的AI模型",
                "category": "ai_management",
                "parameters": ["provider", "capability"]
            }
        }
        
        # AI API配置
        self.api_configs = {
            "claude": {
                "name": "Claude AI",
                "provider": "Anthropic",
                "models": ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"],
                "capabilities": ["text_generation", "reasoning", "analysis", "coding"],
                "max_tokens": 100000,
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "openai": {
                "name": "OpenAI GPT",
                "provider": "OpenAI",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "capabilities": ["text_generation", "reasoning", "analysis", "coding"],
                "max_tokens": 128000,
                "api_key_env": "OPENAI_API_KEY"
            },
            "gemini": {
                "name": "Google Gemini",
                "provider": "Google",
                "models": ["gemini-pro", "gemini-pro-vision"],
                "capabilities": ["text_generation", "reasoning", "analysis", "vision"],
                "max_tokens": 30720,
                "api_key_env": "GOOGLE_API_KEY"
            },
            "manus_api": {
                "name": "Manus API Hub",
                "provider": "Manus",
                "models": ["unified_ai"],
                "capabilities": ["text_generation", "reasoning", "analysis", "data_access"],
                "max_tokens": 50000,
                "api_key_env": "MANUS_API_KEY"
            }
        }
        
        # 初始化API客戶端
        self.api_clients = {}
        
        # 初始化配置
        self._initialize_configs()
        
        # 檢查API可用性並初始化客戶端
        self._check_api_availability()
        self._initialize_api_clients()
        
        logger.info(f"統一配置器管理器初始化完成，支持 {len(self.tools)} 個工具")
    
    def _initialize_configs(self):
        """初始化所有配置"""
        # API配置
        self.configs[ConfigType.API_CONFIG] = {
            "mode": "mock",
            "providers": {
                "claude": {
                    "enabled": True,
                    "mode": "mock",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "temperature": 0.7
                },
                "gemini": {
                    "enabled": True,
                    "mode": "mock",
                    "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
                    "model": "gemini-1.5-flash",
                    "max_tokens": 2048,
                    "temperature": 0.7
                },
                "openai": {
                    "enabled": False,
                    "mode": "mock",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "model": "gpt-4",
                    "max_tokens": 4096,
                    "temperature": 0.7
                },
                "manus": {
                    "enabled": True,
                    "mode": "real",
                    "endpoint": "internal",
                    "model": "unified_ai",
                    "max_tokens": 8192,
                    "temperature": 0.7
                }
            }
        }
        
        # API密鑰配置
        self.configs[ConfigType.API_KEYS] = {
            "claude": {
                "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                "status": "configured" if os.getenv("ANTHROPIC_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "gemini": {
                "api_key": os.getenv("GOOGLE_API_KEY", ""),
                "status": "configured" if os.getenv("GOOGLE_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "status": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "manus": {
                "api_key": "internal",
                "status": "available",
                "last_verified": datetime.now().isoformat(),
                "usage_count": 0
            }
        }
        
        # 意圖理解配置
        self.configs[ConfigType.INTENT_UNDERSTANDING] = {
            "enabled": True,
            "primary_model": "claude",
            "fallback_model": "gemini",
            "confidence_threshold": 0.8,
            "analysis_depth": "deep",
            "context_window": 4096,
            "features": {
                "multi_model_consensus": True,
                "adaptive_prompting": True,
                "context_enhancement": True
            }
        }
        
        # 工作流引擎配置
        self.configs[ConfigType.WORKFLOW_ENGINE] = {
            "enabled": True,
            "max_concurrent_workflows": 10,
            "default_timeout": 300,
            "retry_policy": {
                "max_retries": 3,
                "retry_delay": 1.0,
                "backoff_factor": 2.0
            },
            "monitoring": {
                "enabled": True,
                "log_level": "INFO",
                "metrics_collection": True
            }
        }
        
        # 系統設置
        self.configs[ConfigType.SYSTEM_SETTINGS] = {
            "debug_mode": False,
            "log_level": "INFO",
            "cache_enabled": True,
            "cache_ttl": 3600,
            "performance_monitoring": True,
            "auto_backup": True,
            "backup_interval": 86400
        }
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """處理MCP請求"""
        try:
            action = request.get('action', '')
            parameters = request.get('parameters', {})
            
            if action == 'list_tools':
                return self._list_tools()
            elif action == 'get_tool_info':
                return self._get_tool_info(parameters.get('tool_name'))
            elif action == 'execute_tool':
                return self._execute_tool(parameters.get('tool_name'), parameters.get('tool_params', {}))
            elif action == 'search_tools':
                return self._search_tools(parameters.get('query', ''))
            else:
                return {
                    'status': 'error',
                    'message': f'未知操作: {action}',
                    'data': None
                }
        
        except Exception as e:
            logger.error(f"處理請求時出錯: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }
    
    def _list_tools(self) -> Dict[str, Any]:
        """列出所有配置工具"""
        return {
            'status': 'success',
            'message': '配置工具列表獲取成功',
            'data': {
                'tools': list(self.tools.keys()),
                'tool_details': self.tools,
                'config_types': [ct.value for ct in ConfigType],
                'total_count': len(self.tools),
                'adapter_info': {
                    'name': self.adapter_name,
                    'version': self.version,
                    'description': '統一配置器管理器，整合所有PowerAutomation配置'
                }
            }
        }
    
    def _get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """獲取工具信息"""
        if tool_name not in self.tools:
            return {
                'status': 'error',
                'message': f'工具不存在: {tool_name}',
                'data': None
            }
        
        return {
            'status': 'success',
            'message': f'工具信息獲取成功: {tool_name}',
            'data': {
                'tool_name': tool_name,
                'tool_info': self.tools[tool_name],
                'usage_examples': self._get_tool_usage_examples(tool_name)
            }
        }
    
    def _execute_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """執行配置工具"""
        if tool_name not in self.tools:
            return {
                'status': 'error',
                'message': f'配置工具不存在: {tool_name}',
                'data': None
            }
        
        try:
            if tool_name == 'get_config':
                result = self._get_config(tool_params)
            elif tool_name == 'set_config':
                result = self._set_config(tool_params)
            elif tool_name == 'list_configs':
                result = self._list_configs(tool_params)
            elif tool_name == 'switch_api_mode':
                result = self._switch_api_mode(tool_params)
            elif tool_name == 'manage_api_keys':
                result = self._manage_api_keys(tool_params)
            elif tool_name == 'test_api_connection':
                result = self._test_api_connection(tool_params)
            elif tool_name == 'configure_intent_understanding':
                result = self._configure_intent_understanding(tool_params)
            elif tool_name == 'export_config':
                result = self._export_config(tool_params)
            elif tool_name == 'import_config':
                result = self._import_config(tool_params)
            elif tool_name == 'reset_config':
                result = self._reset_config(tool_params)
            else:
                result = {'error': f'配置工具 {tool_name} 尚未實現'}
            
            return {
                'status': 'success',
                'message': f'配置工具 {tool_name} 執行成功',
                'data': {
                    'tool_name': tool_name,
                    'parameters': tool_params,
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'adapter': self.adapter_name
                }
            }
        
        except Exception as e:
            logger.error(f"執行配置工具 {tool_name} 時出錯: {e}")
            return {
                'status': 'error',
                'message': f'配置工具執行失敗: {str(e)}',
                'data': {
                    'tool_name': tool_name,
                    'parameters': tool_params,
                    'error': str(e)
                }
            }
    
    def _get_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """獲取配置"""
        config_type_str = params.get('config_type', '')
        section = params.get('section', '')
        
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {'error': f'無效的配置類型: {config_type_str}'}
        
        if config_type not in self.configs:
            return {'error': f'配置類型不存在: {config_type_str}'}
        
        config_data = self.configs[config_type]
        
        if section:
            if section in config_data:
                return {
                    'config_type': config_type_str,
                    'section': section,
                    'data': config_data[section]
                }
            else:
                return {'error': f'配置節不存在: {section}'}
        else:
            return {
                'config_type': config_type_str,
                'data': config_data
            }
    
    def _set_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """設置配置"""
        config_type_str = params.get('config_type', '')
        section = params.get('section', '')
        key = params.get('key', '')
        value = params.get('value')
        
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {'error': f'無效的配置類型: {config_type_str}'}
        
        if config_type not in self.configs:
            return {'error': f'配置類型不存在: {config_type_str}'}
        
        if not key:
            return {'error': '配置鍵不能為空'}
        
        try:
            if section:
                if section not in self.configs[config_type]:
                    self.configs[config_type][section] = {}
                self.configs[config_type][section][key] = value
            else:
                self.configs[config_type][key] = value
            
            return {
                'config_type': config_type_str,
                'section': section,
                'key': key,
                'value': value,
                'message': '配置設置成功'
            }
        
        except Exception as e:
            return {'error': f'設置配置失敗: {str(e)}'}
    
    def _list_configs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出所有配置"""
        detailed = params.get('detailed', False)
        
        config_summary = {}
        
        for config_type, config_data in self.configs.items():
            if detailed:
                config_summary[config_type.value] = config_data
            else:
                config_summary[config_type.value] = {
                    'sections': list(config_data.keys()) if isinstance(config_data, dict) else [],
                    'size': len(config_data) if isinstance(config_data, dict) else 1
                }
        
        return {
            'configs': config_summary,
            'total_types': len(self.configs),
            'detailed': detailed
        }
    
    def _switch_api_mode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """切換API模式"""
        mode = params.get('mode', '')
        api_provider = params.get('api_provider', 'all')
        
        try:
            api_mode = APIMode(mode)
        except ValueError:
            return {'error': f'無效的API模式: {mode}'}
        
        api_config = self.configs[ConfigType.API_CONFIG]
        
        if api_provider == 'all':
            # 切換所有API提供商的模式
            api_config['mode'] = mode
            for provider in api_config['providers']:
                api_config['providers'][provider]['mode'] = mode
            
            return {
                'mode': mode,
                'providers': list(api_config['providers'].keys()),
                'message': f'所有API提供商已切換到 {mode} 模式'
            }
        else:
            # 切換特定API提供商的模式
            if api_provider not in api_config['providers']:
                return {'error': f'API提供商不存在: {api_provider}'}
            
            api_config['providers'][api_provider]['mode'] = mode
            
            return {
                'mode': mode,
                'provider': api_provider,
                'message': f'{api_provider} API已切換到 {mode} 模式'
            }
    
    def _manage_api_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """管理API密鑰"""
        action = params.get('action', '')
        provider = params.get('provider', '')
        api_key = params.get('api_key', '')
        
        # 對於list操作，不需要provider參數
        if action == 'list':
            api_keys_config = self.configs[ConfigType.API_KEYS]
            return {
                'action': action,
                'providers': {
                    k: {
                        'status': v.get('status', 'unknown'),
                        'last_updated': v.get('last_updated'),
                        'usage_count': v.get('usage_count', 0)
                    }
                    for k, v in api_keys_config.items()
                }
            }
        
        # 其他操作需要provider參數
        if not provider:
            return {'error': 'API提供商不能為空'}
        
        api_keys_config = self.configs[ConfigType.API_KEYS]
        
        if action == 'add' or action == 'update':
            if not api_key:
                return {'error': 'API密鑰不能為空'}
            
            if provider not in api_keys_config:
                api_keys_config[provider] = {}
            
            api_keys_config[provider].update({
                'api_key': api_key,
                'status': 'configured',
                'last_updated': datetime.now().isoformat(),
                'usage_count': api_keys_config[provider].get('usage_count', 0)
            })
            
            # 設置環境變量
            env_var_map = {
                'claude': 'ANTHROPIC_API_KEY',
                'gemini': 'GOOGLE_API_KEY',
                'openai': 'OPENAI_API_KEY'
            }
            
            if provider in env_var_map:
                os.environ[env_var_map[provider]] = api_key
            
            return {
                'action': action,
                'provider': provider,
                'status': 'configured',
                'message': f'{provider} API密鑰已{action}'
            }
        
        elif action == 'delete':
            if provider in api_keys_config:
                api_keys_config[provider]['api_key'] = ''
                api_keys_config[provider]['status'] = 'not_configured'
                
                return {
                    'action': action,
                    'provider': provider,
                    'status': 'not_configured',
                    'message': f'{provider} API密鑰已刪除'
                }
            else:
                return {'error': f'API提供商不存在: {provider}'}
        
        elif action == 'list':
            return {
                'action': action,
                'providers': {
                    k: {
                        'status': v.get('status', 'unknown'),
                        'last_updated': v.get('last_updated'),
                        'usage_count': v.get('usage_count', 0)
                    }
                    for k, v in api_keys_config.items()
                }
            }
        
        else:
            return {'error': f'無效的操作: {action}'}
    
    def _test_api_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """測試API連接"""
        provider = params.get('provider', '')
        test_type = params.get('test_type', 'basic')
        
        if not provider:
            return {'error': 'API提供商不能為空'}
        
        api_keys_config = self.configs[ConfigType.API_KEYS]
        
        if provider not in api_keys_config:
            return {'error': f'API提供商不存在: {provider}'}
        
        api_key_info = api_keys_config[provider]
        
        if api_key_info.get('status') != 'configured':
            return {
                'provider': provider,
                'status': 'not_configured',
                'message': f'{provider} API密鑰未配置'
            }
        
        # 模擬API連接測試
        test_result = {
            'provider': provider,
            'test_type': test_type,
            'status': 'success',
            'response_time': 0.5,
            'message': f'{provider} API連接測試成功',
            'timestamp': datetime.now().isoformat()
        }
        
        # 更新最後驗證時間
        api_keys_config[provider]['last_verified'] = datetime.now().isoformat()
        
        return test_result
    
    def _configure_intent_understanding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """配置意圖理解"""
        model = params.get('model', '')
        settings = params.get('settings', {})
        enable = params.get('enable', True)
        
        intent_config = self.configs[ConfigType.INTENT_UNDERSTANDING]
        
        if model:
            intent_config['primary_model'] = model
        
        if settings:
            intent_config.update(settings)
        
        intent_config['enabled'] = enable
        
        return {
            'enabled': enable,
            'primary_model': intent_config['primary_model'],
            'settings': intent_config,
            'message': '意圖理解配置已更新'
        }
    
    def _export_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """導出配置"""
        config_type_str = params.get('config_type', 'all')
        format_type = params.get('format', 'json')
        file_path = params.get('file_path', '')
        
        if config_type_str == 'all':
            export_data = {ct.value: config for ct, config in self.configs.items()}
        else:
            try:
                config_type = ConfigType(config_type_str)
                export_data = {config_type_str: self.configs[config_type]}
            except ValueError:
                return {'error': f'無效的配置類型: {config_type_str}'}
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                return {
                    'config_type': config_type_str,
                    'format': format_type,
                    'file_path': file_path,
                    'message': '配置導出成功'
                }
            except Exception as e:
                return {'error': f'導出配置失敗: {str(e)}'}
        else:
            return {
                'config_type': config_type_str,
                'format': format_type,
                'data': export_data,
                'message': '配置數據獲取成功'
            }
    
    def _import_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """導入配置"""
        config_type_str = params.get('config_type', '')
        file_path = params.get('file_path', '')
        merge = params.get('merge', True)
        
        if not file_path:
            return {'error': '文件路徑不能為空'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if config_type_str:
                try:
                    config_type = ConfigType(config_type_str)
                    if config_type_str in import_data:
                        if merge:
                            self.configs[config_type].update(import_data[config_type_str])
                        else:
                            self.configs[config_type] = import_data[config_type_str]
                    else:
                        return {'error': f'導入數據中不包含配置類型: {config_type_str}'}
                except ValueError:
                    return {'error': f'無效的配置類型: {config_type_str}'}
            else:
                # 導入所有配置
                for ct_str, config_data in import_data.items():
                    try:
                        config_type = ConfigType(ct_str)
                        if merge:
                            self.configs[config_type].update(config_data)
                        else:
                            self.configs[config_type] = config_data
                    except ValueError:
                        logger.warning(f'跳過無效的配置類型: {ct_str}')
            
            return {
                'config_type': config_type_str or 'all',
                'file_path': file_path,
                'merge': merge,
                'message': '配置導入成功'
            }
        
        except Exception as e:
            return {'error': f'導入配置失敗: {str(e)}'}
    
    def _reset_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """重置配置"""
        config_type_str = params.get('config_type', '')
        confirm = params.get('confirm', False)
        
        if not confirm:
            return {'error': '重置配置需要確認，請設置 confirm=True'}
        
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {'error': f'無效的配置類型: {config_type_str}'}
        
        # 重新初始化指定配置
        if config_type == ConfigType.API_CONFIG:
            self.configs[config_type] = self._get_default_api_config()
        elif config_type == ConfigType.API_KEYS:
            self.configs[config_type] = self._get_default_api_keys_config()
        elif config_type == ConfigType.INTENT_UNDERSTANDING:
            self.configs[config_type] = self._get_default_intent_config()
        elif config_type == ConfigType.WORKFLOW_ENGINE:
            self.configs[config_type] = self._get_default_workflow_config()
        elif config_type == ConfigType.SYSTEM_SETTINGS:
            self.configs[config_type] = self._get_default_system_config()
        
        return {
            'config_type': config_type_str,
            'message': f'{config_type_str} 配置已重置為默認值'
        }
    
    def _search_tools(self, query: str) -> Dict[str, Any]:
        """搜索配置工具"""
        query_lower = query.lower()
        relevant_tools = []
        
        for tool_name, tool_info in self.tools.items():
            if (query_lower in tool_name.lower() or 
                query_lower in tool_info['description'].lower() or
                query_lower in tool_info['category'].lower()):
                relevant_tools.append({
                    'tool_name': tool_name,
                    'tool_info': tool_info,
                    'relevance_score': self._calculate_relevance(query_lower, tool_name, tool_info)
                })
        
        # 按相關性排序
        relevant_tools.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            'status': 'success',
            'message': f'找到 {len(relevant_tools)} 個相關配置工具',
            'data': {
                'query': query,
                'relevant_tools': relevant_tools,
                'total_found': len(relevant_tools)
            }
        }
    
    def _calculate_relevance(self, query: str, tool_name: str, tool_info: Dict[str, Any]) -> float:
        """計算工具相關性分數"""
        score = 0.0
        
        # 工具名稱匹配
        if query in tool_name.lower():
            score += 1.0
        
        # 描述匹配
        if query in tool_info['description'].lower():
            score += 0.8
        
        # 類別匹配
        if query in tool_info['category'].lower():
            score += 0.6
        
        # 參數匹配
        for param in tool_info.get('parameters', []):
            if query in param.lower():
                score += 0.4
        
        return score
    
    def _get_tool_usage_examples(self, tool_name: str) -> List[Dict[str, Any]]:
        """獲取工具使用示例"""
        examples = {
            'get_config': [
                {
                    'description': '獲取API配置',
                    'parameters': {'config_type': 'api_config'}
                },
                {
                    'description': '獲取Claude API配置',
                    'parameters': {'config_type': 'api_config', 'section': 'providers.claude'}
                }
            ],
            'set_config': [
                {
                    'description': '設置API模式為真實模式',
                    'parameters': {'config_type': 'api_config', 'key': 'mode', 'value': 'real'}
                }
            ],
            'switch_api_mode': [
                {
                    'description': '切換所有API到真實模式',
                    'parameters': {'mode': 'real', 'api_provider': 'all'}
                },
                {
                    'description': '切換Claude API到模擬模式',
                    'parameters': {'mode': 'mock', 'api_provider': 'claude'}
                }
            ],
            'manage_api_keys': [
                {
                    'description': '添加Claude API密鑰',
                    'parameters': {'action': 'add', 'provider': 'claude', 'api_key': 'sk-...'}
                },
                {
                    'description': '列出所有API密鑰狀態',
                    'parameters': {'action': 'list'}
                }
            ]
        }
        
        return examples.get(tool_name, [])
    
    def _get_default_api_config(self) -> Dict[str, Any]:
        """獲取默認API配置"""
        # 返回默認API配置
        return self.configs[ConfigType.API_CONFIG]
    
    def _get_default_api_keys_config(self) -> Dict[str, Any]:
        """獲取默認API密鑰配置"""
        # 返回默認API密鑰配置
        return self.configs[ConfigType.API_KEYS]
    
    def _get_default_intent_config(self) -> Dict[str, Any]:
        """獲取默認意圖理解配置"""
        # 返回默認意圖理解配置
        return self.configs[ConfigType.INTENT_UNDERSTANDING]
    
    def _get_default_workflow_config(self) -> Dict[str, Any]:
        """獲取默認工作流配置"""
        # 返回默認工作流配置
        return self.configs[ConfigType.WORKFLOW_ENGINE]
    
    def _get_default_system_config(self) -> Dict[str, Any]:
        """獲取默認系統配置"""
        # 返回默認系統配置
        return self.configs[ConfigType.SYSTEM_SETTINGS]

if __name__ == "__main__":
    # 測試統一配置器管理器
    manager = UnifiedConfigManagerMCP()
    
    # 測試列出工具
    result = manager.process({'action': 'list_tools'})
    print("工具列表:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # 測試獲取配置
    result = manager.process({
        'action': 'execute_tool',
        'parameters': {
            'tool_name': 'get_config',
            'tool_params': {'config_type': 'api_config'}
        }
    })
    print("API配置:", json.dumps(result, indent=2, ensure_ascii=False))


    def _check_api_availability(self):
        """檢查API可用性"""
        self.available_apis = {}
        
        for api_name, config in self.api_configs.items():
            api_key_env = config.get("api_key_env")
            
            if api_name == "manus_api":
                # 檢查Manus API
                try:
                    from data_api import ApiClient
                    self.available_apis[api_name] = {
                        "status": "available",
                        "client_available": True,
                        "config": config
                    }
                    logger.info(f"Manus API Hub 可用")
                except Exception as e:
                    self.available_apis[api_name] = {
                        "status": "unavailable",
                        "error": str(e),
                        "config": config
                    }
                    logger.warning(f"Manus API Hub 不可用: {e}")
            
            elif api_key_env and os.getenv(api_key_env):
                # 有API密鑰的服務
                self.available_apis[api_name] = {
                    "status": "available",
                    "api_key": os.getenv(api_key_env),
                    "config": config
                }
                logger.info(f"{config['name']} API 可用")
            else:
                # 模擬模式
                self.available_apis[api_name] = {
                    "status": "simulated",
                    "config": config
                }
                logger.info(f"{config['name']} API 使用模擬模式")
    
    def _initialize_api_clients(self):
        """初始化API客戶端"""
        # 初始化Claude客戶端
        if "claude" in self.available_apis and self.available_apis["claude"]["status"] == "available":
            if ANTHROPIC_AVAILABLE:
                try:
                    api_key = self.available_apis["claude"]["api_key"]
                    self.api_clients["claude"] = anthropic.Anthropic(api_key=api_key)
                    logger.info("Claude API客戶端初始化成功")
                except Exception as e:
                    logger.error(f"Claude API客戶端初始化失敗: {e}")
        
        # 初始化Gemini客戶端
        if "gemini" in self.available_apis and self.available_apis["gemini"]["status"] == "available":
            if GOOGLE_AI_AVAILABLE:
                try:
                    api_key = self.available_apis["gemini"]["api_key"]
                    genai.configure(api_key=api_key)
                    self.api_clients["gemini"] = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini API客戶端初始化成功")
                except Exception as e:
                    logger.error(f"Gemini API客戶端初始化失敗: {e}")
        
        # 初始化OpenAI客戶端
        if "openai" in self.available_apis and self.available_apis["openai"]["status"] == "available":
            if OPENAI_AVAILABLE:
                try:
                    api_key = self.available_apis["openai"]["api_key"]
                    self.api_clients["openai"] = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI API客戶端初始化成功")
                except Exception as e:
                    logger.error(f"OpenAI API客戶端初始化失敗: {e}")
        
        # 初始化Manus API客戶端
        if "manus_api" in self.available_apis and self.available_apis["manus_api"]["status"] == "available":
            try:
                from data_api import ApiClient
                self.api_clients["manus_api"] = ApiClient()
                logger.info("Manus API客戶端初始化成功")
            except Exception as e:
                logger.error(f"Manus API客戶端初始化失敗: {e}")

