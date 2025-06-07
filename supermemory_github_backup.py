#!/usr/bin/env python3
"""
SuperMemory GitHub備份系統
將SuperMemory工作區數據備份到GitHub
"""

import os
import sys
import json
import subprocess
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import shutil

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperMemoryBackupManager:
    """SuperMemory GitHub備份管理器"""
    
    def __init__(self, api_key: str = None, github_token: str = None):
        """初始化備份管理器"""
        self.api_key = api_key or os.environ.get("SUPERMEMORY_API_KEY")
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        
        # SuperMemory API配置
        self.base_urls = [
            "https://api.supermemory.ai/v1",
            "https://supermemory.ai/api/v1",
            "https://api.supermemory.com/v1"
        ]
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        # GitHub配置
        self.github_headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.github_token else {}
        
        logger.info("SuperMemory備份管理器初始化完成")
    
    def discover_supermemory_endpoint(self) -> Optional[str]:
        """發現可用的SuperMemory API端點"""
        logger.info("🔍 發現SuperMemory API端點...")
        
        for base_url in self.base_urls:
            try:
                # 嘗試健康檢查
                response = requests.get(
                    f"{base_url}/health", 
                    headers=self.headers, 
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ 發現可用端點: {base_url}")
                    return base_url
                    
            except requests.exceptions.RequestException:
                continue
        
        # 如果沒有找到健康檢查端點，嘗試直接調用API
        for base_url in self.base_urls:
            try:
                response = requests.get(
                    f"{base_url}/workspaces", 
                    headers=self.headers, 
                    timeout=10
                )
                
                if response.status_code in [200, 401, 403]:  # 這些狀態碼表示端點存在
                    logger.info(f"✅ 發現API端點: {base_url}")
                    return base_url
                    
            except requests.exceptions.RequestException:
                continue
        
        logger.warning("❌ 未找到可用的SuperMemory API端點")
        return None
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """列出所有工作區"""
        logger.info("📋 獲取SuperMemory工作區列表...")
        
        endpoint = self.discover_supermemory_endpoint()
        if not endpoint:
            return []
        
        try:
            response = requests.get(
                f"{endpoint}/workspaces",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                workspaces = response.json()
                logger.info(f"✅ 發現 {len(workspaces)} 個工作區")
                return workspaces
            else:
                logger.error(f"❌ 獲取工作區失敗: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 獲取工作區異常: {e}")
            return []
    
    def export_workspace_data(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """導出工作區數據"""
        logger.info(f"📤 導出工作區數據: {workspace_id}")
        
        endpoint = self.discover_supermemory_endpoint()
        if not endpoint:
            return None
        
        try:
            # 獲取工作區詳情
            response = requests.get(
                f"{endpoint}/workspaces/{workspace_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ 獲取工作區詳情失敗: {response.status_code}")
                return None
            
            workspace_info = response.json()
            
            # 獲取工作區中的記憶
            memories_response = requests.get(
                f"{endpoint}/workspaces/{workspace_id}/memories",
                headers=self.headers,
                timeout=60
            )
            
            memories = []
            if memories_response.status_code == 200:
                memories = memories_response.json()
            
            # 組合導出數據
            export_data = {
                "workspace_info": workspace_info,
                "memories": memories,
                "export_timestamp": datetime.now().isoformat(),
                "total_memories": len(memories)
            }
            
            logger.info(f"✅ 工作區數據導出完成: {len(memories)} 條記憶")
            return export_data
            
        except Exception as e:
            logger.error(f"❌ 導出工作區數據異常: {e}")
            return None
    
    def create_github_backup_repo(self, repo_name: str, description: str = None) -> bool:
        """創建GitHub備份倉庫"""
        logger.info(f"🏗️ 創建GitHub備份倉庫: {repo_name}")
        
        if not self.github_token:
            logger.error("❌ 沒有GitHub token")
            return False
        
        try:
            # 檢查倉庫是否已存在
            check_response = requests.get(
                f"https://api.github.com/repos/{self._get_github_username()}/{repo_name}",
                headers=self.github_headers
            )
            
            if check_response.status_code == 200:
                logger.info(f"✅ 倉庫已存在: {repo_name}")
                return True
            
            # 創建新倉庫
            create_data = {
                "name": repo_name,
                "description": description or f"SuperMemory工作區備份 - {datetime.now().strftime('%Y-%m-%d')}",
                "private": True,
                "auto_init": True
            }
            
            response = requests.post(
                "https://api.github.com/user/repos",
                headers=self.github_headers,
                json=create_data
            )
            
            if response.status_code == 201:
                logger.info(f"✅ GitHub倉庫創建成功: {repo_name}")
                return True
            else:
                logger.error(f"❌ 創建GitHub倉庫失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 創建GitHub倉庫異常: {e}")
            return False
    
    def _get_github_username(self) -> str:
        """獲取GitHub用戶名"""
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self.github_headers
            )
            
            if response.status_code == 200:
                return response.json()["login"]
            else:
                return "unknown"
                
        except Exception:
            return "unknown"
    
    def backup_workspace_to_github(self, workspace_id: str, repo_name: str = None) -> bool:
        """備份工作區到GitHub"""
        logger.info(f"🚀 開始備份工作區到GitHub: {workspace_id}")
        
        # 1. 導出工作區數據
        workspace_data = self.export_workspace_data(workspace_id)
        if not workspace_data:
            logger.error("❌ 無法導出工作區數據")
            return False
        
        # 2. 準備倉庫名稱
        if not repo_name:
            workspace_name = workspace_data.get("workspace_info", {}).get("name", workspace_id)
            repo_name = f"supermemory-backup-{workspace_name}".lower().replace(" ", "-")
        
        # 3. 創建GitHub倉庫
        if not self.create_github_backup_repo(repo_name):
            logger.error("❌ 無法創建GitHub倉庫")
            return False
        
        # 4. 克隆倉庫並推送數據
        return self._push_data_to_github(workspace_data, repo_name)
    
    def _push_data_to_github(self, workspace_data: Dict[str, Any], repo_name: str) -> bool:
        """推送數據到GitHub倉庫"""
        logger.info(f"📤 推送數據到GitHub倉庫: {repo_name}")
        
        username = self._get_github_username()
        repo_url = f"https://{self.github_token}@github.com/{username}/{repo_name}.git"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # 克隆倉庫
                subprocess.run([
                    "git", "clone", repo_url, temp_dir
                ], check=True, capture_output=True)
                
                # 創建數據文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 保存工作區信息
                workspace_info_file = Path(temp_dir) / "workspace_info.json"
                with open(workspace_info_file, 'w', encoding='utf-8') as f:
                    json.dump(workspace_data["workspace_info"], f, indent=2, ensure_ascii=False)
                
                # 保存記憶數據
                memories_file = Path(temp_dir) / f"memories_{timestamp}.json"
                with open(memories_file, 'w', encoding='utf-8') as f:
                    json.dump(workspace_data["memories"], f, indent=2, ensure_ascii=False)
                
                # 創建README
                readme_content = f"""# SuperMemory工作區備份

## 工作區信息
- **備份時間**: {workspace_data['export_timestamp']}
- **記憶總數**: {workspace_data['total_memories']}
- **工作區ID**: {workspace_data.get('workspace_info', {}).get('id', 'unknown')}

## 文件說明
- `workspace_info.json`: 工作區基本信息
- `memories_{{timestamp}}.json`: 記憶數據備份

## 備份歷史
- {timestamp}: {workspace_data['total_memories']} 條記憶
"""
                
                readme_file = Path(temp_dir) / "README.md"
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                
                # Git操作
                os.chdir(temp_dir)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run([
                    "git", "commit", "-m", 
                    f"SuperMemory備份 {timestamp} - {workspace_data['total_memories']} 條記憶"
                ], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
                
                logger.info(f"✅ 數據推送成功: {repo_name}")
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Git操作失敗: {e}")
                return False
            except Exception as e:
                logger.error(f"❌ 推送數據異常: {e}")
                return False
    
    def backup_all_workspaces(self) -> Dict[str, bool]:
        """備份所有工作區"""
        logger.info("🚀 開始備份所有SuperMemory工作區...")
        
        workspaces = self.list_workspaces()
        if not workspaces:
            logger.warning("⚠️ 沒有找到工作區")
            return {}
        
        results = {}
        
        for workspace in workspaces:
            workspace_id = workspace.get("id")
            workspace_name = workspace.get("name", workspace_id)
            
            logger.info(f"📋 備份工作區: {workspace_name} ({workspace_id})")
            
            success = self.backup_workspace_to_github(workspace_id)
            results[workspace_id] = success
            
            if success:
                logger.info(f"✅ 工作區備份成功: {workspace_name}")
            else:
                logger.error(f"❌ 工作區備份失敗: {workspace_name}")
        
        # 打印總結
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"📊 備份完成: {successful}/{total} 個工作區成功")
        
        return results

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperMemory GitHub備份工具")
    parser.add_argument("--list-workspaces", action="store_true", help="列出所有工作區")
    parser.add_argument("--backup-workspace", help="備份指定工作區")
    parser.add_argument("--backup-all", action="store_true", help="備份所有工作區")
    parser.add_argument("--repo-name", help="指定GitHub倉庫名稱")
    
    args = parser.parse_args()
    
    # 初始化備份管理器
    backup_manager = SuperMemoryBackupManager()
    
    if args.list_workspaces:
        workspaces = backup_manager.list_workspaces()
        print(f"\n📋 SuperMemory工作區列表 ({len(workspaces)} 個):")
        print("=" * 60)
        
        for workspace in workspaces:
            workspace_id = workspace.get("id", "unknown")
            workspace_name = workspace.get("name", "未命名")
            created_at = workspace.get("created_at", "未知")
            
            print(f"🗂️  {workspace_name}")
            print(f"   ID: {workspace_id}")
            print(f"   創建時間: {created_at}")
            print()
    
    elif args.backup_workspace:
        success = backup_manager.backup_workspace_to_github(
            args.backup_workspace, 
            args.repo_name
        )
        
        if success:
            print("✅ 工作區備份成功!")
        else:
            print("❌ 工作區備份失敗!")
    
    elif args.backup_all:
        results = backup_manager.backup_all_workspaces()
        
        print(f"\n📊 備份結果:")
        print("=" * 60)
        
        for workspace_id, success in results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"{status} {workspace_id}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

