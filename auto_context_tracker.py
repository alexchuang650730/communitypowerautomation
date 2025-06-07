#!/usr/bin/env python3
"""
自動上下文追蹤器 v1.0
自動調用智能監控系統，確保每次對話都被正確追蹤
"""

import os
import sys
import json
from smart_context_monitor import SmartContextMonitor

class AutoContextTracker:
    def __init__(self):
        self.monitor = SmartContextMonitor()
        self.conversation_log = []
        
    def track_user_input(self, text):
        """追蹤用戶輸入"""
        if not text:
            return
            
        # 記錄到監控系統
        status = self.monitor.add_user_input(text)
        
        # 記錄到對話日誌
        self.conversation_log.append({
            'type': 'user_input',
            'text': text,
            'length': len(text),
            'timestamp': self.monitor.get_timestamp(),
            'status': status
        })
        
        # 檢查預警
        if status in ['WARNING', 'CRITICAL']:
            self.handle_warning(status, 'user_input', len(text))
            
        return status
    
    def track_assistant_output(self, text):
        """追蹤助手輸出"""
        if not text:
            return
            
        # 記錄到監控系統
        status = self.monitor.add_assistant_output(text)
        
        # 記錄到對話日誌
        self.conversation_log.append({
            'type': 'assistant_output',
            'text': text,
            'length': len(text),
            'timestamp': self.monitor.get_timestamp(),
            'status': status
        })
        
        # 檢查預警
        if status in ['WARNING', 'CRITICAL']:
            self.handle_warning(status, 'assistant_output', len(text))
            
        return status
    
    def track_file_operation(self, operation_type, file_path, content_size=0):
        """追蹤文件操作"""
        status = self.monitor.add_file_operation(operation_type, content_size)
        
        # 記錄到對話日誌
        self.conversation_log.append({
            'type': 'file_operation',
            'operation': operation_type,
            'file_path': file_path,
            'size': content_size,
            'timestamp': self.monitor.get_timestamp(),
            'status': status
        })
        
        return status
    
    def handle_warning(self, level, trigger_type, trigger_size):
        """處理預警"""
        usage = self.monitor.get_context_usage_percent()
        
        warning_msg = f"""
🚨 上下文預警 - {level}
觸發原因: {trigger_type} ({trigger_size:,} 字符)
當前使用率: {usage:.1f}%
總字符數: {self.monitor.total_chars:,}
交互次數: {self.monitor.interaction_count}
"""
        
        print(warning_msg)
        
        # 創建預警文件
        warning_file = f"context_warning_{level.lower()}.txt"
        with open(warning_file, 'w') as f:
            f.write(warning_msg)
            f.write(f"\n詳細統計:\n")
            f.write(f"用戶輸入: {self.monitor.user_input_chars:,} 字符\n")
            f.write(f"助手輸出: {self.monitor.assistant_output_chars:,} 字符\n")
            f.write(f"文件操作: {self.monitor.file_operations} 次\n")
    
    def get_current_status(self):
        """獲取當前狀態"""
        return {
            'total_chars': self.monitor.total_chars,
            'usage_percent': self.monitor.get_context_usage_percent(),
            'interaction_count': self.monitor.interaction_count,
            'user_input_chars': self.monitor.user_input_chars,
            'assistant_output_chars': self.monitor.assistant_output_chars,
            'file_operations': self.monitor.file_operations,
            'warning_level': self.monitor.check_thresholds()
        }
    
    def save_conversation_log(self):
        """保存對話日誌"""
        log_file = f"conversation_log_{self.monitor.get_timestamp().replace(':', '-')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.conversation_log, f, indent=2, ensure_ascii=False)
        return log_file

# 全局追蹤器實例
_tracker = None

def get_tracker():
    """獲取全局追蹤器實例"""
    global _tracker
    if _tracker is None:
        _tracker = AutoContextTracker()
    return _tracker

def track_user_input(text):
    """便捷函數：追蹤用戶輸入"""
    return get_tracker().track_user_input(text)

def track_assistant_output(text):
    """便捷函數：追蹤助手輸出"""
    return get_tracker().track_assistant_output(text)

def track_file_operation(operation_type, file_path, content_size=0):
    """便捷函數：追蹤文件操作"""
    return get_tracker().track_file_operation(operation_type, file_path, content_size)

def get_current_status():
    """便捷函數：獲取當前狀態"""
    return get_tracker().get_current_status()

if __name__ == "__main__":
    # 測試自動追蹤器
    tracker = AutoContextTracker()
    
    # 模擬對話
    print("測試自動上下文追蹤器...")
    
    status1 = tracker.track_user_input("這是一個測試用戶輸入")
    print(f"用戶輸入狀態: {status1}")
    
    status2 = tracker.track_assistant_output("這是一個測試助手回覆，包含更多的文字內容來測試字符計數功能")
    print(f"助手輸出狀態: {status2}")
    
    status3 = tracker.track_file_operation("read", "test.txt", 1000)
    print(f"文件操作狀態: {status3}")
    
    # 顯示當前狀態
    current_status = tracker.get_current_status()
    print(f"\n當前狀態:")
    for key, value in current_status.items():
        print(f"  {key}: {value}")
    
    # 保存對話日誌
    log_file = tracker.save_conversation_log()
    print(f"\n對話日誌已保存到: {log_file}")

