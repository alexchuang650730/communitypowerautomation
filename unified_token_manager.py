#!/usr/bin/env python3
"""
統一Token管理系統 v1.0
Unified Token Management System

整合ZIP加密和SuperMemory兩套token管理系統
確保所有備份機制都能找到GitHub token
"""

import os
import json
import zipfile
import base64
import hashlib
from typing import Dict, Optional, Any
from datetime import datetime

class UnifiedTokenManager:
    """統一Token管理器"""
    
    def __init__(self):
        self.supermemory_workspace = "data/backup/supermemory_workspaces"
        self.zip_file_path = f"{self.supermemory_workspace}/encrypted_tokens.zip"
        self.json_file_path = f"{self.supermemory_workspace}/secure_tokens.json"
        self.zip_password = b'powerautomation2024'
        
        self.ensure_storage_directory()
        
    def ensure_storage_directory(self):
        """確保存儲目錄存在"""
        os.makedirs(self.supermemory_workspace, exist_ok=True)
        
    def get_token(self, service: str) -> Optional[str]:
        """統一獲取token接口"""
        # 優先從ZIP加密系統獲取
        token = self._get_token_from_zip(service)
        if token:
            return token
            
        # 備用：從JSON文件獲取
        token = self._get_token_from_json(service)
        if token:
            return token
            
        return None
        
    def _get_token_from_zip(self, service: str) -> Optional[str]:
        """從ZIP加密文件獲取token"""
        try:
            if not os.path.exists(self.zip_file_path):
                return None
                
            with zipfile.ZipFile(self.zip_file_path, 'r') as zip_file:
                if 'tokens.json' not in zip_file.namelist():
                    return None
                    
                content = zip_file.read('tokens.json', pwd=self.zip_password)
                tokens_data = json.loads(content.decode())
                
                if service in tokens_data:
                    return tokens_data[service].get('token')
                    
        except Exception as e:
            print(f"從ZIP獲取token失敗: {e}")
            
        return None
        
    def _get_token_from_json(self, service: str) -> Optional[str]:
        """從JSON文件獲取token"""
        try:
            if not os.path.exists(self.json_file_path):
                return None
                
            with open(self.json_file_path, 'r') as f:
                tokens_data = json.load(f)
                
            if service in tokens_data:
                encrypted_token = tokens_data[service].get('encrypted_token')
                if encrypted_token:
                    return base64.b64decode(encrypted_token.encode()).decode()
                    
        except Exception as e:
            print(f"從JSON獲取token失敗: {e}")
            
        return None
        
    def store_token(self, service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
        """統一存儲token接口"""
        success_zip = self._store_token_to_zip(service, token, metadata)
        success_json = self._store_token_to_json(service, token, metadata)
        
        if success_zip or success_json:
            print(f"✅ Token已存儲到統一管理系統: {service}")
            return True
        else:
            print(f"❌ Token存儲失敗: {service}")
            return False
            
    def _store_token_to_zip(self, service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
        """存儲token到ZIP加密文件"""
        try:
            # 讀取現有tokens
            tokens_data = {}
            if os.path.exists(self.zip_file_path):
                with zipfile.ZipFile(self.zip_file_path, 'r') as zip_file:
                    if 'tokens.json' in zip_file.namelist():
                        content = zip_file.read('tokens.json', pwd=self.zip_password)
                        tokens_data = json.loads(content.decode())
            
            # 添加新token
            tokens_data[service] = {
                "service": service,
                "token": token,
                "stored_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "hash": hashlib.sha256(token.encode()).hexdigest()[:8]
            }
            
            # 保存到ZIP
            with zipfile.ZipFile(self.zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('tokens.json', json.dumps(tokens_data, indent=2), pwd=self.zip_password)
                
            return True
            
        except Exception as e:
            print(f"存儲到ZIP失敗: {e}")
            return False
            
    def _store_token_to_json(self, service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
        """存儲token到JSON文件"""
        try:
            # 讀取現有tokens
            tokens_data = {}
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as f:
                    tokens_data = json.load(f)
            
            # 加密token
            encrypted_token = base64.b64encode(token.encode()).decode()
            
            # 添加新token
            tokens_data[service] = {
                "encrypted_token": encrypted_token,
                "stored_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "hash": hashlib.sha256(token.encode()).hexdigest()[:8]
            }
            
            # 保存到JSON
            with open(self.json_file_path, 'w') as f:
                json.dump(tokens_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"存儲到JSON失敗: {e}")
            return False
            
    def sync_tokens(self) -> bool:
        """同步兩套系統的tokens"""
        try:
            # 從ZIP讀取所有tokens
            zip_tokens = {}
            if os.path.exists(self.zip_file_path):
                with zipfile.ZipFile(self.zip_file_path, 'r') as zip_file:
                    if 'tokens.json' in zip_file.namelist():
                        content = zip_file.read('tokens.json', pwd=self.zip_password)
                        zip_tokens = json.loads(content.decode())
            
            # 從JSON讀取所有tokens
            json_tokens = {}
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as f:
                    json_tokens = json.load(f)
            
            # 同步：將ZIP中的tokens同步到JSON
            synced_count = 0
            for service, token_data in zip_tokens.items():
                if service not in json_tokens:
                    token = token_data.get('token')
                    if token:
                        self._store_token_to_json(service, token, token_data.get('metadata', {}))
                        synced_count += 1
            
            # 同步：將JSON中的tokens同步到ZIP
            for service, token_data in json_tokens.items():
                if service not in zip_tokens:
                    encrypted_token = token_data.get('encrypted_token')
                    if encrypted_token:
                        token = base64.b64decode(encrypted_token.encode()).decode()
                        self._store_token_to_zip(service, token, token_data.get('metadata', {}))
                        synced_count += 1
            
            print(f"✅ Token同步完成，同步了 {synced_count} 個tokens")
            return True
            
        except Exception as e:
            print(f"❌ Token同步失敗: {e}")
            return False
            
    def list_tokens(self) -> Dict[str, Dict[str, Any]]:
        """列出所有可用的tokens"""
        all_tokens = {}
        
        # 從ZIP獲取
        try:
            if os.path.exists(self.zip_file_path):
                with zipfile.ZipFile(self.zip_file_path, 'r') as zip_file:
                    if 'tokens.json' in zip_file.namelist():
                        content = zip_file.read('tokens.json', pwd=self.zip_password)
                        zip_tokens = json.loads(content.decode())
                        for service, data in zip_tokens.items():
                            all_tokens[service] = {
                                "source": "ZIP",
                                "stored_at": data.get('stored_at'),
                                "hash": data.get('hash'),
                                "metadata": data.get('metadata', {})
                            }
        except Exception as e:
            print(f"讀取ZIP tokens失敗: {e}")
        
        # 從JSON獲取
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r') as f:
                    json_tokens = json.load(f)
                    for service, data in json_tokens.items():
                        if service not in all_tokens:
                            all_tokens[service] = {
                                "source": "JSON",
                                "stored_at": data.get('stored_at'),
                                "hash": data.get('hash'),
                                "metadata": data.get('metadata', {})
                            }
                        else:
                            all_tokens[service]["source"] = "ZIP+JSON"
        except Exception as e:
            print(f"讀取JSON tokens失敗: {e}")
            
        return all_tokens
        
    def test_token(self, service: str) -> bool:
        """測試token是否可用"""
        token = self.get_token(service)
        if not token:
            print(f"❌ 找不到 {service} 的token")
            return False
            
        if service == "github":
            # 測試GitHub token
            import subprocess
            try:
                # 設置環境變量
                env = os.environ.copy()
                env['GITHUB_TOKEN'] = token
                
                # 測試API調用
                result = subprocess.run([
                    'curl', '-H', f'Authorization: token {token}',
                    'https://api.github.com/user'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and '"login"' in result.stdout:
                    print(f"✅ {service} token 測試成功")
                    return True
                else:
                    print(f"❌ {service} token 測試失敗")
                    return False
                    
            except Exception as e:
                print(f"❌ {service} token 測試出錯: {e}")
                return False
        
        print(f"✅ {service} token 存在 (未測試)")
        return True

# 全局實例
unified_token_manager = UnifiedTokenManager()

def get_token(service: str) -> Optional[str]:
    """便捷函數：獲取token"""
    return unified_token_manager.get_token(service)

def store_token(service: str, token: str, metadata: Dict[str, Any] = None) -> bool:
    """便捷函數：存儲token"""
    return unified_token_manager.store_token(service, token, metadata)

def sync_tokens() -> bool:
    """便捷函數：同步tokens"""
    return unified_token_manager.sync_tokens()

def list_tokens() -> Dict[str, Dict[str, Any]]:
    """便捷函數：列出tokens"""
    return unified_token_manager.list_tokens()

def test_token(service: str) -> bool:
    """便捷函數：測試token"""
    return unified_token_manager.test_token(service)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 unified_token_manager.py sync")
        print("  python3 unified_token_manager.py list")
        print("  python3 unified_token_manager.py get <service>")
        print("  python3 unified_token_manager.py test <service>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sync":
        sync_tokens()
    elif command == "list":
        tokens = list_tokens()
        print("📋 可用的tokens:")
        for service, info in tokens.items():
            print(f"  {service}: {info['source']} (hash: {info['hash']})")
    elif command == "get" and len(sys.argv) > 2:
        service = sys.argv[2]
        token = get_token(service)
        if token:
            print(f"✅ 找到 {service} token: {token[:20]}...")
        else:
            print(f"❌ 找不到 {service} token")
    elif command == "test" and len(sys.argv) > 2:
        service = sys.argv[2]
        test_token(service)
    else:
        print("❌ 未知命令")

