#!/bin/bash

# CI/CD自動檢查腳本
# 用於定期執行質量檢查和監控

set -e

# 配置
PROJECT_ROOT="/home/ubuntu/projects/communitypowerautomation"
PYTHON_CMD="python3"
LOG_DIR="$PROJECT_ROOT/ci_cd/logs"
CONFIG_FILE="$PROJECT_ROOT/ci_cd/config.json"

# 創建日誌目錄
mkdir -p "$LOG_DIR"

# 日誌函數
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/ci_cd.log"
}

# 錯誤處理
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 檢查依賴
check_dependencies() {
    log "檢查依賴..."
    
    if ! command -v $PYTHON_CMD &> /dev/null; then
        error_exit "Python未安裝或不在PATH中"
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        error_exit "配置文件不存在: $CONFIG_FILE"
    fi
    
    log "依賴檢查通過"
}

# 快速檢查
quick_check() {
    log "開始快速質量檢查..."
    
    cd "$PROJECT_ROOT"
    
    # 執行快速檢查
    if $PYTHON_CMD ci_cd/automated_quality_checker.py --type quick --config "$CONFIG_FILE" >> "$LOG_DIR/quick_check.log" 2>&1; then
        log "快速檢查完成"
        return 0
    else
        log "快速檢查失敗"
        return 1
    fi
}

# 完整檢查
full_check() {
    log "開始完整質量檢查..."
    
    cd "$PROJECT_ROOT"
    
    # 執行完整檢查
    if $PYTHON_CMD ci_cd/automated_quality_checker.py --type full --config "$CONFIG_FILE" >> "$LOG_DIR/full_check.log" 2>&1; then
        log "完整檢查完成"
        return 0
    else
        log "完整檢查失敗"
        return 1
    fi
}

# 趨勢分析
trend_analysis() {
    local days=${1:-7}
    log "生成最近${days}天的趨勢分析..."
    
    cd "$PROJECT_ROOT"
    
    $PYTHON_CMD ci_cd/automated_quality_checker.py --trend "$days" >> "$LOG_DIR/trend_analysis.log" 2>&1
    log "趨勢分析完成"
}

# 清理舊文件
cleanup() {
    log "清理舊的測試結果和報告..."
    
    cd "$PROJECT_ROOT"
    
    $PYTHON_CMD ci_cd/automated_quality_checker.py --cleanup >> "$LOG_DIR/cleanup.log" 2>&1
    log "清理完成"
}

# 健康檢查
health_check() {
    log "執行系統健康檢查..."
    
    # 檢查磁盤空間
    local disk_usage=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "WARNING: 磁盤使用率過高: ${disk_usage}%"
    fi
    
    # 檢查內存使用
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$mem_usage" -gt 90 ]; then
        log "WARNING: 內存使用率過高: ${mem_usage}%"
    fi
    
    # 檢查最近的測試結果
    local results_dir="$PROJECT_ROOT/ci_cd/results"
    if [ -d "$results_dir" ]; then
        local recent_results=$(find "$results_dir" -name "*.json" -mtime -1 | wc -l)
        if [ "$recent_results" -eq 0 ]; then
            log "WARNING: 最近24小時沒有測試結果"
        fi
    fi
    
    log "健康檢查完成"
}

# 發送通知
send_notification() {
    local message="$1"
    local severity="${2:-info}"
    
    log "發送通知: $message (嚴重程度: $severity)"
    
    # 這裡可以集成實際的通知系統
    # 例如：curl發送到Slack、郵件等
    
    # 創建通知記錄
    local notifications_dir="$PROJECT_ROOT/ci_cd/notifications"
    mkdir -p "$notifications_dir"
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local notification_file="$notifications_dir/notification_${timestamp}.json"
    
    cat > "$notification_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "message": "$message",
  "severity": "$severity",
  "hostname": "$(hostname)",
  "user": "$(whoami)"
}
EOF
    
    log "通知記錄已保存: $notification_file"
}

# 主函數
main() {
    local command="${1:-quick}"
    
    log "CI/CD自動檢查腳本啟動 - 命令: $command"
    
    # 檢查依賴
    check_dependencies
    
    case "$command" in
        "quick")
            if quick_check; then
                send_notification "快速質量檢查通過" "info"
            else
                send_notification "快速質量檢查失敗" "error"
                exit 1
            fi
            ;;
        "full")
            if full_check; then
                send_notification "完整質量檢查通過" "info"
            else
                send_notification "完整質量檢查失敗" "error"
                exit 1
            fi
            ;;
        "trend")
            trend_analysis "${2:-7}"
            ;;
        "cleanup")
            cleanup
            ;;
        "health")
            health_check
            ;;
        "monitor")
            # 監控模式：執行健康檢查和快速檢查
            health_check
            if quick_check; then
                send_notification "監控檢查正常" "info"
            else
                send_notification "監控檢查發現問題" "warning"
            fi
            ;;
        *)
            echo "用法: $0 {quick|full|trend|cleanup|health|monitor}"
            echo "  quick   - 快速質量檢查"
            echo "  full    - 完整質量檢查"
            echo "  trend   - 趨勢分析"
            echo "  cleanup - 清理舊文件"
            echo "  health  - 健康檢查"
            echo "  monitor - 監控模式"
            exit 1
            ;;
    esac
    
    log "CI/CD自動檢查腳本完成"
}

# 執行主函數
main "$@"

