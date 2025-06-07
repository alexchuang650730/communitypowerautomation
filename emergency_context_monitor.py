#!/usr/bin/env python3
"""
緊急上下文監控系統
用於監控任務狀態並在必要時觸發備份
"""

import os
import time
import json
import subprocess
from datetime import datetime

class EmergencyContextMonitor:
    def __init__(self, project_dir="/home/ubuntu/projects/communitypowerautomation"):
        self.project_dir = project_dir
        self.monitor_file = os.path.join(project_dir, "context_monitor.json")
        self.start_time = time.time()
        self.interaction_count = 0
        self.file_operations = 0
        self.last_backup = None
        
        # 載入或創建監控狀態
        self.load_state()
    
    def load_state(self):
        """載入監控狀態"""
        if os.path.exists(self.monitor_file):
            try:
                with open(self.monitor_file, 'r') as f:
                    data = json.load(f)
                    self.interaction_count = data.get('interaction_count', 0)
                    self.file_operations = data.get('file_operations', 0)
                    self.last_backup = data.get('last_backup')
            except:
                pass
    
    def save_state(self):
        """保存監控狀態"""
        data = {
            'start_time': self.start_time,
            'interaction_count': self.interaction_count,
            'file_operations': self.file_operations,
            'last_backup': self.last_backup,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.monitor_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def increment_interaction(self):
        """增加交互計數"""
        self.interaction_count += 1
        self.save_state()
        self.check_thresholds()
    
    def increment_file_ops(self):
        """增加文件操作計數"""
        self.file_operations += 1
        self.save_state()
        self.check_thresholds()
    
    def check_thresholds(self):
        """檢查閾值並觸發相應動作"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # 時間閾值檢查（30分鐘）
        if elapsed_time > 1800:
            self.trigger_emergency_backup("時間超過30分鐘")
            return True
        
        # 交互次數閾值檢查
        if self.interaction_count > 50:
            self.trigger_emergency_backup("交互次數超過50次")
            return True
        
        # 文件操作閾值檢查
        if self.file_operations > 100:
            self.trigger_emergency_backup("文件操作超過100次")
            return True
        
        # 預警檢查
        if self.interaction_count > 40 or elapsed_time > 1500:
            self.create_warning("接近上下文限制")
        
        return False
    
    def trigger_emergency_backup(self, reason):
        """觸發緊急備份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_msg = f"緊急備份觸發: {reason} at {timestamp}"
        
        # 創建緊急備份標記
        emergency_file = os.path.join(self.project_dir, f"EMERGENCY_BACKUP_{timestamp}.txt")
        with open(emergency_file, 'w') as f:
            f.write(f"{backup_msg}\n")
            f.write(f"交互次數: {self.interaction_count}\n")
            f.write(f"文件操作: {self.file_operations}\n")
            f.write(f"運行時間: {time.time() - self.start_time:.2f}秒\n")
        
        # 嘗試Git提交
        try:
            os.chdir(self.project_dir)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Emergency backup: {reason}'], check=True)
            print(f"✅ Git備份成功: {backup_msg}")
        except:
            print(f"❌ Git備份失敗: {backup_msg}")
        
        self.last_backup = timestamp
        self.save_state()
    
    def create_warning(self, message):
        """創建警告文件"""
        warning_file = os.path.join(self.project_dir, "CONTEXT_WARNING.txt")
        with open(warning_file, 'w') as f:
            f.write(f"⚠️ 上下文警告: {message}\n")
            f.write(f"時間: {datetime.now().isoformat()}\n")
            f.write(f"交互次數: {self.interaction_count}\n")
            f.write(f"建議: 考慮備份並重啟任務\n")
    
    def get_status(self):
        """獲取當前狀態"""
        elapsed_time = time.time() - self.start_time
        return {
            'elapsed_time': elapsed_time,
            'interaction_count': self.interaction_count,
            'file_operations': self.file_operations,
            'last_backup': self.last_backup,
            'warning_level': self.get_warning_level()
        }
    
    def get_warning_level(self):
        """獲取警告級別"""
        elapsed_time = time.time() - self.start_time
        
        if self.interaction_count > 50 or elapsed_time > 1800:
            return "CRITICAL"
        elif self.interaction_count > 40 or elapsed_time > 1500:
            return "WARNING"
        elif self.interaction_count > 30 or elapsed_time > 1200:
            return "CAUTION"
        else:
            return "NORMAL"

if __name__ == "__main__":
    monitor = EmergencyContextMonitor()
    
    # 立即檢查狀態
    status = monitor.get_status()
    print(f"📊 監控狀態:")
    print(f"   運行時間: {status['elapsed_time']:.2f}秒")
    print(f"   交互次數: {status['interaction_count']}")
    print(f"   文件操作: {status['file_operations']}")
    print(f"   警告級別: {status['warning_level']}")
    
    # 增加一次交互計數（因為運行了這個腳本）
    monitor.increment_interaction()

