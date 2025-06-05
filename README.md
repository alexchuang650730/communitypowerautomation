# PowerAutomation

智能自動化工具系統，基於MCP協議的模塊化AI助手平台。

## 🎯 核心功能

### 🧠 智能意圖處理
- 自動意圖識別和分析
- 動態工具創建和管理
- 智能適配器發現

### 🔧 MCP適配器系統
- 統一適配器註冊表
- 17個專業適配器
- 標準MCP協議支持

### 📚 學習與優化
- RAG知識學習系統
- RL-SRT對齊機制
- ThoughtActionRecorder記錄器

### 🧪 完整測試框架
- 10層級測試架構
- 33個專業測試用例
- Mock/Real API雙模式

## 📁 項目結構

```
PowerAutomation/
├── mcptool/                    # 核心MCP工具系統
│   ├── adapters/              # MCP適配器集合
│   │   ├── core/              # 核心適配器
│   │   ├── unified_config_manager/    # 統一配置管理
│   │   ├── unified_smart_tool_engine/ # 智能工具引擎
│   │   └── sequential_thinking_adapter/ # 序列思維適配器
│   ├── cli/                   # 命令行工具
│   ├── config/                # 配置文件
│   └── core/                  # 核心組件
├── test/                      # 測試系統
│   ├── results/               # 測試結果
│   ├── detailed_test_level_plans.py    # 測試層級方案
│   ├── test_execution_engine.py        # 測試執行引擎
│   └── dynamic_adapter_discovery.py    # 動態適配器發現
├── frontend/                  # 前端應用
│   ├── src/                   # 源代碼
│   ├── public/                # 靜態資源
│   └── package.json           # 依賴配置
├── backend/                   # 後端服務
│   ├── api/                   # API接口
│   ├── models/                # 數據模型
│   └── services/              # 業務服務
└── tools/                     # 輔助工具
```

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行測試
```bash
# Mock模式測試
python test/test_execution_engine.py

# 特定層級測試
python test/detailed_test_level_plans.py
```

### 使用MCP適配器
```python
from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry

# 初始化適配器註冊表
registry = UnifiedAdapterRegistry()

# 列出所有適配器
adapters = registry.list_adapters()
print(f"可用適配器: {len(adapters)}個")
```

### 智能意圖處理
```python
from mcptool.adapters.intelligent_intent_processor import get_intent_processor

# 處理用戶意圖
processor = get_intent_processor()
result = await processor.process_intent("我需要一個數據分析工具")
```

## 📊 測試架構

### 10層級測試系統
1. **單元測試** - 核心組件功能驗證
2. **集成測試** - 組件間協作測試
3. **MCP合規測試** - 協議標準驗證
4. **端到端測試** - 完整工作流測試
5. **性能測試** - 系統性能基準
6. **GAIA基準測試** - AI能力評估
7. **動態發現測試** - 自動發現和創建
8. **RAG學習測試** - 知識學習驗證
9. **RL-SRT對齊測試** - 強化學習對齊
10. **自動化測試** - 完整自動化流程

### 測試統計
- **總測試套件**: 10個
- **總測試用例**: 33個
- **成功率**: 100% (Mock模式)
- **執行時間**: ~3.6秒 (Mock模式)

## 🔧 核心組件

### MCP適配器
- **WebAgent適配器**: 網頁智能代理
- **ThoughtActionRecorder**: 思維行動記錄器
- **智能意圖處理器**: 動態工具創建
- **統一配置管理器**: 配置和AI模型管理
- **智能工具引擎**: 工具發現和執行

### 學習系統
- **RAG知識庫**: 自動知識提取和存儲
- **RL-SRT對齊**: 思維-行動對齊機制
- **動態適配器發現**: 自動工具創建

## 📈 性能指標

### Mock模式測試結果
- ✅ **100%測試通過率**
- ⚡ **3.6秒完整測試執行**
- 🔧 **33個測試用例全部通過**
- 📊 **10個測試層級完整覆蓋**

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 📄 許可證

MIT License

## 🔗 相關鏈接

- [MCP協議文檔](https://github.com/modelcontextprotocol)
- [GAIA基準測試](https://huggingface.co/gaia-benchmark)
- [項目Wiki](https://github.com/alexchuang650730/powerautomation/wiki)

---

**PowerAutomation** - 讓AI自動化更智能、更高效！
