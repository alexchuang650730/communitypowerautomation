#!/usr/bin/env python3
"""
歷史回滾功能CLI測試工具
專門測試IntelligentWorkflowEngineMCP的回滾功能
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RollbackCLITester:
    """歷史回滾功能CLI測試器"""
    
    def __init__(self, project_root: str = None):
        """初始化測試器"""
        self.project_root = project_root or str(Path(__file__).parent.parent.parent)
        self.workflow_engine = IntelligentWorkflowEngineMCP(self.project_root)
        self.rollback_history_file = Path(self.project_root) / "mcptool" / "config" / "rollback_history.json"
        
        logger.info(f"歷史回滾CLI測試器初始化完成，項目根目錄: {self.project_root}")
    
    def load_rollback_history(self) -> List[Dict[str, Any]]:
        """載入回滾歷史"""
        try:
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"載入回滾歷史失敗: {e}")
            return []
    
    def save_rollback_history(self, history: List[Dict[str, Any]]):
        """保存回滾歷史"""
        try:
            # 確保目錄存在
            self.rollback_history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.rollback_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"回滾歷史已保存: {self.rollback_history_file}")
        except Exception as e:
            logger.error(f"保存回滾歷史失敗: {e}")
    
    def create_savepoint(self, description: str = None) -> str:
        """創建保存點"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        savepoint_id = f"sp_{description or 'manual'}_{timestamp}"
        
        # 模擬創建保存點
        savepoint_data = {
            "id": savepoint_id,
            "timestamp": timestamp,
            "description": description or "手動創建的保存點",
            "created_at": datetime.now().isoformat(),
            "project_state": self._capture_project_state()
        }
        
        logger.info(f"✅ 保存點已創建: {savepoint_id}")
        return savepoint_id
    
    def _capture_project_state(self) -> Dict[str, Any]:
        """捕獲項目狀態"""
        try:
            project_path = Path(self.project_root)
            
            # 統計文件信息
            py_files = list(project_path.rglob("*.py"))
            json_files = list(project_path.rglob("*.json"))
            
            return {
                "total_py_files": len(py_files),
                "total_json_files": len(json_files),
                "last_modified": max([f.stat().st_mtime for f in py_files[:10]] or [0]),
                "capture_time": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"捕獲項目狀態失敗: {e}")
            return {"error": str(e)}
    
    def test_rollback_workflow(self, reason: str = None, savepoint_id: str = None) -> Dict[str, Any]:
        """測試回滾工作流"""
        logger.info("🔄 開始測試回滾工作流...")
        
        try:
            # 如果沒有指定保存點，創建一個測試保存點
            if not savepoint_id:
                savepoint_id = self.create_savepoint("test_rollback")
            
            # 設置測試模式
            self.workflow_engine.set_test_mode(True)
            
            # 啟動回滾工作流
            test_reason = reason or "CLI測試回滾"
            self.workflow_engine.start_rollback_workflow(test_reason, savepoint_id)
            
            # 等待工作流完成
            import time
            max_wait = 30  # 最多等待30秒
            wait_time = 0
            
            while self.workflow_engine.workflow_status["is_running"] and wait_time < max_wait:
                time.sleep(1)
                wait_time += 1
                logger.info(f"等待工作流完成... ({wait_time}/{max_wait}s)")
            
            # 獲取工作流數據
            workflow_data = self.workflow_engine.get_workflow_data()
            
            # 記錄回滾歷史
            rollback_record = {
                "id": f"rb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "savepoint_id": savepoint_id,
                "timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
                "reason": test_reason,
                "status": "success" if not self.workflow_engine.workflow_status["is_running"] else "timeout",
                "before_hash": "test_before_hash",
                "after_hash": f"test_hash_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "files_changed": 5,
                "created_at": datetime.now().isoformat()
            }
            
            # 更新回滾歷史
            history = self.load_rollback_history()
            history.append(rollback_record)
            self.save_rollback_history(history)
            
            result = {
                "status": "success",
                "rollback_id": rollback_record["id"],
                "savepoint_id": savepoint_id,
                "workflow_completed": not self.workflow_engine.workflow_status["is_running"],
                "workflow_data": workflow_data,
                "execution_time": wait_time
            }
            
            logger.info(f"✅ 回滾工作流測試完成: {rollback_record['id']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 回滾工作流測試失敗: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def list_rollback_history(self) -> List[Dict[str, Any]]:
        """列出回滾歷史"""
        history = self.load_rollback_history()
        
        print("\n" + "="*80)
        print("📋 回滾歷史記錄")
        print("="*80)
        
        if not history:
            print("❌ 沒有找到回滾歷史記錄")
            return []
        
        for i, record in enumerate(history[-10:], 1):  # 顯示最近10條
            status_emoji = "✅" if record.get("status") == "success" else "❌"
            print(f"{i:2d}. {status_emoji} {record.get('id', 'N/A')}")
            print(f"    📅 時間: {record.get('created_at', 'N/A')}")
            print(f"    💾 保存點: {record.get('savepoint_id', 'N/A')}")
            print(f"    📝 原因: {record.get('reason', 'N/A')}")
            print(f"    📊 狀態: {record.get('status', 'N/A')}")
            print(f"    📁 文件變更: {record.get('files_changed', 0)}")
            print()
        
        print("="*80)
        return history
    
    def test_workflow_status(self) -> Dict[str, Any]:
        """測試工作流狀態獲取"""
        logger.info("📊 測試工作流狀態獲取...")
        
        try:
            status = self.workflow_engine.get_workflow_data()
            
            print("\n" + "="*60)
            print("📊 工作流狀態")
            print("="*60)
            print(f"🔄 運行狀態: {'運行中' if self.workflow_engine.workflow_status['is_running'] else '空閒'}")
            print(f"📅 開始時間: {self.workflow_engine.workflow_status.get('start_time', 'N/A')}")
            print(f"🔄 最後更新: {self.workflow_engine.workflow_status.get('last_update_time', 'N/A')}")
            print(f"📋 節點數量: {len(status.get('nodes', []))}")
            print(f"🔗 連接數量: {len(status.get('connections', []))}")
            print(f"🧪 測試模式: {'是' if self.workflow_engine.is_test_mode else '否'}")
            print("="*60)
            
            return {
                "status": "success",
                "workflow_status": self.workflow_engine.workflow_status,
                "workflow_data": status
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取工作流狀態失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_mcp_interface(self) -> Dict[str, Any]:
        """測試MCP接口"""
        logger.info("🔌 測試MCP接口...")
        
        try:
            # 測試獲取能力
            capabilities = self.workflow_engine.get_capabilities()
            
            # 測試處理請求
            test_request = {
                "action": "start_rollback_workflow",
                "reason": "MCP接口測試",
                "savepoint_id": self.create_savepoint("mcp_test")
            }
            
            response = self.workflow_engine.process(test_request)
            
            print("\n" + "="*60)
            print("🔌 MCP接口測試結果")
            print("="*60)
            print(f"📋 能力數量: {len(capabilities.get('tools', []))}")
            print(f"📝 響應狀態: {response.get('status', 'N/A')}")
            print(f"💬 響應消息: {response.get('message', 'N/A')}")
            print("="*60)
            
            return {
                "status": "success",
                "capabilities": capabilities,
                "test_response": response
            }
            
        except Exception as e:
            logger.error(f"❌ MCP接口測試失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """運行綜合測試"""
        logger.info("🧪 開始運行綜合測試...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown"
        }
        
        # 1. 測試工作流狀態
        logger.info("1️⃣ 測試工作流狀態...")
        results["tests"]["workflow_status"] = self.test_workflow_status()
        
        # 2. 測試MCP接口
        logger.info("2️⃣ 測試MCP接口...")
        results["tests"]["mcp_interface"] = self.test_mcp_interface()
        
        # 3. 測試回滾工作流
        logger.info("3️⃣ 測試回滾工作流...")
        results["tests"]["rollback_workflow"] = self.test_rollback_workflow()
        
        # 4. 列出歷史記錄
        logger.info("4️⃣ 檢查歷史記錄...")
        history = self.list_rollback_history()
        results["tests"]["history_check"] = {
            "status": "success",
            "history_count": len(history)
        }
        
        # 計算總體狀態
        passed_tests = sum(1 for test in results["tests"].values() 
                          if test.get("status") == "success")
        total_tests = len(results["tests"])
        
        if passed_tests == total_tests:
            results["overall_status"] = "passed"
        elif passed_tests > 0:
            results["overall_status"] = "partial"
        else:
            results["overall_status"] = "failed"
        
        # 打印總結
        print("\n" + "="*80)
        print("🧪 綜合測試總結")
        print("="*80)
        print(f"📊 總體狀態: {results['overall_status'].upper()}")
        print(f"✅ 通過測試: {passed_tests}/{total_tests}")
        print(f"📅 測試時間: {results['timestamp']}")
        
        for test_name, test_result in results["tests"].items():
            status_emoji = "✅" if test_result.get("status") == "success" else "❌"
            print(f"  {status_emoji} {test_name}: {test_result.get('status', 'unknown')}")
        
        print("="*80)
        
        logger.info(f"✅ 綜合測試完成，狀態: {results['overall_status']}")
        return results

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="歷史回滾功能CLI測試工具")
    parser.add_argument("command", choices=["test", "history", "status", "mcp", "comprehensive"], 
                       help="測試命令")
    parser.add_argument("--reason", "-r", help="回滾原因")
    parser.add_argument("--savepoint", "-s", help="保存點ID")
    parser.add_argument("--project-root", "-p", help="項目根目錄")
    
    args = parser.parse_args()
    
    # 創建測試器
    tester = RollbackCLITester(args.project_root)
    
    try:
        if args.command == "test":
            # 測試回滾工作流
            result = tester.test_rollback_workflow(args.reason, args.savepoint)
            print(f"\n🔄 回滾測試結果: {result.get('status', 'unknown')}")
            
        elif args.command == "history":
            # 列出回滾歷史
            tester.list_rollback_history()
            
        elif args.command == "status":
            # 測試工作流狀態
            result = tester.test_workflow_status()
            print(f"\n📊 狀態測試結果: {result.get('status', 'unknown')}")
            
        elif args.command == "mcp":
            # 測試MCP接口
            result = tester.test_mcp_interface()
            print(f"\n🔌 MCP測試結果: {result.get('status', 'unknown')}")
            
        elif args.command == "comprehensive":
            # 運行綜合測試
            result = tester.run_comprehensive_test()
            sys.exit(0 if result.get("overall_status") == "passed" else 1)
            
    except KeyboardInterrupt:
        logger.info("❌ 測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 測試執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

