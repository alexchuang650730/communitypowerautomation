"""
PowerAutomation 完整測試層級方案設計

基於之前設計的10個測試層級，為每個層級創建詳細的測試方案，
包括測試用例、測試數據、預期結果、成功標準等。
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import unittest
import pytest
from abc import ABC, abstractmethod

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """測試用例定義"""
    id: str
    name: str
    description: str
    category: str
    priority: int  # 1-5, 5最高
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    success_criteria: List[str]
    timeout: int = 30  # 秒
    dependencies: List[str] = None
    tags: List[str] = None

@dataclass
class TestSuite:
    """測試套件定義"""
    id: str
    name: str
    description: str
    level: int  # 測試層級 1-10
    test_cases: List[TestCase]
    setup_requirements: List[str]
    teardown_requirements: List[str]
    parallel_execution: bool = False
    estimated_duration: int = 0  # 分鐘

@dataclass
class TestResult:
    """測試結果"""
    test_case_id: str
    status: str  # passed, failed, skipped, error
    execution_time: float
    output: Dict[str, Any]
    error_message: str = None
    timestamp: str = None

class TestLevelManager:
    """測試層級管理器"""
    
    def __init__(self, project_root: str = None):
        """初始化測試層級管理器"""
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.test_suites: Dict[int, TestSuite] = {}
        self.test_results: List[TestResult] = []
        
        # 初始化所有測試層級
        self._initialize_test_levels()
        
        logger.info("測試層級管理器初始化完成")
    
    def _initialize_test_levels(self):
        """初始化所有測試層級"""
        # 1. 單元測試層級
        self.test_suites[1] = self._create_unit_test_suite()
        
        # 2. 集成測試層級
        self.test_suites[2] = self._create_integration_test_suite()
        
        # 3. MCP合規測試層級
        self.test_suites[3] = self._create_mcp_compliance_test_suite()
        
        # 4. 端到端測試層級
        self.test_suites[4] = self._create_e2e_test_suite()
        
        # 5. 性能測試層級
        self.test_suites[5] = self._create_performance_test_suite()
        
        # 6. GAIA基準測試層級
        self.test_suites[6] = self._create_gaia_benchmark_test_suite()
        
        # 7. 動態發現測試層級
        self.test_suites[7] = self._create_dynamic_discovery_test_suite()
        
        # 8. RAG學習測試層級
        self.test_suites[8] = self._create_rag_learning_test_suite()
        
        # 9. RL-SRT對齊測試層級
        self.test_suites[9] = self._create_rl_srt_alignment_test_suite()
        
        # 10. 自動化測試層級
        self.test_suites[10] = self._create_automation_test_suite()
        
        # 11. MCP完整性測試層級 (新增)
        self.test_suites[11] = self._create_mcp_integrity_test_suite()
    
    def _create_unit_test_suite(self) -> TestSuite:
        """創建單元測試套件"""
        test_cases = [
            TestCase(
                id="unit_001",
                name="BaseMCP初始化測試",
                description="測試BaseMCP基類的初始化功能",
                category="core",
                priority=5,
                input_data={"name": "TestMCP", "config": {}},
                expected_output={"success": True, "name": "TestMCP"},
                success_criteria=["對象成功創建", "名稱正確設置", "日誌器正確初始化"]
            ),
            TestCase(
                id="unit_002", 
                name="UnifiedAdapterRegistry註冊測試",
                description="測試適配器註冊表的註冊和查詢功能",
                category="core",
                priority=5,
                input_data={"adapter_name": "test_adapter", "adapter_config": {}},
                expected_output={"registered": True, "adapter_count": 1},
                success_criteria=["適配器成功註冊", "可以查詢到適配器", "統計信息正確"]
            ),
            TestCase(
                id="unit_003",
                name="ThoughtActionRecorder記錄測試", 
                description="測試思維行動記錄器的基本記錄功能",
                category="core",
                priority=4,
                input_data={"session_id": "test_session", "thought": "測試思維"},
                expected_output={"recorded": True, "session_exists": True},
                success_criteria=["會話成功創建", "思維成功記錄", "數據持久化正確"]
            ),
            TestCase(
                id="unit_004",
                name="IntentAnalyzer意圖分析測試",
                description="測試意圖分析器的意圖識別功能",
                category="ai",
                priority=4,
                input_data={"user_input": "我需要一個PDF分析工具"},
                expected_output={"intent": "create_tool", "confidence": 0.8},
                success_criteria=["意圖正確識別", "信心度合理", "能力正確提取"]
            ),
            TestCase(
                id="unit_005",
                name="KiloCodeIntegration代碼生成測試",
                description="測試Kilo Code集成的代碼生成功能",
                category="ai",
                priority=3,
                input_data={"requirement": "data_analysis_tool"},
                expected_output={"code_generated": True, "code_length": 500},
                success_criteria=["代碼成功生成", "代碼長度合理", "語法正確"]
            )
        ]
        
        return TestSuite(
            id="unit_tests",
            name="單元測試套件",
            description="測試各個組件的基本功能",
            level=1,
            test_cases=test_cases,
            setup_requirements=["初始化測試環境", "清理測試數據"],
            teardown_requirements=["清理測試對象", "重置環境"],
            parallel_execution=True,
            estimated_duration=15
        )
    
    def _create_integration_test_suite(self) -> TestSuite:
        """創建集成測試套件"""
        test_cases = [
            TestCase(
                id="integration_001",
                name="適配器註冊表與MCP集成測試",
                description="測試適配器註冊表與MCP適配器的集成",
                category="integration",
                priority=5,
                input_data={"register_adapters": ["webagent", "thought_recorder"]},
                expected_output={"all_registered": True, "total_adapters": 2},
                success_criteria=["所有適配器成功註冊", "可以查詢所有適配器", "狀態正確"]
            ),
            TestCase(
                id="integration_002",
                name="智能意圖處理器集成測試",
                description="測試智能意圖處理器與各組件的集成",
                category="integration", 
                priority=5,
                input_data={"user_intent": "創建數據分析工具"},
                expected_output={"processing_success": True, "tool_created": True},
                success_criteria=["意圖成功處理", "工具成功創建", "記錄完整"]
            ),
            TestCase(
                id="integration_003",
                name="動態適配器發現與創建集成測試",
                description="測試動態適配器發現與工具創建的集成流程",
                category="integration",
                priority=4,
                input_data={"requirement": "web_scraping_tool"},
                expected_output={"adapter_created": True, "registered": True},
                success_criteria=["適配器成功創建", "自動註冊", "功能可用"]
            ),
            TestCase(
                id="integration_004",
                name="RAG學習與RL-SRT對齊集成測試",
                description="測試RAG學習系統與RL-SRT對齊的集成",
                category="integration",
                priority=3,
                input_data={"learning_sessions": 5, "alignment_data": True},
                expected_output={"rag_data_generated": True, "alignment_score": 0.8},
                success_criteria=["RAG數據生成", "對齊分數合理", "學習效果明顯"]
            )
        ]
        
        return TestSuite(
            id="integration_tests",
            name="集成測試套件", 
            description="測試組件間的集成和協作",
            level=2,
            test_cases=test_cases,
            setup_requirements=["啟動所有服務", "初始化數據庫"],
            teardown_requirements=["停止服務", "清理數據"],
            parallel_execution=False,
            estimated_duration=30
        )
    
    def _create_mcp_compliance_test_suite(self) -> TestSuite:
        """創建MCP合規測試套件"""
        test_cases = [
            TestCase(
                id="mcp_001",
                name="MCP協議合規性測試",
                description="測試所有適配器是否符合MCP協議標準",
                category="compliance",
                priority=5,
                input_data={"check_all_adapters": True},
                expected_output={"compliance_rate": 1.0, "violations": 0},
                success_criteria=["100%合規率", "無協議違規", "標準接口實現"]
            ),
            TestCase(
                id="mcp_002",
                name="MCP工具註冊測試",
                description="測試MCP工具的註冊和發現機制",
                category="compliance",
                priority=4,
                input_data={"register_tools": ["start_session", "record_thought"]},
                expected_output={"tools_registered": True, "discoverable": True},
                success_criteria=["工具成功註冊", "可以發現工具", "元數據正確"]
            ),
            TestCase(
                id="mcp_003",
                name="MCP錯誤處理測試",
                description="測試MCP適配器的錯誤處理機制",
                category="compliance",
                priority=4,
                input_data={"invalid_input": True, "error_scenarios": 5},
                expected_output={"errors_handled": True, "graceful_degradation": True},
                success_criteria=["錯誤正確處理", "優雅降級", "錯誤信息清晰"]
            )
        ]
        
        return TestSuite(
            id="mcp_compliance_tests",
            name="MCP合規測試套件",
            description="驗證MCP協議合規性",
            level=3,
            test_cases=test_cases,
            setup_requirements=["MCP服務器啟動", "協議檢查工具"],
            teardown_requirements=["停止MCP服務器"],
            parallel_execution=True,
            estimated_duration=20
        )
    
    def _create_e2e_test_suite(self) -> TestSuite:
        """創建端到端測試套件"""
        test_cases = [
            TestCase(
                id="e2e_001",
                name="完整工作流端到端測試",
                description="測試從用戶輸入到工具創建的完整流程",
                category="workflow",
                priority=5,
                input_data={
                    "user_input": "我需要分析這個CSV文件的數據",
                    "file_path": "test_data.csv"
                },
                expected_output={
                    "workflow_completed": True,
                    "tool_created": True,
                    "analysis_result": True
                },
                success_criteria=["完整流程執行", "工具成功創建", "分析結果正確"]
            ),
            TestCase(
                id="e2e_002",
                name="多輪對話端到端測試",
                description="測試多輪對話中的上下文保持和工具複用",
                category="workflow",
                priority=4,
                input_data={
                    "conversation_rounds": 3,
                    "context_required": True
                },
                expected_output={
                    "context_maintained": True,
                    "tools_reused": True,
                    "conversation_coherent": True
                },
                success_criteria=["上下文保持", "工具複用", "對話連貫"]
            ),
            TestCase(
                id="e2e_003",
                name="錯誤恢復端到端測試",
                description="測試系統在錯誤情況下的恢復能力",
                category="reliability",
                priority=4,
                input_data={
                    "inject_errors": True,
                    "error_types": ["network", "timeout", "invalid_input"]
                },
                expected_output={
                    "errors_recovered": True,
                    "system_stable": True,
                    "user_notified": True
                },
                success_criteria=["錯誤成功恢復", "系統保持穩定", "用戶得到通知"]
            )
        ]
        
        return TestSuite(
            id="e2e_tests",
            name="端到端測試套件",
            description="測試完整的用戶工作流",
            level=4,
            test_cases=test_cases,
            setup_requirements=["完整系統啟動", "測試數據準備"],
            teardown_requirements=["系統清理", "數據清理"],
            parallel_execution=False,
            estimated_duration=45
        )
    
    def _create_performance_test_suite(self) -> TestSuite:
        """創建性能測試套件"""
        test_cases = [
            TestCase(
                id="perf_001",
                name="適配器載入性能測試",
                description="測試適配器載入的性能和內存使用",
                category="performance",
                priority=4,
                input_data={"adapter_count": 20, "concurrent_loads": 5},
                expected_output={
                    "load_time": 5.0,  # 秒
                    "memory_usage": 100,  # MB
                    "success_rate": 1.0
                },
                success_criteria=["載入時間<5秒", "內存使用<100MB", "100%成功率"]
            ),
            TestCase(
                id="perf_002",
                name="意圖處理性能測試",
                description="測試意圖處理的響應時間和吞吐量",
                category="performance",
                priority=4,
                input_data={"concurrent_requests": 10, "request_count": 100},
                expected_output={
                    "avg_response_time": 1.0,  # 秒
                    "throughput": 50,  # 請求/秒
                    "error_rate": 0.01
                },
                success_criteria=["平均響應時間<1秒", "吞吐量>50/秒", "錯誤率<1%"]
            ),
            TestCase(
                id="perf_003",
                name="大數據處理性能測試",
                description="測試系統處理大量數據的性能",
                category="performance",
                priority=3,
                input_data={"data_size": "10MB", "processing_type": "analysis"},
                expected_output={
                    "processing_time": 30.0,  # 秒
                    "memory_peak": 200,  # MB
                    "cpu_usage": 0.8
                },
                success_criteria=["處理時間<30秒", "內存峰值<200MB", "CPU使用<80%"]
            )
        ]
        
        return TestSuite(
            id="performance_tests",
            name="性能測試套件",
            description="測試系統性能和資源使用",
            level=5,
            test_cases=test_cases,
            setup_requirements=["性能監控工具", "測試數據生成"],
            teardown_requirements=["性能報告生成", "資源清理"],
            parallel_execution=True,
            estimated_duration=60
        )
    
    def _create_gaia_benchmark_test_suite(self) -> TestSuite:
        """創建GAIA基準測試套件"""
        test_cases = [
            TestCase(
                id="gaia_001",
                name="GAIA Level 1 基準測試",
                description="測試系統在GAIA Level 1任務上的表現",
                category="benchmark",
                priority=5,
                input_data={"gaia_level": 1, "task_count": 10},
                expected_output={
                    "accuracy": 0.85,
                    "completion_rate": 0.9,
                    "avg_time": 120  # 秒
                },
                success_criteria=["準確率>85%", "完成率>90%", "平均時間<2分鐘"]
            ),
            TestCase(
                id="gaia_002",
                name="GAIA Level 2 基準測試",
                description="測試系統在GAIA Level 2任務上的表現",
                category="benchmark",
                priority=4,
                input_data={"gaia_level": 2, "task_count": 10},
                expected_output={
                    "accuracy": 0.75,
                    "completion_rate": 0.8,
                    "avg_time": 300  # 秒
                },
                success_criteria=["準確率>75%", "完成率>80%", "平均時間<5分鐘"]
            ),
            TestCase(
                id="gaia_003",
                name="GAIA Level 3 基準測試",
                description="測試系統在GAIA Level 3任務上的表現",
                category="benchmark",
                priority=3,
                input_data={"gaia_level": 3, "task_count": 5},
                expected_output={
                    "accuracy": 0.6,
                    "completion_rate": 0.7,
                    "avg_time": 600  # 秒
                },
                success_criteria=["準確率>60%", "完成率>70%", "平均時間<10分鐘"]
            )
        ]
        
        return TestSuite(
            id="gaia_benchmark_tests",
            name="GAIA基準測試套件",
            description="使用GAIA數據集評估系統能力",
            level=6,
            test_cases=test_cases,
            setup_requirements=["GAIA數據集下載", "評估環境準備"],
            teardown_requirements=["結果分析", "報告生成"],
            parallel_execution=False,
            estimated_duration=120
        )
    
    def _create_dynamic_discovery_test_suite(self) -> TestSuite:
        """創建動態發現測試套件"""
        test_cases = [
            TestCase(
                id="discovery_001",
                name="適配器自動發現測試",
                description="測試系統自動發現現有適配器的能力",
                category="discovery",
                priority=4,
                input_data={"search_query": "data analysis", "existing_adapters": 5},
                expected_output={
                    "adapters_found": 3,
                    "match_scores": [0.9, 0.8, 0.7],
                    "discovery_time": 2.0
                },
                success_criteria=["找到相關適配器", "匹配分數合理", "發現時間<2秒"]
            ),
            TestCase(
                id="discovery_002",
                name="工具自動創建測試",
                description="測試系統在沒有合適工具時自動創建的能力",
                category="creation",
                priority=5,
                input_data={"requirement": "image_processing", "no_existing": True},
                expected_output={
                    "tool_created": True,
                    "code_generated": True,
                    "registration_success": True
                },
                success_criteria=["工具成功創建", "代碼生成正確", "自動註冊成功"]
            ),
            TestCase(
                id="discovery_003",
                name="學習反饋循環測試",
                description="測試系統從使用反饋中學習改進的能力",
                category="learning",
                priority=3,
                input_data={"feedback_cycles": 3, "improvement_expected": True},
                expected_output={
                    "learning_occurred": True,
                    "performance_improved": True,
                    "adaptation_successful": True
                },
                success_criteria=["學習效果明顯", "性能有改善", "適應成功"]
            )
        ]
        
        return TestSuite(
            id="dynamic_discovery_tests",
            name="動態發現測試套件",
            description="測試適配器自動發現和創建",
            level=7,
            test_cases=test_cases,
            setup_requirements=["發現引擎初始化", "創建模板準備"],
            teardown_requirements=["清理創建的工具", "重置學習狀態"],
            parallel_execution=True,
            estimated_duration=40
        )
    
    def _create_rag_learning_test_suite(self) -> TestSuite:
        """創建RAG學習測試套件"""
        test_cases = [
            TestCase(
                id="rag_001",
                name="知識提取測試",
                description="測試從交互中提取知識的能力",
                category="knowledge_extraction",
                priority=4,
                input_data={"interactions": 10, "knowledge_types": ["factual", "procedural"]},
                expected_output={
                    "knowledge_extracted": 8,
                    "quality_score": 0.8,
                    "categorization_accuracy": 0.9
                },
                success_criteria=["知識提取率>80%", "質量分數>0.8", "分類準確率>90%"]
            ),
            TestCase(
                id="rag_002",
                name="知識存儲測試",
                description="測試知識的結構化存儲和索引",
                category="knowledge_storage",
                priority=4,
                input_data={"knowledge_items": 100, "storage_format": "vector"},
                expected_output={
                    "storage_success": True,
                    "retrieval_speed": 0.1,  # 秒
                    "index_accuracy": 0.95
                },
                success_criteria=["存儲成功", "檢索速度<0.1秒", "索引準確率>95%"]
            ),
            TestCase(
                id="rag_003",
                name="知識應用測試",
                description="測試存儲的知識在新任務中的應用效果",
                category="knowledge_application",
                priority=5,
                input_data={"new_tasks": 5, "knowledge_base_size": 1000},
                expected_output={
                    "application_success": 4,
                    "performance_improvement": 0.3,
                    "relevance_score": 0.85
                },
                success_criteria=["應用成功率>80%", "性能提升>30%", "相關性>85%"]
            )
        ]
        
        return TestSuite(
            id="rag_learning_tests",
            name="RAG學習測試套件",
            description="測試知識存儲和學習效果",
            level=8,
            test_cases=test_cases,
            setup_requirements=["RAG系統初始化", "知識庫準備"],
            teardown_requirements=["知識庫清理", "學習狀態重置"],
            parallel_execution=False,
            estimated_duration=50
        )
    
    def _create_rl_srt_alignment_test_suite(self) -> TestSuite:
        """創建RL-SRT對齊測試套件"""
        test_cases = [
            TestCase(
                id="rl_srt_001",
                name="思維-行動對齊測試",
                description="測試思維過程與行動的對齊程度",
                category="alignment",
                priority=5,
                input_data={"thought_action_pairs": 20, "alignment_threshold": 0.8},
                expected_output={
                    "alignment_score": 0.85,
                    "consistency_rate": 0.9,
                    "improvement_trend": True
                },
                success_criteria=["對齊分數>0.8", "一致性>90%", "有改善趨勢"]
            ),
            TestCase(
                id="rl_srt_002",
                name="自我反思訓練測試",
                description="測試系統的自我反思和改進能力",
                category="self_reflection",
                priority=4,
                input_data={"reflection_cycles": 5, "performance_metrics": True},
                expected_output={
                    "reflection_quality": 0.8,
                    "self_improvement": True,
                    "meta_learning": True
                },
                success_criteria=["反思質量>0.8", "自我改進明顯", "元學習有效"]
            ),
            TestCase(
                id="rl_srt_003",
                name="強化學習優化測試",
                description="測試基於獎勵信號的系統優化",
                category="reinforcement_learning",
                priority=4,
                input_data={"training_episodes": 100, "reward_function": "success_rate"},
                expected_output={
                    "learning_curve_positive": True,
                    "final_performance": 0.9,
                    "convergence_achieved": True
                },
                success_criteria=["學習曲線上升", "最終性能>90%", "收斂成功"]
            )
        ]
        
        return TestSuite(
            id="rl_srt_alignment_tests",
            name="RL-SRT對齊測試套件",
            description="測試強化學習和自我反思訓練",
            level=9,
            test_cases=test_cases,
            setup_requirements=["RL環境初始化", "獎勵函數設置"],
            teardown_requirements=["模型保存", "訓練日誌清理"],
            parallel_execution=False,
            estimated_duration=90
        )
    
    def _create_automation_test_suite(self) -> TestSuite:
        """創建自動化測試套件"""
        test_cases = [
            TestCase(
                id="auto_001",
                name="完整自動化流程測試",
                description="測試從需求到部署的完整自動化流程",
                category="automation",
                priority=5,
                input_data={
                    "requirement": "web_scraper",
                    "auto_deploy": True,
                    "monitoring": True
                },
                expected_output={
                    "tool_created": True,
                    "deployed": True,
                    "monitoring_active": True,
                    "end_to_end_time": 300  # 秒
                },
                success_criteria=["工具成功創建", "自動部署成功", "監控啟動", "總時間<5分鐘"]
            ),
            TestCase(
                id="auto_002",
                name="自動化測試執行測試",
                description="測試測試套件的自動化執行能力",
                category="test_automation",
                priority=4,
                input_data={"test_suites": [1, 2, 3], "parallel": True},
                expected_output={
                    "all_suites_executed": True,
                    "results_generated": True,
                    "reports_created": True
                },
                success_criteria=["所有套件執行", "結果正確生成", "報告完整"]
            ),
            TestCase(
                id="auto_003",
                name="持續集成測試",
                description="測試系統的持續集成和部署能力",
                category="ci_cd",
                priority=3,
                input_data={"code_changes": 5, "auto_testing": True},
                expected_output={
                    "ci_triggered": True,
                    "tests_passed": True,
                    "deployment_successful": True
                },
                success_criteria=["CI成功觸發", "測試通過", "部署成功"]
            )
        ]
        
        return TestSuite(
            id="automation_tests",
            name="自動化測試套件",
            description="測試完整自動化流程",
            level=10,
            test_cases=test_cases,
            setup_requirements=["CI/CD環境", "自動化工具"],
            teardown_requirements=["環境清理", "部署回滾"],
            parallel_execution=False,
            estimated_duration=75
        )
    
    def get_test_suite(self, level: int) -> Optional[TestSuite]:
        """獲取指定層級的測試套件"""
        return self.test_suites.get(level)
    
    def get_all_test_suites(self) -> Dict[int, TestSuite]:
        """獲取所有測試套件"""
        return self.test_suites
    
    def get_test_dependencies(self) -> Dict[int, List[int]]:
        """獲取測試層級依賴關係"""
        return {
            1: [],  # 單元測試無依賴
            2: [1],  # 集成測試依賴單元測試
            3: [1, 2],  # MCP合規測試依賴前兩個
            4: [1, 2, 3],  # 端到端測試依賴前三個
            5: [1, 2],  # 性能測試依賴單元和集成
            6: [1, 2, 3, 4],  # GAIA基準測試依賴前四個
            7: [1, 2, 3],  # 動態發現測試依賴前三個
            8: [1, 2, 7],  # RAG學習測試依賴動態發現
            9: [1, 2, 7, 8],  # RL-SRT對齊測試依賴RAG學習
            10: [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 自動化測試依賴所有
        }
    
    def generate_test_plan(self) -> Dict[str, Any]:
        """生成完整的測試計劃"""
        dependencies = self.get_test_dependencies()
        total_duration = sum(suite.estimated_duration for suite in self.test_suites.values())
        total_test_cases = sum(len(suite.test_cases) for suite in self.test_suites.values())
        
        return {
            "test_plan_id": f"plan_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat(),
            "total_test_suites": len(self.test_suites),
            "total_test_cases": total_test_cases,
            "estimated_total_duration": total_duration,
            "test_levels": {
                level: {
                    "suite_name": suite.name,
                    "test_case_count": len(suite.test_cases),
                    "estimated_duration": suite.estimated_duration,
                    "dependencies": dependencies.get(level, []),
                    "parallel_execution": suite.parallel_execution
                }
                for level, suite in self.test_suites.items()
            },
            "execution_order": self._calculate_execution_order(dependencies),
            "critical_path": self._calculate_critical_path(),
            "resource_requirements": self._calculate_resource_requirements()
        }
    
    def _calculate_execution_order(self, dependencies: Dict[int, List[int]]) -> List[List[int]]:
        """計算測試執行順序（考慮依賴關係）"""
        # 拓撲排序算法
        in_degree = {level: 0 for level in self.test_suites.keys()}
        for level, deps in dependencies.items():
            in_degree[level] = len(deps)
        
        execution_order = []
        queue = [level for level, degree in in_degree.items() if degree == 0]
        
        while queue:
            current_batch = queue.copy()
            queue.clear()
            execution_order.append(current_batch)
            
            for level in current_batch:
                for next_level, deps in dependencies.items():
                    if level in deps:
                        in_degree[next_level] -= 1
                        if in_degree[next_level] == 0 and next_level not in queue:
                            queue.append(next_level)
        
        return execution_order
    
    def _calculate_critical_path(self) -> List[int]:
        """計算關鍵路徑（最長執行時間路徑）"""
        # 簡化版本：返回依賴最多的路徑
        dependencies = self.get_test_dependencies()
        max_deps = max(len(deps) for deps in dependencies.values())
        
        critical_path = []
        for level, deps in dependencies.items():
            if len(deps) == max_deps:
                critical_path = deps + [level]
                break
        
        return critical_path
    
    def _calculate_resource_requirements(self) -> Dict[str, Any]:
        """計算資源需求"""
        return {
            "cpu_cores": 4,
            "memory_gb": 8,
            "disk_space_gb": 20,
            "network_bandwidth": "100Mbps",
            "external_services": ["GAIA API", "Kilo Code API"],
            "test_data_size": "1GB",
            "concurrent_processes": 10
        }
    
    def export_test_plan(self, output_path: str = None) -> str:
        """導出測試計劃到文件"""
        if output_path is None:
            output_path = self.project_root / "test" / "results" / "test_plan.json"
        
        test_plan = self.generate_test_plan()
        
        # 確保目錄存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 導出測試計劃
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(test_plan, f, indent=2, ensure_ascii=False)
        
        logger.info(f"測試計劃已導出到: {output_path}")
        return str(output_path)


# 全局測試層級管理器實例
_test_manager = None

def get_test_manager() -> TestLevelManager:
    """獲取全局測試層級管理器實例"""
    global _test_manager
    if _test_manager is None:
        _test_manager = TestLevelManager()
    return _test_manager


if __name__ == "__main__":
    # 測試示例
    manager = get_test_manager()
    
    # 生成測試計劃
    test_plan = manager.generate_test_plan()
    print("測試計劃生成完成:")
    print(json.dumps(test_plan, indent=2, ensure_ascii=False))
    
    # 導出測試計劃
    plan_file = manager.export_test_plan()
    print(f"\n測試計劃已導出到: {plan_file}")
    
    # 顯示各層級測試套件信息
    print("\n各層級測試套件詳情:")
    for level, suite in manager.get_all_test_suites().items():
        print(f"\n層級 {level}: {suite.name}")
        print(f"  描述: {suite.description}")
        print(f"  測試用例數: {len(suite.test_cases)}")
        print(f"  預估時間: {suite.estimated_duration}分鐘")
        print(f"  並行執行: {suite.parallel_execution}")
        print(f"  測試用例:")
        for case in suite.test_cases:
            print(f"    - {case.id}: {case.name} (優先級: {case.priority})")

