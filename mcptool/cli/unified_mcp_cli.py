#!/usr/bin/env python3
"""
統一MCP CLI控制系統
提供命令行界面來管理和操作所有MCP適配器
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import readline
import cmd

# 添加項目路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# 導入適配器註冊表
from mcptool.adapters.core.unified_adapter_registry import get_global_registry

# 導入mcp_core_cli
sys.path.append(str(current_dir))
from mcp_core_cli import MCPCoreCLI

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedMCPCLI(cmd.Cmd):
    """統一MCP CLI交互式界面 - 集成mcp_core_cli功能"""
    
    intro = '''
🚀 PowerAutomation 統一MCP控制系統 v2.0
=====================================
✨ 新增功能: 集成MCP核心CLI支持
輸入 'help' 查看可用命令
輸入 'quit' 或 'exit' 退出系統
'''
    prompt = '(MCP) > '
    
    def __init__(self):
        super().__init__()
        self.registry = get_global_registry()
        self.current_adapter = None
        self.core_cli = MCPCoreCLI()  # 集成核心CLI
        
    def do_list(self, args):
        """列出適配器
        用法: list [category]
        例子: list core
        """
        args = args.strip()
        category = args if args else None
        
        try:
            adapters = self.registry.list_adapters(category)
            
            if not adapters:
                print("❌ 沒有找到適配器")
                return
            
            print(f"\n📋 適配器列表 {'(分類: ' + category + ')' if category else ''}")
            print("=" * 60)
            
            current_category = None
            for adapter in adapters:
                if adapter['category'] != current_category:
                    current_category = adapter['category']
                    print(f"\n📁 {adapter['category_name']} ({adapter['category']})")
                    print("-" * 40)
                
                print(f"  🔧 {adapter['id']}")
                print(f"     名稱: {adapter['name']}")
                print(f"     描述: {adapter['description'][:80]}...")
                print(f"     能力: {len(adapter['capabilities'])} 項")
                print(f"     方法: {adapter['methods_count']} 個")
                print()
                
        except Exception as e:
            print(f"❌ 列出適配器失敗: {e}")
    
    def do_categories(self, args):
        """顯示適配器分類統計
        用法: categories
        """
        try:
            categories = self.registry.get_categories()
            
            print("\n📊 適配器分類統計")
            print("=" * 40)
            
            for cat_id, cat_info in categories.items():
                print(f"📁 {cat_info['name']} ({cat_id})")
                print(f"   適配器數量: {cat_info['count']}")
                print(f"   適配器列表: {', '.join(cat_info['adapters'][:3])}")
                if len(cat_info['adapters']) > 3:
                    print(f"   ... 還有 {len(cat_info['adapters']) - 3} 個")
                print()
                
        except Exception as e:
            print(f"❌ 獲取分類統計失敗: {e}")
    
    def do_search(self, args):
        """搜索適配器
        用法: search <關鍵詞>
        例子: search config
        """
        if not args.strip():
            print("❌ 請提供搜索關鍵詞")
            return
        
        try:
            results = self.registry.search_adapters(args.strip())
            
            if not results:
                print(f"❌ 沒有找到包含 '{args}' 的適配器")
                return
            
            print(f"\n🔍 搜索結果: '{args}'")
            print("=" * 40)
            
            for result in results:
                print(f"🔧 {result['id']} (評分: {result['score']})")
                print(f"   名稱: {result['name']}")
                print(f"   分類: {result['category']}")
                print(f"   描述: {result['description'][:60]}...")
                print()
                
        except Exception as e:
            print(f"❌ 搜索失敗: {e}")
    
    def do_info(self, args):
        """顯示適配器詳細信息
        用法: info <adapter_id>
        例子: info core.webagent
        """
        if not args.strip():
            print("❌ 請提供適配器ID")
            return
        
        try:
            adapter_info = self.registry.get_adapter_info(args.strip())
            
            print(f"\n📋 適配器詳細信息: {adapter_info['id']}")
            print("=" * 60)
            print(f"名稱: {adapter_info['name']}")
            print(f"分類: {adapter_info['category_name']} ({adapter_info['category']})")
            print(f"描述: {adapter_info['description']}")
            print(f"文件路徑: {adapter_info['file_path']}")
            print(f"模塊路徑: {adapter_info['module_path']}")
            print(f"註冊時間: {adapter_info['registered_at']}")
            print(f"實例狀態: {'已創建' if adapter_info['has_instance'] else '未創建'}")
            
            if adapter_info['capabilities']:
                print(f"\n🎯 能力列表 ({len(adapter_info['capabilities'])} 項):")
                for i, capability in enumerate(adapter_info['capabilities'], 1):
                    print(f"  {i}. {capability}")
            
            if adapter_info['methods']:
                print(f"\n🔧 方法列表 ({len(adapter_info['methods'])} 個):")
                for method in adapter_info['methods'][:5]:  # 只顯示前5個
                    print(f"  • {method['name']}{method['signature']}")
                    if method['doc'] != "無文檔":
                        print(f"    {method['doc'][:60]}...")
                
                if len(adapter_info['methods']) > 5:
                    print(f"  ... 還有 {len(adapter_info['methods']) - 5} 個方法")
                    
        except Exception as e:
            print(f"❌ 獲取適配器信息失敗: {e}")
    
    def do_exec(self, args):
        """執行適配器
        用法: exec <adapter_id> <action> [parameters_json]
        例子: exec core.webagent get_capabilities
        例子: exec core.webagent semantic_extract '{"url": "https://example.com"}'
        """
        parts = args.strip().split(' ', 2)
        if len(parts) < 2:
            print("❌ 用法: exec <adapter_id> <action> [parameters_json]")
            return
        
        adapter_id = parts[0]
        action = parts[1]
        parameters_str = parts[2] if len(parts) > 2 else '{}'
        
        try:
            # 解析參數
            if parameters_str.strip():
                try:
                    parameters = json.loads(parameters_str)
                except json.JSONDecodeError:
                    print(f"❌ 參數JSON格式錯誤: {parameters_str}")
                    return
            else:
                parameters = {}
            
            # 構建輸入數據
            input_data = {
                "action": action,
                "parameters": parameters
            }
            
            print(f"🚀 執行適配器: {adapter_id}")
            print(f"   動作: {action}")
            print(f"   參數: {json.dumps(parameters, ensure_ascii=False)}")
            print("-" * 40)
            
            # 執行適配器
            result = self.registry.execute_adapter(adapter_id, input_data)
            
            if result['status'] == 'success':
                print("✅ 執行成功")
                print(f"結果: {json.dumps(result['result'], indent=2, ensure_ascii=False)}")
            else:
                print("❌ 執行失敗")
                print(f"錯誤: {result['error']}")
                
        except Exception as e:
            print(f"❌ 執行適配器失敗: {e}")
    
    def do_use(self, args):
        """選擇當前適配器
        用法: use <adapter_id>
        例子: use core.webagent
        """
        if not args.strip():
            if self.current_adapter:
                print(f"當前適配器: {self.current_adapter}")
            else:
                print("沒有選擇適配器")
            return
        
        adapter_id = args.strip()
        
        try:
            # 驗證適配器存在
            adapter_info = self.registry.get_adapter_info(adapter_id)
            self.current_adapter = adapter_id
            self.prompt = f'(MCP:{adapter_id}) > '
            
            print(f"✅ 已選擇適配器: {adapter_info['name']} ({adapter_id})")
            
        except Exception as e:
            print(f"❌ 選擇適配器失敗: {e}")
    
    def do_run(self, args):
        """在當前適配器上執行動作
        用法: run <action> [parameters_json]
        例子: run get_capabilities
        例子: run semantic_extract '{"url": "https://example.com"}'
        """
        if not self.current_adapter:
            print("❌ 請先使用 'use' 命令選擇適配器")
            return
        
        # 重用exec命令的邏輯
        self.do_exec(f"{self.current_adapter} {args}")
    
    def do_status(self, args):
        """顯示系統狀態
        用法: status
        """
        try:
            status = self.registry.get_registry_status()
            
            print("\n📊 系統狀態")
            print("=" * 30)
            print(f"總適配器數: {status['total_adapters']}")
            print(f"活躍實例數: {status['active_instances']}")
            print(f"適配器根目錄: {status['adapters_root']}")
            print(f"最後發現時間: {status['last_discovery']}")
            
            print(f"\n📁 分類統計:")
            for cat_id, cat_info in status['categories'].items():
                print(f"  {cat_info['name']}: {cat_info['count']} 個")
                
        except Exception as e:
            print(f"❌ 獲取系統狀態失敗: {e}")
    
    def do_config(self, args):
        """配置管理
        用法: config list                    # 列出所有配置
        用法: config get <key>              # 獲取配置值
        用法: config set <key> <value>      # 設置配置值
        """
        parts = args.strip().split()
        if not parts:
            print("❌ 用法: config <list|get|set> [key] [value]")
            return
        
        command = parts[0]
        
        if command == "list":
            print("\n⚙️ 配置列表")
            print("=" * 30)
            print("logging_level: INFO")
            print("adapters_root: " + self.registry.adapters_root)
            print("current_adapter: " + (self.current_adapter or "None"))
            
        elif command == "get":
            if len(parts) < 2:
                print("❌ 用法: config get <key>")
                return
            
            key = parts[1]
            if key == "logging_level":
                print(f"{key}: {logging.getLogger().level}")
            elif key == "adapters_root":
                print(f"{key}: {self.registry.adapters_root}")
            elif key == "current_adapter":
                print(f"{key}: {self.current_adapter or 'None'}")
            else:
                print(f"❌ 未知配置項: {key}")
                
        elif command == "set":
            if len(parts) < 3:
                print("❌ 用法: config set <key> <value>")
                return
            
            key = parts[1]
            value = parts[2]
            
            if key == "logging_level":
                level = getattr(logging, value.upper(), None)
                if level:
                    logging.getLogger().setLevel(level)
                    print(f"✅ 設置 {key} = {value}")
                else:
                    print(f"❌ 無效的日誌級別: {value}")
            else:
                print(f"❌ 不支持設置配置項: {key}")
        else:
            print(f"❌ 未知配置命令: {command}")
    
    def do_core(self, args):
        """執行核心CLI命令
        用法: core <command> [args]
        例子: core list
        例子: core info thoughtactionrecordermcp
        例子: core registry --stats
        """
        if not args.strip():
            print("❌ 用法: core <command> [args]")
            print("可用命令: list, info, exec, registry, config, tools, recorder, discovery")
            return
        
        try:
            # 將命令傳遞給核心CLI
            result = self.core_cli.run(args.split())
            if result != 0:
                print("❌ 核心CLI命令執行失敗")
        except Exception as e:
            print(f"❌ 執行核心CLI命令失敗: {e}")
    
    def do_claude(self, args):
        """Claude適配器專用命令
        用法: claude generate <prompt> [language]
        用法: claude optimize <code> [language] [type]
        用法: claude complete <text>
        """
        if not args.strip():
            print("❌ 用法: claude <generate|optimize|complete> [args]")
            return
        
        parts = args.strip().split(maxsplit=1)
        action = parts[0]
        
        if action == "generate":
            if len(parts) < 2:
                print("❌ 用法: claude generate <prompt> [language]")
                return
            
            prompt_parts = parts[1].split()
            prompt = " ".join(prompt_parts[:-1]) if len(prompt_parts) > 1 else parts[1]
            language = prompt_parts[-1] if len(prompt_parts) > 1 and prompt_parts[-1] in ["python", "javascript", "java", "cpp", "go"] else "python"
            
            data = {
                "action": "generate_code",
                "prompt": prompt,
                "language": language
            }
            
            self.do_exec(f"claudemcp {json.dumps(data)}")
            
        elif action == "optimize":
            print("❌ Claude optimize命令需要更多參數實現")
            
        elif action == "complete":
            if len(parts) < 2:
                print("❌ 用法: claude complete <text>")
                return
            
            data = {
                "action": "complete_text",
                "prompt": parts[1]
            }
            
            self.do_exec(f"claudemcp {json.dumps(data)}")
            
        else:
            print(f"❌ 未知Claude命令: {action}")
    
    def do_gemini(self, args):
        """Gemini適配器專用命令
        用法: gemini generate <prompt> [language]
        用法: gemini optimize <code> [language] [type]
        用法: gemini complete <text>
        """
        if not args.strip():
            print("❌ 用法: gemini <generate|optimize|complete> [args]")
            return
        
        parts = args.strip().split(maxsplit=1)
        action = parts[0]
        
        if action == "generate":
            if len(parts) < 2:
                print("❌ 用法: gemini generate <prompt> [language]")
                return
            
            prompt_parts = parts[1].split()
            prompt = " ".join(prompt_parts[:-1]) if len(prompt_parts) > 1 else parts[1]
            language = prompt_parts[-1] if len(prompt_parts) > 1 and prompt_parts[-1] in ["python", "javascript", "java", "cpp", "go"] else "python"
            
            data = {
                "action": "generate_code",
                "prompt": prompt,
                "language": language
            }
            
            self.do_exec(f"geminimcp {json.dumps(data)}")
            
        elif action == "complete":
            if len(parts) < 2:
                print("❌ 用法: gemini complete <text>")
                return
            
            data = {
                "action": "complete_text",
                "prompt": parts[1]
            }
            
            self.do_exec(f"geminimcp {json.dumps(data)}")
            
        else:
            print(f"❌ 未知Gemini命令: {action}")
    
    def do_supermemory(self, args):
        """SuperMemory適配器專用命令
        用法: supermemory store <key> <value>
        用法: supermemory retrieve <key>
        用法: supermemory search <query>
        用法: supermemory delete <key>
        """
        if not args.strip():
            print("❌ 用法: supermemory <store|retrieve|search|delete> [args]")
            return
        
        parts = args.strip().split(maxsplit=1)
        action = parts[0]
        
        if action == "store":
            if len(parts) < 2:
                print("❌ 用法: supermemory store <key> <value>")
                return
            
            key_value = parts[1].split(maxsplit=1)
            if len(key_value) < 2:
                print("❌ 用法: supermemory store <key> <value>")
                return
                
            key = key_value[0]
            value = key_value[1]
            
            data = {
                "action": "store",
                "key": key,
                "value": value
            }
            
            self.do_exec(f"supermemorymcp {json.dumps(data)}")
            
        elif action == "retrieve":
            if len(parts) < 2:
                print("❌ 用法: supermemory retrieve <key>")
                return
            
            key = parts[1]
            
            data = {
                "action": "retrieve",
                "key": key
            }
            
            self.do_exec(f"supermemorymcp {json.dumps(data)}")
            
        elif action == "search":
            if len(parts) < 2:
                print("❌ 用法: supermemory search <query>")
                return
            
            query = parts[1]
            
            data = {
                "action": "search",
                "query": query
            }
            
            self.do_exec(f"supermemorymcp {json.dumps(data)}")
            
        elif action == "delete":
            if len(parts) < 2:
                print("❌ 用法: supermemory delete <key>")
                return
            
            key = parts[1]
            
            data = {
                "action": "delete",
                "key": key
            }
            
            self.do_exec(f"supermemorymcp {json.dumps(data)}")
            
        else:
            print(f"❌ 未知SuperMemory命令: {action}")

    def do_kilo(self, args):
        """KiloCode適配器專用命令
        用法: kilo generate <prompt> [language]
        用法: kilo optimize <code> [language] [type]
        用法: kilo explain <code> [language]
        """
        if not args.strip():
            print("❌ 用法: kilo <generate|optimize|explain> [args]")
            return
        
        parts = args.strip().split(maxsplit=1)
        action = parts[0]
        
        if action == "generate":
            if len(parts) < 2:
                print("❌ 用法: kilo generate <prompt> [language]")
                return
            
            prompt_parts = parts[1].split()
            prompt = " ".join(prompt_parts[:-1]) if len(prompt_parts) > 1 else parts[1]
            language = prompt_parts[-1] if len(prompt_parts) > 1 and prompt_parts[-1] in ["python", "javascript", "java", "cpp", "go"] else "python"
            
            data = {
                "action": "generate_code",
                "prompt": prompt,
                "language": language
            }
            
            self.do_exec(f"kilocodemcp {json.dumps(data)}")
            
        elif action == "explain":
            if len(parts) < 2:
                print("❌ 用法: kilo explain <code> [language]")
                return
            
            code_parts = parts[1].split()
            code = " ".join(code_parts[:-1]) if len(code_parts) > 1 else parts[1]
            language = code_parts[-1] if len(code_parts) > 1 and code_parts[-1] in ["python", "javascript", "java", "cpp", "go"] else "python"
            
            data = {
                "action": "explain_code",
                "code": code,
                "language": language
            }
            
            self.do_exec(f"kilocodemcp {json.dumps(data)}")
            
        else:
            print(f"❌ 未知KiloCode命令: {action}")

    def do_quit(self, args):
        """退出系統"""
        print("👋 再見！")
        return True
    
    def do_exit(self, args):
        """退出系統"""
        return self.do_quit(args)
    
    def do_clear(self, args):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def emptyline(self):
        """空行時不執行任何操作"""
        pass
    
    def default(self, line):
        """處理未知命令"""
        print(f"❌ 未知命令: {line}")
        print("輸入 'help' 查看可用命令")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation 統一MCP控制系統")
    parser.add_argument('command', nargs='?', help='要執行的命令')
    parser.add_argument('args', nargs='*', help='命令參數')
    parser.add_argument('--interactive', '-i', action='store_true', help='進入交互模式')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 創建CLI實例
    cli = UnifiedMCPCLI()
    
    if args.interactive or not args.command:
        # 交互模式
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("\n👋 再見！")
        except Exception as e:
            print(f"❌ 系統錯誤: {e}")
    else:
        # 命令模式
        command_line = args.command + ' ' + ' '.join(args.args)
        cli.onecmd(command_line)

if __name__ == "__main__":
    main()

