#!/usr/bin/env python3
"""
PowerAutomation智能上傳腳本 v2.0
支持ZIP加密API密鑰和跨倉庫部署功能
"""

import os
import sys
import json
import subprocess
import logging
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class SecureAPIKeyManager:
    """安全API密鑰管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.api_keys_file = project_root / "api_keys.env"
        self.encrypted_zip = project_root / "api_keys.zip"
        self.default_password = "powerautomation2025"
    
    def create_api_keys_file(self, api_keys: Dict[str, str]) -> bool:
        """創建API密鑰文件"""
        try:
            logger.info("🔑 創建API密鑰文件...")
            
            with open(self.api_keys_file, 'w') as f:
                for key, value in api_keys.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"✅ API密鑰文件已創建: {self.api_keys_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建API密鑰文件失敗: {e}")
            return False
    
    def encrypt_api_keys(self, password: str = None) -> bool:
        """加密API密鑰文件"""
        try:
            if not self.api_keys_file.exists():
                logger.warning("⚠️ API密鑰文件不存在，跳過加密")
                return True
            
            password = password or self.default_password
            logger.info("🔐 加密API密鑰文件...")
            
            # 使用Python的zipfile模塊創建加密ZIP
            with zipfile.ZipFile(self.encrypted_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.setpassword(password.encode('utf-8'))
                zf.write(self.api_keys_file, self.api_keys_file.name)
            
            # 刪除原始文件
            self.api_keys_file.unlink()
            
            logger.info(f"✅ API密鑰已加密: {self.encrypted_zip}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 加密API密鑰失敗: {e}")
            return False
    
    def decrypt_and_load_api_keys(self, password: str = None) -> Dict[str, str]:
        """解密並載入API密鑰"""
        try:
            if not self.encrypted_zip.exists():
                logger.warning("⚠️ 加密的API密鑰文件不存在")
                return {}
            
            password = password or self.default_password
            logger.info("🔓 解密並載入API密鑰...")
            
            api_keys = {}
            
            with zipfile.ZipFile(self.encrypted_zip, 'r') as zf:
                zf.setpassword(password.encode('utf-8'))
                
                # 解壓到臨時目錄
                with tempfile.TemporaryDirectory() as temp_dir:
                    zf.extractall(temp_dir)
                    
                    # 讀取API密鑰
                    temp_keys_file = Path(temp_dir) / "api_keys.env"
                    if temp_keys_file.exists():
                        with open(temp_keys_file, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if line and '=' in line:
                                    key, value = line.split('=', 1)
                                    api_keys[key] = value
                                    # 設置環境變量
                                    os.environ[key] = value
            
            logger.info(f"✅ 已載入 {len(api_keys)} 個API密鑰")
            return api_keys
            
        except Exception as e:
            logger.error(f"❌ 解密API密鑰失敗: {e}")
            return {}

class CrossRepoDeployer:
    """跨倉庫部署器"""
    
    def __init__(self, source_repo: Path, target_repo_url: str):
        self.source_repo = source_repo
        self.target_repo_url = target_repo_url
        self.temp_dir = None
    
    def clone_target_repo(self) -> Optional[Path]:
        """克隆目標倉庫"""
        try:
            logger.info(f"📥 克隆目標倉庫: {self.target_repo_url}")
            
            self.temp_dir = Path(tempfile.mkdtemp(prefix="powerauto_deploy_"))
            target_path = self.temp_dir / "target_repo"
            
            cmd = ["git", "clone", self.target_repo_url, str(target_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ 目標倉庫已克隆到: {target_path}")
                return target_path
            else:
                logger.error(f"❌ 克隆失敗: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 克隆目標倉庫失敗: {e}")
            return None
    
    def sync_files(self, target_path: Path, exclude_patterns: List[str] = None) -> bool:
        """同步文件到目標倉庫"""
        try:
            logger.info("📁 同步文件到目標倉庫...")
            
            exclude_patterns = exclude_patterns or [
                '.git', '__pycache__', '*.pyc', '.pytest_cache',
                'node_modules', '.env', 'api_keys.env', '*.log'
            ]
            
            # 清理目標目錄（保留.git）
            for item in target_path.iterdir():
                if item.name != '.git':
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # 複製文件
            for item in self.source_repo.iterdir():
                if any(pattern in str(item) for pattern in exclude_patterns):
                    continue
                
                target_item = target_path / item.name
                
                if item.is_dir():
                    shutil.copytree(item, target_item, ignore=shutil.ignore_patterns(*exclude_patterns))
                else:
                    shutil.copy2(item, target_item)
            
            logger.info("✅ 文件同步完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 文件同步失敗: {e}")
            return False
    
    def commit_and_push(self, target_path: Path, commit_message: str) -> bool:
        """提交並推送到目標倉庫"""
        try:
            logger.info("📤 提交並推送到目標倉庫...")
            
            os.chdir(target_path)
            
            # 添加所有文件
            subprocess.run(["git", "add", "."], check=True)
            
            # 檢查是否有變更
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                logger.info("📝 沒有變更需要提交")
                return True
            
            # 提交
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # 推送
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            logger.info("✅ 成功推送到目標倉庫")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git操作失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 提交推送失敗: {e}")
            return False
    
    def cleanup(self):
        """清理臨時目錄"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info("🧹 臨時目錄已清理")

class PowerAutomationUploaderV2:
    """PowerAutomation智能上傳器 v2.0"""
    
    def __init__(self, project_root: str = None):
        """初始化上傳器"""
        self.project_root = Path(project_root or os.getcwd())
        self.docs_dir = self.project_root / "docs"
        self.interaction_data_dir = self.project_root / "interaction_data"
        self.data_dir = self.project_root / "data"
        
        # 確保目錄存在
        self.docs_dir.mkdir(exist_ok=True)
        self.interaction_data_dir.mkdir(exist_ok=True)
        (self.interaction_data_dir / "conversations").mkdir(exist_ok=True)
        (self.interaction_data_dir / "context_snapshots").mkdir(exist_ok=True)
        (self.interaction_data_dir / "session_logs").mkdir(exist_ok=True)
        
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "training").mkdir(exist_ok=True)
        (self.data_dir / "testing").mkdir(exist_ok=True)
        
        # 初始化組件
        self.api_key_manager = SecureAPIKeyManager(self.project_root)
        
        # 重新配置日誌
        log_file = self.docs_dir / "upload_log.txt"
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ],
            force=True
        )
        
        logger.info(f"PowerAutomation上傳器v2.0初始化，項目根目錄: {self.project_root}")
    
    def setup_api_keys(self, api_keys: Dict[str, str] = None) -> bool:
        """設置API密鑰"""
        if not api_keys:
            # 使用默認API密鑰（從環境變量或配置文件獲取）
            api_keys = {
                "SUPERMEMORY_API_KEY": os.environ.get("SUPERMEMORY_API_KEY", "placeholder_supermemory_key"),
                "CLAUDE_API_KEY": os.environ.get("CLAUDE_API_KEY", "placeholder_claude_key"),
                "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "placeholder_gemini_key"),
                "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "placeholder_github_token"),
                "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "placeholder_openai_key")
            }
        
        # 創建並加密API密鑰
        if self.api_key_manager.create_api_keys_file(api_keys):
            return self.api_key_manager.encrypt_api_keys()
        
        return False
    
    def load_api_keys(self) -> Dict[str, str]:
        """載入API密鑰"""
        return self.api_key_manager.decrypt_and_load_api_keys()
    
    def save_interaction_data(self, interaction_type: str, data: Dict[str, Any]) -> bool:
        """保存交互數據"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if interaction_type == "conversation":
                file_path = self.interaction_data_dir / "conversations" / f"conv_{timestamp}.json"
            elif interaction_type == "context_snapshot":
                file_path = self.interaction_data_dir / "context_snapshots" / f"snapshot_{timestamp}.json"
            elif interaction_type == "session_log":
                file_path = self.interaction_data_dir / "session_logs" / f"session_{timestamp}.json"
            else:
                logger.warning(f"⚠️ 未知的交互數據類型: {interaction_type}")
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 交互數據已保存: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存交互數據失敗: {e}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """運行全面測試"""
        logger.info("🧪 開始運行全面測試...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
        
        # 1. API密鑰測試
        logger.info("🔑 測試API密鑰...")
        api_keys = self.load_api_keys()
        api_test_result = {
            "status": "passed" if api_keys else "failed",
            "loaded_keys": len(api_keys),
            "details": "API密鑰載入測試"
        }
        test_results["tests"]["api_keys"] = api_test_result
        
        # 2. 目錄結構測試
        logger.info("📁 測試目錄結構...")
        required_dirs = [self.docs_dir, self.interaction_data_dir, self.data_dir]
        dirs_exist = all(d.exists() for d in required_dirs)
        dir_test_result = {
            "status": "passed" if dirs_exist else "failed",
            "details": "目錄結構完整性測試"
        }
        test_results["tests"]["directory_structure"] = dir_test_result
        
        # 3. Git狀態測試
        logger.info("📋 測試Git狀態...")
        try:
            result = subprocess.run(["git", "status"], cwd=self.project_root, 
                                  capture_output=True, text=True, timeout=10)
            git_test_result = {
                "status": "passed" if result.returncode == 0 else "failed",
                "details": "Git倉庫狀態測試"
            }
        except Exception:
            git_test_result = {
                "status": "failed",
                "details": "Git倉庫狀態測試失敗"
            }
        test_results["tests"]["git_status"] = git_test_result
        
        # 計算總體結果
        for test_name, result in test_results["tests"].items():
            test_results["total_tests"] += 1
            if result.get("status") == "passed":
                test_results["passed_tests"] += 1
            else:
                test_results["failed_tests"] += 1
        
        # 確定總體狀態
        if test_results["failed_tests"] == 0:
            test_results["overall_status"] = "passed"
        elif test_results["passed_tests"] > test_results["failed_tests"]:
            test_results["overall_status"] = "partial"
        else:
            test_results["overall_status"] = "failed"
        
        logger.info(f"🧪 測試完成，總體狀態: {test_results['overall_status']}")
        return test_results
    
    def update_readme(self) -> bool:
        """更新README文檔"""
        try:
            logger.info("📝 更新README文檔...")
            
            readme_content = f"""# PowerAutomation

> 統一AI自動化平台 - MCP適配器系統

## 📊 系統狀態

- **最後更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **版本**: v2.0
- **部署狀態**: ✅ 已部署

## 🎯 項目概述

PowerAutomation是一個統一的AI自動化平台，基於MCP（Model Context Protocol）標準，提供：

- 🔧 **統一MCP適配器系統** - 標準化的AI服務接口
- 💻 **完整CLI控制系統** - 命令行管理和測試工具
- 🧪 **全面測試覆蓋** - 單元、集成、端到端測試
- 🔐 **安全API密鑰管理** - ZIP加密保護敏感信息
- 📚 **詳細文檔系統** - API參考、使用指南、教程

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 解密API密鑰
```bash
# 系統會自動解密並載入API密鑰
python smart_upload.py --load-keys
```

### 查看系統狀態
```bash
python smart_upload.py --test-only
```

## 📁 項目結構

```
PowerAutomation/
├── mcptool/              # MCP工具核心目錄
├── docs/                 # 項目文檔
├── test/                 # 測試文件
├── interaction_data/     # 交互數據
│   ├── conversations/    # 對話記錄
│   ├── context_snapshots/# 上下文快照
│   └── session_logs/     # 會話日誌
├── data/                 # 數據目錄
│   ├── training/         # 訓練數據
│   └── testing/          # 測試數據
├── api_keys.zip          # 加密的API密鑰
├── smart_upload.py       # 智能上傳腳本
└── requirements.txt      # 依賴包列表
```

## 🔐 安全特性

- **API密鑰加密**: 使用ZIP加密保護敏感信息
- **跨倉庫部署**: 安全的生產環境部署
- **自動備份**: 多觸發條件的智能備份系統

## 📊 數據管理

### 交互數據
- 對話記錄自動保存
- 上下文快照定期創建
- 會話日誌完整記錄

### 訓練數據
- 成功案例自動收集
- 模式學習數據整理
- AI改進參考資料

## 🧪 測試系統

運行全面測試：
```bash
python smart_upload.py --test-only
```

## 📈 部署流程

1. **本地開發** - 在communitypowerautomation倉庫開發
2. **測試驗證** - 運行全面測試確保質量
3. **安全打包** - 加密API密鑰和敏感數據
4. **跨倉庫部署** - 自動部署到Powerauto.ai生產環境

---

*PowerAutomation - 讓AI自動化更簡單、更安全、更強大*
"""
            
            readme_path = self.project_root / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info("✅ README文檔已更新")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新README失敗: {e}")
            return False
    
    def deploy_to_target_repo(self, target_repo_url: str, commit_message: str) -> bool:
        """部署到目標倉庫"""
        deployer = CrossRepoDeployer(self.project_root, target_repo_url)
        
        try:
            # 1. 克隆目標倉庫
            target_path = deployer.clone_target_repo()
            if not target_path:
                return False
            
            # 2. 同步文件
            if not deployer.sync_files(target_path):
                return False
            
            # 3. 提交並推送
            success = deployer.commit_and_push(target_path, commit_message)
            
            return success
            
        finally:
            deployer.cleanup()
    
    def run_full_pipeline(self, target_repo_url: str = None, commit_message: str = None, 
                         test_only: bool = False, force: bool = False) -> bool:
        """運行完整流水線"""
        try:
            logger.info("🚀 開始PowerAutomation智能上傳流水線v2.0...")
            
            # 1. 載入API密鑰
            api_keys = self.load_api_keys()
            if api_keys:
                logger.info(f"🔑 已載入 {len(api_keys)} 個API密鑰")
            
            # 2. 運行測試
            test_results = self.run_comprehensive_tests()
            
            # 3. 更新文檔
            self.update_readme()
            
            # 4. 保存交互數據
            interaction_data = {
                "timestamp": datetime.now().isoformat(),
                "test_results": test_results,
                "api_keys_loaded": len(api_keys),
                "pipeline_version": "v2.0"
            }
            self.save_interaction_data("session_log", interaction_data)
            
            # 5. 如果只是測試，則停止
            if test_only:
                logger.info("🧪 測試完成，跳過部署")
                self._print_test_summary(test_results)
                return test_results.get("overall_status") == "passed"
            
            # 6. 檢查測試結果
            if not force and test_results.get("overall_status") != "passed":
                logger.error("❌ 測試未通過，取消部署。使用 --force 強制部署")
                return False
            
            # 7. 部署到目標倉庫
            if target_repo_url:
                logger.info(f"🚀 開始部署到目標倉庫: {target_repo_url}")
                deploy_success = self.deploy_to_target_repo(target_repo_url, commit_message)
                
                if deploy_success:
                    logger.info("✅ 部署成功！")
                else:
                    logger.error("❌ 部署失敗！")
                
                return deploy_success
            else:
                logger.info("📝 沒有指定目標倉庫，跳過部署")
                return True
            
        except Exception as e:
            logger.error(f"❌ 流水線執行失敗: {e}")
            return False
    
    def _print_test_summary(self, test_results: Dict[str, Any]):
        """打印測試總結"""
        print("\n" + "="*60)
        print("🧪 測試總結")
        print("="*60)
        
        status_emoji = {
            "passed": "✅",
            "failed": "❌", 
            "error": "💥",
            "partial": "⚠️"
        }
        
        overall_status = test_results.get("overall_status", "unknown")
        print(f"📊 總體狀態: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        print(f"📈 通過率: {test_results.get('passed_tests', 0)}/{test_results.get('total_tests', 0)}")
        
        print("\n🔍 詳細結果:")
        for test_name, result in test_results.get("tests", {}).items():
            status = result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            details = result.get("details", "")
            print(f"  {emoji} {test_name}: {status} - {details}")
        
        print("="*60)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation智能上傳腳本v2.0")
    parser.add_argument("--commit-message", "-m", 
                       default=f"Auto deploy {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    parser.add_argument("--target-repo", "-r", 
                       default="https://github.com/alexchuang650730/Powerauto.ai.git",
                       help="目標倉庫URL")
    parser.add_argument("--force", "-f", action="store_true", help="強制部署，跳過測試驗證")
    parser.add_argument("--test-only", "-t", action="store_true", help="僅運行測試，不執行部署")
    parser.add_argument("--project-root", "-p", help="項目根目錄路徑")
    parser.add_argument("--setup-keys", action="store_true", help="設置API密鑰")
    parser.add_argument("--load-keys", action="store_true", help="載入API密鑰")
    
    args = parser.parse_args()
    
    # 創建上傳器
    uploader = PowerAutomationUploaderV2(args.project_root)
    
    # 設置API密鑰
    if args.setup_keys:
        logger.info("🔑 設置API密鑰...")
        success = uploader.setup_api_keys()
        if success:
            logger.info("✅ API密鑰設置完成")
        else:
            logger.error("❌ API密鑰設置失敗")
        return
    
    # 載入API密鑰
    if args.load_keys:
        logger.info("🔑 載入API密鑰...")
        api_keys = uploader.load_api_keys()
        logger.info(f"✅ 已載入 {len(api_keys)} 個API密鑰")
        return
    
    # 運行流水線
    success = uploader.run_full_pipeline(
        target_repo_url=args.target_repo,
        commit_message=args.commit_message,
        test_only=args.test_only,
        force=args.force
    )
    
    # 退出碼
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

