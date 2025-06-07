#!/usr/bin/env python3
"""
PowerAutomation統一測試管理器
整合所有測試腳本，提供統一的CLI測試接口
"""

import os
import sys
import argparse
import json
import logging
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class UnifiedTestManager:
    """統一測試管理器"""
    
    def __init__(self):
        """初始化測試管理器"""
        self.test_root = Path(__file__).parent
        self.project_root = self.test_root.parent
        self.setup_logging()
        
        # 測試分類
        self.test_categories = {
            "unit": "單元測試",
            "integration": "集成測試", 
            "e2e": "端到端測試",
            "performance": "性能測試",
            "automation": "自動化測試",
            "mcp_compliance": "MCP合規測試",
            "gaia": "GAIA基準測試"
        }
        
        # 發現所有測試腳本
        self.test_scripts = self._discover_test_scripts()
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _discover_test_scripts(self) -> Dict[str, List[Path]]:
        """發現所有測試腳本"""
        scripts = {}
        
        for category in self.test_categories.keys():
            category_path = self.test_root / category
            scripts[category] = []
            
            if category_path.exists():
                # 遞歸查找Python文件
                for py_file in category_path.rglob("*.py"):
                    if not py_file.name.startswith("__"):
                        scripts[category].append(py_file)
        
        # 添加根目錄的特殊測試
        for special_test in ["gaia.py", "unified_test_cli.py"]:
            test_path = self.test_root / special_test
            if test_path.exists():
                if special_test == "gaia.py":
                    scripts.setdefault("gaia", []).append(test_path)
                else:
                    scripts.setdefault("automation", []).append(test_path)
        
        return scripts
    
    def list_tests(self, category: str = None) -> Dict[str, Any]:
        """列出測試腳本"""
        if category and category not in self.test_categories:
            raise ValueError(f"未知測試分類: {category}")
        
        result = {}
        categories = [category] if category else self.test_categories.keys()
        
        for cat in categories:
            if cat in self.test_scripts:
                result[cat] = {
                    "name": self.test_categories[cat],
                    "count": len(self.test_scripts[cat]),
                    "scripts": [str(script.relative_to(self.test_root)) 
                              for script in self.test_scripts[cat]]
                }
        
        return result
    
    def run_test_script(self, script_path: Path, args: List[str] = None) -> Tuple[int, str, str]:
        """運行單個測試腳本"""
        if not script_path.exists():
            return 1, "", f"測試腳本不存在: {script_path}"
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5分鐘超時
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "測試超時"
        except Exception as e:
            return 1, "", f"執行錯誤: {e}"
    
    def run_category_tests(self, category: str, verbose: bool = False) -> Dict[str, Any]:
        """運行指定分類的所有測試"""
        if category not in self.test_categories:
            raise ValueError(f"未知測試分類: {category}")
        
        if category not in self.test_scripts:
            return {
                "category": category,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "results": []
            }
        
        scripts = self.test_scripts[category]
        results = []
        passed = 0
        
        print(f"\n🧪 運行 {self.test_categories[category]} ({len(scripts)} 個腳本)")
        print("=" * 60)
        
        for script in scripts:
            script_name = script.relative_to(self.test_root)
            print(f"🔄 運行: {script_name}")
            
            returncode, stdout, stderr = self.run_test_script(script)
            
            if returncode == 0:
                print(f"  ✅ 通過")
                passed += 1
                status = "passed"
            else:
                print(f"  ❌ 失敗")
                status = "failed"
            
            result = {
                "script": str(script_name),
                "status": status,
                "returncode": returncode,
                "stdout": stdout if verbose else stdout[:200] + "..." if len(stdout) > 200 else stdout,
                "stderr": stderr if verbose else stderr[:200] + "..." if len(stderr) > 200 else stderr
            }
            results.append(result)
            
            if verbose and (stdout or stderr):
                print(f"    輸出: {stdout[:100]}...")
                if stderr:
                    print(f"    錯誤: {stderr[:100]}...")
        
        return {
            "category": category,
            "total": len(scripts),
            "passed": passed,
            "failed": len(scripts) - passed,
            "results": results
        }
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """運行所有測試"""
        print("🚀 運行PowerAutomation完整測試套件")
        print("=" * 60)
        
        all_results = {}
        total_passed = 0
        total_failed = 0
        
        for category in self.test_categories.keys():
            if category in self.test_scripts and self.test_scripts[category]:
                result = self.run_category_tests(category, verbose)
                all_results[category] = result
                total_passed += result["passed"]
                total_failed += result["failed"]
        
        # 生成總結報告
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_categories": len(all_results),
            "total_scripts": total_passed + total_failed,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0,
            "categories": all_results
        }
        
        print(f"\n📊 測試總結")
        print("=" * 40)
        print(f"📁 測試分類: {summary['total_categories']}")
        print(f"📄 測試腳本: {summary['total_scripts']}")
        print(f"✅ 通過: {summary['total_passed']}")
        print(f"❌ 失敗: {summary['total_failed']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        
        return summary
    
    def run_gaia_tests(self, level: int = 1, max_tasks: int = 10, verbose: bool = False) -> Dict[str, Any]:
        """運行GAIA測試"""
        gaia_script = self.test_root / "gaia.py"
        if not gaia_script.exists():
            return {"error": "GAIA測試腳本不存在"}
        
        print(f"🧠 運行GAIA Level {level} 測試 (最多 {max_tasks} 個任務)")
        print("=" * 50)
        
        args = ["test", f"--level={level}", f"--max-tasks={max_tasks}"]
        if verbose:
            args.append("--verbose")
        
        returncode, stdout, stderr = self.run_test_script(gaia_script, args)
        
        # 解析GAIA測試結果
        try:
            # 從輸出中提取結果
            lines = stdout.split('\n')
            results = {}
            
            for line in lines:
                if "準確度:" in line:
                    accuracy = float(line.split(":")[-1].strip().rstrip('%'))
                    results["accuracy"] = accuracy
                elif "完成任務:" in line:
                    completed = int(line.split("/")[0].split(":")[-1].strip())
                    total = int(line.split("/")[1].strip())
                    results["completed"] = completed
                    results["total"] = total
            
            results.update({
                "level": level,
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr
            })
            
            return results
            
        except Exception as e:
            return {
                "error": f"解析GAIA結果失敗: {e}",
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr
            }
    
    def generate_test_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """生成測試報告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.json"
        
        output_path = self.test_root / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 測試報告已生成: {output_path}")
        return str(output_path)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation統一測試管理器")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細輸出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出測試腳本")
    list_parser.add_argument("--category", choices=["unit", "integration", "e2e", "performance", "automation", "mcp_compliance", "gaia"], help="測試分類")
    
    # run命令
    run_parser = subparsers.add_parser("run", help="運行測試")
    run_parser.add_argument("category", nargs="?", choices=["unit", "integration", "e2e", "performance", "automation", "mcp_compliance", "gaia", "all"], help="測試分類")
    
    # gaia命令
    gaia_parser = subparsers.add_parser("gaia", help="運行GAIA測試")
    gaia_parser.add_argument("--level", type=int, default=1, choices=[1, 2, 3], help="GAIA測試級別")
    gaia_parser.add_argument("--max-tasks", type=int, default=10, help="最大任務數")
    
    # report命令
    report_parser = subparsers.add_parser("report", help="生成測試報告")
    report_parser.add_argument("--output", help="輸出文件名")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = UnifiedTestManager()
    
    try:
        if args.command == "list":
            tests = manager.list_tests(args.category)
            print("📋 PowerAutomation測試腳本")
            print("=" * 40)
            
            for category, info in tests.items():
                print(f"\n📁 {info['name']} ({info['count']} 個腳本)")
                for script in info['scripts']:
                    print(f"  • {script}")
        
        elif args.command == "run":
            if args.category == "all":
                results = manager.run_all_tests(args.verbose)
                if args.verbose:
                    report_path = manager.generate_test_report(results)
            else:
                results = manager.run_category_tests(args.category, args.verbose)
                print(f"\n📊 {args.category} 測試結果: {results['passed']}/{results['total']} 通過")
        
        elif args.command == "gaia":
            results = manager.run_gaia_tests(args.level, args.max_tasks, args.verbose)
            if "error" in results:
                print(f"❌ GAIA測試失敗: {results['error']}")
                return 1
            else:
                accuracy = results.get("accuracy", 0)
                print(f"🎯 GAIA Level {args.level} 準確度: {accuracy:.1f}%")
                if accuracy >= 90:
                    print("🎉 達到90%準確度目標！")
                else:
                    print(f"⚠️  距離90%目標還差 {90-accuracy:.1f}%")
        
        elif args.command == "report":
            # 運行完整測試並生成報告
            results = manager.run_all_tests(args.verbose)
            report_path = manager.generate_test_report(results, args.output)
        
        return 0
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

