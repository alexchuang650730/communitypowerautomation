#!/usr/bin/env python3
"""
智能推送系統 v2.0
Smart Push System with Timeout, Monitoring and Auto-retry

解決推送進程卡死問題：
- 超時機制
- 進程監控  
- 自動重試
- 卡死檢測和清理
"""

import os
import time
import signal
import subprocess
import threading
import psutil
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from unified_token_manager import get_token

class SmartPushSystem:
    """智能推送系統"""
    
    def __init__(self):
        self.timeout = 60  # 60秒超時
        self.max_retries = 3
        self.retry_delay = 10  # 重試間隔10秒
        self.process_monitor_interval = 5  # 5秒檢查一次進程
        
        # 進程追蹤
        self.active_processes: Dict[int, Dict] = {}
        self.push_history: List[Dict] = []
        
        # 監控線程
        self.monitor_thread = None
        self.monitoring = False
        
    def start_monitoring(self):
        """啟動進程監控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        self.monitor_thread.start()
        print("✅ 進程監控已啟動")
        
    def stop_monitoring(self):
        """停止進程監控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ 進程監控已停止")
        
    def _monitor_processes(self):
        """監控進程狀態"""
        while self.monitoring:
            try:
                current_time = time.time()
                dead_processes = []
                
                for pid, info in self.active_processes.items():
                    # 檢查進程是否還存在
                    if not psutil.pid_exists(pid):
                        dead_processes.append(pid)
                        continue
                        
                    # 檢查是否超時
                    if current_time - info['start_time'] > self.timeout:
                        print(f"🚨 檢測到超時進程 PID {pid}，正在終止...")
                        self._kill_process(pid)
                        dead_processes.append(pid)
                        
                        # 記錄超時
                        info['status'] = 'timeout'
                        info['end_time'] = current_time
                        self.push_history.append(info.copy())
                
                # 清理已死進程
                for pid in dead_processes:
                    self.active_processes.pop(pid, None)
                    
                time.sleep(self.process_monitor_interval)
                
            except Exception as e:
                print(f"❌ 進程監控出錯: {e}")
                time.sleep(self.process_monitor_interval)
                
    def _kill_process(self, pid: int):
        """安全終止進程"""
        try:
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                
                # 先嘗試優雅終止
                process.terminate()
                
                # 等待3秒
                try:
                    process.wait(timeout=3)
                except psutil.TimeoutExpired:
                    # 強制終止
                    process.kill()
                    print(f"🔪 強制終止進程 PID {pid}")
                else:
                    print(f"✅ 優雅終止進程 PID {pid}")
                    
        except Exception as e:
            print(f"❌ 終止進程失敗 PID {pid}: {e}")
            
    def clean_stuck_processes(self):
        """清理所有卡死的Git進程"""
        try:
            # 查找所有Git推送進程
            git_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    if proc.info['name'] == 'git' and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'push' in cmdline:
                            git_processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline,
                                'create_time': proc.info['create_time'],
                                'age': time.time() - proc.info['create_time']
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not git_processes:
                print("✅ 沒有發現卡死的Git進程")
                return
                
            print(f"🔍 發現 {len(git_processes)} 個Git推送進程:")
            for proc in git_processes:
                age_minutes = proc['age'] / 60
                print(f"  PID {proc['pid']}: {proc['cmdline']} (運行 {age_minutes:.1f} 分鐘)")
                
                # 終止運行超過5分鐘的進程
                if proc['age'] > 300:  # 5分鐘
                    print(f"🚨 終止長時間運行的進程 PID {proc['pid']}")
                    self._kill_process(proc['pid'])
                    
        except Exception as e:
            print(f"❌ 清理進程失敗: {e}")
            
    def push_with_retry(self, commit_message: str = None, branch: str = "main") -> bool:
        """帶重試的智能推送"""
        if not self.monitoring:
            self.start_monitoring()
            
        for attempt in range(self.max_retries):
            print(f"🚀 推送嘗試 {attempt + 1}/{self.max_retries}")
            
            success = self._single_push(commit_message, branch, attempt)
            if success:
                print("✅ 推送成功！")
                return True
                
            if attempt < self.max_retries - 1:
                print(f"⏳ {self.retry_delay}秒後重試...")
                time.sleep(self.retry_delay)
                
        print("❌ 所有推送嘗試都失敗了")
        return False
        
    def _single_push(self, commit_message: str = None, branch: str = "main", attempt: int = 0) -> bool:
        """單次推送嘗試"""
        try:
            # 獲取GitHub token
            token = get_token("github")
            if not token:
                print("❌ 找不到GitHub token")
                return False
                
            # 準備Git命令
            if commit_message:
                # 先提交
                add_result = self._run_git_command(['git', 'add', '.'], timeout=30)
                if not add_result:
                    return False
                    
                commit_result = self._run_git_command([
                    'git', 'commit', '-m', commit_message
                ], timeout=30)
                if not commit_result:
                    print("⚠️ 提交失敗，可能沒有變更")
            
            # 設置認證
            remote_url = f"https://{token}@github.com/alexchuang650730/Powerauto.ai.git"
            
            # 設置遠程URL
            self._run_git_command([
                'git', 'remote', 'set-url', 'origin', remote_url
            ], timeout=10)
            
            # 推送
            push_result = self._run_git_command([
                'git', 'push', 'origin', branch
            ], timeout=self.timeout)
            
            return push_result
            
        except Exception as e:
            print(f"❌ 推送失敗 (嘗試 {attempt + 1}): {e}")
            return False
            
    def _run_git_command(self, command: List[str], timeout: int = 60) -> bool:
        """運行Git命令，帶超時和監控"""
        try:
            print(f"🔧 執行: {' '.join(command)}")
            
            # 啟動進程
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            # 記錄進程信息
            process_info = {
                'pid': process.pid,
                'command': ' '.join(command),
                'start_time': time.time(),
                'status': 'running'
            }
            self.active_processes[process.pid] = process_info
            
            try:
                # 等待完成，帶超時
                stdout, stderr = process.communicate(timeout=timeout)
                
                # 更新進程狀態
                process_info['status'] = 'completed'
                process_info['end_time'] = time.time()
                process_info['return_code'] = process.returncode
                process_info['stdout'] = stdout
                process_info['stderr'] = stderr
                
                # 移除活動進程記錄
                self.active_processes.pop(process.pid, None)
                
                # 添加到歷史
                self.push_history.append(process_info.copy())
                
                if process.returncode == 0:
                    print(f"✅ 命令成功: {' '.join(command)}")
                    return True
                else:
                    print(f"❌ 命令失敗: {' '.join(command)}")
                    print(f"錯誤輸出: {stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ 命令超時: {' '.join(command)}")
                
                # 終止進程
                self._kill_process(process.pid)
                
                # 更新狀態
                process_info['status'] = 'timeout'
                process_info['end_time'] = time.time()
                self.active_processes.pop(process.pid, None)
                self.push_history.append(process_info.copy())
                
                return False
                
        except Exception as e:
            print(f"❌ 執行命令出錯: {e}")
            return False
            
    def get_status(self) -> Dict:
        """獲取推送系統狀態"""
        return {
            'monitoring': self.monitoring,
            'active_processes': len(self.active_processes),
            'total_pushes': len(self.push_history),
            'recent_pushes': self.push_history[-5:] if self.push_history else [],
            'active_process_details': list(self.active_processes.values())
        }
        
    def emergency_push(self, message: str = None) -> bool:
        """緊急推送（清理所有卡死進程後推送）"""
        print("🚨 執行緊急推送...")
        
        # 清理卡死進程
        self.clean_stuck_processes()
        
        # 等待清理完成
        time.sleep(2)
        
        # 執行推送
        if not message:
            message = f"Emergency push at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        return self.push_with_retry(message)

# 全局實例
smart_push_system = SmartPushSystem()

def emergency_push(message: str = None) -> bool:
    """便捷函數：緊急推送"""
    return smart_push_system.emergency_push(message)

def push_with_retry(commit_message: str = None, branch: str = "main") -> bool:
    """便捷函數：帶重試的推送"""
    return smart_push_system.push_with_retry(commit_message, branch)

def clean_stuck_processes():
    """便捷函數：清理卡死進程"""
    return smart_push_system.clean_stuck_processes()

def get_push_status() -> Dict:
    """便捷函數：獲取狀態"""
    return smart_push_system.get_status()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 smart_push_system.py emergency")
        print("  python3 smart_push_system.py push [message]")
        print("  python3 smart_push_system.py clean")
        print("  python3 smart_push_system.py status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "emergency":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        emergency_push(message)
    elif command == "push":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        push_with_retry(message)
    elif command == "clean":
        clean_stuck_processes()
    elif command == "status":
        status = get_push_status()
        print("📊 推送系統狀態:")
        print(f"  監控中: {status['monitoring']}")
        print(f"  活動進程: {status['active_processes']}")
        print(f"  總推送次數: {status['total_pushes']}")
        if status['recent_pushes']:
            print("  最近推送:")
            for push in status['recent_pushes']:
                print(f"    {push['command']} - {push['status']}")
    else:
        print("❌ 未知命令")

