# PowerAutomation 測試系統

PowerAutomation採用多層次的測試策略，確保系統的質量、可靠性和性能。

## 📋 測試目錄結構

```
test/
├── README.md                          # 測試系統總覽
├── ten_layer_test_executor.py         # 十層級測試執行器
├── unified_test_manager.py            # 統一測試管理器
├── comprehensive_test_framework.py    # 綜合測試框架
├── results/                           # 測試結果目錄
│   ├── ten_layer_test_results_latest.json
│   └── ci_ten_layer_results.json
├── unit/                              # 第1層級：單元測試
│   ├── test_base_mcp.py
│   ├── test_adapter_registry.py
│   ├── test_thought_recorder.py
│   ├── test_intent_analyzer.py
│   └── test_kilo_code.py
├── integration/                       # 第2層級：集成測試
│   ├── test_adapter_integration.py
│   ├── test_intent_processor.py
│   ├── test_rag_system.py
│   └── test_config_manager.py
├── mcp_compliance/                    # 第3層級：MCP合規測試
│   ├── test_mcp_protocol.py
│   ├── test_tool_registration.py
│   └── test_error_handling.py
├── e2e/                              # 第4層級：端到端測試
│   ├── test_tool_creation.py
│   ├── test_multi_turn_dialog.py
│   └── test_error_recovery.py
├── performance/                       # 第5層級：性能測試
│   ├── test_response_time.py
│   ├── test_throughput.py
│   ├── test_memory_usage.py
│   └── test_concurrent_load.py
├── security/                         # 第6層級：安全測試
│   ├── test_input_validation.py
│   ├── test_auth_security.py
│   ├── test_data_protection.py
│   └── test_vulnerability_scan.py
├── compatibility/                    # 第7層級：兼容性測試
│   ├── test_python_versions.py
│   ├── test_os_compatibility.py
│   └── test_dependency_versions.py
├── stress/                          # 第8層級：壓力測試
│   ├── test_high_load.py
│   ├── test_long_running.py
│   └── test_resource_limits.py
├── gaia/                            # 第9層級：GAIA基準測試
│   ├── gaia.py
│   └── gaia_test_runner.py
└── ai_capability/                   # 第10層級：AI能力評估
    ├── test_reasoning_ability.py
    ├── test_learning_capability.py
    └── test_adaptation_skills.py
```

## 🧪 測試層級說明

### 第1層級：單元測試 (Unit Tests)
**目標**: 驗證個別組件的功能正確性

**測試範圍**:
- BaseMCP基類功能
- 適配器註冊表
- 思維記錄器
- 意圖分析器
- KiloCode生成器

**執行方式**:
```bash
# 運行所有單元測試
python -m pytest test/unit/ -v

# 運行特定測試
python -m pytest test/unit/test_base_mcp.py -v

# 生成覆蓋率報告
python -m pytest test/unit/ --cov=mcptool --cov-report=html
```

### 第2層級：集成測試 (Integration Tests)
**目標**: 驗證組件間的交互和數據流

**測試範圍**:
- 適配器與MCP的集成
- 智能意圖處理器集成
- RAG學習系統集成
- 配置管理器集成

**執行方式**:
```bash
# 運行集成測試
python -m pytest test/integration/ -v

# 並行執行
python -m pytest test/integration/ -n auto
```

### 第3層級：MCP合規測試 (MCP Compliance Tests)
**目標**: 確保符合MCP協議標準

**測試範圍**:
- MCP協議格式驗證
- 工具註冊和發現機制
- 錯誤處理和恢復

**執行方式**:
```bash
# 運行MCP合規測試
python -m pytest test/mcp_compliance/ -v

# 驗證協議兼容性
python test/mcp_compliance/validate_protocol.py
```

### 第4層級：端到端測試 (End-to-End Tests)
**目標**: 驗證完整的用戶工作流程

**測試範圍**:
- 完整工具創建流程
- 多輪對話處理
- 錯誤恢復機制

**執行方式**:
```bash
# 運行端到端測試
python -m pytest test/e2e/ -v --tb=short

# 模擬真實用戶場景
python test/e2e/simulate_user_scenarios.py
```

### 第5層級：性能測試 (Performance Tests)
**目標**: 驗證系統性能指標

**測試範圍**:
- 響應時間測試
- 吞吐量測試
- 內存使用測試
- 並發負載測試

**執行方式**:
```bash
# 運行性能測試
python -m pytest test/performance/ -v

# 基準測試
python test/performance/benchmark_runner.py

# 生成性能報告
python test/performance/generate_report.py
```

### 第6層級：安全測試 (Security Tests)
**目標**: 識別安全漏洞和風險

**測試範圍**:
- 輸入驗證測試
- 身份認證安全
- 數據保護測試
- 漏洞掃描

**執行方式**:
```bash
# 運行安全測試
python -m pytest test/security/ -v

# 安全掃描
bandit -r mcptool/
safety check
semgrep --config=auto .
```

### 第7層級：兼容性測試 (Compatibility Tests)
**目標**: 確保跨平台和版本兼容性

**測試範圍**:
- Python版本兼容性
- 操作系統兼容性
- 依賴版本兼容性

**執行方式**:
```bash
# 運行兼容性測試
tox

# 特定Python版本測試
python3.8 -m pytest test/compatibility/
python3.9 -m pytest test/compatibility/
python3.10 -m pytest test/compatibility/
python3.11 -m pytest test/compatibility/
```

### 第8層級：壓力測試 (Stress Tests)
**目標**: 驗證系統在極限條件下的表現

**測試範圍**:
- 高負載測試
- 長時間運行測試
- 資源限制測試

**執行方式**:
```bash
# 運行壓力測試
python -m pytest test/stress/ -v --timeout=3600

# 負載測試
locust -f test/stress/load_test.py --host=http://localhost:8000
```

### 第9層級：GAIA基準測試 (GAIA Benchmark Tests)
**目標**: 評估AI能力和智能化水平

**測試範圍**:
- GAIA Level 1基準測試
- 問題分類和處理
- 工具選擇準確性
- 兜底機制效果

**執行方式**:
```bash
# 運行GAIA測試
python test/gaia/gaia.py

# 快速GAIA測試
python enhanced_gaia_system/integrated_gaia_test_v4.py

# 大規模GAIA測試
python enhanced_gaia_system/large_scale_gaia_tester.py
```

### 第10層級：AI能力評估 (AI Capability Assessment)
**目標**: 全面評估AI系統的智能化能力

**測試範圍**:
- 邏輯推理能力
- 知識整合能力
- 創新解決方案能力
- 自適應學習能力

**執行方式**:
```bash
# 運行AI能力評估
python -m pytest test/ai_capability/ -v

# 推理能力測試
python test/ai_capability/test_reasoning_ability.py

# 學習能力評估
python test/ai_capability/evaluate_learning.py
```

## 🚀 快速執行

### 十層級測試執行器

```bash
# 運行所有層級測試
python test/ten_layer_test_executor.py --mode all

# 運行關鍵層級測試（適合CI/CD）
python test/ten_layer_test_executor.py --mode critical

# 運行單個層級測試
python test/ten_layer_test_executor.py --mode layer --layer 9

# 關鍵失敗時不停止
python test/ten_layer_test_executor.py --mode all --no-stop

# 自定義輸出文件
python test/ten_layer_test_executor.py --mode all --output custom_results.json
```

### 統一測試管理器

```bash
# 列出所有測試
python test/unified_test_manager.py list

# 運行特定分類測試
python test/unified_test_manager.py run --category unit
python test/unified_test_manager.py run --category integration

# 運行所有測試
python test/unified_test_manager.py run --all

# 生成測試報告
python test/unified_test_manager.py report --output test_report.html
```

## 📊 測試結果和報告

### 結果文件格式

測試結果以JSON格式保存在`test/results/`目錄：

```json
{
  "start_time": "2025-06-05T11:00:00",
  "end_time": "2025-06-05T11:30:00",
  "test_mode": "critical",
  "summary": {
    "total_layers": 5,
    "passed_layers": 5,
    "failed_layers": 0,
    "critical_failures": 0,
    "total_execution_time": 1200.5
  },
  "layers": {
    "1": {
      "name": "單元測試",
      "category": "unit",
      "critical": true,
      "overall_success": true,
      "execution_time": 120.3,
      "scripts_results": [...]
    }
  }
}
```

### 報告查看

```bash
# 查看最新測試結果
cat test/results/ten_layer_test_results_latest.json | jq .summary

# 查看特定層級結果
cat test/results/ten_layer_test_results_latest.json | jq '.layers["9"]'

# 生成HTML報告
python test/generate_html_report.py --input test/results/ten_layer_test_results_latest.json
```

## 🎯 質量門檻

### 關鍵層級要求
- **第1層級（單元測試）**: 100%通過，覆蓋率≥95%
- **第2層級（集成測試）**: 100%通過
- **第3層級（MCP合規）**: 100%通過
- **第4層級（端到端）**: 100%通過
- **第9層級（GAIA基準）**: ≥90%成功率

### 性能要求
- **響應時間**: 工具選擇<10ms，兜底機制<50ms
- **內存使用**: <100MB
- **並發處理**: 100+ requests/sec
- **錯誤率**: <1%

### 安全要求
- **漏洞掃描**: 無高危漏洞
- **依賴檢查**: 無已知安全問題
- **代碼掃描**: 通過安全規則檢查

## 🔧 測試配置

### pytest配置 (pytest.ini)

```ini
[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=mcptool
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=95
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
    critical: Critical tests that must pass
```

### tox配置 (tox.ini)

```ini
[tox]
envlist = py38,py39,py310,py311,flake8,mypy

[testenv]
deps = 
    pytest
    pytest-cov
    pytest-mock
    pytest-asyncio
commands = pytest {posargs}

[testenv:flake8]
deps = flake8
commands = flake8 mcptool test

[testenv:mypy]
deps = mypy
commands = mypy mcptool
```

## 🚨 故障排除

### 常見問題

1. **測試超時**
   ```bash
   # 增加超時時間
   python -m pytest test/ --timeout=300
   ```

2. **依賴問題**
   ```bash
   # 重新安裝測試依賴
   pip install -r test/requirements-test.txt
   ```

3. **權限問題**
   ```bash
   # 設置執行權限
   chmod +x test/ten_layer_test_executor.py
   chmod +x test/unified_test_manager.py
   ```

4. **環境變量**
   ```bash
   # 設置測試環境變量
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   export TEST_ENV=true
   ```

### 調試模式

```bash
# 啟用詳細日誌
python test/ten_layer_test_executor.py --mode all --verbose

# 調試特定測試
python -m pytest test/unit/test_base_mcp.py::TestBaseMCP::test_init -v -s

# 進入調試器
python -m pytest test/unit/test_base_mcp.py --pdb
```

## 📈 持續改進

### 測試優化策略
- **並行執行**: 使用pytest-xdist並行運行測試
- **智能選擇**: 基於代碼變更智能選擇測試
- **緩存機制**: 緩存測試結果和依賴
- **增量測試**: 只運行受影響的測試

### 新測試添加流程
1. 確定測試層級和分類
2. 創建測試文件和用例
3. 更新測試配置
4. 運行測試驗證
5. 更新文檔
6. 提交代碼審查

### 測試指標監控
- 測試執行時間趨勢
- 測試成功率變化
- 代碼覆蓋率統計
- 性能指標監控

## 🤝 貢獻指南

### 編寫測試的最佳實踐

1. **測試命名**: 使用描述性的測試名稱
2. **測試獨立**: 每個測試應該獨立運行
3. **數據隔離**: 使用測試專用數據
4. **清理機制**: 測試後清理資源
5. **斷言明確**: 使用明確的斷言語句

### 測試代碼示例

```python
import pytest
from mcptool.core.base_mcp import BaseMCP

class TestBaseMCP:
    """BaseMCP基類測試"""
    
    def setup_method(self):
        """測試前設置"""
        self.config = {"test": True}
    
    def teardown_method(self):
        """測試後清理"""
        pass
    
    def test_init_success(self):
        """測試成功初始化"""
        adapter = BaseMCP(self.config)
        assert adapter.config == self.config
        assert adapter.client is None
    
    def test_init_invalid_config(self):
        """測試無效配置初始化"""
        with pytest.raises(ValueError):
            BaseMCP(None)
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """測試成功連接"""
        adapter = BaseMCP(self.config)
        result = await adapter.connect()
        assert result is True
```

### 提交測試代碼

1. 確保所有測試通過
2. 檢查代碼覆蓋率
3. 運行代碼質量檢查
4. 更新相關文檔
5. 提交Pull Request

