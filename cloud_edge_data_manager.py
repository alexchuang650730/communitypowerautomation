"""
PowerAutomation v0.3 端雲協同數據管理系統

此模塊實現端雲協同的數據管理功能，包括：
- VS Code插件交互數據接收
- 數據預處理和標準化
- 訓練數據管理
- 模型數據同步
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import aiofiles
import aiohttp
from cryptography.fernet import Fernet

# 導入標準化日誌系統
from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """交互類型枚舉"""
    CODE_COMPLETION = "code_completion"
    DEBUG = "debug"
    REFACTOR = "refactor"
    TEST = "test"
    DOCUMENTATION = "documentation"
    ERROR_FIX = "error_fix"
    OPTIMIZATION = "optimization"

class DataStatus(Enum):
    """數據狀態枚舉"""
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    TRAINING_READY = "training_ready"
    ARCHIVED = "archived"
    ERROR = "error"

@dataclass
class InteractionData:
    """標準化交互數據結構"""
    session_id: str
    timestamp: str
    user_id: str
    interaction_type: InteractionType
    context: Dict[str, Any]
    user_action: Dict[str, Any]
    ai_response: Dict[str, Any]
    outcome: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        data = asdict(self)
        data['interaction_type'] = self.interaction_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionData':
        """從字典創建實例"""
        data['interaction_type'] = InteractionType(data['interaction_type'])
        return cls(**data)

class CloudEdgeDataManager:
    """端雲協同數據管理器"""
    
    def __init__(self, data_dir: str = "data/training"):
        self.data_dir = Path(data_dir)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 確保目錄結構存在
        self._ensure_directory_structure()
        
        # 數據統計
        self.stats = {
            "total_interactions": 0,
            "daily_interactions": {},
            "user_interactions": {},
            "type_interactions": {}
        }
        
        log_info(LogCategory.SYSTEM, "端雲協同數據管理器初始化完成", {
            "data_dir": str(self.data_dir),
            "encryption_enabled": True
        })
    
    def _get_or_create_encryption_key(self) -> bytes:
        """獲取或創建加密密鑰"""
        key_file = self.data_dir / "encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(self.data_dir, exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _ensure_directory_structure(self):
        """確保目錄結構存在"""
        directories = [
            "interaction_data/daily",
            "interaction_data/by_user", 
            "interaction_data/by_project_type",
            "processed_data/training_sets",
            "processed_data/validation_sets",
            "processed_data/test_sets",
            "models/rl_models",
            "models/srt_models", 
            "models/ensemble_models",
            "metrics/performance_logs",
            "metrics/user_feedback",
            "metrics/model_comparisons"
        ]
        
        for dir_path in directories:
            (self.data_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    @performance_monitor("receive_interaction_data")
    async def receive_interaction_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """接收來自VS Code插件的交互數據"""
        try:
            # 驗證數據格式
            interaction = InteractionData.from_dict(data)
            
            # 生成唯一ID
            data_id = self._generate_data_id(interaction)
            
            # 加密敏感數據
            encrypted_data = self._encrypt_sensitive_data(interaction.to_dict())
            
            # 存儲原始數據
            await self._store_raw_data(data_id, encrypted_data)
            
            # 更新統計信息
            self._update_statistics(interaction)
            
            # 觸發數據處理
            asyncio.create_task(self._process_interaction_data(data_id, interaction))
            
            log_info(LogCategory.MEMORY, "接收交互數據成功", {
                "data_id": data_id,
                "interaction_type": interaction.interaction_type.value,
                "user_id": interaction.user_id[:8] + "..."  # 部分隱藏
            })
            
            return {
                "status": "success",
                "data_id": data_id,
                "message": "交互數據接收成功"
            }
            
        except Exception as e:
            log_error(LogCategory.MEMORY, "接收交互數據失敗", {
                "error": str(e),
                "data_preview": str(data)[:100] + "..."
            })
            return {
                "status": "error",
                "message": f"數據接收失敗: {str(e)}"
            }
    
    def _generate_data_id(self, interaction: InteractionData) -> str:
        """生成數據唯一ID"""
        content = f"{interaction.session_id}_{interaction.timestamp}_{interaction.user_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """加密敏感數據"""
        sensitive_fields = ['user_action', 'ai_response', 'context']
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data:
                field_data = json.dumps(encrypted_data[field]).encode()
                encrypted_data[field] = self.cipher_suite.encrypt(field_data).decode()
        
        return encrypted_data
    
    async def _store_raw_data(self, data_id: str, data: Dict[str, Any]):
        """存儲原始數據"""
        # 按日期存儲
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_dir = self.data_dir / "interaction_data" / "daily" / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = daily_dir / f"{data_id}.json"
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 按用戶存儲
        user_id = data.get('user_id', 'unknown')
        user_dir = self.data_dir / "interaction_data" / "by_user" / user_id[:8]
        user_dir.mkdir(parents=True, exist_ok=True)
        
        user_file = user_dir / f"{data_id}.json"
        async with aiofiles.open(user_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _update_statistics(self, interaction: InteractionData):
        """更新統計信息"""
        self.stats["total_interactions"] += 1
        
        # 按日期統計
        date_str = datetime.now().strftime("%Y-%m-%d")
        if date_str not in self.stats["daily_interactions"]:
            self.stats["daily_interactions"][date_str] = 0
        self.stats["daily_interactions"][date_str] += 1
        
        # 按用戶統計
        user_id = interaction.user_id[:8]
        if user_id not in self.stats["user_interactions"]:
            self.stats["user_interactions"][user_id] = 0
        self.stats["user_interactions"][user_id] += 1
        
        # 按類型統計
        interaction_type = interaction.interaction_type.value
        if interaction_type not in self.stats["type_interactions"]:
            self.stats["type_interactions"][interaction_type] = 0
        self.stats["type_interactions"][interaction_type] += 1
    
    async def _process_interaction_data(self, data_id: str, interaction: InteractionData):
        """處理交互數據"""
        try:
            # 數據清洗
            cleaned_data = await self._clean_data(interaction)
            
            # 特徵提取
            features = await self._extract_features(cleaned_data)
            
            # 生成訓練樣本
            training_sample = await self._generate_training_sample(cleaned_data, features)
            
            # 存儲處理後的數據
            await self._store_processed_data(data_id, training_sample)
            
            log_info(LogCategory.MEMORY, "交互數據處理完成", {
                "data_id": data_id,
                "features_count": len(features),
                "training_ready": True
            })
            
        except Exception as e:
            log_error(LogCategory.MEMORY, "交互數據處理失敗", {
                "data_id": data_id,
                "error": str(e)
            })
    
    async def _clean_data(self, interaction: InteractionData) -> Dict[str, Any]:
        """數據清洗"""
        # 移除敏感信息
        cleaned = interaction.to_dict()
        
        # 標準化代碼內容
        if 'context' in cleaned and 'surrounding_code' in cleaned['context']:
            code = cleaned['context']['surrounding_code']
            # 移除註釋中的敏感信息
            # 標準化變量名
            # 移除硬編碼的路徑和密鑰
            cleaned['context']['surrounding_code'] = self._sanitize_code(code)
        
        return cleaned
    
    def _sanitize_code(self, code: str) -> str:
        """代碼脫敏處理"""
        # 簡單的脫敏處理，實際應用中需要更複雜的邏輯
        import re
        
        # 移除可能的密鑰和密碼
        code = re.sub(r'(password|key|secret|token)\s*=\s*["\'][^"\']+["\']', 
                     r'\1="***"', code, flags=re.IGNORECASE)
        
        # 移除絕對路徑
        code = re.sub(r'/[a-zA-Z0-9_/.-]+/', '/path/to/', code)
        
        return code
    
    async def _extract_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """特徵提取"""
        features = {
            "interaction_type": data.get("interaction_type"),
            "code_length": len(data.get("context", {}).get("surrounding_code", "")),
            "response_time": data.get("ai_response", {}).get("response_time_ms", 0),
            "confidence_score": data.get("ai_response", {}).get("confidence_score", 0),
            "user_accepted": data.get("outcome", {}).get("accepted", False),
            "user_modified": data.get("outcome", {}).get("modified", False),
            "feedback_score": self._convert_feedback_to_score(
                data.get("outcome", {}).get("user_feedback", "neutral")
            )
        }
        
        return features
    
    def _convert_feedback_to_score(self, feedback: str) -> float:
        """將用戶反饋轉換為數值分數"""
        feedback_map = {
            "positive": 1.0,
            "neutral": 0.5,
            "negative": 0.0
        }
        return feedback_map.get(feedback, 0.5)
    
    async def _generate_training_sample(self, data: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """生成訓練樣本"""
        training_sample = {
            "input": {
                "context": data.get("context", {}),
                "user_action": data.get("user_action", {}),
                "features": features
            },
            "output": {
                "ai_response": data.get("ai_response", {}),
                "outcome": data.get("outcome", {})
            },
            "metadata": {
                "timestamp": data.get("timestamp"),
                "interaction_type": data.get("interaction_type"),
                "quality_score": features.get("feedback_score", 0.5)
            }
        }
        
        return training_sample
    
    async def _store_processed_data(self, data_id: str, training_sample: Dict[str, Any]):
        """存儲處理後的數據"""
        # 根據質量分數決定存儲位置
        quality_score = training_sample["metadata"]["quality_score"]
        
        if quality_score >= 0.8:
            target_dir = "training_sets"
        elif quality_score >= 0.6:
            target_dir = "validation_sets"
        else:
            target_dir = "test_sets"
        
        processed_dir = self.data_dir / "processed_data" / target_dir
        file_path = processed_dir / f"{data_id}_processed.json"
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(training_sample, ensure_ascii=False, indent=2))
    
    async def get_training_data(self, data_type: str = "training_sets", limit: int = None) -> List[Dict[str, Any]]:
        """獲取訓練數據"""
        data_dir = self.data_dir / "processed_data" / data_type
        training_data = []
        
        if not data_dir.exists():
            return training_data
        
        files = list(data_dir.glob("*.json"))
        if limit:
            files = files[:limit]
        
        for file_path in files:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    training_data.append(data)
            except Exception as e:
                log_error(LogCategory.MEMORY, "讀取訓練數據失敗", {
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return training_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return self.stats.copy()
    
    async def cleanup_old_data(self, days: int = 30):
        """清理舊數據"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        daily_dir = self.data_dir / "interaction_data" / "daily"
        if daily_dir.exists():
            for date_dir in daily_dir.iterdir():
                if date_dir.is_dir() and date_dir.name < cutoff_str:
                    # 歸檔而不是刪除
                    archive_dir = self.data_dir / "archived" / date_dir.name
                    archive_dir.parent.mkdir(parents=True, exist_ok=True)
                    date_dir.rename(archive_dir)
                    
                    log_info(LogCategory.SYSTEM, "數據歸檔完成", {
                        "date": date_dir.name,
                        "archive_path": str(archive_dir)
                    })

# 全局實例
cloud_edge_manager = CloudEdgeDataManager()

# 導出主要接口
__all__ = [
    'CloudEdgeDataManager',
    'InteractionData', 
    'InteractionType',
    'DataStatus',
    'cloud_edge_manager'
]

