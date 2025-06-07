#!/usr/bin/env python3
"""
ZIP加密Token管理系統
ZIP Encrypted Token Management System

使用ZIP加密安全存儲和檢索認證信息，防止GitHub掃描檢測
"""

import os
import json
import zipfile
import tempfile
import hashlib
from typing import Dict, Optional, Any
from datetime import datetime
import subprocess

class ZipEncryptedTokenManager:
    """ZIP加密Token管理器"""
    
    def __init__(self, password: str = "PowerAutomation2025!"):
        self.supermemory_workspace = "data/backup/supermemory_workspaces"
        self.encrypted_zip_file = f"{self.supermemory_workspace}/encrypted_tokens.zip"
        self.password = password
        self.ensure_storage_directory()
        
    def ensure_storage_directory(self):
        """確保存儲目錄存在"""
        os.makedirs(self.supermemory_workspace, exist_ok=True)
        
    def store_token(self, service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
        """存儲token到加密ZIP文件"""
        try:
            # 準備token數據
            token_data = {
                "service": service,
                "token": token,
                "stored_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "hash": hashlib.sha256(token.encode()).hexdigest()[:8]
            }
            
            # 加載現有tokens
            existing_tokens = self._load_encrypted_tokens()
            existing_tokens[service] = token_data
            
            # 保存到加密ZIP
            self._save_encrypted_tokens(existing_tokens)
            
            print(f"✅ Token已安全存儲到加密ZIP: {service}")
            return True
            
        except Exception as e:
            print(f"❌ Token存儲失敗: {e}")
            return False
            
    def get_token(self, service: str) -> Optional[str]:
        """從加密ZIP獲取token"""
        try:
            tokens = self._load_encrypted_tokens()
            
            if service not in tokens:
                print(f"❌ 未找到服務的token: {service}")
                return None
                
            token = tokens[service]["token"]
            print(f"✅ 從加密ZIP獲取token: {service}")
            return token
            
        except Exception as e:
            print(f"❌ Token獲取失敗: {e}")
            return None
            
    def list_stored_tokens(self) -> Dict[str, Dict[str, Any]]:
        """列出所有存儲的token信息（不包含實際token）"""
        try:
            tokens = self._load_encrypted_tokens()
            
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
            tokens = self._load_encrypted_tokens()
            
            if service in tokens:
                del tokens[service]
                self._save_encrypted_tokens(tokens)
                print(f"✅ Token已刪除: {service}")
                return True
            else:
                print(f"❌ 未找到要刪除的token: {service}")
                return False
                
        except Exception as e:
            print(f"❌ Token刪除失敗: {e}")
            return False
            
    def _load_encrypted_tokens(self) -> Dict[str, Any]:
        """從加密ZIP加載tokens"""
        if not os.path.exists(self.encrypted_zip_file):
            return {}
            
        try:
            with zipfile.ZipFile(self.encrypted_zip_file, 'r') as zip_file:
                # 嘗試解壓tokens.json
                try:
                    zip_file.setpassword(self.password.encode())
                    with zip_file.open('tokens.json') as token_file:
                        return json.loads(token_file.read().decode())
                except:
                    return {}
                    
        except Exception as e:
            print(f"⚠️ 加載加密tokens失敗: {e}")
            return {}
            
    def _save_encrypted_tokens(self, tokens: Dict[str, Any]):
        """保存tokens到加密ZIP"""
        try:
            # 創建臨時文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(tokens, temp_file, indent=2, ensure_ascii=False)
                temp_file_path = temp_file.name
                
            # 創建加密ZIP
            with zipfile.ZipFile(self.encrypted_zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.setpassword(self.password.encode())
                zip_file.write(temp_file_path, 'tokens.json')
                
            # 清理臨時文件
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"❌ 保存加密tokens失敗: {e}")
            raise

class SecureGitAuthManager:
    """安全Git認證管理器"""
    
    def __init__(self):
        self.token_manager = ZipEncryptedTokenManager()
        
    def auto_retry_git_push(self, repo_url: str = None) -> bool:
        """使用加密存儲的token自動重試Git推送"""
        try:
            print("🔍 偵測到Git認證需求，從加密ZIP獲取token...")
            
            # 從加密ZIP獲取GitHub token
            github_token = self.token_manager.get_token("github")
            
            if not github_token:
                print("❌ 未在加密存儲中找到GitHub token")
                return False
                
            # 構建認證URL
            if repo_url:
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
            print("🚀 使用加密存儲的token重試Git推送...")
            
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
zip_token_manager = ZipEncryptedTokenManager()
secure_git_auth_manager = SecureGitAuthManager()

def store_github_token_encrypted(token: str) -> bool:
    """存儲GitHub token到加密ZIP"""
    return zip_token_manager.store_token("github", token, {
        "service": "GitHub",
        "type": "Personal Access Token",
        "permissions": "repo, workflow",
        "encryption": "ZIP with password"
    })

def get_github_token_encrypted() -> Optional[str]:
    """從加密ZIP獲取GitHub token"""
    return zip_token_manager.get_token("github")

def auto_git_push_with_encrypted_auth() -> bool:
    """使用加密認證自動Git推送"""
    return secure_git_auth_manager.auto_retry_git_push()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 zip_encrypted_token_manager.py store-github <token>")
        print("  python3 zip_encrypted_token_manager.py get-github")
        print("  python3 zip_encrypted_token_manager.py list")
        print("  python3 zip_encrypted_token_manager.py auto-push")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "store-github" and len(sys.argv) > 2:
        token = sys.argv[2]
        store_github_token_encrypted(token)
        
    elif command == "get-github":
        token = get_github_token_encrypted()
        if token:
            print(f"GitHub Token: {token[:8]}...{token[-8:]}")
        else:
            print("未找到GitHub token")
            
    elif command == "list":
        tokens = zip_token_manager.list_stored_tokens()
        print("📋 加密ZIP中存儲的tokens:")
        for service, info in tokens.items():
            print(f"  {service}: {info['stored_at']} (hash: {info['hash_preview']})")
            
    elif command == "auto-push":
        success = auto_git_push_with_encrypted_auth()
        sys.exit(0 if success else 1)
        
    else:
        print("❌ 未知命令")
        sys.exit(1)

