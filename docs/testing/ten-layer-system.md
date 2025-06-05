# PowerAutomation 十層級測試系統

PowerAutomation採用創新的十層級測試架構，確保系統的完整性、可靠性和智能化水平。

## 🏗️ 測試架構概覽

十層級測試系統是一個分層的、漸進式的測試框架，從基礎的單元測試到高級的AI能力評估，全面覆蓋系統的各個方面。

```
第10層: AI能力評估     ┌─────────────────┐
第9層:  GAIA基準測試   │   高級AI測試    │
第8層:  壓力測試       └─────────────────┘
第7層:  兼容性測試     ┌─────────────────┐
第6層:  安全測試       │   系統級測試    │
第5層:  性能測試       └─────────────────┘
第4層:  端到端測試     ┌─────────────────┐
第3層:  MCP合規測試    │   集成測試      │
第2層:  集成測試       └─────────────────┘
第1層:  單元測試       ┌─────────────────┐
                      │   基礎測試      │
                      └─────────────────┘
```

## 📋 測試層級詳細說明

### 第1層級：單元測試 (Unit Tests)
**目標**: 驗證個別組件的功能正確性

- **測試範圍**: 類、函數、方法的獨立功能
- **測試工具**: pytest, unittest
- **覆蓋率要求**: ≥95%
- **執行頻率**: 每次代碼提交
- **關鍵性**: 🔴 關鍵

**測試項目**:
- BaseMCP基類初始化
- UnifiedAdapterRegistry註冊功能
- ThoughtActionRecorder記錄功能
- IntentAnalyzer意圖分析
- KiloCode代碼生成

### 第2層級：集成測試 (Integration Tests)
**目標**: 驗證組件間的交互和數據流

- **測試範圍**: 模塊間接口、數據傳遞
- **測試工具**: pytest, mock
- **執行時間**: 5-10分鐘
- **執行頻率**: 每次合併到主分支
- **關鍵性**: 🔴 關鍵

**測試項目**:
- 適配器註冊表與MCP集成
- 智能意圖處理器集成
- RAG學習系統集成
- 配置管理器集成

### 第3層級：MCP合規測試 (MCP Compliance Tests)
**目標**: 確保符合MCP協議標準

- **測試範圍**: MCP協議實現、工具註冊
- **測試工具**: 自定義MCP驗證器
- **執行時間**: 3-5分鐘
- **執行頻率**: 每次MCP相關代碼變更
- **關鍵性**: 🔴 關鍵

**測試項目**:
- MCP協議格式驗證
- 工具註冊和發現
- 錯誤處理機制

### 第4層級：端到端測試 (End-to-End Tests)
**目標**: 驗證完整的用戶工作流程

- **測試範圍**: 完整業務流程、用戶場景
- **測試工具**: Selenium, API測試
- **執行時間**: 10-15分鐘
- **執行頻率**: 每日構建
- **關鍵性**: 🔴 關鍵

**測試項目**:
- 完整工具創建流程
- 多輪對話端到端測試
- 錯誤恢復端到端測試

### 第5層級：性能測試 (Performance Tests)
**目標**: 驗證系統性能指標

- **測試範圍**: 響應時間、吞吐量、資源使用
- **測試工具**: pytest-benchmark, locust
- **執行時間**: 10-20分鐘
- **執行頻率**: 每週
- **關鍵性**: 🟡 重要

**性能指標**:
- 工具選擇響應時間: <10ms
- 兜底機制響應時間: <50ms
- 內存使用: <100MB
- 並發處理: 100+ requests/sec

### 第6層級：安全測試 (Security Tests)
**目標**: 識別安全漏洞和風險

- **測試範圍**: 輸入驗證、權限控制、數據保護
- **測試工具**: bandit, safety, semgrep
- **執行時間**: 5-10分鐘
- **執行頻率**: 每週
- **關鍵性**: 🟡 重要

**安全檢查**:
- 代碼安全漏洞掃描
- 依賴安全性檢查
- 輸入驗證測試
- 權限控制驗證

### 第7層級：兼容性測試 (Compatibility Tests)
**目標**: 確保跨平台和版本兼容性

- **測試範圍**: 不同Python版本、操作系統
- **測試工具**: tox, Docker
- **執行時間**: 15-30分鐘
- **執行頻率**: 每週
- **關鍵性**: 🟡 重要

**兼容性矩陣**:
- Python版本: 3.8, 3.9, 3.10, 3.11
- 操作系統: Ubuntu, CentOS, Windows, macOS
- 依賴版本: 主要依賴的多個版本

### 第8層級：壓力測試 (Stress Tests)
**目標**: 驗證系統在極限條件下的表現

- **測試範圍**: 高負載、長時間運行、資源限制
- **測試工具**: locust, stress-ng
- **執行時間**: 30-60分鐘
- **執行頻率**: 每月
- **關鍵性**: 🟡 重要

**壓力場景**:
- 高並發請求處理
- 大量數據處理
- 長時間運行穩定性
- 內存和CPU壓力測試

### 第9層級：GAIA基準測試 (GAIA Benchmark Tests)
**目標**: 評估AI能力和智能化水平

- **測試範圍**: GAIA Level 1基準測試
- **測試工具**: 集成GAIA測試系統
- **執行時間**: 20-40分鐘
- **執行頻率**: 每次AI相關代碼變更
- **關鍵性**: 🔴 關鍵

**GAIA指標**:
- 成功率: ≥90%
- 兜底成功率: ≥75%
- 工具覆蓋率: ≥95%
- 問題類型覆蓋: 6種類型

### 第10層級：AI能力評估 (AI Capability Assessment)
**目標**: 全面評估AI系統的智能化能力

- **測試範圍**: 推理能力、學習能力、適應性
- **測試工具**: 自定義AI評估框架
- **執行時間**: 60-120分鐘
- **執行頻率**: 每月
- **關鍵性**: 🟡 重要

**評估維度**:
- 邏輯推理能力
- 知識整合能力
- 創新解決方案能力
- 自適應學習能力

## 🚀 執行方式

### 命令行執行

```bash
# 運行所有層級測試
python test/ten_layer_test_executor.py --mode all

# 運行關鍵層級測試
python test/ten_layer_test_executor.py --mode critical

# 運行單個層級測試
python test/ten_layer_test_executor.py --mode layer --layer 9

# 關鍵失敗時不停止
python test/ten_layer_test_executor.py --mode all --no-stop
```

### CI/CD集成

十層級測試系統已完全集成到GitHub Actions中：

```yaml
# 每次Push觸發關鍵層級測試
on: push
jobs:
  ten-layer-tests:
    runs-on: ubuntu-latest
    steps:
      - name: 運行十層級測試
        run: python test/ten_layer_test_executor.py --mode critical
```

### 本地開發

```bash
# 快速檢查（關鍵層級）
make test-quick

# 完整測試（所有層級）
make test-full

# 性能測試
make test-performance
```

## 📊 測試報告

### 結果格式

測試結果以JSON格式保存，包含詳細的執行信息：

```json
{
  "start_time": "2025-06-05T11:00:00",
  "end_time": "2025-06-05T11:30:00",
  "summary": {
    "total_layers": 10,
    "passed_layers": 9,
    "failed_layers": 1,
    "critical_failures": 0,
    "total_execution_time": 1800.5
  },
  "layers": {
    "1": {
      "name": "單元測試",
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
cat test/results/ten_layer_test_results_latest.json

# 查看測試趨勢
python test/analyze_test_trends.py --days 7
```

## 🎯 質量門檻

### 關鍵層級要求
- 第1層級（單元測試）: 100%通過
- 第2層級（集成測試）: 100%通過
- 第3層級（MCP合規）: 100%通過
- 第4層級（端到端）: 100%通過
- 第9層級（GAIA基準）: ≥90%成功率

### 整體要求
- 關鍵失敗數: 0
- 總體成功率: ≥90%
- 執行時間: <60分鐘（關鍵層級）

## 🔧 故障排除

### 常見問題

1. **測試超時**
   ```bash
   # 增加超時時間
   python test/ten_layer_test_executor.py --timeout 3600
   ```

2. **依賴問題**
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   pip install -r test/requirements-test.txt
   ```

3. **權限問題**
   ```bash
   # 設置執行權限
   chmod +x test/ten_layer_test_executor.py
   ```

### 調試模式

```bash
# 啟用詳細日誌
python test/ten_layer_test_executor.py --mode all --verbose

# 保存調試信息
python test/ten_layer_test_executor.py --mode all --debug --output debug_results.json
```

## 📈 持續改進

### 測試優化
- 並行執行非關鍵層級
- 智能測試選擇
- 緩存機制優化
- 測試數據管理

### 新層級擴展
- 第11層級：用戶體驗測試
- 第12層級：業務邏輯驗證
- 第13層級：生態系統集成

### 指標監控
- 測試執行時間趨勢
- 成功率變化分析
- 性能指標監控
- 資源使用優化

## 🤝 貢獻指南

### 添加新測試

1. 確定測試層級
2. 創建測試腳本
3. 更新測試配置
4. 編寫測試文檔
5. 提交Pull Request

### 測試最佳實踐

- 測試獨立性：每個測試應該獨立運行
- 數據隔離：使用測試專用數據
- 清理機制：測試後清理資源
- 錯誤處理：優雅處理測試失敗
- 文檔更新：及時更新測試文檔

