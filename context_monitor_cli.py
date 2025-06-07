#!/usr/bin/env python3
"""
上下文監控CLI工具 v1.0
提供命令行接口來監控和管理上下文使用情況
"""

import argparse
import sys
import os
from auto_context_tracker import get_tracker, get_current_status

def show_status():
    """顯示當前上下文狀態"""
    status = get_current_status()
    
    print("📊 上下文監控狀態")
    print("=" * 50)
    print(f"總字符數: {status['total_chars']:,}")
    print(f"使用率: {status['usage_percent']:.2f}%")
    print(f"交互次數: {status['interaction_count']}")
    print(f"用戶輸入: {status['user_input_chars']:,} 字符")
    print(f"助手輸出: {status['assistant_output_chars']:,} 字符")
    print(f"文件操作: {status['file_operations']} 次")
    print(f"警告級別: {status['warning_level']}")
    
    # 預估剩餘容量
    remaining = 200000 - status['total_chars']
    print(f"預估剩餘: {remaining:,} 字符")
    
    # 警告提示
    if status['warning_level'] == 'CRITICAL':
        print("\n🚨 危險：建議立即備份並重啟任務！")
    elif status['warning_level'] == 'WARNING':
        print("\n⚠️ 警告：接近上下文限制，建議準備備份")
    elif status['warning_level'] == 'CAUTION':
        print("\n💡 注意：上下文使用量較高，請留意")

def track_conversation(user_input, assistant_output):
    """手動追蹤一次對話"""
    tracker = get_tracker()
    
    if user_input:
        status1 = tracker.track_user_input(user_input)
        print(f"✅ 用戶輸入已追蹤: {len(user_input)} 字符 (狀態: {status1})")
    
    if assistant_output:
        status2 = tracker.track_assistant_output(assistant_output)
        print(f"✅ 助手輸出已追蹤: {len(assistant_output)} 字符 (狀態: {status2})")
    
    # 顯示更新後的狀態
    show_status()

def estimate_current_conversation():
    """估算當前對話的實際長度"""
    print("🔍 估算當前對話長度...")
    
    # 這裡可以添加邏輯來分析當前的對話歷史
    # 目前先提供一個手動輸入的方式
    
    print("請提供當前對話的估算信息：")
    try:
        user_chars = int(input("用戶輸入總字符數: "))
        assistant_chars = int(input("助手輸出總字符數: "))
        
        tracker = get_tracker()
        
        # 重置並設置實際數據
        tracker.monitor.user_input_chars = user_chars
        tracker.monitor.assistant_output_chars = assistant_chars
        tracker.monitor.total_chars = user_chars + assistant_chars
        tracker.monitor.save_state()
        
        print(f"✅ 已更新實際對話長度: {user_chars + assistant_chars:,} 字符")
        show_status()
        
    except ValueError:
        print("❌ 請輸入有效的數字")
    except KeyboardInterrupt:
        print("\n操作已取消")

def reset_monitor():
    """重置監控系統"""
    tracker = get_tracker()
    tracker.monitor.user_input_chars = 0
    tracker.monitor.assistant_output_chars = 0
    tracker.monitor.total_chars = 0
    tracker.monitor.interaction_count = 0
    tracker.monitor.file_operations = 0
    tracker.monitor.save_state()
    
    print("✅ 監控系統已重置")
    show_status()

def backup_now():
    """立即執行備份"""
    tracker = get_tracker()
    tracker.monitor.trigger_emergency_backup("手動觸發備份")
    print("✅ 備份已執行")

def main():
    parser = argparse.ArgumentParser(description="上下文監控CLI工具")
    parser.add_argument('command', choices=['status', 'track', 'estimate', 'reset', 'backup'], 
                       help='執行的命令')
    parser.add_argument('--user-input', help='用戶輸入文本')
    parser.add_argument('--assistant-output', help='助手輸出文本')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'track':
        track_conversation(args.user_input, args.assistant_output)
    elif args.command == 'estimate':
        estimate_current_conversation()
    elif args.command == 'reset':
        reset_monitor()
    elif args.command == 'backup':
        backup_now()

if __name__ == "__main__":
    main()

