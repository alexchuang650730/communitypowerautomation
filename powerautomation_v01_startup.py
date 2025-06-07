#!/usr/bin/env python3
"""
PowerAutomation v0.1 快速啟動腳本
Quick Start Script for PowerAutomation v0.1

一鍵啟動所有核心功能，包括MCP註冊、記憶系統、備份系統
"""

import os
import sys
import json
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_mcp_adapters():
    """設置MCP適配器"""
    print("🔧 設置MCP適配器...")
    
    try:
        from mcptool.adapters.core.unified_adapter_registry import get_global_registry
        registry = get_global_registry()
        
        # 核心MCP適配器
        core_mcps = [
            {
                "id": "thought_action_recorder",
                "module": "mcptool.adapters.thought_action_recorder_mcp",
                "class": "ThoughtActionRecorderMCP",
                "name": "思考操作記錄器"
            },
            {
                "id": "supermemory",
                "module": "mcptool.adapters.supermemory_adapter.supermemory_mcp", 
                "class": "SuperMemoryMCP",
                "name": "SuperMemory適配器"
            }
        ]
        
        registered_count = 0
        for mcp_info in core_mcps:
            try:
                # 動態導入
                module = __import__(mcp_info["module"], fromlist=[mcp_info["class"]])
                mcp_class = getattr(module, mcp_info["class"])
                
                # 註冊
                registry.registered_adapters[mcp_info["id"]] = {
                    "name": mcp_info["name"],
                    "class": mcp_class,
                    "category": "core",
                    "status": "active",
                    "module_path": mcp_info["module"]
                }
                
                print(f"✅ {mcp_info['name']} 註冊成功")
                registered_count += 1
                
            except Exception as e:
                print(f"⚠️ {mcp_info['name']} 註冊失敗: {e}")
                
        print(f"📊 MCP設置完成: {registered_count} 個適配器已註冊")
        return registered_count > 0
        
    except Exception as e:
        print(f"❌ MCP設置失敗: {e}")
        return False

def setup_memory_system():
    """設置記憶系統"""
    print("\n🧠 設置記憶系統...")
    
    try:
        # 初始化智能分類器
        from memory_system.intelligent_classifier.intelligent_classifier import classifier
        
        # 測試分類功能
        test_memory = classifier.classify_memory(
            "PowerAutomation v0.1 系統啟動",
            "system_startup",
            {"importance": "high", "system": "powerautomation"}
        )
        
        print(f"✅ 記憶系統初始化成功")
        print(f"   測試記憶ID: {test_memory.id}")
        print(f"   重要性: {test_memory.importance_level.emoji} {test_memory.importance_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ 記憶系統設置失敗: {e}")
        return False

def setup_backup_system():
    """設置備份系統"""
    print("\n💾 設置備份系統...")
    
    try:
        # 初始化SuperMemory工作區管理器
        from supermemory_workspace_manager import workspace_manager
        
        # 獲取統計信息
        stats = workspace_manager.get_statistics()
        
        print(f"✅ 備份系統初始化成功")
        print(f"   備份目錄: {stats['backup_directory']}")
        print(f"   API配置: {'已配置' if stats['api_configured'] else '未配置'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 備份系統設置失敗: {e}")
        return False

def setup_data_flow():
    """設置數據流管理"""
    print("\n🔄 設置數據流管理...")
    
    try:
        # 初始化數據流管理器
        from data_flow_manager import data_flow_manager
        
        # 獲取統計信息
        stats = data_flow_manager.get_statistics()
        
        print(f"✅ 數據流管理初始化成功")
        print(f"   隊列大小: {stats['queue_size']}")
        print(f"   存儲配置: GitHub({'✅' if stats['storage_config']['github']['enabled'] else '❌'})")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據流設置失敗: {e}")
        return False

def test_smart_upload():
    """測試Smart Upload功能"""
    print("\n📤 測試Smart Upload功能...")
    
    try:
        # 檢查Smart Upload腳本
        smart_upload_files = [
            "smart_upload.py",
            "smart_upload_v2.py"
        ]
        
        available_uploads = []
        for upload_file in smart_upload_files:
            if os.path.exists(upload_file):
                available_uploads.append(upload_file)
                
        if available_uploads:
            print(f"✅ Smart Upload腳本可用: {available_uploads}")
            print(f"💡 手動執行: python3 {available_uploads[-1]}")
            return True
        else:
            print(f"❌ 未找到Smart Upload腳本")
            return False
            
    except Exception as e:
        print(f"❌ Smart Upload測試失敗: {e}")
        return False

def test_cli_functionality():
    """測試CLI功能"""
    print("\n🖥️ 測試CLI功能...")
    
    try:
        # 測試CLI導入
        from mcptool.cli.unified_mcp_cli import UnifiedMCPCLI
        
        print("✅ CLI模塊導入成功")
        print("💡 使用方法:")
        print("   python3 mcptool/cli/unified_mcp_cli.py list")
        print("   python3 mcptool/cli/unified_mcp_cli.py info thought_action_recorder")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI測試失敗: {e}")
        return False

def create_v01_status_file():
    """創建v0.1版本狀態文件"""
    status = {
        "version": "0.1",
        "status": "ready",
        "components": {
            "mcp_adapters": "active",
            "memory_system": "active", 
            "backup_system": "active",
            "data_flow": "active",
            "smart_upload": "manual_ready",
            "cli": "active"
        },
        "initialized_at": "2025-06-07T04:55:00Z",
        "ready_for_testing": True
    }
    
    with open("powerautomation_v01_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
        
    print(f"\n📋 v0.1狀態文件已創建: powerautomation_v01_status.json")

def main():
    """主啟動函數"""
    print("🚀 PowerAutomation v0.1 快速啟動")
    print("=" * 50)
    
    # 系統組件啟動檢查清單
    components = [
        ("MCP適配器", setup_mcp_adapters),
        ("記憶系統", setup_memory_system),
        ("備份系統", setup_backup_system), 
        ("數據流管理", setup_data_flow),
        ("Smart Upload", test_smart_upload),
        ("CLI功能", test_cli_functionality)
    ]
    
    success_count = 0
    total_count = len(components)
    
    for component_name, setup_func in components:
        try:
            if setup_func():
                success_count += 1
        except Exception as e:
            print(f"❌ {component_name} 啟動失敗: {e}")
            
    print("\n" + "=" * 50)
    print(f"📊 PowerAutomation v0.1 啟動完成")
    print(f"✅ 成功: {success_count}/{total_count} 個組件")
    
    if success_count == total_count:
        print("🎉 所有組件啟動成功！PowerAutomation v0.1 已就緒")
        create_v01_status_file()
        
        print("\n🎯 v0.1版本功能:")
        print("   📝 記憶系統 - 智能分類和存儲")
        print("   💾 備份系統 - SuperMemory和GitHub備份")
        print("   🔄 數據流管理 - 三層存儲架構")
        print("   📤 Smart Upload - 手動上傳功能")
        print("   🖥️ CLI控制 - 統一命令行接口")
        
        print("\n🚀 開始使用:")
        print("   python3 mcptool/cli/unified_mcp_cli.py list")
        print("   python3 smart_upload_v2.py")
        
    else:
        print("⚠️ 部分組件啟動失敗，請檢查錯誤信息")
        
    return success_count == total_count

if __name__ == "__main__":
    main()

