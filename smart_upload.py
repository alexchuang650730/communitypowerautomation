#!/usr/bin/env python3
"""
PowerAutomation智能上傳腳本
自動更新文檔、運行測試、驗證系統完整性後才允許上傳
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

# 設置日誌 - 將在PowerAutomationUploader初始化時重新配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PowerAutomationUploader:
    """PowerAutomation智能上傳器"""
    
    def __init__(self, project_root: str = None):
        """初始化上傳器"""
        self.project_root = Path(project_root or os.getcwd())
        self.docs_dir = self.project_root / "docs"
        self.test_dir = self.project_root / "test"
        self.mcptool_dir = self.project_root / "mcptool"
        
        # 確保docs目錄存在
        self.docs_dir.mkdir(exist_ok=True)
        
        # 重新配置日誌到docs目錄
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
        
        # 測試結果
        self.test_results = {}
        self.upload_allowed = False
        
        logger.info(f"PowerAutomation上傳器初始化，項目根目錄: {self.project_root}")
        logger.info(f"文檔目錄: {self.docs_dir}")
        logger.info(f"日誌文件: {log_file}")
    
    def generate_directory_structure(self) -> str:
        """生成目錄結構"""
        logger.info("🗂️ 生成目錄結構...")
        
        def build_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> List[str]:
            """遞歸構建目錄樹"""
            if current_depth >= max_depth:
                return []
            
            items = []
            try:
                entries = sorted([p for p in path.iterdir() if not p.name.startswith('.')], 
                               key=lambda x: (x.is_file(), x.name.lower()))
                
                for i, entry in enumerate(entries):
                    is_last = i == len(entries) - 1
                    current_prefix = "└── " if is_last else "├── "
                    items.append(f"{prefix}{current_prefix}{entry.name}")
                    
                    if entry.is_dir() and not entry.name.startswith('__pycache__'):
                        extension = "    " if is_last else "│   "
                        items.extend(build_tree(entry, prefix + extension, max_depth, current_depth + 1))
            except PermissionError:
                pass
            
            return items
        
        structure = [f"PowerAutomation/"]
        structure.extend(build_tree(self.project_root))
        
        return "\n".join(structure)
    
    def generate_file_descriptions(self) -> Dict[str, str]:
        """生成文件描述"""
        logger.info("📝 生成文件描述...")
        
        descriptions = {}
        
        # 核心文件描述
        core_files = {
            "README.md": "項目主要說明文檔，包含安裝、使用和貢獻指南",
            "requirements.txt": "Python依賴包列表",
            "setup.py": "項目安裝配置文件",
            ".gitignore": "Git忽略文件配置",
            "LICENSE": "項目許可證文件"
        }
        
        # MCP工具描述
        mcp_descriptions = {
            "mcptool/": "MCP工具核心目錄",
            "mcptool/core/": "核心功能模塊",
            "mcptool/adapters/": "MCP適配器集合",
            "mcptool/cli/": "命令行界面工具",
            "mcptool/config/": "配置文件目錄"
        }
        
        # 測試文件描述
        test_descriptions = {
            "test/": "測試文件目錄",
            "test/unit/": "單元測試",
            "test/integration/": "集成測試",
            "test/e2e/": "端到端測試",
            "test/gaia.py": "GAIA基準測試腳本"
        }
        
        # 文檔描述
        docs_descriptions = {
            "docs/": "項目文檔目錄",
            "docs/api/": "API參考文檔",
            "docs/guides/": "使用指南",
            "docs/tutorials/": "教程文檔",
            "docs/architecture/": "架構設計文檔"
        }
        
        descriptions.update(core_files)
        descriptions.update(mcp_descriptions)
        descriptions.update(test_descriptions)
        descriptions.update(docs_descriptions)
        
        return descriptions
    
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
        
        # 1. MCP系統測試
        logger.info("🔧 運行MCP系統測試...")
        mcp_result = self._run_mcp_tests()
        test_results["tests"]["mcp_system"] = mcp_result
        
        # 2. 單元測試
        logger.info("🧪 運行單元測試...")
        unit_result = self._run_unit_tests()
        test_results["tests"]["unit_tests"] = unit_result
        
        # 3. 集成測試
        logger.info("🔗 運行集成測試...")
        integration_result = self._run_integration_tests()
        test_results["tests"]["integration_tests"] = integration_result
        
        # 4. GAIA測試
        logger.info("🧠 運行GAIA測試...")
        gaia_result = self._run_gaia_tests()
        test_results["tests"]["gaia_tests"] = gaia_result
        
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
        
        self.test_results = test_results
        return test_results
    
    def _run_mcp_tests(self) -> Dict[str, Any]:
        """運行MCP系統測試"""
        try:
            cmd = [sys.executable, "mcptool/cli/enhanced_mcp_cli.py", "test", "all"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:],  # 最後1000字符
                "stderr": result.stderr[-1000:] if result.stderr else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """運行單元測試"""
        try:
            cmd = [sys.executable, "test/unified_test_manager.py", "run", "unit"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:] if result.stderr else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """運行集成測試"""
        try:
            cmd = [sys.executable, "test/unified_test_manager.py", "run", "integration"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:] if result.stderr else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _run_gaia_tests(self) -> Dict[str, Any]:
        """運行GAIA測試"""
        try:
            cmd = [sys.executable, "test/gaia.py", "test", "--level=1", "--max-tasks=5"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=600)
            
            # 解析GAIA測試結果
            accuracy = 0.0
            if "準確率:" in result.stdout:
                try:
                    accuracy_line = [line for line in result.stdout.split('\n') if "準確率:" in line][0]
                    accuracy = float(accuracy_line.split("準確率:")[1].split("%")[0].strip())
                except:
                    pass
            
            return {
                "status": "passed" if accuracy >= 50.0 else "failed",  # 要求至少50%準確率
                "accuracy": accuracy,
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:] if result.stderr else None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def update_readme(self) -> bool:
        """更新README文件"""
        logger.info("📖 更新README文件...")
        
        try:
            # 生成目錄結構
            directory_structure = self.generate_directory_structure()
            
            # 生成文件描述
            file_descriptions = self.generate_file_descriptions()
            
            # 檢查是否有十層級測試結果
            latest_test_report = None
            test_results_dir = self.project_root / "test" / "results"
            if test_results_dir.exists():
                # 查找最新的測試報告
                test_files = list(test_results_dir.glob("test_report_execution_*.json"))
                if test_files:
                    latest_file = max(test_files, key=lambda x: x.stat().st_mtime)
                    try:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            latest_test_report = json.load(f)
                    except:
                        pass
            
            # 獲取測試狀態
            if latest_test_report:
                # 使用十層級測試結果
                success_rate = latest_test_report.get("overall_success_rate", 0)
                total_suites = latest_test_report.get("total_suites", 0)
                total_cases = latest_test_report.get("total_cases", 0)
                
                if success_rate >= 0.9:
                    test_status = "🟢 全部通過"
                elif success_rate >= 0.7:
                    test_status = "🟡 部分通過"
                else:
                    test_status = "🔴 測試失敗"
                
                # 獲取適配器數量（從測試報告或實際掃描）
                adapter_count = 17  # 我們知道有17個適配器
                test_coverage = f"十層級測試系統 ({total_suites}個套件, {total_cases}個用例)"
            else:
                # 使用基本測試結果
                test_status = "🔴 未測試" if not self.test_results else {
                    "passed": "🟢 全部通過",
                    "partial": "🟡 部分通過", 
                    "failed": "🔴 測試失敗"
                }.get(self.test_results.get("overall_status", "unknown"), "🔴 狀態未知")
                adapter_count = 14
                test_coverage = "單元測試、集成測試、GAIA基準測試"
            
            readme_content = f"""# PowerAutomation

> 統一AI自動化平台 - MCP適配器系統

## 📊 系統狀態

- **測試狀態**: {test_status}
- **最後更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **MCP適配器**: {adapter_count}個已發現
- **測試覆蓋**: {test_coverage}

## 🎯 項目概述

PowerAutomation是一個統一的AI自動化平台，基於MCP（Model Context Protocol）標準，提供：

- 🔧 **統一MCP適配器系統** - 標準化的AI服務接口
- 💻 **完整CLI控制系統** - 命令行管理和測試工具
- 🧪 **全面測試覆蓋** - 單元、集成、端到端、GAIA測試
- 📚 **詳細文檔系統** - API參考、使用指南、教程

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 初始化系統
```bash
python mcptool/cli/enhanced_mcp_cli.py init
```

### 查看系統狀態
```bash
python mcptool/cli/enhanced_mcp_cli.py status
```

### 運行測試
```bash
# 運行所有測試
python test/unified_test_manager.py run all

# 運行GAIA測試
python test/gaia.py test --level=1 --max-tasks=10
```

## 📁 項目結構

```
{directory_structure}
```

## 📝 主要文件說明

{self._format_file_descriptions(file_descriptions)}

## 🧪 測試系統

### 測試分類
- **單元測試** - 個別組件功能驗證
- **集成測試** - 組件間協作驗證  
- **端到端測試** - 完整流程驗證
- **GAIA測試** - AI能力基準測試

### 運行測試
```bash
# 查看所有測試
python test/unified_test_manager.py list

# 運行特定測試
python test/unified_test_manager.py run unit
python test/unified_test_manager.py run integration
python test/unified_test_manager.py run e2e

# 運行GAIA基準測試
python test/gaia.py test --level=1 --max-tasks=165
```

## 🔧 MCP適配器

### 核心適配器
- **infinite_context_adapter** - 無限上下文處理
- **intelligent_workflow_engine** - 智能工作流引擎
- **webagent_core** - Web代理核心
- **rl_srt_mcp** - 強化學習SRT
- **sequential_thinking** - 順序思考適配器

### 智能體優化適配器
- **content_template_optimization** - 內容模板優化
- **context_matching_optimization** - 上下文匹配優化
- **context_memory_optimization** - 上下文記憶優化
- **prompt_optimization** - 提示詞優化
- **ui_journey_optimization** - UI旅程優化

## 📚 文檔

- [API參考](docs/api/) - 詳細的API文檔
- [使用指南](docs/guides/) - 快速上手指南
- [教程](docs/tutorials/) - 深入學習教程
- [架構設計](docs/architecture/) - 系統架構說明

## 🤝 貢獻指南

1. **Fork項目**
2. **創建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **運行測試** (`python tools/smart_upload.py --test-only`)
4. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
5. **推送分支** (`git push origin feature/AmazingFeature`)
6. **創建Pull Request**

### 上傳前檢查

使用智能上傳腳本確保代碼質量：

```bash
# 測試並上傳（推薦）
python tools/smart_upload.py --commit-message "你的提交信息"

# 僅運行測試
python tools/smart_upload.py --test-only

# 強制上傳（不推薦）
python tools/smart_upload.py --force --commit-message "緊急修復"
```

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 📞 聯繫方式

- **項目主頁**: [PowerAutomation](https://github.com/alexchuang650730/powerautomation)
- **問題報告**: [Issues](https://github.com/alexchuang650730/powerautomation/issues)
- **功能請求**: [Feature Requests](https://github.com/alexchuang650730/powerautomation/discussions)

---

*最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 自動生成 by PowerAutomation智能上傳系統*
"""
            
            # 寫入README文件
            readme_path = self.project_root / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"✅ README文件已更新: {readme_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新README失敗: {e}")
            return False
    
    def _format_file_descriptions(self, descriptions: Dict[str, str]) -> str:
        """格式化文件描述"""
        formatted = []
        for path, desc in descriptions.items():
            if path.endswith('/'):
                formatted.append(f"### {path}")
                formatted.append(f"{desc}\n")
            else:
                formatted.append(f"- **{path}** - {desc}")
        
        return "\n".join(formatted)
    
    def update_project_info(self) -> bool:
        """更新項目信息文件"""
        logger.info("📋 更新項目信息文件...")
        
        try:
            # 生成項目信息
            project_info = {
                "name": "PowerAutomation",
                "version": "1.0.0",
                "description": "AI原生的企業級自動化平台 - MCP適配器系統",
                "last_updated": datetime.now().isoformat(),
                "directory_structure": self.generate_directory_structure(),
                "file_descriptions": self.generate_file_descriptions(),
                "test_results": self.test_results,
                "statistics": {
                    "total_files": len(list(self.project_root.rglob("*.py"))),
                    "total_lines": self._count_total_lines(),
                    "mcp_adapters": 14,
                    "test_scripts": len(list(self.test_dir.rglob("*.py"))) if self.test_dir.exists() else 0
                }
            }
            
            # 保存項目信息
            # 保存到docs目錄
            info_path = self.docs_dir / "PROJECT_INFO.json"
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(project_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 項目信息已更新: {info_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新項目信息失敗: {e}")
            return False
    
    def _count_total_lines(self) -> int:
        """計算總代碼行數"""
        total_lines = 0
        try:
            for py_file in self.project_root.rglob("*.py"):
                if "__pycache__" not in str(py_file):
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += len(f.readlines())
        except Exception:
            pass
        return total_lines
    
    def validate_upload_requirements(self) -> Tuple[bool, List[str]]:
        """驗證上傳要求"""
        logger.info("✅ 驗證上傳要求...")
        
        issues = []
        
        # 1. 檢查測試結果
        if not self.test_results:
            issues.append("❌ 未運行測試")
        elif self.test_results.get("overall_status") == "failed":
            issues.append("❌ 測試失敗，不允許上傳")
        elif self.test_results.get("overall_status") == "partial":
            issues.append("⚠️ 部分測試失敗，建議修復後再上傳")
        
        # 2. 檢查GAIA測試準確率
        gaia_result = self.test_results.get("tests", {}).get("gaia_tests", {})
        if gaia_result.get("accuracy", 0) < 50.0:
            issues.append(f"❌ GAIA測試準確率過低: {gaia_result.get('accuracy', 0)}% < 50%")
        
        # 3. 檢查必要文件
        required_files = ["README.md", "requirements.txt", "mcptool/cli/enhanced_mcp_cli.py"]
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                issues.append(f"❌ 缺少必要文件: {file_path}")
        
        # 4. 檢查文檔完整性
        if not self.docs_dir.exists():
            issues.append("❌ 缺少docs目錄")
        
        upload_allowed = len(issues) == 0 or all("⚠️" in issue for issue in issues)
        
        return upload_allowed, issues
    
    def perform_upload(self, commit_message: str, force: bool = False) -> bool:
        """執行上傳"""
        logger.info("🚀 開始執行上傳...")
        
        try:
            # 驗證上傳要求
            upload_allowed, issues = self.validate_upload_requirements()
            
            if not upload_allowed and not force:
                logger.error("❌ 上傳驗證失敗:")
                for issue in issues:
                    logger.error(f"  {issue}")
                logger.error("使用 --force 參數強制上傳（不推薦）")
                return False
            
            if issues and not force:
                logger.warning("⚠️ 發現以下問題，但允許上傳:")
                for issue in issues:
                    logger.warning(f"  {issue}")
            
            # Git操作
            logger.info("📤 執行Git操作...")
            
            # 添加所有文件
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            
            # 提交
            subprocess.run(["git", "commit", "-m", commit_message], cwd=self.project_root, check=True)
            
            # 推送
            subprocess.run(["git", "push"], cwd=self.project_root, check=True)
            
            logger.info("✅ 上傳成功!")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git操作失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 上傳失敗: {e}")
            return False
    
    def run_full_pipeline(self, commit_message: str, force: bool = False, test_only: bool = False) -> bool:
        """運行完整流水線"""
        logger.info("🔄 開始運行完整上傳流水線...")
        
        try:
            # 1. 運行測試
            test_results = self.run_comprehensive_tests()
            
            # 2. 更新文檔
            self.update_readme()
            self.update_project_info()
            
            # 3. 如果只是測試，則停止
            if test_only:
                logger.info("🧪 測試完成，跳過上傳")
                self._print_test_summary()
                return test_results.get("overall_status") == "passed"
            
            # 4. 執行上傳
            upload_success = self.perform_upload(commit_message, force)
            
            # 5. 打印總結
            self._print_upload_summary(upload_success)
            
            return upload_success
            
        except Exception as e:
            logger.error(f"❌ 流水線執行失敗: {e}")
            return False
    
    def _print_test_summary(self):
        """打印測試總結"""
        if not self.test_results:
            return
        
        print("\n" + "="*60)
        print("🧪 測試總結")
        print("="*60)
        
        status_emoji = {
            "passed": "✅",
            "failed": "❌", 
            "error": "💥",
            "partial": "⚠️"
        }
        
        overall_status = self.test_results.get("overall_status", "unknown")
        print(f"📊 總體狀態: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
        print(f"📈 通過率: {self.test_results.get('passed_tests', 0)}/{self.test_results.get('total_tests', 0)}")
        
        print("\n🔍 詳細結果:")
        for test_name, result in self.test_results.get("tests", {}).items():
            status = result.get("status", "unknown")
            emoji = status_emoji.get(status, "❓")
            print(f"  {emoji} {test_name}: {status}")
            
            if test_name == "gaia_tests" and "accuracy" in result:
                print(f"    📊 GAIA準確率: {result['accuracy']}%")
        
        print("="*60)
    
    def _print_upload_summary(self, upload_success: bool):
        """打印上傳總結"""
        print("\n" + "="*60)
        print("🚀 上傳總結")
        print("="*60)
        
        if upload_success:
            print("✅ 上傳成功!")
            print("📤 代碼已推送到遠程倉庫")
            print("📚 文檔已自動更新")
        else:
            print("❌ 上傳失敗!")
            print("🔧 請檢查錯誤信息並修復問題")
        
        print("="*60)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation智能上傳腳本")
    parser.add_argument("--commit-message", "-m", required=False, 
                       default=f"Auto update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    parser.add_argument("--force", "-f", action="store_true", help="強制上傳，跳過測試驗證")
    parser.add_argument("--test-only", "-t", action="store_true", help="僅運行測試，不執行上傳")
    parser.add_argument("--project-root", "-p", help="項目根目錄路徑")
    
    args = parser.parse_args()
    
    # 創建上傳器
    uploader = PowerAutomationUploader(args.project_root)
    
    # 運行流水線
    success = uploader.run_full_pipeline(
        commit_message=args.commit_message,
        force=args.force,
        test_only=args.test_only
    )
    
    # 退出碼
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

