#!/usr/bin/env python3
"""
系統級數據採集框架
System-Level Data Collection Framework

用於從多個來源收集、標準化、分類存儲所有的交互數據
包括VS Code插件、CLI工具、API調用、文件操作等
"""

import os
import json
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DataSource(Enum):
    """數據來源類型"""
    DIRECT_CHAT = "direct_chat"          # 直接對話
    VSCODE_PLUGIN = "vscode_plugin"      # VS Code插件
    CLI_TOOL = "cli_tool"                # CLI工具
    API_CALL = "api_call"                # API調用
    FILE_OPERATION = "file_operation"    # 文件操作
    SYSTEM_LOG = "system_log"            # 系統日誌

class ConversationType(Enum):
    """對話類型"""
    THINKING = "thinking"                # 思考分析
    EXECUTION = "execution"              # 執行操作
    CONFIRMATION = "confirmation"        # 確認驗證
    REPLAY = "replay"                    # 回放查詢
    CODE_GENERATION = "code_generation"  # 代碼生成
    CODE_REVIEW = "code_review"          # 代碼審查
    DEBUGGING = "debugging"              # 調試排錯

@dataclass
class DataEntry:
    """數據條目"""
    timestamp: str
    source: DataSource
    conversation_type: ConversationType
    input_text: str
    output_text: str
    input_length: int
    output_length: int
    context_info: Dict[str, Any]
    session_id: str
    user_id: str = "default"

class SystemDataCollector:
    """系統級數據採集器"""
    
    def __init__(self, data_dir: str = "data/system_collection"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # 數據存儲
        self.daily_file = self.get_daily_file()
        self.session_data: List[DataEntry] = []
        
        # 統計信息
        self.stats = {
            'total_entries': 0,
            'by_source': {},
            'by_type': {},
            'total_input_chars': 0,
            'total_output_chars': 0
        }
        
        # 監控線程
        self.monitoring = False
        self.monitor_threads: List[threading.Thread] = []
        
    def ensure_data_dir(self):
        """確保數據目錄存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/daily", exist_ok=True)
        os.makedirs(f"{self.data_dir}/sessions", exist_ok=True)
        os.makedirs(f"{self.data_dir}/vscode", exist_ok=True)
        os.makedirs(f"{self.data_dir}/api_logs", exist_ok=True)
        
    def get_daily_file(self) -> str:
        """獲取今日數據文件路徑"""
        today = datetime.now().strftime("%Y%m%d")
        return f"{self.data_dir}/daily/data_{today}.jsonl"
        
    def collect_data(self, 
                    input_text: str,
                    output_text: str,
                    source: DataSource,
                    conversation_type: ConversationType,
                    context_info: Optional[Dict[str, Any]] = None,
                    session_id: Optional[str] = None) -> DataEntry:
        """收集數據條目"""
        
        if context_info is None:
            context_info = {}
            
        if session_id is None:
            session_id = f"session_{int(time.time())}"
            
        entry = DataEntry(
            timestamp=datetime.now().isoformat(),
            source=source,
            conversation_type=conversation_type,
            input_text=input_text,
            output_text=output_text,
            input_length=len(input_text),
            output_length=len(output_text),
            context_info=context_info,
            session_id=session_id
        )
        
        # 保存到會話數據
        self.session_data.append(entry)
        
        # 更新統計
        self.update_stats(entry)
        
        # 持久化保存
        self.save_entry(entry)
        
        return entry
        
    def update_stats(self, entry: DataEntry):
        """更新統計信息"""
        self.stats['total_entries'] += 1
        self.stats['total_input_chars'] += entry.input_length
        self.stats['total_output_chars'] += entry.output_length
        
        # 按來源統計
        source_key = entry.source.value
        if source_key not in self.stats['by_source']:
            self.stats['by_source'][source_key] = 0
        self.stats['by_source'][source_key] += 1
        
        # 按類型統計
        type_key = entry.conversation_type.value
        if type_key not in self.stats['by_type']:
            self.stats['by_type'][type_key] = 0
        self.stats['by_type'][type_key] += 1
        
    def save_entry(self, entry: DataEntry):
        """保存數據條目到文件"""
        with open(self.daily_file, 'a', encoding='utf-8') as f:
            json.dump(asdict(entry), f, ensure_ascii=False)
            f.write('\n')
            
    def start_vscode_monitoring(self):
        """啟動VS Code監控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        
        # 監控VS Code日誌
        vscode_thread = threading.Thread(
            target=self._monitor_vscode_logs,
            daemon=True
        )
        vscode_thread.start()
        self.monitor_threads.append(vscode_thread)
        
        # 監控文件變化
        file_thread = threading.Thread(
            target=self._monitor_file_changes,
            daemon=True
        )
        file_thread.start()
        self.monitor_threads.append(file_thread)
        
    def _monitor_vscode_logs(self):
        """監控VS Code日誌"""
        vscode_log_paths = [
            "~/.vscode/logs",
            "~/.vscode-server/data/logs",
            "/tmp/vscode-logs"
        ]
        
        for log_path in vscode_log_paths:
            expanded_path = os.path.expanduser(log_path)
            if os.path.exists(expanded_path):
                print(f"📊 開始監控VS Code日誌: {expanded_path}")
                # 這裡可以實現具體的日誌監控邏輯
                break
                
    def _monitor_file_changes(self):
        """監控文件變化"""
        # 使用inotify監控文件系統變化
        try:
            import pyinotify
            # 實現文件變化監控
            print("📊 開始監控文件系統變化")
        except ImportError:
            print("⚠️ pyinotify未安裝，跳過文件監控")
            
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            **self.stats,
            'session_entries': len(self.session_data),
            'daily_file': self.daily_file,
            'monitoring_active': self.monitoring
        }
        
    def export_session_data(self, session_id: str) -> str:
        """導出會話數據"""
        session_file = f"{self.data_dir}/sessions/session_{session_id}.json"
        session_entries = [
            entry for entry in self.session_data 
            if entry.session_id == session_id
        ]
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(entry) for entry in session_entries], f, 
                     ensure_ascii=False, indent=2)
                     
        return session_file
        
    def query_data(self, 
                  source: Optional[DataSource] = None,
                  conversation_type: Optional[ConversationType] = None,
                  start_time: Optional[str] = None,
                  end_time: Optional[str] = None) -> List[DataEntry]:
        """查詢數據"""
        results = self.session_data.copy()
        
        if source:
            results = [e for e in results if e.source == source]
            
        if conversation_type:
            results = [e for e in results if e.conversation_type == conversation_type]
            
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
            
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
            
        return results

# 全局數據採集器實例
collector = SystemDataCollector()

# 便捷函數
def collect_direct_chat(input_text: str, output_text: str, 
                       conversation_type: ConversationType = ConversationType.THINKING):
    """收集直接對話數據"""
    return collector.collect_data(
        input_text=input_text,
        output_text=output_text,
        source=DataSource.DIRECT_CHAT,
        conversation_type=conversation_type
    )

def collect_vscode_interaction(input_text: str, output_text: str,
                              file_path: str = "",
                              selected_text: str = ""):
    """收集VS Code插件交互數據"""
    context_info = {
        'file_path': file_path,
        'selected_text': selected_text,
        'workspace': os.getcwd()
    }
    
    return collector.collect_data(
        input_text=input_text,
        output_text=output_text,
        source=DataSource.VSCODE_PLUGIN,
        conversation_type=ConversationType.CODE_GENERATION,
        context_info=context_info
    )

def collect_cli_interaction(command: str, output: str, tool_name: str = ""):
    """收集CLI工具交互數據"""
    context_info = {
        'tool_name': tool_name,
        'working_directory': os.getcwd()
    }
    
    return collector.collect_data(
        input_text=command,
        output_text=output,
        source=DataSource.CLI_TOOL,
        conversation_type=ConversationType.EXECUTION,
        context_info=context_info
    )

def collect_api_call(request: str, response: str, api_endpoint: str = ""):
    """收集API調用數據"""
    context_info = {
        'api_endpoint': api_endpoint,
        'timestamp': datetime.now().isoformat()
    }
    
    return collector.collect_data(
        input_text=request,
        output_text=response,
        source=DataSource.API_CALL,
        conversation_type=ConversationType.EXECUTION,
        context_info=context_info
    )

if __name__ == "__main__":
    # 測試數據採集
    print("🚀 系統級數據採集框架測試")
    
    # 測試直接對話收集
    collect_direct_chat(
        "你這個是系統及的數據採集",
        "是的，這是一個系統級的數據採集框架",
        ConversationType.THINKING
    )
    
    # 測試VS Code交互收集
    collect_vscode_interaction(
        "生成一個Python函數",
        "def hello_world(): return 'Hello, World!'",
        file_path="/path/to/file.py"
    )
    
    # 顯示統計信息
    stats = collector.get_stats()
    print(f"📊 數據採集統計:")
    print(f"   總條目數: {stats['total_entries']}")
    print(f"   總輸入字符: {stats['total_input_chars']:,}")
    print(f"   總輸出字符: {stats['total_output_chars']:,}")
    print(f"   按來源分布: {stats['by_source']}")
    print(f"   按類型分布: {stats['by_type']}")
    
    print(f"\n✅ 數據保存到: {collector.daily_file}")

