#!/usr/bin/env python3
"""
MCP適配器完整性測試
檢查所有MCP適配器是否都有對應的CLI和工具註冊表入口
"""

import os
import sys
import json
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

class MCPIntegrityTester:
    """MCP適配器完整性測試器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.mcptool_dir = self.project_root / "mcptool"
        self.adapters_dir = self.mcptool_dir / "adapters"
        self.cli_dir = self.mcptool_dir / "cli"
        
        # 測試結果
        self.test_results = {
            "discovered_adapters": [],
            "registered_adapters": [],
            "cli_commands": [],
            "missing_registrations": [],
            "missing_cli_commands": [],
            "orphaned_cli_commands": [],
            "integrity_score": 0.0,
            "total_adapters": 0,
            "total_registered": 0,
            "total_cli_commands": 0
        }
        
        logger.info("MCP適配器完整性測試器初始化")
    
    def discover_all_mcp_adapters(self) -> List[Dict[str, Any]]:
        """發現所有MCP適配器"""
        adapters = []
        
        try:
            # 遍歷適配器目錄
            for py_file in self.adapters_dir.rglob("*_mcp.py"):
                if py_file.name.startswith("__"):
                    continue
                
                adapter_info = {
                    "file_path": str(py_file),
                    "relative_path": str(py_file.relative_to(self.adapters_dir)),
                    "module_name": py_file.stem,
                    "category": self._get_adapter_category(py_file),
                    "class_name": None,
                    "has_class": False
                }
                
                # 檢查是否有MCP適配器類
                try:
                    adapter_class = self._extract_adapter_class(py_file)
                    if adapter_class:
                        adapter_info["class_name"] = adapter_class
                        adapter_info["has_class"] = True
                except Exception as e:
                    logger.debug(f"無法提取適配器類 {py_file}: {e}")
                
                adapters.append(adapter_info)
        
        except Exception as e:
            logger.error(f"適配器發現失敗: {e}")
        
        self.test_results["discovered_adapters"] = adapters
        self.test_results["total_adapters"] = len(adapters)
        
        return adapters
    
    def _get_adapter_category(self, py_file: Path) -> str:
        """獲取適配器分類"""
        path_parts = py_file.parts
        
        # 根據路徑確定分類
        if "agent" in path_parts:
            return "agent_optimization"
        elif "claude_adapter" in path_parts:
            return "claude_adapter"
        elif "gemini_adapter" in path_parts:
            return "gemini_adapter"
        elif "kilocode_adapter" in path_parts:
            return "kilocode_adapter"
        elif "infinite_context_adapter" in path_parts:
            return "infinite_context_adapter"
        elif "enhanced_aci_dev_adapter" in path_parts:
            return "enhanced_aci_dev_adapter"
        elif "zapier_adapter" in path_parts:
            return "zapier_adapter"
        elif "rl_srt" in path_parts:
            return "rl_srt"
        elif "sequential_thinking_adapter" in path_parts:
            return "sequential_thinking_adapter"
        elif "unified_smart_tool_engine" in path_parts:
            return "unified_smart_tool_engine"
        elif "unified_config_manager" in path_parts:
            return "unified_config_manager"
        else:
            return "core"
    
    def _extract_adapter_class(self, py_file: Path) -> Optional[str]:
        """提取適配器類名"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找類定義
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('class ') and 'MCP' in line and ':' in line:
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    return class_name
            
            return None
        except Exception:
            return None
    
    def check_registry_registration(self) -> List[Dict[str, Any]]:
        """檢查註冊表註冊情況"""
        registered_adapters = []
        
        try:
            # 導入統一適配器註冊表
            sys.path.append(str(self.mcptool_dir))
            from adapters.core.unified_adapter_registry import UnifiedAdapterRegistry
            
            # 創建註冊表實例
            registry = UnifiedAdapterRegistry()
            
            # 獲取已註冊的適配器
            for adapter_name, adapter_info in registry.registered_adapters.items():
                registered_adapters.append({
                    "name": adapter_name,
                    "class": adapter_info.get("class", "Unknown"),
                    "category": adapter_info.get("category", "Unknown"),
                    "status": adapter_info.get("status", "Unknown"),
                    "file_path": adapter_info.get("file_path", "Unknown")
                })
        
        except Exception as e:
            logger.error(f"註冊表檢查失敗: {e}")
        
        self.test_results["registered_adapters"] = registered_adapters
        self.test_results["total_registered"] = len(registered_adapters)
        
        return registered_adapters
    
    def check_cli_commands(self) -> List[Dict[str, Any]]:
        """檢查CLI命令"""
        cli_commands = []
        
        try:
            # 檢查主要CLI文件
            cli_files = [
                self.cli_dir / "enhanced_mcp_cli.py",
                self.cli_dir / "rollback_cli.py",
                self.mcptool_dir / "cli_testing" / "unified_adapter_cli.py"
            ]
            
            for cli_file in cli_files:
                if cli_file.exists():
                    commands = self._extract_cli_commands(cli_file)
                    cli_commands.extend(commands)
        
        except Exception as e:
            logger.error(f"CLI命令檢查失敗: {e}")
        
        self.test_results["cli_commands"] = cli_commands
        self.test_results["total_cli_commands"] = len(cli_commands)
        
        return cli_commands
    
    def _extract_cli_commands(self, cli_file: Path) -> List[Dict[str, Any]]:
        """提取CLI命令"""
        commands = []
        
        try:
            with open(cli_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找命令定義
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 查找argparse子命令或函數定義
                if 'add_parser(' in line or 'subparsers.add_parser(' in line:
                    # 提取命令名
                    if "'" in line:
                        command_name = line.split("'")[1]
                    elif '"' in line:
                        command_name = line.split('"')[1]
                    else:
                        continue
                    
                    commands.append({
                        "command": command_name,
                        "file": str(cli_file.relative_to(self.project_root)),
                        "line": i + 1,
                        "type": "subparser"
                    })
                
                # 查找函數定義（可能是命令處理函數）
                elif line.startswith('def ') and ('_command' in line or '_cmd' in line):
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    commands.append({
                        "command": func_name,
                        "file": str(cli_file.relative_to(self.project_root)),
                        "line": i + 1,
                        "type": "function"
                    })
        
        except Exception as e:
            logger.debug(f"CLI命令提取失敗 {cli_file}: {e}")
        
        return commands
    
    def analyze_integrity(self) -> Dict[str, Any]:
        """分析完整性"""
        # 獲取所有數據
        discovered_adapters = self.discover_all_mcp_adapters()
        registered_adapters = self.check_registry_registration()
        cli_commands = self.check_cli_commands()
        
        # 創建適配器名稱集合
        discovered_names = {adapter["module_name"] for adapter in discovered_adapters}
        registered_names = {adapter["name"] for adapter in registered_adapters}
        cli_command_names = {cmd["command"] for cmd in cli_commands}
        
        # 查找缺失的註冊
        missing_registrations = discovered_names - registered_names
        self.test_results["missing_registrations"] = list(missing_registrations)
        
        # 查找缺失的CLI命令（簡化檢查，因為不是所有適配器都需要專門的CLI命令）
        # 主要檢查核心適配器是否有對應的CLI支持
        core_adapters = {adapter["module_name"] for adapter in discovered_adapters 
                        if adapter["category"] in ["core", "unified_smart_tool_engine", "unified_config_manager"]}
        missing_cli_commands = core_adapters - cli_command_names
        self.test_results["missing_cli_commands"] = list(missing_cli_commands)
        
        # 查找孤立的CLI命令
        orphaned_cli_commands = cli_command_names - discovered_names
        self.test_results["orphaned_cli_commands"] = list(orphaned_cli_commands)
        
        # 計算完整性分數
        total_adapters = len(discovered_adapters)
        registered_count = len(registered_adapters)
        
        if total_adapters > 0:
            registration_score = registered_count / total_adapters
            missing_penalty = len(missing_registrations) / total_adapters if total_adapters > 0 else 0
            integrity_score = max(0, registration_score - missing_penalty * 0.5)
        else:
            integrity_score = 0.0
        
        self.test_results["integrity_score"] = integrity_score
        
        return self.test_results
    
    def generate_report(self) -> str:
        """生成完整性報告"""
        results = self.analyze_integrity()
        
        report = f"""
# MCP適配器完整性測試報告

## 📊 總體統計
- **發現的適配器**: {results['total_adapters']}個
- **已註冊適配器**: {results['total_registered']}個
- **CLI命令**: {results['total_cli_commands']}個
- **完整性分數**: {results['integrity_score']:.2%}

## 🔍 詳細分析

### 發現的適配器 ({results['total_adapters']}個)
"""
        
        for adapter in results["discovered_adapters"]:
            status = "✅" if adapter["has_class"] else "❌"
            report += f"- {status} **{adapter['module_name']}** ({adapter['category']})\n"
        
        report += f"""
### 已註冊適配器 ({results['total_registered']}個)
"""
        
        for adapter in results["registered_adapters"]:
            report += f"- ✅ **{adapter['name']}** ({adapter['category']}) - {adapter['status']}\n"
        
        if results["missing_registrations"]:
            report += f"""
### ⚠️ 缺失註冊 ({len(results['missing_registrations'])}個)
"""
            for missing in results["missing_registrations"]:
                report += f"- ❌ **{missing}** - 未在註冊表中找到\n"
        
        if results["missing_cli_commands"]:
            report += f"""
### ⚠️ 缺失CLI命令 ({len(results['missing_cli_commands'])}個)
"""
            for missing in results["missing_cli_commands"]:
                report += f"- ❌ **{missing}** - 核心適配器缺少CLI支持\n"
        
        report += f"""
### CLI命令 ({results['total_cli_commands']}個)
"""
        
        for cmd in results["cli_commands"]:
            report += f"- 🔧 **{cmd['command']}** ({cmd['type']}) - {cmd['file']}\n"
        
        report += f"""
## 🎯 建議

### 完整性評估
- **優秀** (90%+): 系統完整性很好
- **良好** (70-90%): 有少量問題需要修復
- **需要改進** (<70%): 存在較多完整性問題

### 當前狀態: {"優秀" if results['integrity_score'] >= 0.9 else "良好" if results['integrity_score'] >= 0.7 else "需要改進"}

### 改進建議
"""
        
        if results["missing_registrations"]:
            report += "1. **修復缺失註冊**: 將未註冊的適配器添加到統一註冊表中\n"
        
        if results["missing_cli_commands"]:
            report += "2. **添加CLI支持**: 為核心適配器添加CLI命令支持\n"
        
        if results["orphaned_cli_commands"]:
            report += "3. **清理孤立命令**: 移除不再需要的CLI命令\n"
        
        if results['integrity_score'] >= 0.9:
            report += "✅ **系統完整性良好，無需特別改進**\n"
        
        report += f"""
---
*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def run_integrity_test(self) -> Dict[str, Any]:
        """運行完整性測試"""
        logger.info("開始MCP適配器完整性測試...")
        
        try:
            results = self.analyze_integrity()
            
            # 生成報告
            report = self.generate_report()
            
            # 保存報告
            report_file = self.project_root / "docs" / "MCP適配器完整性測試報告.md"
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"完整性測試完成，報告已保存到: {report_file}")
            
            # 返回測試結果
            return {
                "success": True,
                "integrity_score": results["integrity_score"],
                "total_adapters": results["total_adapters"],
                "total_registered": results["total_registered"],
                "missing_registrations": len(results["missing_registrations"]),
                "missing_cli_commands": len(results["missing_cli_commands"]),
                "report_file": str(report_file),
                "message": f"完整性分數: {results['integrity_score']:.2%}"
            }
        
        except Exception as e:
            logger.error(f"完整性測試失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "完整性測試執行失敗"
            }

def main():
    """主函數"""
    tester = MCPIntegrityTester()
    result = tester.run_integrity_test()
    
    if result["success"]:
        print(f"✅ MCP適配器完整性測試完成")
        print(f"📊 完整性分數: {result['integrity_score']:.2%}")
        print(f"📁 報告文件: {result['report_file']}")
    else:
        print(f"❌ 完整性測試失敗: {result['message']}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

