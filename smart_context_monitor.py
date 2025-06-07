#!/usr/bin/env python3
"""
智能上下文監控系統 v2.0
基於雙向文本長度的精確上下文預測
"""

import os
import time
import json
import subprocess
from datetime import datetime

class SmartContextMonitor:
    def __init__(self, project_dir="/home/ubuntu/projects/communitypowerautomation"):
        self.project_dir = project_dir
        self.monitor_file = os.path.join(project_dir, "smart_context_monitor.json")
        self.start_time = time.time()
        
        # 文本長度追蹤
        self.user_input_chars = 0
        self.assistant_output_chars = 0
        self.total_chars = 0
        
        # 交互追蹤
        self.interaction_count = 0
        self.file_operations = 0
        self.last_backup = None
        
        # 上下文限制估算 (基於經驗值)
        self.estimated_context_limit = 200000  # 約20萬字符
        self.warning_threshold = 0.8  # 80%時警告
        self.critical_threshold = 0.9  # 90%時強制備份
        
        self.load_state()
    
    def load_state(self):
        """載入監控狀態"""
        if os.path.exists(self.monitor_file):
            try:
                with open(self.monitor_file, 'r') as f:
                    data = json.load(f)
                    self.user_input_chars = data.get('user_input_chars', 0)
                    self.assistant_output_chars = data.get('assistant_output_chars', 0)
                    self.total_chars = data.get('total_chars', 0)
                    self.interaction_count = data.get('interaction_count', 0)
                    self.file_operations = data.get('file_operations', 0)
                    self.last_backup = data.get('last_backup')
            except:
                pass
    
    def save_state(self):
        """保存監控狀態"""
        data = {
            'start_time': self.start_time,
            'user_input_chars': self.user_input_chars,
            'assistant_output_chars': self.assistant_output_chars,
            'total_chars': self.total_chars,
            'interaction_count': self.interaction_count,
            'file_operations': self.file_operations,
            'last_backup': self.last_backup,
            'timestamp': datetime.now().isoformat(),
            'context_usage_percent': self.get_context_usage_percent()
        }
        with open(self.monitor_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_user_input(self, text):
        """記錄用戶輸入"""
        chars = len(text)
        self.user_input_chars += chars
        self.total_chars += chars
        self.interaction_count += 1
        self.save_state()
        return self.check_thresholds()
    
    def add_assistant_output(self, text):
        """記錄助手輸出"""
        chars = len(text)
        self.assistant_output_chars += chars
        self.total_chars += chars
        self.save_state()
        return self.check_thresholds()
    
    def add_file_operation(self, operation_type="unknown", size=0):
        """記錄文件操作"""
        self.file_operations += 1
        if size > 0:
            self.total_chars += size  # 文件內容也計入上下文
        self.save_state()
        return self.check_thresholds()
    
    def get_context_usage_percent(self):
        """獲取上下文使用百分比"""
        return (self.total_chars / self.estimated_context_limit) * 100
    
    def check_thresholds(self):
        """檢查閾值並觸發相應動作"""
        usage_percent = self.get_context_usage_percent()
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # 上下文使用量檢查
        if usage_percent >= self.critical_threshold * 100:
            self.trigger_emergency_backup(f"上下文使用量達到{usage_percent:.1f}%")
            return "CRITICAL"
        
        if usage_percent >= self.warning_threshold * 100:
            self.create_warning(f"上下文使用量達到{usage_percent:.1f}%")
            return "WARNING"
        
        # 時間閾值檢查（30分鐘）
        if elapsed_time > 1800:
            self.trigger_emergency_backup("時間超過30分鐘")
            return "CRITICAL"
        
        # 交互次數閾值檢查
        if self.interaction_count > 100:
            self.trigger_emergency_backup("交互次數超過100次")
            return "CRITICAL"
        
        return "NORMAL"
    
    def trigger_emergency_backup(self, reason):
        """觸發緊急備份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        usage_percent = self.get_context_usage_percent()
        
        backup_msg = f"緊急備份觸發: {reason} at {timestamp}"
        
        # 創建緊急備份標記
        emergency_file = os.path.join(self.project_dir, f"EMERGENCY_BACKUP_{timestamp}.txt")
        with open(emergency_file, 'w') as f:
            f.write(f"{backup_msg}\n")
            f.write(f"上下文使用量: {usage_percent:.1f}%\n")
            f.write(f"總字符數: {self.total_chars:,}\n")
            f.write(f"用戶輸入: {self.user_input_chars:,} 字符\n")
            f.write(f"助手輸出: {self.assistant_output_chars:,} 字符\n")
            f.write(f"交互次數: {self.interaction_count}\n")
            f.write(f"文件操作: {self.file_operations}\n")
            f.write(f"運行時間: {time.time() - self.start_time:.2f}秒\n")
        
        # 嘗試Git提交
        try:
            os.chdir(self.project_dir)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Emergency backup: {reason} (Context: {usage_percent:.1f}%)'], check=True)
            print(f"✅ Git備份成功: {backup_msg}")
        except Exception as e:
            print(f"❌ Git備份失敗: {backup_msg} - {e}")
        
        self.last_backup = timestamp
        self.save_state()
    
    def create_warning(self, message):
        """創建警告文件"""
        warning_file = os.path.join(self.project_dir, "CONTEXT_WARNING.txt")
        usage_percent = self.get_context_usage_percent()
        
        with open(warning_file, 'w') as f:
            f.write(f"⚠️ 上下文警告: {message}\n")
            f.write(f"時間: {datetime.now().isoformat()}\n")
            f.write(f"上下文使用量: {usage_percent:.1f}%\n")
            f.write(f"總字符數: {self.total_chars:,}\n")
            f.write(f"預估剩餘容量: {self.estimated_context_limit - self.total_chars:,} 字符\n")
            f.write(f"建議: 考慮備份並重啟任務\n")
    
    def get_detailed_status(self):
        """獲取詳細狀態"""
        elapsed_time = time.time() - self.start_time
        usage_percent = self.get_context_usage_percent()
        
        return {
            'elapsed_time': elapsed_time,
            'interaction_count': self.interaction_count,
            'file_operations': self.file_operations,
            'user_input_chars': self.user_input_chars,
            'assistant_output_chars': self.assistant_output_chars,
            'total_chars': self.total_chars,
            'context_usage_percent': usage_percent,
            'estimated_remaining': self.estimated_context_limit - self.total_chars,
            'warning_level': self.get_warning_level(),
            'last_backup': self.last_backup
        }
    
    def get_warning_level(self):
        """獲取警告級別"""
        usage_percent = self.get_context_usage_percent()
        elapsed_time = time.time() - self.start_time
        
        if usage_percent >= 90 or self.interaction_count > 100 or elapsed_time > 1800:
            return "CRITICAL"
        elif usage_percent >= 80 or self.interaction_count > 80 or elapsed_time > 1500:
            return "WARNING"
        elif usage_percent >= 60 or self.interaction_count > 60 or elapsed_time > 1200:
            return "CAUTION"
        else:
            return "NORMAL"
    
    def get_timestamp(self):
        """獲取當前時間戳"""
        return datetime.now().isoformat()

# 全局監控實例
monitor = SmartContextMonitor()

def track_user_input(text):
    """追蹤用戶輸入"""
    return monitor.add_user_input(text)

def track_assistant_output(text):
    """追蹤助手輸出"""
    return monitor.add_assistant_output(text)

def track_file_operation(op_type="unknown", size=0):
    """追蹤文件操作"""
    return monitor.add_file_operation(op_type, size)

if __name__ == "__main__":
    # 測試當前狀態
    status = monitor.get_detailed_status()
    print(f"📊 智能上下文監控狀態:")
    print(f"   運行時間: {status['elapsed_time']:.2f}秒")
    print(f"   交互次數: {status['interaction_count']}")
    print(f"   總字符數: {status['total_chars']:,}")
    print(f"   用戶輸入: {status['user_input_chars']:,} 字符")
    print(f"   助手輸出: {status['assistant_output_chars']:,} 字符")
    print(f"   上下文使用量: {status['context_usage_percent']:.1f}%")
    print(f"   預估剩餘: {status['estimated_remaining']:,} 字符")
    print(f"   警告級別: {status['warning_level']}")
    
    # 模擬用戶輸入
    test_input = "你可以偵測你回覆的文本長度對吧"
    monitor.add_user_input(test_input)
    print(f"\n✅ 已記錄用戶輸入: {len(test_input)} 字符")

