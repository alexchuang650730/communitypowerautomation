# PowerAutomation GitHub Actions CI/CD 集成

這個目錄包含PowerAutomation系統的GitHub Actions工作流程配置。

## 工作流程說明

### 1. 主要質量檢查 (`ci-cd-quality-check.yml`)

**觸發條件:**
- 推送到主分支 (main/master)
- Pull Request到主分支
- 每天凌晨2點定時執行
- 手動觸發

**作業類型:**
- **快速檢查**: 50個問題的質量檢查 (Push/PR觸發)
- **完整檢查**: 165個問題的完整測試 (定時/手動觸發)
- **健康檢查**: 系統健康狀態監控
- **部署檢查**: 檢查系統是否準備好部署
- **性能監控**: 分析性能趨勢

**功能特性:**
- 自動PR評論測試結果
- Slack通知集成
- 測試結果工件上傳
- 自動部署標籤創建

### 2. 安全掃描 (`security-scan.yml`)

**觸發條件:**
- 推送到主分支
- Pull Request
- 每週一早上6點定時執行

**掃描工具:**
- **Bandit**: Python安全漏洞掃描
- **Safety**: 依賴安全性檢查
- **Semgrep**: 代碼安全模式掃描

### 3. 性能基準測試 (`performance-benchmark.yml`)

**觸發條件:**
- 每週日早上4點定時執行
- 手動觸發

**測試內容:**
- 工具選擇性能測試
- 兜底系統性能測試
- 內存使用分析
- 性能趨勢監控

## 配置要求

### GitHub Secrets

需要在GitHub倉庫設置以下Secrets：

```
SLACK_WEBHOOK_URL          # Slack通知Webhook URL
NOTIFICATION_EMAIL         # 通知郵箱地址
DEPLOY_TOKEN               # 部署令牌（如果需要）
```

### 分支保護規則

建議設置以下分支保護規則：

```yaml
# .github/branch-protection.yml
protection_rules:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "quick-check"
        - "security-scan"
    enforce_admins: false
    required_pull_request_reviews:
      required_approving_review_count: 1
      dismiss_stale_reviews: true
    restrictions: null
```

## 使用指南

### 1. 自動觸發

**推送代碼時:**
```bash
git push origin main
# 自動觸發快速檢查和安全掃描
```

**創建Pull Request時:**
```bash
gh pr create --title "Feature: 新功能" --body "描述"
# 自動觸發快速檢查，結果會評論到PR
```

### 2. 手動觸發

**快速檢查:**
```bash
gh workflow run "PowerAutomation CI/CD Quality Check" \
  --field test_type=quick \
  --field force_run=true
```

**完整檢查:**
```bash
gh workflow run "PowerAutomation CI/CD Quality Check" \
  --field test_type=full
```

**性能基準測試:**
```bash
gh workflow run "PowerAutomation Performance Benchmark" \
  --field benchmark_type=standard
```

### 3. 查看結果

**工作流程狀態:**
```bash
gh run list --workflow="PowerAutomation CI/CD Quality Check"
```

**下載工件:**
```bash
gh run download <run-id> --name quick-check-results
```

## 質量門檻

### 快速檢查門檻
- 成功率 ≥ 90%
- 兜底成功率 ≥ 75%
- 平均信心度 ≥ 80%
- 執行時間 ≤ 300秒

### 完整檢查門檻
- 成功率 ≥ 90%
- 兜底成功率 ≥ 75%
- 工具覆蓋 ≥ 5個
- 類型覆蓋率 ≥ 95%

### 性能門檻
- 工具選擇平均時間 ≤ 10ms
- 兜底系統平均時間 ≤ 50ms
- 內存使用 ≤ 100MB

## 通知配置

### Slack集成

1. 創建Slack App和Webhook
2. 設置GitHub Secret: `SLACK_WEBHOOK_URL`
3. 配置頻道: `#powerautomation-ci`

### 郵件通知

可以通過GitHub Actions的郵件Action發送通知：

```yaml
- name: 發送郵件通知
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: PowerAutomation CI/CD 結果
    body: 檢查結果詳情...
    to: ${{ secrets.NOTIFICATION_EMAIL }}
```

## 故障排除

### 常見問題

1. **Python依賴安裝失敗**
   - 檢查requirements.txt文件
   - 確保Python版本兼容性

2. **測試超時**
   - 調整timeout設置
   - 檢查測試用例數量

3. **權限問題**
   - 檢查GitHub Token權限
   - 確保Secrets配置正確

4. **工件上傳失敗**
   - 檢查文件路徑
   - 確保文件存在

### 調試方法

**啟用調試日誌:**
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

**查看詳細日誌:**
```bash
gh run view <run-id> --log
```

## 最佳實踐

### 1. 分階段檢查
- PR階段：快速檢查
- 合併後：完整檢查
- 定期：性能和安全掃描

### 2. 失敗處理
- 快速檢查失敗：阻止合併
- 完整檢查失敗：發送告警
- 安全掃描失敗：創建Issue

### 3. 性能優化
- 使用緩存加速依賴安裝
- 並行執行獨立作業
- 合理設置超時時間

### 4. 監控和告警
- 設置Slack通知
- 監控成功率趨勢
- 定期檢查性能指標

## 擴展配置

### 添加新的檢查

1. 創建新的工作流程文件
2. 定義觸發條件和作業
3. 集成到現有通知系統
4. 更新文檔

### 集成外部服務

可以集成以下外部服務：
- **Codecov**: 代碼覆蓋率
- **SonarQube**: 代碼質量分析
- **Snyk**: 安全漏洞掃描
- **Datadog**: 性能監控

### 自定義通知

可以創建自定義通知Action：

```yaml
- name: 自定義通知
  uses: ./.github/actions/custom-notification
  with:
    webhook_url: ${{ secrets.CUSTOM_WEBHOOK }}
    message: "自定義消息"
    severity: "info"
```

