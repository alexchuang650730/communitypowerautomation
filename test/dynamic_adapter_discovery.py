"""
動態適配器發現和工具創建系統

當系統需要某個功能但沒有對應適配器時，自動創建工具並註冊到系統中。
整合到測試流程中，支持RAG學習和RL-SRT對齊。
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import importlib.util
import inspect

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class ToolRequirement:
    """工具需求定義"""
    name: str
    description: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    priority: int = 1
    category: str = "general"

@dataclass
class AdapterDiscoveryResult:
    """適配器發現結果"""
    found: bool
    adapter_id: Optional[str] = None
    adapter_name: Optional[str] = None
    match_score: float = 0.0
    capabilities: List[str] = None
    created_new: bool = False
    creation_details: Optional[Dict[str, Any]] = None

class DynamicAdapterDiscovery:
    """動態適配器發現系統"""
    
    def __init__(self, project_root: str = None):
        """初始化動態發現系統"""
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.adapters_dir = self.project_root / "mcptool" / "adapters"
        self.generated_dir = self.adapters_dir / "generated"
        
        # 確保生成目錄存在
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # 適配器註冊表
        self.adapter_registry = None
        self._initialize_registry()
        
        # 工具創建模板
        self.tool_templates = self._load_tool_templates()
        
        # 發現歷史
        self.discovery_history: List[Dict[str, Any]] = []
        
        logger.info(f"動態適配器發現系統初始化完成")
    
    def _initialize_registry(self):
        """初始化適配器註冊表"""
        try:
            from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry
            self.adapter_registry = UnifiedAdapterRegistry()
            logger.info("適配器註冊表初始化成功")
        except ImportError as e:
            logger.warning(f"無法初始化適配器註冊表: {e}")
    
    def _load_tool_templates(self) -> Dict[str, str]:
        """載入工具創建模板"""
        return {
            "basic_mcp_adapter": '''"""
{description}

自動生成的MCP適配器
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{{name}}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子類必須實現此方法")
        
        def validate_input(self, input_data: Dict[str, Any]) -> bool:
            return True
        
        def get_capabilities(self) -> List[str]:
            return ["基礎MCP適配功能"]

class {class_name}(BaseMCP):
    """自動生成的{name}適配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="{name}")
        self.config = config or {{}}
        self.capabilities = {capabilities}
        self.is_available = True
        
        self.logger.info(f"{{self.name}} 適配器初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理輸入數據"""
        try:
            # 驗證輸入
            if not self.validate_input(input_data):
                return {{"error": "輸入數據驗證失敗"}}
            
            # 執行主要邏輯
            result = self._execute_main_logic(input_data)
            
            return {{
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }}
        
        except Exception as e:
            self.logger.error(f"處理失敗: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }}
    
    def _execute_main_logic(self, input_data: Dict[str, Any]) -> Any:
        """執行主要邏輯 - 需要根據具體需求實現"""
        # TODO: 實現具體的業務邏輯
        return {{"message": "功能實現中", "input": input_data}}
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        # TODO: 根據input_schema實現驗證邏輯
        return isinstance(input_data, dict)
    
    def get_capabilities(self) -> List[str]:
        """獲取適配器能力"""
        return self.capabilities
    
    def get_tool_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {{
            "name": "{name}",
            "description": "{description}",
            "capabilities": self.capabilities,
            "input_schema": {input_schema},
            "output_schema": {output_schema},
            "category": "{category}",
            "auto_generated": True,
            "created_at": datetime.now().isoformat()
        }}

# 創建適配器實例
def create_adapter(config: Optional[Dict] = None) -> {class_name}:
    """創建適配器實例"""
    return {class_name}(config)
''',
            
            "advanced_tool_adapter": '''"""
{description}

高級自動生成的工具適配器，支持多種操作模式
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from abc import ABC, abstractmethod

try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{{name}}")

class {class_name}(BaseMCP):
    """高級自動生成的{name}適配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="{name}")
        self.config = config or {{}}
        self.capabilities = {capabilities}
        self.is_available = True
        
        # 工具註冊表
        self.tools: Dict[str, Callable] = {{}}
        self._register_default_tools()
        
        # 執行統計
        self.metrics = {{
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0
        }}
        
        self.logger.info(f"{{self.name}} 高級適配器初始化完成")
    
    def _register_default_tools(self):
        """註冊默認工具"""
        self.tools.update({{
            "process_data": self._process_data_tool,
            "analyze_input": self._analyze_input_tool,
            "generate_output": self._generate_output_tool,
            "validate_result": self._validate_result_tool
        }})
    
    async def execute_tool(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行指定工具"""
        start_time = datetime.now()
        
        try:
            if tool_name not in self.tools:
                return {{
                    "success": False,
                    "error": f"工具不存在: {{tool_name}}",
                    "available_tools": list(self.tools.keys())
                }}
            
            # 執行工具
            tool_func = self.tools[tool_name]
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(input_data)
            else:
                result = tool_func(input_data)
            
            # 更新統計
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(True, execution_time)
            
            return {{
                "success": True,
                "tool": tool_name,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }}
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(False, execution_time)
            
            self.logger.error(f"工具執行失敗: {{tool_name}} - {{e}}")
            return {{
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }}
    
    def _process_data_tool(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """數據處理工具"""
        # TODO: 實現數據處理邏輯
        return {{"processed": True, "data": input_data}}
    
    def _analyze_input_tool(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """輸入分析工具"""
        # TODO: 實現輸入分析邏輯
        analysis = {{
            "type": type(input_data).__name__,
            "size": len(str(input_data)),
            "keys": list(input_data.keys()) if isinstance(input_data, dict) else []
        }}
        return {{"analysis": analysis}}
    
    def _generate_output_tool(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """輸出生成工具"""
        # TODO: 實現輸出生成邏輯
        return {{"generated": True, "output": f"Generated from {{input_data}}"}}
    
    def _validate_result_tool(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """結果驗證工具"""
        # TODO: 實現結果驗證邏輯
        is_valid = isinstance(input_data, dict) and "result" in input_data
        return {{"valid": is_valid, "validation_details": {{"has_result": "result" in input_data}}}}
    
    def _update_metrics(self, success: bool, execution_time: float):
        """更新執行統計"""
        self.metrics["total_executions"] += 1
        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1
        
        # 更新平均執行時間
        total_time = self.metrics["average_execution_time"] * (self.metrics["total_executions"] - 1)
        self.metrics["average_execution_time"] = (total_time + execution_time) / self.metrics["total_executions"]
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取執行統計"""
        return self.metrics.copy()
    
    def register_custom_tool(self, name: str, tool_func: Callable):
        """註冊自定義工具"""
        self.tools[name] = tool_func
        self.logger.info(f"註冊自定義工具: {{name}}")
    
    def list_tools(self) -> List[str]:
        """列出所有可用工具"""
        return list(self.tools.keys())
    
    def get_tool_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {{
            "name": "{name}",
            "description": "{description}",
            "capabilities": self.capabilities,
            "available_tools": self.list_tools(),
            "input_schema": {input_schema},
            "output_schema": {output_schema},
            "category": "{category}",
            "auto_generated": True,
            "advanced_features": True,
            "metrics": self.get_metrics(),
            "created_at": datetime.now().isoformat()
        }}

# 創建適配器實例
def create_adapter(config: Optional[Dict] = None) -> {class_name}:
    """創建高級適配器實例"""
    return {class_name}(config)
'''
        }
    
    async def discover_adapter(self, requirement: ToolRequirement) -> AdapterDiscoveryResult:
        """發現或創建適配器"""
        logger.info(f"開始發現適配器: {requirement.name}")
        
        # 1. 首先嘗試在現有適配器中查找
        existing_result = await self._search_existing_adapters(requirement)
        if existing_result.found and existing_result.match_score > 0.8:
            logger.info(f"找到匹配的現有適配器: {existing_result.adapter_id}")
            return existing_result
        
        # 2. 如果沒有找到合適的適配器，創建新的
        logger.info(f"未找到合適的適配器，開始創建新適配器")
        creation_result = await self._create_new_adapter(requirement)
        
        # 3. 記錄發現歷史
        self._record_discovery(requirement, creation_result)
        
        return creation_result
    
    async def _search_existing_adapters(self, requirement: ToolRequirement) -> AdapterDiscoveryResult:
        """搜索現有適配器"""
        if not self.adapter_registry:
            return AdapterDiscoveryResult(found=False)
        
        try:
            # 獲取所有適配器
            adapters = self.adapter_registry.list_adapters()
            
            best_match = None
            best_score = 0.0
            
            for adapter in adapters:
                # 計算匹配分數
                score = self._calculate_match_score(requirement, adapter)
                if score > best_score:
                    best_score = score
                    best_match = adapter
            
            if best_match and best_score > 0.5:  # 閾值可調整
                return AdapterDiscoveryResult(
                    found=True,
                    adapter_id=best_match["id"],
                    adapter_name=best_match["name"],
                    match_score=best_score,
                    capabilities=best_match.get("capabilities", [])
                )
            
        except Exception as e:
            logger.error(f"搜索現有適配器失敗: {e}")
        
        return AdapterDiscoveryResult(found=False)
    
    def _calculate_match_score(self, requirement: ToolRequirement, adapter: Dict[str, Any]) -> float:
        """計算適配器匹配分數"""
        score = 0.0
        
        # 1. 名稱相似度 (30%)
        name_similarity = self._calculate_text_similarity(
            requirement.name.lower(), 
            adapter.get("name", "").lower()
        )
        score += name_similarity * 0.3
        
        # 2. 描述相似度 (20%)
        desc_similarity = self._calculate_text_similarity(
            requirement.description.lower(),
            adapter.get("description", "").lower()
        )
        score += desc_similarity * 0.2
        
        # 3. 能力匹配度 (40%)
        adapter_capabilities = adapter.get("capabilities", [])
        if adapter_capabilities:
            capability_matches = 0
            for req_cap in requirement.capabilities:
                for adapter_cap in adapter_capabilities:
                    if req_cap.lower() in adapter_cap.lower() or adapter_cap.lower() in req_cap.lower():
                        capability_matches += 1
                        break
            
            capability_score = capability_matches / len(requirement.capabilities)
            score += capability_score * 0.4
        
        # 4. 分類匹配 (10%)
        if requirement.category.lower() in adapter.get("category_name", "").lower():
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似度（簡化實現）"""
        if not text1 or not text2:
            return 0.0
        
        # 簡單的詞匯重疊計算
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _create_new_adapter(self, requirement: ToolRequirement) -> AdapterDiscoveryResult:
        """創建新適配器"""
        try:
            # 生成適配器代碼
            adapter_code = self._generate_adapter_code(requirement)
            
            # 保存適配器文件
            adapter_filename = f"{requirement.name.lower().replace(' ', '_')}_adapter.py"
            adapter_path = self.generated_dir / adapter_filename
            
            with open(adapter_path, 'w', encoding='utf-8') as f:
                f.write(adapter_code)
            
            # 嘗試動態載入適配器
            adapter_module = self._load_adapter_module(adapter_path)
            
            # 註冊到適配器註冊表
            if self.adapter_registry and adapter_module:
                self._register_new_adapter(requirement, adapter_module)
            
            creation_details = {
                "adapter_file": str(adapter_path),
                "code_lines": len(adapter_code.split('\n')),
                "template_used": self._select_template(requirement),
                "capabilities_implemented": requirement.capabilities
            }
            
            logger.info(f"成功創建新適配器: {requirement.name}")
            
            return AdapterDiscoveryResult(
                found=True,
                adapter_id=f"generated.{requirement.name.lower().replace(' ', '_')}",
                adapter_name=requirement.name,
                match_score=1.0,
                capabilities=requirement.capabilities,
                created_new=True,
                creation_details=creation_details
            )
        
        except Exception as e:
            logger.error(f"創建新適配器失敗: {e}")
            return AdapterDiscoveryResult(
                found=False,
                created_new=False,
                creation_details={"error": str(e)}
            )
    
    def _generate_adapter_code(self, requirement: ToolRequirement) -> str:
        """生成適配器代碼"""
        template_name = self._select_template(requirement)
        template = self.tool_templates[template_name]
        
        # 生成類名
        class_name = ''.join(word.capitalize() for word in requirement.name.split()) + "MCP"
        
        # 填充模板
        code = template.format(
            name=requirement.name,
            description=requirement.description,
            class_name=class_name,
            capabilities=json.dumps(requirement.capabilities, ensure_ascii=False),
            input_schema=json.dumps(requirement.input_schema, ensure_ascii=False, indent=8),
            output_schema=json.dumps(requirement.output_schema, ensure_ascii=False, indent=8),
            category=requirement.category
        )
        
        return code
    
    def _select_template(self, requirement: ToolRequirement) -> str:
        """選擇適當的模板"""
        # 根據需求複雜度選擇模板
        if len(requirement.capabilities) > 3 or requirement.priority > 5:
            return "advanced_tool_adapter"
        else:
            return "basic_mcp_adapter"
    
    def _load_adapter_module(self, adapter_path: Path):
        """動態載入適配器模塊"""
        try:
            spec = importlib.util.spec_from_file_location("generated_adapter", adapter_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"載入適配器模塊失敗: {e}")
            return None
    
    def _register_new_adapter(self, requirement: ToolRequirement, adapter_module):
        """註冊新適配器到註冊表"""
        try:
            # 這裡需要根據實際的註冊表API進行調整
            logger.info(f"註冊新適配器: {requirement.name}")
        except Exception as e:
            logger.error(f"註冊適配器失敗: {e}")
    
    def _record_discovery(self, requirement: ToolRequirement, result: AdapterDiscoveryResult):
        """記錄發現歷史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "requirement": {
                "name": requirement.name,
                "description": requirement.description,
                "capabilities": requirement.capabilities,
                "category": requirement.category,
                "priority": requirement.priority
            },
            "result": {
                "found": result.found,
                "adapter_id": result.adapter_id,
                "adapter_name": result.adapter_name,
                "match_score": result.match_score,
                "created_new": result.created_new,
                "creation_details": result.creation_details
            }
        }
        
        self.discovery_history.append(record)
        
        # 保存歷史記錄
        self._save_discovery_history()
    
    def _save_discovery_history(self):
        """保存發現歷史"""
        history_file = self.project_root / "test" / "results" / "adapter_discovery_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.discovery_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存發現歷史失敗: {e}")
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """獲取發現統計"""
        total_discoveries = len(self.discovery_history)
        successful_discoveries = len([r for r in self.discovery_history if r["result"]["found"]])
        new_creations = len([r for r in self.discovery_history if r["result"]["created_new"]])
        
        return {
            "total_discoveries": total_discoveries,
            "successful_discoveries": successful_discoveries,
            "success_rate": successful_discoveries / total_discoveries if total_discoveries > 0 else 0,
            "new_creations": new_creations,
            "creation_rate": new_creations / total_discoveries if total_discoveries > 0 else 0,
            "categories_covered": list(set(r["requirement"]["category"] for r in self.discovery_history)),
            "average_match_score": sum(r["result"]["match_score"] for r in self.discovery_history if r["result"]["found"]) / max(successful_discoveries, 1)
        }


class DynamicDiscoveryTestSuite:
    """動態發現測試套件"""
    
    def __init__(self, discovery_system: DynamicAdapterDiscovery):
        self.discovery_system = discovery_system
        self.test_requirements = self._generate_test_requirements()
    
    def _generate_test_requirements(self) -> List[ToolRequirement]:
        """生成測試需求"""
        return [
            ToolRequirement(
                name="文檔分析器",
                description="分析和提取文檔內容的工具",
                capabilities=["document_parsing", "content_extraction", "text_analysis"],
                input_schema={"document_path": "string", "format": "string"},
                output_schema={"content": "string", "metadata": "object"},
                priority=3,
                category="document_processing"
            ),
            ToolRequirement(
                name="數據可視化生成器",
                description="根據數據生成圖表和可視化",
                capabilities=["chart_generation", "data_visualization", "export_formats"],
                input_schema={"data": "array", "chart_type": "string", "options": "object"},
                output_schema={"chart_url": "string", "chart_data": "object"},
                priority=5,
                category="data_analysis"
            ),
            ToolRequirement(
                name="API測試工具",
                description="自動化API端點測試",
                capabilities=["api_testing", "endpoint_validation", "response_analysis"],
                input_schema={"endpoint": "string", "method": "string", "headers": "object"},
                output_schema={"status": "string", "response": "object", "metrics": "object"},
                priority=4,
                category="testing"
            )
        ]
    
    async def run_discovery_tests(self) -> Dict[str, Any]:
        """運行動態發現測試"""
        results = []
        
        for requirement in self.test_requirements:
            logger.info(f"測試需求: {requirement.name}")
            
            start_time = datetime.now()
            discovery_result = await self.discovery_system.discover_adapter(requirement)
            duration = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                "requirement": requirement.name,
                "success": discovery_result.found,
                "created_new": discovery_result.created_new,
                "match_score": discovery_result.match_score,
                "duration": duration,
                "details": discovery_result.creation_details
            }
            
            results.append(test_result)
        
        # 生成測試報告
        return {
            "test_suite": "dynamic_discovery",
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r["success"]]),
            "new_adapters_created": len([r for r in results if r["created_new"]]),
            "average_duration": sum(r["duration"] for r in results) / len(results),
            "results": results,
            "statistics": self.discovery_system.get_discovery_statistics(),
            "timestamp": datetime.now().isoformat()
        }


# 全局動態發現系統實例
_discovery_system = None

def get_discovery_system() -> DynamicAdapterDiscovery:
    """獲取全局動態發現系統實例"""
    global _discovery_system
    if _discovery_system is None:
        _discovery_system = DynamicAdapterDiscovery()
    return _discovery_system


if __name__ == "__main__":
    # 示例使用
    async def main():
        discovery = get_discovery_system()
        test_suite = DynamicDiscoveryTestSuite(discovery)
        
        # 運行動態發現測試
        results = await test_suite.run_discovery_tests()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    asyncio.run(main())

