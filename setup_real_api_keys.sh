#!/bin/bash
# PowerAutomation Real API密鑰設置腳本
# 此腳本用於臨時設置真實API密鑰進行測試
# 注意：此腳本不會被提交到Git，僅用於本地測試

echo "🔐 PowerAutomation Real API密鑰設置"
echo "=================================="
echo ""
echo "⚠️  注意：此腳本將臨時設置真實API密鑰"
echo "⚠️  請確保在安全環境中運行"
echo "⚠️  測試完成後請清除環境變量"
echo ""

# 檢查是否已有API密鑰
check_existing_keys() {
    echo "📋 檢查現有API密鑰狀態："
    echo "CLAUDE_API_KEY: ${CLAUDE_API_KEY:+已設置}"
    echo "GEMINI_API_KEY: ${GEMINI_API_KEY:+已設置}"
    echo "KILO_API_KEY: ${KILO_API_KEY:+已設置}"
    echo "SUPERMEMORY_API_KEY: ${SUPERMEMORY_API_KEY:+已設置}"
    echo "GITHUB_TOKEN: ${GITHUB_TOKEN:+已設置}"
    echo ""
}

# 設置Claude API密鑰
set_claude_key() {
    echo "🤖 設置Claude API密鑰："
    echo "請輸入Claude API密鑰 (sk-ant-...)："
    read -s CLAUDE_KEY
    if [[ $CLAUDE_KEY == sk-ant-* ]]; then
        export CLAUDE_API_KEY="$CLAUDE_KEY"
        echo "✅ Claude API密鑰已設置"
    else
        echo "❌ 無效的Claude API密鑰格式"
    fi
    echo ""
}

# 設置Gemini API密鑰
set_gemini_key() {
    echo "🔮 設置Gemini API密鑰："
    echo "請輸入Gemini API密鑰："
    read -s GEMINI_KEY
    if [[ -n $GEMINI_KEY ]]; then
        export GEMINI_API_KEY="$GEMINI_KEY"
        echo "✅ Gemini API密鑰已設置"
    else
        echo "❌ Gemini API密鑰不能為空"
    fi
    echo ""
}

# 設置KiloCode API密鑰
set_kilo_key() {
    echo "⚡ 設置KiloCode API密鑰："
    echo "請輸入KiloCode API密鑰："
    read -s KILO_KEY
    if [[ -n $KILO_KEY ]]; then
        export KILO_API_KEY="$KILO_KEY"
        echo "✅ KiloCode API密鑰已設置"
    else
        echo "❌ KiloCode API密鑰不能為空"
    fi
    echo ""
}

# 設置SuperMemory API密鑰
set_supermemory_key() {
    echo "🧠 設置SuperMemory API密鑰："
    echo "請輸入SuperMemory API密鑰："
    read -s SUPERMEMORY_KEY
    if [[ -n $SUPERMEMORY_KEY ]]; then
        export SUPERMEMORY_API_KEY="$SUPERMEMORY_KEY"
        echo "✅ SuperMemory API密鑰已設置"
    else
        echo "❌ SuperMemory API密鑰不能為空"
    fi
    echo ""
}

# 設置GitHub Token
set_github_token() {
    echo "🐙 設置GitHub Token："
    echo "請輸入GitHub Personal Access Token (ghp_...)："
    read -s GITHUB_TOK
    if [[ $GITHUB_TOK == ghp_* ]] || [[ $GITHUB_TOK == github_pat_* ]]; then
        export GITHUB_TOKEN="$GITHUB_TOK"
        echo "✅ GitHub Token已設置"
    else
        echo "❌ 無效的GitHub Token格式"
    fi
    echo ""
}

# 清除所有API密鑰
clear_all_keys() {
    echo "🧹 清除所有API密鑰..."
    unset CLAUDE_API_KEY
    unset GEMINI_API_KEY
    unset KILO_API_KEY
    unset SUPERMEMORY_API_KEY
    unset GITHUB_TOKEN
    echo "✅ 所有API密鑰已清除"
    echo ""
}

# 驗證API密鑰
verify_keys() {
    echo "🔍 驗證API密鑰..."
    echo "正在運行MCP完整性測試..."
    python test/mcp_integrity_test.py
    echo ""
    echo "正在運行GAIA測試..."
    python test/gaia.py --level=1 --max-tasks=3
    echo ""
}

# 主菜單
main_menu() {
    while true; do
        echo "🎯 請選擇操作："
        echo "1) 檢查現有密鑰狀態"
        echo "2) 設置Claude API密鑰"
        echo "3) 設置Gemini API密鑰"
        echo "4) 設置KiloCode API密鑰"
        echo "5) 設置SuperMemory API密鑰"
        echo "6) 設置GitHub Token"
        echo "7) 設置所有API密鑰"
        echo "8) 驗證API密鑰"
        echo "9) 清除所有API密鑰"
        echo "0) 退出"
        echo ""
        echo -n "請輸入選項 (0-9): "
        read choice
        echo ""
        
        case $choice in
            1) check_existing_keys ;;
            2) set_claude_key ;;
            3) set_gemini_key ;;
            4) set_kilo_key ;;
            5) set_supermemory_key ;;
            6) set_github_token ;;
            7) 
                set_claude_key
                set_gemini_key
                set_kilo_key
                set_supermemory_key
                set_github_token
                ;;
            8) verify_keys ;;
            9) clear_all_keys ;;
            0) 
                echo "👋 退出API密鑰設置"
                break
                ;;
            *) 
                echo "❌ 無效選項，請重新選擇"
                echo ""
                ;;
        esac
    done
}

# 運行主菜單
main_menu

