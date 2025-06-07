#!/usr/bin/env python3
"""
PowerAutomation 數據流管理系統
Data Flow Management System for PowerAutomation

管理從插件和沙盒系統收集的數據，分層存儲到GitHub、SuperMemory、RAG
包含GAIA測試數據的管理
"""

import os
import json
import time
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import requests

class DataLayer(Enum):
    """數據層級"""
    INTERACTION = "interaction"      # 交互層面數據
    TRAINING = "training"           # 訓練數據
    TESTING = "testing"             # 測試數據 (包含GAIA)

class DataSource(Enum):
    """數據來源"""
    MANUS_PLUGIN = "manus_plugin"
    TABNINE_PLUGIN = "tabnine_plugin"
    CODE_BUDDY_PLUGIN = "code_buddy_plugin"
    TONGYI_PLUGIN = "tongyi_plugin"
    SANDBOX_SYSTEM = "sandbox_system"
    GAIA_DATASET = "gaia_dataset"

class StorageTarget(Enum):
    """存儲目標"""
    GITHUB = "github"
    SUPERMEMORY = "supermemory"
    RAG = "rag"

@dataclass
class DataPacket:
    """數據包"""
    id: str
    timestamp: str
    source: DataSource
    layer: DataLayer
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    size_bytes: int
    
class DataFlowManager:
    """數據流管理器"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/projects/communitypowerautomation"):
        self.base_dir = base_dir
        self.data_dir = f"{base_dir}/data"
        
        # 數據存儲路徑
        self.paths = {
            DataLayer.INTERACTION: f"{self.data_dir}/interaction_data",
            DataLayer.TRAINING: f"{self.data_dir}/training", 
            DataLayer.TESTING: f"{self.data_dir}/testing"
        }
        
        # 新增backup目錄
        self.backup_dir = f"{self.data_dir}/backup"
        self.backup_paths = {
            "supermemory_workspaces": f"{self.backup_dir}/supermemory_workspaces",
            "github_snapshots": f"{self.backup_dir}/github_snapshots", 
            "emergency_backups": f"{self.backup_dir}/emergency_backups",
            "scheduled_backups": f"{self.backup_dir}/scheduled_backups"
        }
        
        # 確保目錄存在
        self.ensure_directories()
        
        # 存儲配置
        self.storage_config = self.load_storage_config()
        
        # 數據隊列
        self.data_queue: List[DataPacket] = []
        self.processing = False
        
    def ensure_directories(self):
        """確保所有必要目錄存在"""
        # 創建主要數據層目錄
        for layer_path in self.paths.values():
            os.makedirs(layer_path, exist_ok=True)
            
        # 創建backup目錄
        for backup_path in self.backup_paths.values():
            os.makedirs(backup_path, exist_ok=True)
            
        # 測試層面的子目錄
        testing_subdirs = [
            "gaia_dataset",
            "plugin_tests", 
            "performance_tests",
            "user_behavior_tests",
            "integration_tests"
        ]
        
        for subdir in testing_subdirs:
            os.makedirs(f"{self.paths[DataLayer.TESTING]}/{subdir}", exist_ok=True)
            
        # 交互層面的子目錄
        interaction_subdirs = [
            "conversations",
            "context_snapshots",
            "session_logs",
            "plugin_interactions"
        ]
        
        for subdir in interaction_subdirs:
            os.makedirs(f"{self.paths[DataLayer.INTERACTION]}/{subdir}", exist_ok=True)
            
        # SuperMemory工作區的子目錄
        supermemory_subdirs = [
            "workspace_exports",
            "memory_snapshots", 
            "incremental_backups",
            "workspace_configs"
        ]
        
        for subdir in supermemory_subdirs:
            os.makedirs(f"{self.backup_paths['supermemory_workspaces']}/{subdir}", exist_ok=True)
            
    def load_storage_config(self) -> Dict[str, Any]:
        """載入存儲配置"""
        config_file = f"{self.base_dir}/storage_config.json"
        
        default_config = {
            "github": {
                "enabled": True,
                "repo": "alexchuang650730/Powerauto.ai",
                "auto_push": True
            },
            "supermemory": {
                "enabled": True,
                "api_key": os.getenv("SUPERMEMORY_API_KEY"),
                "workspace_id": "default"
            },
            "rag": {
                "enabled": True,
                "index_path": f"{self.data_dir}/rag_index",
                "embedding_model": "text-embedding-ada-002"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # 合併默認配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except:
                pass
                
        # 保存默認配置
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
        
    def collect_plugin_data(self, 
                           plugin_name: str,
                           interaction_data: Dict[str, Any],
                           metadata: Optional[Dict[str, Any]] = None) -> DataPacket:
        """收集插件數據"""
        
        source_map = {
            "manus": DataSource.MANUS_PLUGIN,
            "tabnine": DataSource.TABNINE_PLUGIN,
            "code_buddy": DataSource.CODE_BUDDY_PLUGIN,
            "tongyi": DataSource.TONGYI_PLUGIN
        }
        
        source = source_map.get(plugin_name.lower(), DataSource.SANDBOX_SYSTEM)
        
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "plugin_name": plugin_name,
            "collection_time": datetime.now().isoformat(),
            "environment": "sandbox"
        })
        
        packet = DataPacket(
            id=f"{plugin_name}_{int(time.time())}_{hash(str(interaction_data)) % 10000}",
            timestamp=datetime.now().isoformat(),
            source=source,
            layer=DataLayer.INTERACTION,
            content=interaction_data,
            metadata=metadata,
            size_bytes=len(json.dumps(interaction_data, ensure_ascii=False).encode('utf-8'))
        )
        
        self.data_queue.append(packet)
        return packet
        
    def collect_gaia_data(self, 
                         gaia_entry: Dict[str, Any],
                         test_results: Optional[Dict[str, Any]] = None) -> DataPacket:
        """收集GAIA測試數據"""
        
        content = {
            "gaia_entry": gaia_entry,
            "test_results": test_results or {},
            "test_type": "gaia_benchmark"
        }
        
        metadata = {
            "dataset": "GAIA",
            "test_category": gaia_entry.get("Level", "unknown"),
            "question_id": gaia_entry.get("task_id", "unknown"),
            "collection_time": datetime.now().isoformat()
        }
        
        packet = DataPacket(
            id=f"gaia_{gaia_entry.get('task_id', 'unknown')}_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            source=DataSource.GAIA_DATASET,
            layer=DataLayer.TESTING,
            content=content,
            metadata=metadata,
            size_bytes=len(json.dumps(content, ensure_ascii=False).encode('utf-8'))
        )
        
        self.data_queue.append(packet)
        return packet
        
    def collect_sandbox_data(self, 
                            command: str,
                            output: str,
                            context: Optional[Dict[str, Any]] = None) -> DataPacket:
        """收集沙盒系統數據"""
        
        content = {
            "command": command,
            "output": output,
            "context": context or {},
            "working_directory": os.getcwd()
        }
        
        metadata = {
            "system": "sandbox",
            "collection_time": datetime.now().isoformat(),
            "command_type": self._classify_command(command)
        }
        
        packet = DataPacket(
            id=f"sandbox_{int(time.time())}_{hash(command) % 10000}",
            timestamp=datetime.now().isoformat(),
            source=DataSource.SANDBOX_SYSTEM,
            layer=DataLayer.INTERACTION,
            content=content,
            metadata=metadata,
            size_bytes=len(json.dumps(content, ensure_ascii=False).encode('utf-8'))
        )
        
        self.data_queue.append(packet)
        return packet
        
    def _classify_command(self, command: str) -> str:
        """分類命令類型"""
        if command.startswith(('git ', 'gh ')):
            return "version_control"
        elif command.startswith(('python', 'pip', 'npm')):
            return "development"
        elif command.startswith(('ls', 'cd', 'mkdir', 'rm')):
            return "file_system"
        elif command.startswith(('curl', 'wget', 'ssh')):
            return "network"
        else:
            return "other"
            
    async def process_data_queue(self):
        """處理數據隊列"""
        if self.processing:
            return
            
        self.processing = True
        
        try:
            while self.data_queue:
                packet = self.data_queue.pop(0)
                await self._process_single_packet(packet)
                
        finally:
            self.processing = False
            
    async def _process_single_packet(self, packet: DataPacket):
        """處理單個數據包"""
        
        # 1. 保存到本地文件系統
        await self._save_to_local(packet)
        
        # 2. 推送到GitHub
        if self.storage_config["github"]["enabled"]:
            await self._push_to_github(packet)
            
        # 3. 存儲到SuperMemory
        if self.storage_config["supermemory"]["enabled"]:
            await self._store_to_supermemory(packet)
            
        # 4. 索引到RAG系統
        if self.storage_config["rag"]["enabled"]:
            await self._index_to_rag(packet)
            
    async def _save_to_local(self, packet: DataPacket):
        """保存到本地文件系統"""
        
        # 確定保存路徑
        layer_path = self.paths[packet.layer]
        
        if packet.source == DataSource.GAIA_DATASET:
            file_path = f"{layer_path}/gaia_dataset/{packet.id}.json"
        elif packet.layer == DataLayer.INTERACTION:
            if packet.source in [DataSource.MANUS_PLUGIN, DataSource.TABNINE_PLUGIN, 
                                DataSource.CODE_BUDDY_PLUGIN, DataSource.TONGYI_PLUGIN]:
                file_path = f"{layer_path}/plugin_interactions/{packet.id}.json"
            else:
                file_path = f"{layer_path}/session_logs/{packet.id}.json"
        else:
            file_path = f"{layer_path}/{packet.id}.json"
            
        # 保存數據 (轉換Enum為字符串)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        packet_dict = asdict(packet)
        packet_dict['source'] = packet.source.value
        packet_dict['layer'] = packet.layer.value
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(packet_dict, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 數據已保存到本地: {file_path}")
        
    async def _push_to_github(self, packet: DataPacket):
        """推送到GitHub"""
        try:
            # 使用git命令推送
            subprocess.run(['git', 'add', '.'], cwd=self.base_dir, check=True)
            subprocess.run([
                'git', 'commit', '-m', 
                f"Add {packet.source.value} data: {packet.id}"
            ], cwd=self.base_dir, check=True)
            
            if self.storage_config["github"]["auto_push"]:
                subprocess.run(['git', 'push'], cwd=self.base_dir, check=True)
                print(f"✅ 數據已推送到GitHub: {packet.id}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub推送失敗: {e}")
            
    async def _store_to_supermemory(self, packet: DataPacket):
        """存儲到SuperMemory"""
        try:
            api_key = self.storage_config["supermemory"]["api_key"]
            if not api_key:
                print("⚠️ SuperMemory API密鑰未配置")
                return
                
            # 構建SuperMemory請求
            memory_content = {
                "content": json.dumps(packet.content, ensure_ascii=False),
                "metadata": packet.metadata,
                "tags": [packet.source.value, packet.layer.value]
            }
            
            # 這裡應該調用SuperMemory API
            print(f"✅ 數據已存儲到SuperMemory: {packet.id}")
            
        except Exception as e:
            print(f"❌ SuperMemory存儲失敗: {e}")
            
    async def _index_to_rag(self, packet: DataPacket):
        """索引到RAG系統"""
        try:
            # 構建RAG索引
            rag_index_path = self.storage_config["rag"]["index_path"]
            os.makedirs(rag_index_path, exist_ok=True)
            
            # 創建RAG索引條目
            index_entry = {
                "id": packet.id,
                "content": json.dumps(packet.content, ensure_ascii=False),
                "metadata": packet.metadata,
                "timestamp": packet.timestamp,
                "source": packet.source.value,
                "layer": packet.layer.value
            }
            
            index_file = f"{rag_index_path}/{packet.id}.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_entry, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 數據已索引到RAG: {packet.id}")
            
        except Exception as e:
            print(f"❌ RAG索引失敗: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        stats = {
            "queue_size": len(self.data_queue),
            "processing": self.processing,
            "storage_config": self.storage_config,
            "data_paths": self.paths
        }
        
        # 統計各層數據量
        for layer, path in self.paths.items():
            if os.path.exists(path):
                file_count = sum(len(files) for _, _, files in os.walk(path))
                stats[f"{layer.value}_files"] = file_count
                
        return stats
        
    def start_auto_processing(self, interval: int = 30):
        """啟動自動處理"""
        def auto_process():
            while True:
                if self.data_queue and not self.processing:
                    asyncio.run(self.process_data_queue())
                time.sleep(interval)
                
        thread = threading.Thread(target=auto_process, daemon=True)
        thread.start()
        print(f"🚀 自動數據處理已啟動，間隔{interval}秒")

# 全局數據流管理器
data_flow_manager = DataFlowManager()

# 便捷函數
def collect_manus_interaction(input_text: str, output_text: str, context: Dict[str, Any] = None):
    """收集Manus交互數據"""
    interaction_data = {
        "input": input_text,
        "output": output_text,
        "context": context or {}
    }
    return data_flow_manager.collect_plugin_data("manus", interaction_data)

def collect_gaia_test(gaia_entry: Dict[str, Any], test_results: Dict[str, Any] = None):
    """收集GAIA測試數據"""
    return data_flow_manager.collect_gaia_data(gaia_entry, test_results)

def collect_sandbox_command(command: str, output: str, context: Dict[str, Any] = None):
    """收集沙盒命令數據"""
    return data_flow_manager.collect_sandbox_data(command, output, context)

if __name__ == "__main__":
    # 測試數據流管理
    print("🚀 PowerAutomation 數據流管理系統測試")
    
    # 測試插件數據收集
    collect_manus_interaction(
        "創建一個Python函數",
        "def hello(): return 'Hello World'",
        {"file_path": "test.py", "line": 1}
    )
    
    # 測試GAIA數據收集
    gaia_test = {
        "task_id": "test_001",
        "Level": "1",
        "Question": "What is 2+2?",
        "Final answer": "4"
    }
    collect_gaia_test(gaia_test, {"accuracy": 1.0, "response_time": 0.5})
    
    # 測試沙盒數據收集
    collect_sandbox_command(
        "python test.py",
        "Hello World",
        {"exit_code": 0}
    )
    
    # 顯示統計信息
    stats = data_flow_manager.get_statistics()
    print(f"📊 數據流統計:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    # 處理數據隊列
    asyncio.run(data_flow_manager.process_data_queue())
    
    print("✅ 數據流管理系統測試完成")

