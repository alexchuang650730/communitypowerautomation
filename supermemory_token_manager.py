#!/usr/bin/env python3
"""
SuperMemory Token管理系統
SuperMemory Token Management System

安全存儲和檢索GitHub token等認證信息
"""

import os
import json
import base64
import hashlib
from typing import Dict, Optional, Any
from datetime import datetime
import subprocess

class SuperMemoryTokenManager:
    """SuperMemory Token管理器"""
    
    def __init__(self):
        self.supermemory_workspace = "data/backup/supermemory_workspaces"
        self.token_storage_file = f"{self.supermemory_workspace}/secure_tokens.json"
        self.ensure_storage_directory()
        
    def ensure_storage_directory(self):
        """確保存儲目錄存在"""
        os.makedirs(self.supermemory_workspace, exist_ok=True)
        
    def store_token(self, service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
        """存儲token到SuperMemory"""
        try:
            # 加載現有tokens
            tokens = self._load_tokens()
            
            # 加密token (簡單的base64編碼，實際應用中應使用更強的加密)
            encrypted_token = base64.b64encode(token.encode()).decode()
            
            # 存儲token信息
            tokens[service] = {
                "encrypted_token": encrypted_token,
                "stored_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "hash": hashlib.sha256(token.encode()).hexdigest()[:8]  # 用於驗證
            }
            
            # 保存到文件
            self._save_tokens(tokens)
            
            print(f"✅ Token已安全存儲到SuperMemory: {service}")
            return True
            
        except Exception as e:
            print(f"❌ Token存儲失敗: {e}")
            return False
            
    def get_token(self, service: str) -> Optional[str]:
        """從SuperMemory獲取token"""
        try:
            tokens = self._load_tokens()
            
            if service not in tokens:
                print(f"❌ 未找到服務的token: {service}")
                return None
                
            # 解密token
            encrypted_token = tokens[service]["encrypted_token"]
            token = base64.b64decode(encrypted_token.encode()).decode()
            
            print(f"✅ 從SuperMemory獲取token: {service}")
            return token
            
        except Exception as e:
            print(f"❌ Token獲取失敗: {e}")
            return None
            
    def list_stored_tokens(self) -> Dict[str, Dict[str, Any]]:
        """列出所有存儲的token信息（不包含實際token）"""
        try:
            tokens = self._load_tokens()
            
            # 返回不包含實際token的信息
            safe_info = {}
            for service, info in tokens.items():
                safe_info[service] = {
                    "stored_at": info["stored_at"],
                    "metadata": info["metadata"],
                    "hash_preview": info["hash"]
                }
                
            return safe_info
            
        except Exception as e:
            print(f"❌ 列出token失敗: {e}")
            return {}
            
    def delete_token(self, service: str) -> bool:
        """刪除指定服務的token"""
        try:
            tokens = self._load_tokens()
            
            if service in tokens:
                del tokens[service]
                self._save_tokens(tokens)
                print(f"✅ Token已刪除: {service}")
                return True
            else:
                print(f"❌ 未找到要刪除的token: {service}")
                return False
                
        except Exception as e:
            print(f"❌ Token刪除失敗: {e}")
            return False
            
    def _load_tokens(self) -> Dict[str, Any]:
        """加載tokens文件"""
        if os.path.exists(self.token_storage_file):
            try:
                with open(self.token_storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def _save_tokens(self, tokens: Dict[str, Any]):
        """保存tokens到文件"""
        with open(self.token_storage_file, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)

class GitAuthManager:
    """Git認證管理器"""
    
    def __init__(self):
        self.token_manager = SuperMemoryTokenManager()
        
    def detect_auth_failure(self, git_output: str) -> bool:
        """偵測Git認證失敗"""
        auth_failure_indicators = [
            "Username for 'https://github.com':",
            "Password for 'https://",
            "Authentication failed",
            "Permission denied",
            "fatal: Authentication failed"
        ]
        
        return any(indicator in git_output for indicator in auth_failure_indicators)
        
    def auto_retry_git_push(self, repo_url: str = None) -> bool:
        """自動重試Git推送"""
        try:
            print("🔍 偵測到Git認證需求，從SuperMemory獲取token...")
            
            # 從SuperMemory獲取GitHub token
            github_token = self.token_manager.get_token("github")
            
            if not github_token:
                print("❌ 未在SuperMemory中找到GitHub token")
                return False
                
            # 構建認證URL
            if repo_url:
                # 提取倉庫信息
                if "github.com/" in repo_url:
                    repo_path = repo_url.split("github.com/")[1].replace(".git", "")
                    auth_url = f"https://{github_token}@github.com/{repo_path}.git"
                else:
                    auth_url = repo_url
            else:
                # 使用當前origin
                result = subprocess.run(["git", "remote", "get-url", "origin"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    origin_url = result.stdout.strip()
                    if "github.com/" in origin_url:
                        repo_path = origin_url.split("github.com/")[1].replace(".git", "")
                        auth_url = f"https://{github_token}@github.com/{repo_path}.git"
                    else:
                        auth_url = origin_url
                else:
                    print("❌ 無法獲取Git remote URL")
                    return False
                    
            # 臨時設置認證URL並推送
            print("🚀 使用SuperMemory token重試Git推送...")
            
            # 設置臨時remote
            subprocess.run(["git", "remote", "set-url", "origin", auth_url])
            
            # 執行推送
            result = subprocess.run(["git", "push", "origin", "main"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Git推送成功！")
                
                # 恢復原始URL（移除token）
                clean_url = auth_url.replace(f"{github_token}@", "")
                subprocess.run(["git", "remote", "set-url", "origin", clean_url])
                
                return True
            else:
                print(f"❌ Git推送失敗: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 自動重試失敗: {e}")
            return False

# 全局實例
token_manager = SuperMemoryTokenManager()
git_auth_manager = GitAuthManager()

def store_github_token(token: str) -> bool:
    """存儲GitHub token到SuperMemory"""
    return token_manager.store_token("github", token, {
        "service": "GitHub",
        "type": "Personal Access Token",
        "permissions": "repo, workflow"
    })

def get_github_token() -> Optional[str]:
    """從SuperMemory獲取GitHub token"""
    return token_manager.get_token("github")

def auto_git_push_with_supermemory_auth() -> bool:
    """使用SuperMemory認證自動Git推送"""
    return git_auth_manager.auto_retry_git_push()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 supermemory_token_manager.py store-github <token>")
        print("  python3 supermemory_token_manager.py get-github")
        print("  python3 supermemory_token_manager.py list")
        print("  python3 supermemory_token_manager.py auto-push")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "store-github" and len(sys.argv) > 2:
        token = sys.argv[2]
        store_github_token(token)
        
    elif command == "get-github":
        token = get_github_token()
        if token:
            print(f"GitHub Token: {token[:8]}...{token[-8:]}")
        else:
            print("未找到GitHub token")
            
    elif command == "list":
        tokens = token_manager.list_stored_tokens()
        print("📋 SuperMemory中存儲的tokens:")
        for service, info in tokens.items():
            print(f"  {service}: {info['stored_at']} (hash: {info['hash_preview']})")
            
    elif command == "auto-push":
        success = auto_git_push_with_supermemory_auth()
        sys.exit(0 if success else 1)
        
    else:
        print("❌ 未知命令")
        sys.exit(1)

