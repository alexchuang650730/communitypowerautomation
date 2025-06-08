#!/usr/bin/env python3
"""
自動備份系統實現 v2.0
基於四種觸發條件的智能備份機制
集成統一token管理和智能推送系統
"""

import os
import time
import threading
import subprocess
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 導入統一系統
from unified_token_manager import get_token
from smart_push_system import push_with_retry, emergency_push

class AutoBackupSystem:
    def __init__(self, project_dir="/home/ubuntu/projects/communitypowerautomation"):
        self.project_dir = project_dir
        self.backup_log = os.path.join(project_dir, "backup_log.json")
        self.interaction_count = 0
        self.last_backup_time = time.time()
        self.context_monitor = None
        
        # 備份統計
        self.backup_stats = {
            "file_triggered": 0,
            "time_triggered": 0,
            "interaction_triggered": 0,
            "context_triggered": 0,
            "total_backups": 0
        }
        
        self.load_stats()
    
    def load_stats(self):
        """載入備份統計"""
        if os.path.exists(self.backup_log):
            try:
                with open(self.backup_log, 'r') as f:
                    data = json.load(f)
                    self.backup_stats = data.get('stats', self.backup_stats)
                    self.interaction_count = data.get('interaction_count', 0)
            except:
                pass
    
    def save_stats(self):
        """保存備份統計"""
        data = {
            'stats': self.backup_stats,
            'interaction_count': self.interaction_count,
            'last_backup_time': self.last_backup_time,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.backup_log, 'w') as f:
            json.dump(data, f, indent=2)
    
    def trigger_git_backup(self, reason, trigger_type="manual"):
        """執行Git備份 - 使用智能推送系統"""
        try:
            os.chdir(self.project_dir)
            
            # 檢查是否有變更
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                print(f"⏭️ 跳過備份: 沒有變更 ({reason})")
                return False
            
            # 使用智能推送系統執行備份
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            commit_msg = f"Auto backup: {reason} [{timestamp}]"
            
            print(f"🚀 執行智能備份: {commit_msg}")
            
            # 使用智能推送系統（帶重試和超時保護）
            success = push_with_retry(commit_msg)
            
            if success:
                print(f"✅ 備份成功: {reason}")
                self.backup_stats[f"{trigger_type}_triggered"] += 1
                self.backup_stats["total_backups"] += 1
                self.last_backup_time = time.time()
                self.save_stats()
                return True
            else:
                print(f"❌ 備份失敗: {reason}")
                # 嘗試緊急推送
                print("🚨 嘗試緊急推送...")
                emergency_success = emergency_push(f"Emergency: {commit_msg}")
                if emergency_success:
                    print("✅ 緊急推送成功")
                    return True
                else:
                    print("❌ 緊急推送也失敗")
                    return False
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            # 更新統計
            self.backup_stats[f"{trigger_type}_triggered"] += 1
            self.backup_stats["total_backups"] += 1
            self.last_backup_time = time.time()
            self.save_stats()
            
            print(f"✅ 備份成功: {reason}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 備份失敗: {reason} - {e}")
            return False
        except Exception as e:
            print(f"❌ 備份錯誤: {reason} - {e}")
            return False

class FileChangeHandler(FileSystemEventHandler):
    """文件變更處理器"""
    
    def __init__(self, backup_system):
        self.backup_system = backup_system
        self.last_trigger = 0
        self.cooldown = 10  # 10秒冷卻時間，避免頻繁觸發
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # 檢查文件類型
        if not event.src_path.endswith(('.py', '.md', '.json')):
            return
            
        # 冷卻時間檢查
        current_time = time.time()
        if current_time - self.last_trigger < self.cooldown:
            return
            
        self.last_trigger = current_time
        filename = os.path.basename(event.src_path)
        
        self.backup_system.trigger_git_backup(
            f"File modified: {filename}", 
            "file"
        )

class AutoBackupManager:
    """自動備份管理器"""
    
    def __init__(self, project_dir="/home/ubuntu/projects/communitypowerautomation"):
        self.project_dir = project_dir
        self.backup_system = AutoBackupSystem(project_dir)
        self.observer = None
        self.time_thread = None
        self.running = False
        
    def start_file_monitoring(self):
        """啟動文件監控"""
        if self.observer:
            return
            
        event_handler = FileChangeHandler(self.backup_system)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.project_dir, recursive=True)
        self.observer.start()
        print("📁 文件監控已啟動")
    
    def start_time_monitoring(self):
        """啟動時間觸發監控"""
        if self.time_thread:
            return
            
        def time_backup_loop():
            while self.running:
                time.sleep(300)  # 5分鐘
                if self.running:
                    self.backup_system.trigger_git_backup(
                        "Scheduled backup (5 minutes)", 
                        "time"
                    )
        
        self.time_thread = threading.Thread(target=time_backup_loop, daemon=True)
        self.time_thread.start()
        print("⏰ 定時備份已啟動 (每5分鐘)")
    
    def check_interaction_trigger(self):
        """檢查交互觸發"""
        self.backup_system.interaction_count += 1
        
        if self.backup_system.interaction_count % 10 == 0:
            self.backup_system.trigger_git_backup(
                f"Interaction threshold: {self.backup_system.interaction_count}", 
                "interaction"
            )
    
    def check_context_trigger(self, context_usage_percent):
        """檢查上下文觸發"""
        if context_usage_percent >= 70:
            self.backup_system.trigger_git_backup(
                f"Context usage: {context_usage_percent:.1f}%", 
                "context"
            )
    
    def start_all_monitoring(self):
        """啟動所有監控"""
        self.running = True
        self.start_file_monitoring()
        self.start_time_monitoring()
        print("🚀 自動備份系統已全面啟動")
    
    def stop_all_monitoring(self):
        """停止所有監控"""
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
        if self.time_thread:
            self.time_thread = None
            
        print("⏹️ 自動備份系統已停止")
    
    def get_status(self):
        """獲取備份狀態"""
        return {
            "running": self.running,
            "stats": self.backup_system.backup_stats,
            "interaction_count": self.backup_system.interaction_count,
            "last_backup": datetime.fromtimestamp(self.backup_system.last_backup_time).isoformat()
        }

if __name__ == "__main__":
    # 測試自動備份系統
    manager = AutoBackupManager()
    
    print("📊 當前備份狀態:")
    status = manager.get_status()
    print(f"   總備份次數: {status['stats']['total_backups']}")
    print(f"   文件觸發: {status['stats']['file_triggered']}")
    print(f"   時間觸發: {status['stats']['time_triggered']}")
    print(f"   交互觸發: {status['stats']['interaction_triggered']}")
    print(f"   上下文觸發: {status['stats']['context_triggered']}")
    print(f"   交互計數: {status['interaction_count']}")
    
    # 啟動監控
    manager.start_all_monitoring()
    
    # 測試交互觸發
    print("\n🧪 測試交互觸發...")
    for i in range(3):
        manager.check_interaction_trigger()
        print(f"   交互 {manager.backup_system.interaction_count}")
    
    print("\n✅ 自動備份系統測試完成")
    print("💡 系統將持續在背景運行，監控文件變更和定時備份")

