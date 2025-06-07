#!/usr/bin/env python3
"""
記憶存儲模塊 (Memory Storage Module)
PowerAutomation 記憶系統的存儲層

提供高效的記憶存儲、檢索和管理功能
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StoredMemory:
    """存儲的記憶條目"""
    id: str
    content: str
    memory_type: str
    importance_score: int
    importance_level: str
    context_info: Dict[str, Any]
    created_at: str
    updated_at: str
    tags: List[str]
    source: str
    session_id: str
    related_memories: List[str]
    access_count: int
    last_accessed: str

class MemoryStorage:
    """記憶存儲管理器"""
    
    def __init__(self, db_path: str = "memory-system/memory-storage/memories.db"):
        self.db_path = db_path
        self.ensure_database()
        
    def ensure_database(self):
        """確保數據庫和表結構存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance_score INTEGER NOT NULL,
                    importance_level TEXT NOT NULL,
                    context_info TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    source TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    related_memories TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # 創建索引以提高查詢性能
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance_score ON memories(importance_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON memories(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memories(session_id)")
            
            conn.commit()
            
    def store_memory(self, memory: StoredMemory) -> bool:
        """存儲記憶"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, content, memory_type, importance_score, importance_level,
                     context_info, created_at, updated_at, tags, source, session_id,
                     related_memories, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    memory.memory_type,
                    memory.importance_score,
                    memory.importance_level,
                    json.dumps(memory.context_info, ensure_ascii=False),
                    memory.created_at,
                    memory.updated_at,
                    json.dumps(memory.tags, ensure_ascii=False),
                    memory.source,
                    memory.session_id,
                    json.dumps(memory.related_memories, ensure_ascii=False),
                    memory.access_count,
                    memory.last_accessed
                ))
                conn.commit()
                
            logger.info(f"記憶已存儲: {memory.id}")
            return True
            
        except Exception as e:
            logger.error(f"存儲記憶失敗: {e}")
            return False
            
    def get_memory(self, memory_id: str) -> Optional[StoredMemory]:
        """獲取指定記憶"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
                row = cursor.fetchone()
                
                if row:
                    # 更新訪問統計
                    self._update_access_stats(memory_id)
                    return self._row_to_memory(row)
                    
            return None
            
        except Exception as e:
            logger.error(f"獲取記憶失敗: {e}")
            return None
            
    def search_memories(self, 
                       query: str = None,
                       memory_type: str = None,
                       min_importance: int = None,
                       max_importance: int = None,
                       source: str = None,
                       session_id: str = None,
                       tags: List[str] = None,
                       limit: int = 50) -> List[StoredMemory]:
        """搜索記憶"""
        try:
            conditions = []
            params = []
            
            if query:
                conditions.append("content LIKE ?")
                params.append(f"%{query}%")
                
            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type)
                
            if min_importance is not None:
                conditions.append("importance_score >= ?")
                params.append(min_importance)
                
            if max_importance is not None:
                conditions.append("importance_score <= ?")
                params.append(max_importance)
                
            if source:
                conditions.append("source = ?")
                params.append(source)
                
            if session_id:
                conditions.append("session_id = ?")
                params.append(session_id)
                
            if tags:
                for tag in tags:
                    conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
                    
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f"""
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ?
            """
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_memory(row) for row in rows]
                
        except Exception as e:
            logger.error(f"搜索記憶失敗: {e}")
            return []
            
    def get_recent_memories(self, hours: int = 24, limit: int = 20) -> List[StoredMemory]:
        """獲取最近的記憶"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM memories 
                    WHERE created_at >= ?
                    ORDER BY importance_score DESC, created_at DESC
                    LIMIT ?
                """, (cutoff_time, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_memory(row) for row in rows]
                
        except Exception as e:
            logger.error(f"獲取最近記憶失敗: {e}")
            return []
            
    def get_important_memories(self, min_score: int = 7, limit: int = 30) -> List[StoredMemory]:
        """獲取重要記憶"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM memories 
                    WHERE importance_score >= ?
                    ORDER BY importance_score DESC, access_count DESC
                    LIMIT ?
                """, (min_score, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_memory(row) for row in rows]
                
        except Exception as e:
            logger.error(f"獲取重要記憶失敗: {e}")
            return []
            
    def get_related_memories(self, memory_id: str, limit: int = 10) -> List[StoredMemory]:
        """獲取相關記憶"""
        try:
            # 首先獲取目標記憶
            target_memory = self.get_memory(memory_id)
            if not target_memory:
                return []
                
            # 獲取直接關聯的記憶
            related_ids = target_memory.related_memories
            related_memories = []
            
            for related_id in related_ids:
                memory = self.get_memory(related_id)
                if memory:
                    related_memories.append(memory)
                    
            # 如果直接關聯不足，基於標籤和類型查找相似記憶
            if len(related_memories) < limit:
                similar_memories = self.search_memories(
                    memory_type=target_memory.memory_type,
                    tags=target_memory.tags,
                    limit=limit - len(related_memories)
                )
                
                # 排除已有的記憶
                existing_ids = {m.id for m in related_memories} | {memory_id}
                for memory in similar_memories:
                    if memory.id not in existing_ids:
                        related_memories.append(memory)
                        
            return related_memories[:limit]
            
        except Exception as e:
            logger.error(f"獲取相關記憶失敗: {e}")
            return []
            
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """更新記憶"""
        try:
            # 構建更新語句
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in ['context_info', 'tags', 'related_memories']:
                    set_clauses.append(f"{field} = ?")
                    params.append(json.dumps(value, ensure_ascii=False))
                else:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
                    
            # 添加更新時間
            set_clauses.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            params.append(memory_id)
            
            sql = f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(sql, params)
                conn.commit()
                
            logger.info(f"記憶已更新: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新記憶失敗: {e}")
            return False
            
    def delete_memory(self, memory_id: str) -> bool:
        """刪除記憶"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                
            logger.info(f"記憶已刪除: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"刪除記憶失敗: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """獲取存儲統計信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 總記憶數
                total_count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                
                # 按重要性分布
                importance_dist = {}
                cursor = conn.execute("SELECT importance_level, COUNT(*) FROM memories GROUP BY importance_level")
                for level, count in cursor.fetchall():
                    importance_dist[level] = count
                    
                # 按類型分布
                type_dist = {}
                cursor = conn.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
                for mem_type, count in cursor.fetchall():
                    type_dist[mem_type] = count
                    
                # 最近活動
                recent_count = conn.execute("""
                    SELECT COUNT(*) FROM memories 
                    WHERE created_at >= ?
                """, ((datetime.now() - timedelta(days=7)).isoformat(),)).fetchone()[0]
                
                return {
                    "total_memories": total_count,
                    "importance_distribution": importance_dist,
                    "type_distribution": type_dist,
                    "recent_memories_7days": recent_count,
                    "database_path": self.db_path
                }
                
        except Exception as e:
            logger.error(f"獲取統計信息失敗: {e}")
            return {}
            
    def _update_access_stats(self, memory_id: str):
        """更新訪問統計"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE memories 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), memory_id))
                conn.commit()
                
        except Exception as e:
            logger.error(f"更新訪問統計失敗: {e}")
            
    def _row_to_memory(self, row) -> StoredMemory:
        """將數據庫行轉換為記憶對象"""
        return StoredMemory(
            id=row[0],
            content=row[1],
            memory_type=row[2],
            importance_score=row[3],
            importance_level=row[4],
            context_info=json.loads(row[5]) if row[5] else {},
            created_at=row[6],
            updated_at=row[7],
            tags=json.loads(row[8]) if row[8] else [],
            source=row[9],
            session_id=row[10],
            related_memories=json.loads(row[11]) if row[11] else [],
            access_count=row[12] or 0,
            last_accessed=row[13]
        )

# 全局實例
memory_storage = MemoryStorage()

def create_memory_id(content: str, timestamp: str = None) -> str:
    """創建記憶ID"""
    if not timestamp:
        timestamp = datetime.now().isoformat()
    return hashlib.md5(f"{content}_{timestamp}".encode()).hexdigest()

if __name__ == "__main__":
    # 測試記憶存儲功能
    storage = MemoryStorage()
    
    # 創建測試記憶
    test_memory = StoredMemory(
        id=create_memory_id("測試記憶存儲功能"),
        content="測試記憶存儲功能",
        memory_type="file_operation",
        importance_score=5,
        importance_level="Normal",
        context_info={"test": True},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        tags=["test", "memory", "storage"],
        source="memory_storage_test",
        session_id="test_session",
        related_memories=[],
        access_count=0,
        last_accessed=datetime.now().isoformat()
    )
    
    # 測試存儲
    if storage.store_memory(test_memory):
        print("✅ 記憶存儲測試成功")
        
        # 測試檢索
        retrieved = storage.get_memory(test_memory.id)
        if retrieved:
            print(f"✅ 記憶檢索測試成功: {retrieved.content}")
            
        # 測試搜索
        results = storage.search_memories(query="測試", limit=5)
        print(f"✅ 記憶搜索測試成功: 找到 {len(results)} 條記憶")
        
        # 測試統計
        stats = storage.get_statistics()
        print(f"✅ 統計信息: {stats}")
        
    else:
        print("❌ 記憶存儲測試失敗")

