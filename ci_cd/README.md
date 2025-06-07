# CI/CD自動檢查系統

這個目錄包含PowerAutomation系統的CI/CD自動檢查組件。

## 組件說明

### 1. 自動質量檢查器 (`automated_quality_checker.py`)
- **功能**: 執行自動化GAIA測試和質量評估
- **支持**: 快速檢查(50個問題)和完整檢查(165個問題)
- **輸出**: 測試結果、質量報告、告警信息

### 2. 配置文件 (`config.json`)
- **質量門檻**: 成功率、信心度、執行時間等標準
- **測試設置**: 樣本大小、超時時間等參數
- **通知配置**: 郵件、Slack、Webhook等告警方式

### 3. 自動檢查腳本 (`run_checks.sh`)
- **功能**: 定期執行質量檢查的Shell腳本
- **模式**: 快速檢查、完整檢查、趨勢分析、健康檢查
- **日誌**: 自動記錄執行日誌和結果

## 使用方法

### 快速檢查
```bash
./ci_cd/run_checks.sh quick
```

### 完整檢查
```bash
./ci_cd/run_checks.sh full
```

### 趨勢分析
```bash
./ci_cd/run_checks.sh trend 7  # 最近7天
```

### 健康檢查
```bash
./ci_cd/run_checks.sh health
```

### 監控模式
```bash
./ci_cd/run_checks.sh monitor
```

## Python API使用

```python
from ci_cd.automated_quality_checker import AutomatedQualityChecker

# 創建檢查器
checker = AutomatedQualityChecker("ci_cd/config.json")

# 運行快速檢查
result = checker.run_quick_check()

# 運行完整檢查
result = checker.run_full_check()

# 獲取趨勢分析
trend = checker.get_trend_analysis(days=7)
```

## 質量門檻

系統使用以下質量門檻來評估測試結果：

- **最低成功率**: 90%
- **最低兜底成功率**: 75%
- **最低平均信心度**: 80%
- **最大執行時間**: 300秒
- **最少工具覆蓋**: 5個工具
- **最低類型覆蓋率**: 95%

## 輸出文件

### 結果文件 (`results/`)
- 包含詳細的測試結果JSON文件
- 按時間戳命名，便於追蹤歷史

### 報告文件 (`reports/`)
- Markdown格式的測試報告
- 包含指標分析和改進建議

### 告警文件 (`alerts/`)
- 質量檢查失敗時的告警記錄
- 包含問題詳情和修復建議

### 日誌文件 (`logs/`)
- 執行日誌和錯誤信息
- 按檢查類型分類存儲

## 定時任務設置

可以使用crontab設置定時執行：

```bash
# 每30分鐘執行快速檢查
*/30 * * * * /home/ubuntu/projects/communitypowerautomation/ci_cd/run_checks.sh quick

# 每天凌晨2點執行完整檢查
0 2 * * * /home/ubuntu/projects/communitypowerautomation/ci_cd/run_checks.sh full

# 每週一早上8點執行清理
0 8 * * 1 /home/ubuntu/projects/communitypowerautomation/ci_cd/run_checks.sh cleanup
```

## 集成GitHub Actions

這個CI/CD系統設計為可以輕鬆集成到GitHub Actions中，詳見下一階段的GitHub Actions配置。

## 故障排除

### 常見問題

1. **Python模塊導入錯誤**
   - 確保項目路徑正確
   - 檢查Python環境和依賴

2. **權限問題**
   - 確保腳本有執行權限
   - 檢查文件和目錄的讀寫權限

3. **磁盤空間不足**
   - 定期運行清理命令
   - 調整報告保留天數

4. **測試超時**
   - 調整配置文件中的超時設置
   - 檢查系統資源使用情況

### 日誌查看

```bash
# 查看最新的檢查日誌
tail -f ci_cd/logs/ci_cd.log

# 查看快速檢查日誌
tail -f ci_cd/logs/quick_check.log

# 查看完整檢查日誌
tail -f ci_cd/logs/full_check.log
```

