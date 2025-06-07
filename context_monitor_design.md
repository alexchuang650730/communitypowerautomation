# 上下文監控系統設計

## 問題分析
- Manus無法直接監控自己的上下文長度
- 需要設計間接監控機制
- 必須在溢出前觸發預警

## 間接監控策略

### 1. 對話輪次計數
- 記錄每次交互的輪次
- 設定閾值（如50輪對話後警告）
- 自動觸發備份機制

### 2. 文件操作計數
- 統計文件讀寫次數
- 大量操作表示上下文增長
- 達到閾值時強制備份

### 3. 時間基礎監控
- 任務開始時間記錄
- 超過特定時間（如30分鐘）自動備份
- 定期檢查點機制

### 4. 內容長度估算
- 監控生成的文件總大小
- 估算對話內容長度
- 預測上下文使用量

## 實現方案

### 監控守護進程
```python
class ContextMonitor:
    def __init__(self):
        self.interaction_count = 0
        self.file_operations = 0
        self.start_time = time.time()
        self.content_size = 0
    
    def check_thresholds(self):
        # 檢查各種閾值
        if self.interaction_count > 50:
            self.trigger_backup()
        if time.time() - self.start_time > 1800:  # 30分鐘
            self.trigger_backup()
```

### 自動備份觸發
- Git提交重要文件
- 創建檢查點文件
- 記錄當前狀態

## 預警機制
- 達到80%閾值時警告
- 達到90%閾值時強制備份
- 達到95%閾值時建議重啟任務

