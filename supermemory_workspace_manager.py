#!/usr/bin/env python3
"""
SuperMemory工作區備份管理器
SuperMemory Workspace Backup Manager

專門負責SuperMemory工作區的發現、備份、恢復和管理
"""

import os
import json
import time
import shutil
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess

class SuperMemoryWorkspaceManager:
    """SuperMemory工作區管理器"""
    
    def __init__(self, backup_dir: str = "data/backup/supermemory_workspaces"):
        self.backup_dir = Path(backup_dir)
        self.api_key = os.getenv("SUPERMEMORY_API_KEY")
        self.api_base = "https://api.supermemory.com/v1"
        
        # 確保備份目錄存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 工作區緩存
        self.workspaces_cache = {}
        self.last_discovery = None
        
    def discover_workspaces(self) -> List[Dict[str, Any]]:
        """發現所有SuperMemory工作區"""
        if not self.api_key:
            print("⚠️ SuperMemory API密鑰未配置")
            return []
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 嘗試獲取工作區列表
            response = requests.get(f"{self.api_base}/workspaces", headers=headers)
            
            if response.status_code == 200:
                workspaces = response.json().get("workspaces", [])
                self.workspaces_cache = {ws["id"]: ws for ws in workspaces}
                self.last_discovery = datetime.now().isoformat()
                
                print(f"✅ 發現 {len(workspaces)} 個SuperMemory工作區")
                return workspaces
            else:
                print(f"❌ 獲取工作區失敗: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 工作區發現失敗: {e}")
            return []
            
    def backup_workspace(self, workspace_id: str, backup_type: str = "full") -> Optional[str]:
        """備份指定工作區"""
        if not self.api_key:
            print("⚠️ SuperMemory API密鑰未配置")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 獲取工作區信息
            workspace_info = self._get_workspace_info(workspace_id, headers)
            if not workspace_info:
                return None
                
            # 獲取工作區記憶數據
            memories = self._get_workspace_memories(workspace_id, headers)
            
            # 創建備份
            backup_data = {
                "workspace_info": workspace_info,
                "memories": memories,
                "backup_type": backup_type,
                "backup_time": datetime.now().isoformat(),
                "total_memories": len(memories),
                "api_version": "v1"
            }
            
            # 保存備份文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"workspace_{workspace_id}_{backup_type}_{timestamp}.json"
            backup_path = self.backup_dir / "workspace_exports" / backup_filename
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 工作區 {workspace_id} 備份完成: {backup_path}")
            
            # 更新備份索引
            self._update_backup_index(workspace_id, backup_filename, backup_data)
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ 工作區備份失敗: {e}")
            return None
            
    def _get_workspace_info(self, workspace_id: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """獲取工作區基本信息"""
        try:
            response = requests.get(f"{self.api_base}/workspaces/{workspace_id}", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 獲取工作區信息失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 獲取工作區信息異常: {e}")
            return None
            
    def _get_workspace_memories(self, workspace_id: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """獲取工作區記憶數據"""
        try:
            memories = []
            page = 1
            page_size = 100
            
            while True:
                response = requests.get(
                    f"{self.api_base}/workspaces/{workspace_id}/memories",
                    headers=headers,
                    params={"page": page, "size": page_size}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    batch_memories = data.get("memories", [])
                    memories.extend(batch_memories)
                    
                    # 檢查是否還有更多數據
                    if len(batch_memories) < page_size:
                        break
                    page += 1
                else:
                    print(f"❌ 獲取記憶數據失敗: {response.status_code}")
                    break
                    
            return memories
            
        except Exception as e:
            print(f"❌ 獲取記憶數據異常: {e}")
            return []
            
    def _update_backup_index(self, workspace_id: str, backup_filename: str, backup_data: Dict[str, Any]):
        """更新備份索引"""
        index_file = self.backup_dir / "backup_index.json"
        
        # 載入現有索引
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"workspaces": {}, "last_updated": None}
            
        # 更新索引
        if workspace_id not in index["workspaces"]:
            index["workspaces"][workspace_id] = {"backups": []}
            
        backup_entry = {
            "filename": backup_filename,
            "backup_time": backup_data["backup_time"],
            "backup_type": backup_data["backup_type"],
            "total_memories": backup_data["total_memories"],
            "file_size": os.path.getsize(self.backup_dir / "workspace_exports" / backup_filename)
        }
        
        index["workspaces"][workspace_id]["backups"].append(backup_entry)
        index["last_updated"] = datetime.now().isoformat()
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
            
    def backup_all_workspaces(self) -> List[str]:
        """備份所有工作區"""
        workspaces = self.discover_workspaces()
        backup_paths = []
        
        for workspace in workspaces:
            workspace_id = workspace.get("id")
            if workspace_id:
                backup_path = self.backup_workspace(workspace_id)
                if backup_path:
                    backup_paths.append(backup_path)
                    
        return backup_paths
        
    def list_backups(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """列出備份"""
        index_file = self.backup_dir / "backup_index.json"
        
        if not index_file.exists():
            return {"workspaces": {}, "total_backups": 0}
            
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
            
        if workspace_id:
            workspace_backups = index["workspaces"].get(workspace_id, {"backups": []})
            return {
                "workspace_id": workspace_id,
                "backups": workspace_backups["backups"],
                "total_backups": len(workspace_backups["backups"])
            }
        else:
            total_backups = sum(len(ws["backups"]) for ws in index["workspaces"].values())
            return {
                "workspaces": index["workspaces"],
                "total_backups": total_backups,
                "last_updated": index.get("last_updated")
            }
            
    def restore_workspace(self, backup_filename: str, target_workspace_id: Optional[str] = None) -> bool:
        """恢復工作區（這裡只是示例，實際恢復需要SuperMemory API支持）"""
        backup_path = self.backup_dir / "workspace_exports" / backup_filename
        
        if not backup_path.exists():
            print(f"❌ 備份文件不存在: {backup_filename}")
            return False
            
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                
            print(f"📋 備份信息:")
            print(f"   備份時間: {backup_data['backup_time']}")
            print(f"   備份類型: {backup_data['backup_type']}")
            print(f"   記憶數量: {backup_data['total_memories']}")
            
            # 實際的恢復邏輯需要SuperMemory API支持
            print("⚠️ 恢復功能需要SuperMemory API支持，當前僅顯示備份信息")
            
            return True
            
        except Exception as e:
            print(f"❌ 恢復失敗: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """獲取備份統計信息"""
        backups_info = self.list_backups()
        
        stats = {
            "total_workspaces": len(backups_info["workspaces"]),
            "total_backups": backups_info["total_backups"],
            "backup_directory": str(self.backup_dir),
            "api_configured": bool(self.api_key),
            "last_discovery": self.last_discovery
        }
        
        # 計算備份文件總大小
        exports_dir = self.backup_dir / "workspace_exports"
        if exports_dir.exists():
            total_size = sum(f.stat().st_size for f in exports_dir.rglob("*.json"))
            stats["total_backup_size"] = total_size
            stats["total_backup_size_mb"] = round(total_size / (1024 * 1024), 2)
            
        return stats

# 全局工作區管理器
workspace_manager = SuperMemoryWorkspaceManager()

# 便捷函數
def backup_supermemory_workspace(workspace_id: str) -> Optional[str]:
    """備份指定SuperMemory工作區"""
    return workspace_manager.backup_workspace(workspace_id)

def backup_all_supermemory_workspaces() -> List[str]:
    """備份所有SuperMemory工作區"""
    return workspace_manager.backup_all_workspaces()

def list_supermemory_backups(workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """列出SuperMemory備份"""
    return workspace_manager.list_backups(workspace_id)

def discover_supermemory_workspaces() -> List[Dict[str, Any]]:
    """發現SuperMemory工作區"""
    return workspace_manager.discover_workspaces()

if __name__ == "__main__":
    # 測試SuperMemory工作區管理
    print("🚀 SuperMemory工作區備份管理器測試")
    
    # 獲取統計信息
    stats = workspace_manager.get_statistics()
    print(f"📊 備份統計:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
        
    # 發現工作區
    workspaces = workspace_manager.discover_workspaces()
    print(f"\n🔍 發現的工作區: {len(workspaces)}")
    
    # 如果有工作區，嘗試備份第一個
    if workspaces:
        first_workspace = workspaces[0]
        workspace_id = first_workspace.get("id")
        if workspace_id:
            print(f"\n📦 嘗試備份工作區: {workspace_id}")
            backup_path = workspace_manager.backup_workspace(workspace_id)
            if backup_path:
                print(f"✅ 備份成功: {backup_path}")
                
    # 列出所有備份
    backups = workspace_manager.list_backups()
    print(f"\n📋 備份列表: {backups['total_backups']} 個備份")
    
    print("✅ SuperMemory工作區管理器測試完成")

