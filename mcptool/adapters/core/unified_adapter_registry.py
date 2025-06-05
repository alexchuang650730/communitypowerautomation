#!/usr/bin/env python3
"""
統一適配器註冊表
自動發現、註冊和管理所有MCP適配器
"""

import os
import sys
import json
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedAdapterRegistry:
    """統一適配器註冊表"""
    
    def __init__(self, adapters_root: str = None):
        # 適配器根目錄
        self.adapters_root = str(Path(__file__).parent.parent)
        self.registered_adapters = {}
        self.adapter_instances = {}
        self.adapter_metadata = {}
        
        # 適配器分類
        self.adapter_categories = {
            "core": "核心組件",
            "ai_enhanced": "AI增強功能", 
            "unified_config_manager": "統一配置管理",
            "unified_smart_tool_engine": "統一智能工具引擎",
            "optimization": "優化相關",
            "workflow": "工作流引擎",
            "development_tools": "開發工具",
            "integration": "多適配器整合",
            "claude_adapter": "Claude適配器",
            "gemini_adapter": "Gemini適配器",
            "kilocode_adapter": "Kilocode適配器",
            "infinite_context_adapter": "無限上下文適配器",
            "enhanced_aci_dev_adapter": "增強ACI.dev適配器",
            "zapier_adapter": "Zapier適配器",
            "rl_srt": "強化學習SRT",
            "srt": "SRT適配器",
            "real_ai_adapter": "真實AI適配器",
            "fixed_mcp_so_adapter": "固定MCP.so適配器"
        }
        
        # 自動發現和註冊適配器
        self._discover_adapters()
        
        logger.info(f"統一適配器註冊表初始化完成，註冊了 {len(self.registered_adapters)} 個適配器")
    
    def _discover_adapters(self):
        """自動發現適配器"""
        try:
            adapters_path = Path(self.adapters_root)
            if not adapters_path.exists():
                logger.warning(f"適配器目錄不存在: {self.adapters_root}")
                return
            
            # 遍歷所有Python文件
            for py_file in adapters_path.rglob("*.py"):
                if py_file.name.startswith("__") or py_file.name in ["base_mcp.py", "error_handler.py"]:
                    continue
                
                try:
                    self._register_adapter_from_file(py_file)
                except Exception as e:
                    logger.warning(f"無法從文件註冊適配器 {py_file}: {e}")
            
        except Exception as e:
            logger.error(f"適配器發現失敗: {e}")
    
    def _register_adapter_from_file(self, py_file: Path):
        """從文件註冊適配器 - 改進版本，確保所有適配器都能正確註冊"""
        # 計算模塊路徑
        relative_path = py_file.relative_to(Path(self.adapters_root).parent)
        module_path = str(relative_path.with_suffix("")).replace(os.sep, ".")
        
        try:
            # 動態導入模塊
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if spec is None or spec.loader is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找MCP適配器類
            adapter_found = False
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_mcp_adapter_class(obj, module):
                    self._register_adapter_class(name, obj, py_file)
                    adapter_found = True
            
            # 如果沒有找到適配器類，使用文件名作為備用方案
            if not adapter_found and py_file.stem.endswith('_mcp'):
                # 從文件名創建一個虛擬適配器註冊
                adapter_id = py_file.stem.lower()
                self.registered_adapters[adapter_id] = {
                    "name": py_file.stem,
                    "class": None,  # 沒有實際類
                    "category": self._determine_category(py_file),
                    "file_path": str(py_file),
                    "module_path": module_path,
                    "registered_at": datetime.now().isoformat(),
                    "status": "file_only"  # 標記為僅文件存在
                }
                logger.debug(f"從文件名註冊適配器: {adapter_id} (無類定義)")
                    
        except Exception as e:
            logger.debug(f"模塊導入失敗 {module_path}: {e}")
    
    def _is_mcp_adapter_class(self, cls: Type, module) -> bool:
        """判斷是否為MCP適配器類 - 改進版本，更好地識別MCP類"""
        # 檢查是否在當前模塊中定義
        if cls.__module__ != module.__name__:
            return False
        
        # 直接檢查類名是否包含MCP
        if 'mcp' in cls.__name__.lower():
            return True
        
        # 檢查是否有process方法
        if hasattr(cls, 'process'):
            return True
        
        # 檢查是否有get_capabilities方法
        if hasattr(cls, 'get_capabilities'):
            return True
            
        # 檢查類名模式
        class_name = cls.__name__.lower()
        mcp_patterns = ['adapter', 'engine', 'core', 'manager']
        
        return any(pattern in class_name for pattern in mcp_patterns)
    
    def _register_adapter_class(self, name: str, cls: Type, file_path: Path):
        """註冊適配器類"""
        # 確定適配器類別
        category = self._determine_category(file_path)
        
        # 生成適配器ID
        adapter_id = self._generate_adapter_id(name, category)
        
        # 註冊適配器
        self.registered_adapters[adapter_id] = {
            "name": name,
            "class": cls,
            "category": category,
            "file_path": str(file_path),
            "module_path": cls.__module__,
            "registered_at": datetime.now().isoformat()
        }
        
        # 收集元數據
        self._collect_adapter_metadata(adapter_id, cls)
        
        logger.debug(f"註冊適配器: {adapter_id} ({name})")
    
    def _determine_category(self, file_path: Path) -> str:
        """確定適配器類別"""
        path_parts = file_path.parts
        
        for part in path_parts:
            if part in self.adapter_categories:
                return part
        
        # 根據文件名推斷類別
        file_name = file_path.stem.lower()
        
        if "config" in file_name or "manager" in file_name:
            return "unified_config_manager"
        elif "tool" in file_name or "engine" in file_name:
            return "unified_smart_tool_engine"
        elif "optimization" in file_name:
            return "optimization"
        elif "workflow" in file_name:
            return "workflow"
        elif "core" in file_name:
            return "core"
        elif "ai" in file_name or "enhanced" in file_name:
            return "ai_enhanced"
        else:
            return "integration"
    
    def _generate_adapter_id(self, name: str, category: str) -> str:
        """生成適配器ID - 修復命名不一致問題"""
        # 直接使用文件名作為ID，保持一致性
        file_name = name.lower()
        
        # 移除常見後綴但保持原始結構
        if file_name.endswith('_mcp'):
            # 保留_mcp後綴以保持與文件名一致
            return file_name
        elif file_name.endswith('_adapter'):
            return file_name
        elif file_name.endswith('_engine'):
            return file_name
        else:
            return file_name
    
    def _collect_adapter_metadata(self, adapter_id: str, cls: Type):
        """收集適配器元數據"""
        metadata = {
            "description": cls.__doc__ or "無描述",
            "capabilities": [],
            "methods": [],
            "has_process": hasattr(cls, 'process'),
            "has_validate_input": hasattr(cls, 'validate_input'),
            "has_get_capabilities": hasattr(cls, 'get_capabilities')
        }
        
        # 收集方法信息
        for method_name, method in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith('_'):
                metadata["methods"].append({
                    "name": method_name,
                    "signature": str(inspect.signature(method)),
                    "doc": method.__doc__ or "無文檔"
                })
        
        # 嘗試獲取能力列表
        try:
            if hasattr(cls, 'get_capabilities'):
                # 創建臨時實例獲取能力
                temp_instance = cls()
                metadata["capabilities"] = temp_instance.get_capabilities()
        except Exception as e:
            logger.debug(f"無法獲取適配器能力 {adapter_id}: {e}")
        
        self.adapter_metadata[adapter_id] = metadata
    
    def get_adapter(self, adapter_id: str, **kwargs):
        """獲取適配器實例"""
        if adapter_id not in self.registered_adapters:
            raise ValueError(f"未找到適配器: {adapter_id}")
        
        # 檢查是否已有實例
        if adapter_id in self.adapter_instances:
            return self.adapter_instances[adapter_id]
        
        # 創建新實例
        adapter_info = self.registered_adapters[adapter_id]
        adapter_class = adapter_info["class"]
        
        try:
            instance = adapter_class(**kwargs)
            self.adapter_instances[adapter_id] = instance
            return instance
        except Exception as e:
            logger.error(f"創建適配器實例失敗 {adapter_id}: {e}")
            raise
    
    def list_adapters(self, category: str = None) -> List[Dict[str, Any]]:
        """列出適配器"""
        adapters = []
        
        for adapter_id, adapter_info in self.registered_adapters.items():
            if category and adapter_info["category"] != category:
                continue
            
            metadata = self.adapter_metadata.get(adapter_id, {})
            
            adapters.append({
                "id": adapter_id,
                "name": adapter_info["name"],
                "category": adapter_info["category"],
                "category_name": self.adapter_categories.get(adapter_info["category"], "未知"),
                "description": metadata.get("description", "無描述"),
                "capabilities": metadata.get("capabilities", []),
                "methods_count": len(metadata.get("methods", [])),
                "file_path": adapter_info["file_path"],
                "registered_at": adapter_info["registered_at"]
            })
        
        return sorted(adapters, key=lambda x: (x["category"], x["name"]))
    
    def get_categories(self) -> Dict[str, Any]:
        """獲取適配器分類統計"""
        categories = {}
        
        for category_id, category_name in self.adapter_categories.items():
            count = sum(1 for info in self.registered_adapters.values() 
                       if info["category"] == category_id)
            
            if count > 0:
                categories[category_id] = {
                    "name": category_name,
                    "count": count,
                    "adapters": [adapter_id for adapter_id, info in self.registered_adapters.items()
                               if info["category"] == category_id]
                }
        
        return categories
    
    def search_adapters(self, query: str) -> List[Dict[str, Any]]:
        """搜索適配器"""
        query_lower = query.lower()
        results = []
        
        for adapter_id, adapter_info in self.registered_adapters.items():
            metadata = self.adapter_metadata.get(adapter_id, {})
            
            # 搜索匹配
            score = 0
            if query_lower in adapter_id.lower():
                score += 3
            if query_lower in adapter_info["name"].lower():
                score += 2
            if query_lower in metadata.get("description", "").lower():
                score += 1
            
            # 搜索能力
            for capability in metadata.get("capabilities", []):
                if query_lower in capability.lower():
                    score += 2
            
            if score > 0:
                result = {
                    "id": adapter_id,
                    "name": adapter_info["name"],
                    "category": adapter_info["category"],
                    "description": metadata.get("description", "無描述"),
                    "score": score
                }
                results.append(result)
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def get_adapter_info(self, adapter_id: str) -> Dict[str, Any]:
        """獲取適配器詳細信息"""
        if adapter_id not in self.registered_adapters:
            raise ValueError(f"未找到適配器: {adapter_id}")
        
        adapter_info = self.registered_adapters[adapter_id]
        metadata = self.adapter_metadata.get(adapter_id, {})
        
        return {
            "id": adapter_id,
            "name": adapter_info["name"],
            "category": adapter_info["category"],
            "category_name": self.adapter_categories.get(adapter_info["category"], "未知"),
            "description": metadata.get("description", "無描述"),
            "capabilities": metadata.get("capabilities", []),
            "methods": metadata.get("methods", []),
            "file_path": adapter_info["file_path"],
            "module_path": adapter_info["module_path"],
            "registered_at": adapter_info["registered_at"],
            "has_instance": adapter_id in self.adapter_instances
        }
    
    def execute_adapter(self, adapter_id: str, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """執行適配器"""
        try:
            adapter = self.get_adapter(adapter_id, **kwargs)
            
            if not hasattr(adapter, 'process'):
                raise ValueError(f"適配器 {adapter_id} 沒有process方法")
            
            result = adapter.process(input_data)
            
            return {
                "status": "success",
                "adapter_id": adapter_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"執行適配器失敗 {adapter_id}: {e}")
            return {
                "status": "error",
                "adapter_id": adapter_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_registry_info(self) -> Dict[str, Any]:
        """獲取註冊表狀態"""
        return {
            "total_adapters": len(self.registered_adapters),
            "active_instances": len(self.adapter_instances),
            "categories": self.get_categories(),
            "adapters_root": self.adapters_root,
            "last_discovery": datetime.now().isoformat()
        }

# 全局註冊表實例
_global_registry = None

def get_global_registry() -> UnifiedAdapterRegistry:
    """獲取全局註冊表實例"""
    global _global_registry
    if _global_registry is None:
        _global_registry = UnifiedAdapterRegistry()
    return _global_registry

# 測試代碼
if __name__ == "__main__":
    # 創建註冊表
    registry = UnifiedAdapterRegistry()
    
    # 列出所有適配器
    print("=== 所有適配器 ===")
    adapters = registry.list_adapters()
    for adapter in adapters:
        print(f"- {adapter['id']}: {adapter['name']} ({adapter['category_name']})")
    
    # 獲取分類統計
    print(f"\n=== 分類統計 ===")
    categories = registry.get_categories()
    for cat_id, cat_info in categories.items():
        print(f"- {cat_info['name']}: {cat_info['count']} 個適配器")
    
    # 搜索適配器
    print(f"\n=== 搜索結果 (關鍵詞: 'config') ===")
    search_results = registry.search_adapters("config")
    for result in search_results:
        print(f"- {result['id']}: {result['name']} (評分: {result['score']})")
    
    # 獲取註冊表狀態
    print(f"\n=== 註冊表狀態 ===")
    status = registry.get_registry_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))

