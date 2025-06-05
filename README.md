# PowerAutomation

> 統一AI自動化平台 - MCP適配器系統

## 📊 系統狀態

- **測試狀態**: 🟢 全部通過
- **最後更新**: 2025-06-05 08:15:06
- **MCP適配器**: 17個已發現
- **測試覆蓋**: 十層級測試系統 (10個套件, 33個用例)

## 🎯 項目概述

PowerAutomation是一個統一的AI自動化平台，基於MCP（Model Context Protocol）標準，提供：

- 🔧 **統一MCP適配器系統** - 標準化的AI服務接口
- 💻 **完整CLI控制系統** - 命令行管理和測試工具
- 🧪 **全面測試覆蓋** - 單元、集成、端到端、GAIA測試
- 📚 **詳細文檔系統** - API參考、使用指南、教程

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 初始化系統
```bash
python mcptool/cli/enhanced_mcp_cli.py init
```

### 查看系統狀態
```bash
python mcptool/cli/enhanced_mcp_cli.py status
```

### 運行測試
```bash
# 運行所有測試
python test/unified_test_manager.py run all

# 運行GAIA測試
python test/gaia.py test --level=1 --max-tasks=10
```

## 📁 項目結構

```
PowerAutomation/
├── backend
│   ├── agents_backup
│   │   ├── base_agent.py
│   │   ├── general_agent.py
│   │   ├── ppt_agent.py
│   │   └── web_agent.py
│   ├── routes
│   │   ├── code_agent_routes.py
│   │   ├── general_agent_routes.py
│   │   ├── ppt_agent_routes.py
│   │   └── web_agent_routes.py
│   ├── services
│   │   ├── general_service.py
│   │   ├── ppt_service.py
│   │   └── web_service.py
│   └── main.py
├── docs
│   ├── PROJECT_INFO.json
│   ├── upload_log.txt
│   ├── 十個層級測試方案報告.md
│   └── 項目完成總結報告.md
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── components
│   │   ├── data
│   │   ├── docs
│   │   ├── styles
│   │   ├── App.css
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── tests
│   │   ├── cli
│   │   ├── e2e
│   │   ├── report
│   │   └── visual
│   ├── 1
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tsconfig.node.tsbuildinfo
│   ├── tsconfig.tsbuildinfo
│   ├── vite.config.ts
│   └── vite.config.ts~
├── mcptool
│   ├── adapters
│   │   ├── __pycache__
│   │   ├── agent
│   │   ├── ai_enhanced
│   │   ├── claude
│   │   ├── claude_adapter
│   │   ├── core
│   │   ├── enhanced_aci_dev_adapter
│   │   ├── gemini_adapter
│   │   ├── general_agent
│   │   ├── infinite_context_adapter
│   │   ├── integration
│   │   ├── interfaces
│   │   ├── kilocode_adapter
│   │   ├── manus
│   │   ├── rl_srt
│   │   ├── sequential_thinking_adapter
│   │   ├── unified_config_manager
│   │   ├── unified_smart_tool_engine
│   │   ├── workflow
│   │   ├── zapier_adapter
│   │   ├── __init__.py
│   │   ├── ai_api_key_manager.py.backup
│   │   ├── ai_coordination_hub.py
│   │   ├── ai_enhanced_intent_understanding_mcp.py.backup
│   │   ├── api_config_manager.py.backup
│   │   ├── base_mcp.py
│   │   ├── enhanced_mcp_brainstorm.py
│   │   ├── enhanced_mcp_planner.py
│   │   ├── error_handler.py
│   │   ├── fixed_api_manager.py.backup
│   │   ├── infinite_context_adapter_mcp.py
│   │   ├── intelligent_intent_processor.py
│   │   ├── intelligent_workflow_engine_mcp.py
│   │   ├── multi_adapter_synthesizer.py
│   │   ├── playwright_adapter.py
│   │   ├── release_discovery_mcp.py
│   │   ├── sequential_thinking_adapter.py
│   │   ├── thought_action_recorder_mcp.py
│   │   ├── unified_smart_tool_engine_mcp.py
│   │   └── webagent_adapter.py
│   ├── cli
│   │   ├── enhanced_mcp_cli.py
│   │   ├── rollback_cli.py
│   │   └── unified_mcp_cli.py
│   ├── cli_testing
│   │   ├── config
│   │   ├── releases
│   │   ├── config_cli.py
│   │   ├── gaia.py
│   │   ├── mcpcoordinator_cli.py
│   │   ├── unified_adapter_cli.py
│   │   ├── unified_cli_tester.py
│   │   ├── unified_cli_tester_v2.py
│   │   └── workflow_engine_cli.py
│   ├── config
│   │   ├── agent_problem_solver.json
│   │   ├── release_manager.json
│   │   ├── rollback_history.json
│   │   ├── savepoints.json
│   │   └── work_nodes.json
│   ├── core
│   │   ├── __pycache__
│   │   ├── development_tools
│   │   ├── __init__.py
│   │   ├── agent_problem_solver_mcp.py
│   │   ├── base_mcp.py
│   │   ├── enhanced_mcp_brainstorm.py
│   │   ├── enhanced_mcp_planner.py
│   │   ├── mcp_brainstorm.py
│   │   ├── mcp_central_coordinator.py
│   │   ├── mcp_core_loader.py
│   │   ├── mcp_http_api_server.py
│   │   ├── mcp_planner.py
│   │   ├── mcp_tool_engine_server.py
│   │   ├── playwright_adapter.py
│   │   ├── proactive_problem_solver.py
│   │   ├── release_manager_mcp.py
│   │   └── unified_mcp_manager.py
│   └── mcptool
│       ├── adapters
│       └── config
├── test
│   ├── automation
│   │   ├── report_generator.py
│   │   └── test_runner.py
│   ├── cli
│   │   └── rollback_cli_test.py
│   ├── config
│   │   ├── agent_problem_solver.json
│   │   └── release_manager.json
│   ├── e2e
│   │   ├── release_workflow.py
│   │   ├── thought_action_workflow.py
│   │   └── tool_discovery_workflow.py
│   ├── integration
│   │   ├── mcptool_kilocode_integration.py
│   │   ├── multi_model_synergy.py
│   │   ├── rlfactory_srt_integration.py
│   │   └── workflow_integration.py
│   ├── mcp_compliance
│   │   ├── compliance_checker.py
│   │   └── protocol_validation.py
│   ├── performance
│   │   └── load_testing.py
│   ├── results
│   │   ├── gaia_level_1_cli_results_20250605_063356.json
│   │   ├── gaia_level_1_cli_results_20250605_063412.json
│   │   ├── gaia_level_1_cli_results_20250605_063837.json
│   │   ├── test_plan.json
│   │   ├── test_report_execution_1749123239.json
│   │   ├── test_report_execution_1749123387.json
│   │   ├── test_report_execution_1749125244.json
│   │   ├── test_report_execution_1749125254.json
│   │   └── test_report_execution_1749125269.json
│   ├── unit
│   │   ├── adapters
│   │   ├── config
│   │   ├── core
│   │   ├── interfaces
│   │   └── tools
│   ├── complete_test_report.md
│   ├── complete_test_report_final.md
│   ├── complete_test_report_fixed.md
│   ├── comprehensive_test_framework.py
│   ├── detailed_test_level_plans.py
│   ├── dynamic_adapter_discovery.py
│   ├── gaia.py
│   ├── README.md
│   ├── test_execution_engine.py
│   ├── unified_test_cli.py
│   ├── unified_test_manager.py
│   ├── unit_test_coverage_continuous_fix_final_report.md
│   ├── unit_test_coverage_continuous_improvement_report.md
│   └── unit_test_coverage_final_report.md
├── tools
├── README.md
├── requirements.txt
├── run_backend.py
└── smart_upload.py
```

## 📝 主要文件說明

- **README.md** - 項目主要說明文檔，包含安裝、使用和貢獻指南
- **requirements.txt** - Python依賴包列表
- **setup.py** - 項目安裝配置文件
- **.gitignore** - Git忽略文件配置
- **LICENSE** - 項目許可證文件
### mcptool/
MCP工具核心目錄

### mcptool/core/
核心功能模塊

### mcptool/adapters/
MCP適配器集合

### mcptool/cli/
命令行界面工具

### mcptool/config/
配置文件目錄

### test/
測試文件目錄

### test/unit/
單元測試

### test/integration/
集成測試

### test/e2e/
端到端測試

- **test/gaia.py** - GAIA基準測試腳本
### docs/
項目文檔目錄

### docs/api/
API參考文檔

### docs/guides/
使用指南

### docs/tutorials/
教程文檔

### docs/architecture/
架構設計文檔


## 🧪 測試系統

### 測試分類
- **單元測試** - 個別組件功能驗證
- **集成測試** - 組件間協作驗證  
- **端到端測試** - 完整流程驗證
- **GAIA測試** - AI能力基準測試

### 運行測試
```bash
# 查看所有測試
python test/unified_test_manager.py list

# 運行特定測試
python test/unified_test_manager.py run unit
python test/unified_test_manager.py run integration
python test/unified_test_manager.py run e2e

# 運行GAIA基準測試
python test/gaia.py test --level=1 --max-tasks=165
```

## 🔧 MCP適配器

### 核心適配器
- **infinite_context_adapter** - 無限上下文處理
- **intelligent_workflow_engine** - 智能工作流引擎
- **webagent_core** - Web代理核心
- **rl_srt_mcp** - 強化學習SRT
- **sequential_thinking** - 順序思考適配器

### 智能體優化適配器
- **content_template_optimization** - 內容模板優化
- **context_matching_optimization** - 上下文匹配優化
- **context_memory_optimization** - 上下文記憶優化
- **prompt_optimization** - 提示詞優化
- **ui_journey_optimization** - UI旅程優化

## 📚 文檔

- [API參考](docs/api/) - 詳細的API文檔
- [使用指南](docs/guides/) - 快速上手指南
- [教程](docs/tutorials/) - 深入學習教程
- [架構設計](docs/architecture/) - 系統架構說明

## 🤝 貢獻指南

1. **Fork項目**
2. **創建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **運行測試** (`python tools/smart_upload.py --test-only`)
4. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
5. **推送分支** (`git push origin feature/AmazingFeature`)
6. **創建Pull Request**

### 上傳前檢查

使用智能上傳腳本確保代碼質量：

```bash
# 測試並上傳（推薦）
python tools/smart_upload.py --commit-message "你的提交信息"

# 僅運行測試
python tools/smart_upload.py --test-only

# 強制上傳（不推薦）
python tools/smart_upload.py --force --commit-message "緊急修復"
```

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 📞 聯繫方式

- **項目主頁**: [PowerAutomation](https://github.com/alexchuang650730/powerautomation)
- **問題報告**: [Issues](https://github.com/alexchuang650730/powerautomation/issues)
- **功能請求**: [Feature Requests](https://github.com/alexchuang650730/powerautomation/discussions)

---

*最後更新: 2025-06-05 08:15:06 | 自動生成 by PowerAutomation智能上傳系統*
