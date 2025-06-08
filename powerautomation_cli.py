#!/usr/bin/env python3
"""
PowerAutomation v0.3 統一CLI接口

整合所有MCP組件的統一命令行接口，提供：
- 智能命令路由
- 交互式和批處理模式
- 實時狀態管理
- 完整的MCP生態系統控制

作者: PowerAutomation團隊
版本: 0.3.0
日期: 2025-06-08
"""

import os
import sys
import json
import argparse
import asyncio
import logging
import readline
import cmd
import shlex
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import signal
import threading
import time

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入所有MCP組件
try:
    from mcptool.adapters.cloud_edge_data_mcp import CloudEdgeDataMCP
    from mcptool.adapters.rl_srt_dataflow_mcp import RLSRTDataFlowMCP
    from mcptool.adapters.unified_memory_mcp import UnifiedMemoryMCP
    from mcptool.adapters.context_monitor_mcp import ContextMonitorMCP
    from mcptool.adapters.smart_routing_mcp import SmartRoutingMCP
    from mcptool.adapters.dev_deploy_loop_coordinator_mcp import DevDeployLoopCoordinatorMCP
    from mcptool.adapters.mcp_registry_integration_manager import MCPRegistryIntegrationManager
except ImportError as e:
    logging.warning(f"導入MCP組件失敗: {e}")
    # 創建Mock類
    class MockMCP:
        def __init__(self, name):
            self.name = name
        def process(self, data):
            return {"status": "mock", "message": f"Mock {self.name}"}
    
    CloudEdgeDataMCP = lambda: MockMCP("CloudEdgeDataMCP")
    RLSRTDataFlowMCP = lambda: MockMCP("RLSRTDataFlowMCP")
    UnifiedMemoryMCP = lambda: MockMCP("UnifiedMemoryMCP")
    ContextMonitorMCP = lambda: MockMCP("ContextMonitorMCP")
    SmartRoutingMCP = lambda: MockMCP("SmartRoutingMCP")
    DevDeployLoopCoordinatorMCP = lambda: MockMCP("DevDeployLoopCoordinatorMCP")
    MCPRegistryIntegrationManager = lambda: MockMCP("MCPRegistryIntegrationManager")

# 導入標準化日誌系統
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    class LogCategory:
        SYSTEM = "system"
        CLI = "cli"

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("powerautomation_cli")

class PowerAutomationCLI(cmd.Cmd):
    """PowerAutomation v0.3 統一CLI接口"""
    
    intro = '''
🚀 PowerAutomation v0.3 統一控制系統
=====================================
✨ 端雲協同 | 智慧路由 | 開發閉環 | 記憶管理
輸入 'help' 查看可用命令
輸入 'status' 查看系統狀態
輸入 'quit' 或 'exit' 退出系統
'''
    prompt = '(PowerAutomation) > '
    
    def __init__(self):
        super().__init__()
        
        # 初始化MCP組件
        self.mcps = {}
        self.current_mcp = None
        self.auto_route = True
        self.batch_mode = False
        
        # 命令歷史
        self.command_history = []
        self.max_history = 100
        
        # 狀態監控
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 初始化系統
        self._initialize_mcps()
        self._setup_signal_handlers()
        
        log_info(LogCategory.CLI, "PowerAutomation CLI初始化完成", {
            "mcps_loaded": len(self.mcps),
            "auto_route": self.auto_route
        })
    
    def _initialize_mcps(self):
        """初始化所有MCP組件"""
        try:
            # 初始化MCP組件
            mcp_configs = {
                "cloud_edge_data": CloudEdgeDataMCP,
                "rl_srt_dataflow": RLSRTDataFlowMCP,
                "unified_memory": UnifiedMemoryMCP,
                "context_monitor": ContextMonitorMCP,
                "smart_routing": SmartRoutingMCP,
                "dev_deploy_loop": DevDeployLoopCoordinatorMCP,
                "registry_manager": MCPRegistryIntegrationManager
            }
            
            for mcp_name, mcp_class in mcp_configs.items():
                try:
                    self.mcps[mcp_name] = mcp_class()
                    log_info(LogCategory.CLI, f"MCP組件初始化成功: {mcp_name}", {})
                except Exception as e:
                    log_error(LogCategory.CLI, f"MCP組件初始化失敗: {mcp_name}", {"error": str(e)})
                    self.mcps[mcp_name] = None
            
            # 設置智慧路由為默認路由器
            if "smart_routing" in self.mcps and self.mcps["smart_routing"]:
                self.current_mcp = "smart_routing"
            
        except Exception as e:
            log_error(LogCategory.CLI, "MCP組件初始化失敗", {"error": str(e)})
    
    def _setup_signal_handlers(self):
        """設置信號處理器"""
        def signal_handler(signum, frame):
            print("\n\n🛑 接收到中斷信號，正在安全退出...")
            self._cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _cleanup(self):
        """清理資源"""
        try:
            # 停止監控
            if self.monitoring_active:
                self.monitoring_active = False
                if self.monitor_thread:
                    self.monitor_thread.join(timeout=2)
            
            log_info(LogCategory.CLI, "CLI資源清理完成", {})
        except Exception as e:
            log_error(LogCategory.CLI, "CLI資源清理失敗", {"error": str(e)})
    
    def _record_command(self, command: str):
        """記錄命令歷史"""
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "current_mcp": self.current_mcp
        })
        
        # 保持歷史記錄在合理範圍內
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def _route_command(self, command: str, args: List[str]) -> str:
        """智能路由命令到最適合的MCP"""
        if not self.auto_route or not self.mcps.get("smart_routing"):
            return self.current_mcp or "registry_manager"
        
        try:
            # 使用智慧路由MCP進行命令路由
            routing_result = self.mcps["smart_routing"].process({
                "operation": "route_request",
                "params": {
                    "user_intent": f"{command} {' '.join(args)}",
                    "operation": command,
                    "params": {"args": args}
                }
            })
            
            if routing_result.get("status") == "success":
                selected_mcp = routing_result.get("selected_mcp", "")
                if selected_mcp in self.mcps:
                    return selected_mcp
            
        except Exception as e:
            log_warning(LogCategory.CLI, f"智能路由失敗: {str(e)}", {})
        
        # 備用路由邏輯
        command_mcp_map = {
            "memory": "unified_memory",
            "query": "unified_memory",
            "search": "unified_memory",
            "monitor": "context_monitor",
            "context": "context_monitor",
            "alert": "context_monitor",
            "deploy": "dev_deploy_loop",
            "develop": "dev_deploy_loop",
            "loop": "dev_deploy_loop",
            "route": "smart_routing",
            "balance": "smart_routing",
            "data": "cloud_edge_data",
            "sync": "cloud_edge_data",
            "train": "rl_srt_dataflow",
            "model": "rl_srt_dataflow",
            "registry": "registry_manager",
            "register": "registry_manager"
        }
        
        for keyword, mcp_name in command_mcp_map.items():
            if keyword in command.lower():
                return mcp_name
        
        return self.current_mcp or "registry_manager"
    
    def _execute_mcp_command(self, mcp_name: str, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行MCP命令"""
        try:
            if mcp_name not in self.mcps or not self.mcps[mcp_name]:
                return {
                    "status": "error",
                    "message": f"MCP組件不可用: {mcp_name}"
                }
            
            mcp = self.mcps[mcp_name]
            
            # 構建輸入數據
            input_data = {
                "operation": operation,
                "params": params
            }
            
            # 執行MCP操作
            result = mcp.process(input_data)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"MCP命令執行失敗: {str(e)}"
            }
    
    def _format_result(self, result: Dict[str, Any], compact: bool = False) -> str:
        """格式化結果輸出"""
        try:
            if compact:
                status = result.get("status", "unknown")
                message = result.get("message", "")
                return f"[{status.upper()}] {message}"
            else:
                return json.dumps(result, indent=2, ensure_ascii=False)
        except:
            return str(result)
    
    # ==================== 基礎命令 ====================
    
    def do_status(self, args):
        """顯示系統狀態
        用法: status [mcp_name]
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if args_list:
                # 顯示特定MCP狀態
                mcp_name = args_list[0]
                if mcp_name in self.mcps:
                    if self.mcps[mcp_name]:
                        result = self._execute_mcp_command(mcp_name, "get_status", {})
                        print(f"\n📊 {mcp_name.upper()} 狀態:")
                        print(self._format_result(result))
                    else:
                        print(f"❌ MCP組件未初始化: {mcp_name}")
                else:
                    print(f"❌ 未知的MCP組件: {mcp_name}")
            else:
                # 顯示整體系統狀態
                print(f"\n🚀 PowerAutomation v0.3 系統狀態")
                print(f"{'='*50}")
                print(f"當前MCP: {self.current_mcp or 'None'}")
                print(f"自動路由: {'✅' if self.auto_route else '❌'}")
                print(f"批處理模式: {'✅' if self.batch_mode else '❌'}")
                print(f"監控狀態: {'🟢 運行中' if self.monitoring_active else '🔴 已停止'}")
                print(f"\n📦 MCP組件狀態:")
                
                for mcp_name, mcp_instance in self.mcps.items():
                    status_icon = "🟢" if mcp_instance else "🔴"
                    print(f"  {status_icon} {mcp_name}")
                
                print(f"\n📈 命令歷史: {len(self.command_history)} 條記錄")
                
        except Exception as e:
            print(f"❌ 獲取狀態失敗: {str(e)}")
    
    def do_switch(self, args):
        """切換當前MCP組件
        用法: switch <mcp_name>
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定要切換的MCP組件名稱")
                print("可用組件:", ", ".join(self.mcps.keys()))
                return
            
            mcp_name = args_list[0]
            
            if mcp_name in self.mcps:
                if self.mcps[mcp_name]:
                    old_mcp = self.current_mcp
                    self.current_mcp = mcp_name
                    print(f"✅ 已切換到MCP組件: {mcp_name}")
                    if old_mcp:
                        print(f"   (從 {old_mcp} 切換)")
                else:
                    print(f"❌ MCP組件未初始化: {mcp_name}")
            else:
                print(f"❌ 未知的MCP組件: {mcp_name}")
                print("可用組件:", ", ".join(self.mcps.keys()))
                
        except Exception as e:
            print(f"❌ 切換MCP失敗: {str(e)}")
    
    def do_list(self, args):
        """列出可用的MCP組件和操作
        用法: list [mcps|operations|history]
        """
        try:
            args_list = shlex.split(args) if args else ["mcps"]
            list_type = args_list[0] if args_list else "mcps"
            
            if list_type == "mcps":
                print(f"\n📦 可用MCP組件:")
                print(f"{'='*50}")
                for mcp_name, mcp_instance in self.mcps.items():
                    status = "🟢 可用" if mcp_instance else "🔴 不可用"
                    current = " (當前)" if mcp_name == self.current_mcp else ""
                    print(f"  {mcp_name}: {status}{current}")
            
            elif list_type == "operations":
                if self.current_mcp and self.mcps.get(self.current_mcp):
                    print(f"\n⚙️ {self.current_mcp} 可用操作:")
                    print(f"{'='*50}")
                    
                    # 嘗試獲取操作列表
                    result = self._execute_mcp_command(self.current_mcp, "list_operations", {})
                    if result.get("status") == "success":
                        operations = result.get("operations", [])
                        for op in operations:
                            print(f"  • {op}")
                    else:
                        print("  無法獲取操作列表")
                else:
                    print("❌ 沒有選擇當前MCP組件")
            
            elif list_type == "history":
                print(f"\n📈 命令歷史 (最近10條):")
                print(f"{'='*50}")
                recent_history = self.command_history[-10:]
                for i, entry in enumerate(recent_history, 1):
                    timestamp = entry["timestamp"][:19]  # 只顯示到秒
                    command = entry["command"]
                    mcp = entry.get("current_mcp", "N/A")
                    print(f"  {i:2d}. [{timestamp}] {command} (MCP: {mcp})")
            
            else:
                print("❌ 無效的列表類型，可用選項: mcps, operations, history")
                
        except Exception as e:
            print(f"❌ 列出信息失敗: {str(e)}")
    
    def do_config(self, args):
        """配置CLI設置
        用法: config <setting> <value>
        設置: auto_route, batch_mode, max_history
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if len(args_list) == 0:
                # 顯示當前配置
                print(f"\n⚙️ 當前配置:")
                print(f"{'='*30}")
                print(f"auto_route: {self.auto_route}")
                print(f"batch_mode: {self.batch_mode}")
                print(f"max_history: {self.max_history}")
                print(f"monitoring_active: {self.monitoring_active}")
                return
            
            if len(args_list) != 2:
                print("❌ 用法: config <setting> <value>")
                return
            
            setting, value = args_list
            
            if setting == "auto_route":
                self.auto_route = value.lower() in ["true", "1", "yes", "on"]
                print(f"✅ auto_route 設置為: {self.auto_route}")
            
            elif setting == "batch_mode":
                self.batch_mode = value.lower() in ["true", "1", "yes", "on"]
                print(f"✅ batch_mode 設置為: {self.batch_mode}")
            
            elif setting == "max_history":
                try:
                    self.max_history = int(value)
                    print(f"✅ max_history 設置為: {self.max_history}")
                except ValueError:
                    print("❌ max_history 必須是數字")
            
            else:
                print(f"❌ 未知設置: {setting}")
                print("可用設置: auto_route, batch_mode, max_history")
                
        except Exception as e:
            print(f"❌ 配置設置失敗: {str(e)}")
    
    # ==================== MCP專用命令 ====================
    
    def do_memory(self, args):
        """記憶系統操作
        用法: memory <operation> [args...]
        操作: query, insert, update, delete, backup, sync
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定記憶操作")
                print("可用操作: query, insert, update, delete, backup, sync")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "query":
                if len(args_list) < 2:
                    print("❌ 用法: memory query <search_term> [source]")
                    return
                params = {
                    "search_term": args_list[1],
                    "source": args_list[2] if len(args_list) > 2 else "all"
                }
            
            elif operation == "insert":
                if len(args_list) < 3:
                    print("❌ 用法: memory insert <key> <content> [source]")
                    return
                params = {
                    "key": args_list[1],
                    "content": args_list[2],
                    "source": args_list[3] if len(args_list) > 3 else "local"
                }
            
            elif operation in ["backup", "sync"]:
                params = {"target": args_list[1] if len(args_list) > 1 else "all"}
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到統一記憶MCP
            mcp_name = "unified_memory"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n🧠 記憶系統 - {operation.upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 記憶操作失敗: {str(e)}")
    
    def do_deploy(self, args):
        """開發部署閉環操作
        用法: deploy <operation> [args...]
        操作: start, status, pause, resume, cancel
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定部署操作")
                print("可用操作: start, status, pause, resume, cancel")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "start":
                if len(args_list) < 3:
                    print("❌ 用法: deploy start <requirement> <project_name> [language] [target]")
                    return
                params = {
                    "user_requirement": args_list[1],
                    "project_name": args_list[2],
                    "target_language": args_list[3] if len(args_list) > 3 else "python",
                    "deployment_target": args_list[4] if len(args_list) > 4 else "development"
                }
                operation = "start_dev_loop"
            
            elif operation == "status":
                if len(args_list) > 1:
                    params = {"execution_id": args_list[1]}
                    operation = "get_loop_status"
                else:
                    operation = "get_active_loops"
            
            elif operation in ["pause", "resume", "cancel"]:
                if len(args_list) < 2:
                    print(f"❌ 用法: deploy {operation} <execution_id>")
                    return
                params = {"execution_id": args_list[1]}
                operation = f"{operation}_loop"
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到開發部署閉環協調器MCP
            mcp_name = "dev_deploy_loop"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n🚀 開發部署閉環 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 部署操作失敗: {str(e)}")
    
    def do_route(self, args):
        """智慧路由操作
        用法: route <operation> [args...]
        操作: request, stats, nodes, strategy
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定路由操作")
                print("可用操作: request, stats, nodes, strategy")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "request":
                if len(args_list) < 3:
                    print("❌ 用法: route request <intent> <operation> [strategy]")
                    return
                params = {
                    "user_intent": args_list[1],
                    "operation": args_list[2],
                    "strategy": args_list[3] if len(args_list) > 3 else None
                }
                operation = "route_request"
            
            elif operation == "stats":
                operation = "get_routing_stats"
            
            elif operation == "nodes":
                params = {"status_filter": args_list[1] if len(args_list) > 1 else None}
                operation = "get_mcp_nodes"
            
            elif operation == "strategy":
                if len(args_list) > 1:
                    params = {"strategy": args_list[1]}
                    operation = "set_routing_strategy"
                else:
                    print("❌ 用法: route strategy <strategy_name>")
                    return
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到智慧路由MCP
            mcp_name = "smart_routing"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n🎯 智慧路由 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 路由操作失敗: {str(e)}")
    
    def do_monitor(self, args):
        """上下文監控操作
        用法: monitor <operation> [args...]
        操作: start, stop, status, alert, threshold
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定監控操作")
                print("可用操作: start, stop, status, alert, threshold")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "start":
                operation = "start_monitoring"
            
            elif operation == "stop":
                operation = "stop_monitoring"
            
            elif operation == "status":
                operation = "get_monitoring_status"
            
            elif operation == "alert":
                operation = "get_alerts"
            
            elif operation == "threshold":
                if len(args_list) > 1:
                    try:
                        threshold = float(args_list[1])
                        params = {"threshold": threshold}
                        operation = "set_threshold"
                    except ValueError:
                        print("❌ 閾值必須是數字")
                        return
                else:
                    print("❌ 用法: monitor threshold <value>")
                    return
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到上下文監控MCP
            mcp_name = "context_monitor"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n📊 上下文監控 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 監控操作失敗: {str(e)}")
    
    def do_data(self, args):
        """端雲協同數據操作
        用法: data <operation> [args...]
        操作: sync, upload, download, status, stats
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定數據操作")
                print("可用操作: sync, upload, download, status, stats")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "sync":
                params = {"direction": args_list[1] if len(args_list) > 1 else "bidirectional"}
                operation = "sync_data"
            
            elif operation == "upload":
                if len(args_list) < 2:
                    print("❌ 用法: data upload <file_path>")
                    return
                params = {"file_path": args_list[1]}
                operation = "upload_data"
            
            elif operation == "download":
                if len(args_list) < 2:
                    print("❌ 用法: data download <remote_path>")
                    return
                params = {"remote_path": args_list[1]}
                operation = "download_data"
            
            elif operation == "status":
                operation = "get_sync_status"
            
            elif operation == "stats":
                operation = "get_data_stats"
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到端雲協同數據MCP
            mcp_name = "cloud_edge_data"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n☁️ 端雲協同數據 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 數據操作失敗: {str(e)}")
    
    def do_train(self, args):
        """RL-SRT訓練操作
        用法: train <operation> [args...]
        操作: start, stop, status, evaluate, deploy
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定訓練操作")
                print("可用操作: start, stop, status, evaluate, deploy")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "start":
                params = {
                    "mode": args_list[1] if len(args_list) > 1 else "async",
                    "data_source": args_list[2] if len(args_list) > 2 else "default"
                }
                operation = "start_training"
            
            elif operation == "stop":
                operation = "stop_training"
            
            elif operation == "status":
                operation = "get_training_status"
            
            elif operation == "evaluate":
                params = {"model_id": args_list[1] if len(args_list) > 1 else "latest"}
                operation = "evaluate_model"
            
            elif operation == "deploy":
                params = {"model_id": args_list[1] if len(args_list) > 1 else "latest"}
                operation = "deploy_model"
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到RL-SRT數據流MCP
            mcp_name = "rl_srt_dataflow"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n🤖 RL-SRT訓練 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 訓練操作失敗: {str(e)}")
    
    def do_registry(self, args):
        """MCP註冊表操作
        用法: registry <operation> [args...]
        操作: list, register, match, stats, refresh
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定註冊表操作")
                print("可用操作: list, register, match, stats, refresh")
                return
            
            operation = args_list[0]
            params = {}
            
            if operation == "list":
                params = {
                    "category": args_list[1] if len(args_list) > 1 else None,
                    "status": args_list[2] if len(args_list) > 2 else None
                }
                operation = "list_registered_mcps"
            
            elif operation == "register":
                if len(args_list) < 2:
                    print("❌ 用法: registry register <mcp_info_json>")
                    return
                try:
                    mcp_info = json.loads(args_list[1])
                    params = {"mcp_info": mcp_info}
                    operation = "register_mcp"
                except json.JSONDecodeError:
                    print("❌ MCP信息必須是有效的JSON格式")
                    return
            
            elif operation == "match":
                if len(args_list) < 2:
                    print("❌ 用法: registry match <user_intent>")
                    return
                params = {"user_intent": args_list[1]}
                operation = "match_intent"
            
            elif operation == "stats":
                operation = "get_performance_stats"
            
            elif operation == "refresh":
                operation = "refresh_registry"
            
            else:
                params = {"args": args_list[1:]}
            
            # 路由到MCP註冊表管理器
            mcp_name = "registry_manager"
            result = self._execute_mcp_command(mcp_name, operation, params)
            
            print(f"\n📋 MCP註冊表 - {args_list[0].upper()}:")
            print(self._format_result(result, compact=self.batch_mode))
            
        except Exception as e:
            print(f"❌ 註冊表操作失敗: {str(e)}")
    
    # ==================== 高級功能 ====================
    
    def do_batch(self, args):
        """批處理模式
        用法: batch <file_path>
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定批處理文件路徑")
                return
            
            file_path = args_list[0]
            
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                return
            
            print(f"🔄 開始執行批處理文件: {file_path}")
            
            # 保存當前模式
            original_batch_mode = self.batch_mode
            self.batch_mode = True
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands = f.readlines()
                
                for i, command in enumerate(commands, 1):
                    command = command.strip()
                    if not command or command.startswith('#'):
                        continue
                    
                    print(f"\n[{i}] 執行: {command}")
                    self.onecmd(command)
                
                print(f"\n✅ 批處理完成，共執行 {len([c for c in commands if c.strip() and not c.strip().startswith('#')])} 條命令")
                
            finally:
                # 恢復原始模式
                self.batch_mode = original_batch_mode
                
        except Exception as e:
            print(f"❌ 批處理執行失敗: {str(e)}")
    
    def do_export(self, args):
        """導出系統數據
        用法: export <type> [output_path]
        類型: config, history, stats, all
        """
        try:
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定導出類型")
                print("可用類型: config, history, stats, all")
                return
            
            export_type = args_list[0]
            output_path = args_list[1] if len(args_list) > 1 else f"powerautomation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "export_type": export_type,
                "cli_version": "0.3.0"
            }
            
            if export_type in ["config", "all"]:
                export_data["config"] = {
                    "current_mcp": self.current_mcp,
                    "auto_route": self.auto_route,
                    "batch_mode": self.batch_mode,
                    "max_history": self.max_history,
                    "monitoring_active": self.monitoring_active
                }
            
            if export_type in ["history", "all"]:
                export_data["command_history"] = self.command_history
            
            if export_type in ["stats", "all"]:
                stats_data = {}
                for mcp_name, mcp_instance in self.mcps.items():
                    if mcp_instance:
                        try:
                            result = self._execute_mcp_command(mcp_name, "get_stats", {})
                            if result.get("status") == "success":
                                stats_data[mcp_name] = result
                        except:
                            pass
                export_data["mcp_stats"] = stats_data
            
            # 保存導出數據
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 數據已導出到: {output_path}")
            print(f"📊 導出類型: {export_type}")
            print(f"📁 文件大小: {os.path.getsize(output_path)} 字節")
            
        except Exception as e:
            print(f"❌ 導出失敗: {str(e)}")
    
    def do_watch(self, args):
        """實時監控系統狀態
        用法: watch [interval]
        """
        try:
            args_list = shlex.split(args) if args else []
            interval = int(args_list[0]) if args_list else 5
            
            if self.monitoring_active:
                print("❌ 監控已在運行中，使用 'unwatch' 停止")
                return
            
            print(f"🔍 開始實時監控 (間隔: {interval}秒)")
            print("按 Ctrl+C 停止監控")
            
            self.monitoring_active = True
            
            def monitor_loop():
                try:
                    while self.monitoring_active:
                        # 清屏
                        os.system('clear' if os.name == 'posix' else 'cls')
                        
                        # 顯示時間戳
                        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("="*60)
                        
                        # 顯示系統狀態
                        self.do_status("")
                        
                        # 等待間隔
                        time.sleep(interval)
                        
                except KeyboardInterrupt:
                    pass
                finally:
                    self.monitoring_active = False
            
            # 在新線程中運行監控
            self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            self.monitor_thread.start()
            
        except Exception as e:
            print(f"❌ 啟動監控失敗: {str(e)}")
            self.monitoring_active = False
    
    def do_unwatch(self, args):
        """停止實時監控
        用法: unwatch
        """
        if self.monitoring_active:
            self.monitoring_active = False
            print("✅ 實時監控已停止")
        else:
            print("❌ 監控未在運行")
    
    # ==================== 系統命令 ====================
    
    def do_help(self, args):
        """顯示幫助信息"""
        if args:
            # 顯示特定命令的幫助
            super().do_help(args)
        else:
            # 顯示總體幫助
            print(f"""
🚀 PowerAutomation v0.3 統一CLI幫助
=====================================

📋 基礎命令:
  status [mcp_name]     - 顯示系統或特定MCP狀態
  switch <mcp_name>     - 切換當前MCP組件
  list [type]           - 列出MCP組件/操作/歷史
  config [setting] [value] - 配置CLI設置

🧠 記憶系統:
  memory query <term>   - 查詢記憶內容
  memory insert <key> <content> - 插入記憶
  memory backup         - 備份記憶數據

🚀 開發部署:
  deploy start <req> <name> - 啟動開發閉環
  deploy status [id]    - 查看部署狀態
  deploy pause <id>     - 暫停部署

🎯 智慧路由:
  route request <intent> <op> - 路由請求
  route stats           - 查看路由統計
  route strategy <name> - 設置路由策略

📊 監控系統:
  monitor start         - 啟動監控
  monitor status        - 查看監控狀態
  monitor threshold <val> - 設置閾值

☁️ 數據同步:
  data sync             - 同步端雲數據
  data upload <file>    - 上傳文件
  data status           - 查看同步狀態

🤖 模型訓練:
  train start [mode]    - 開始訓練
  train status          - 查看訓練狀態
  train evaluate        - 評估模型

📋 註冊表:
  registry list         - 列出註冊的MCP
  registry match <intent> - 匹配意圖
  registry stats        - 查看統計

🔧 高級功能:
  batch <file>          - 批處理執行
  export <type> [path]  - 導出數據
  watch [interval]      - 實時監控
  unwatch               - 停止監控

💡 提示:
  - 使用 Tab 鍵自動補全
  - 使用 'help <command>' 查看詳細幫助
  - 使用 'quit' 或 'exit' 退出系統
""")
    
    def do_quit(self, args):
        """退出CLI"""
        print("\n👋 感謝使用PowerAutomation v0.3！")
        self._cleanup()
        return True
    
    def do_exit(self, args):
        """退出CLI"""
        return self.do_quit(args)
    
    def do_EOF(self, args):
        """處理EOF (Ctrl+D)"""
        print("\n")
        return self.do_quit(args)
    
    def default(self, line):
        """處理未知命令"""
        self._record_command(line)
        
        # 嘗試智能路由
        if self.auto_route and line.strip():
            try:
                parts = shlex.split(line)
                if parts:
                    command = parts[0]
                    args = parts[1:]
                    
                    # 路由到最適合的MCP
                    target_mcp = self._route_command(command, args)
                    
                    if target_mcp and target_mcp in self.mcps and self.mcps[target_mcp]:
                        print(f"🎯 智能路由到: {target_mcp}")
                        
                        # 嘗試執行
                        result = self._execute_mcp_command(target_mcp, command, {"args": args})
                        print(self._format_result(result, compact=self.batch_mode))
                        return
            except:
                pass
        
        print(f"❌ 未知命令: {line}")
        print("輸入 'help' 查看可用命令")
    
    def emptyline(self):
        """處理空行"""
        pass
    
    def precmd(self, line):
        """命令預處理"""
        # 記錄命令
        if line.strip():
            self._record_command(line.strip())
        
        return line
    
    def postcmd(self, stop, line):
        """命令後處理"""
        return stop

def create_argument_parser():
    """創建命令行參數解析器"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation v0.3 統一CLI接口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  powerautomation                          # 啟動交互式CLI
  powerautomation --batch commands.txt    # 批處理模式
  powerautomation --command "status"      # 執行單個命令
  powerautomation --export config         # 導出配置
        """
    )
    
    parser.add_argument(
        "--batch", "-b",
        metavar="FILE",
        help="批處理模式，從文件讀取命令"
    )
    
    parser.add_argument(
        "--command", "-c",
        metavar="COMMAND",
        help="執行單個命令後退出"
    )
    
    parser.add_argument(
        "--export", "-e",
        metavar="TYPE",
        choices=["config", "history", "stats", "all"],
        help="導出數據後退出"
    )
    
    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        help="指定導出文件路徑"
    )
    
    parser.add_argument(
        "--no-auto-route",
        action="store_true",
        help="禁用自動路由"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細輸出模式"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="PowerAutomation CLI v0.3.0"
    )
    
    return parser

def main():
    """主函數"""
    try:
        # 解析命令行參數
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # 設置日誌級別
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 創建CLI實例
        cli = PowerAutomationCLI()
        
        # 應用配置
        if args.no_auto_route:
            cli.auto_route = False
        
        # 處理不同模式
        if args.export:
            # 導出模式
            output_path = args.output or f"powerautomation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cli.do_export(f"{args.export} {output_path}")
            
        elif args.command:
            # 單命令模式
            cli.batch_mode = True
            cli.onecmd(args.command)
            
        elif args.batch:
            # 批處理模式
            cli.do_batch(args.batch)
            
        else:
            # 交互式模式
            print("🎉 歡迎使用PowerAutomation v0.3統一CLI！")
            print("💡 輸入 'help' 查看可用命令")
            cli.cmdloop()
    
    except KeyboardInterrupt:
        print("\n\n🛑 用戶中斷，正在退出...")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ CLI啟動失敗: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

