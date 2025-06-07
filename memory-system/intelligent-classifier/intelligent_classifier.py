#!/usr/bin/env python3
"""
智能分類器 (Intelligent Classifier)
PowerAutomation 記憶系統的核心組件

負責自動判斷記憶的重要性和類型，實現智能分類
"""

import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportanceLevel(Enum):
    """重要性級別"""
    CRITICAL = (9, 10, "🔴", "Critical")    # bug、錯誤、崩潰
    IMPORTANT = (6, 8, "🟡", "Important")   # 決策、設計、解決方案
    NORMAL = (3, 5, "🟢", "Normal")         # 創建、更新、測試
    LOW = (1, 2, "⚪", "Low")               # 調試、臨時記錄
    
    def __init__(self, min_score, max_score, emoji, label):
        self.min_score = min_score
        self.max_score = max_score
        self.emoji = emoji
        self.label = label

class MemoryType(Enum):
    """記憶類型"""
    FILE_OPERATION = ("📁", "file_operation", "文件創建/修改/刪除")
    DECISION_MAKING = ("🧠", "decision_making", "設計決策、方案選擇")
    PROBLEM_SOLVING = ("🔧", "problem_solving", "問題發現和解決")
    STATUS_UPDATE = ("📊", "status_update", "項目狀態變更")
    CONVERSATION = ("💬", "conversation", "重要對話內容")
    
    def __init__(self, emoji, code, description):
        self.emoji = emoji
        self.code = code
        self.description = description

@dataclass
class MemoryEntry:
    """記憶條目"""
    id: str
    content: str
    source: str
    timestamp: str
    importance_score: int
    importance_level: ImportanceLevel
    memory_type: MemoryType
    keywords: List[str]
    context: Dict[str, Any]
    metadata: Dict[str, Any]

class IntelligentClassifier:
    """智能分類器"""
    
    def __init__(self, db_path: str = "memory-system/memory-storage/memories.db"):
        self.db_path = db_path
        self.init_database()
        
        # 重要性關鍵詞權重
        self.importance_keywords = {
            # Critical (9-10)
            "critical": {"weight": 10, "keywords": [
                "error", "bug", "crash", "fail", "exception", "critical", "urgent",
                "錯誤", "崩潰", "失敗", "異常", "緊急", "嚴重", "故障"
            ]},
            # Important (6-8)
            "important": {"weight": 7, "keywords": [
                "decision", "design", "solution", "architecture", "strategy", "plan",
                "決策", "設計", "解決方案", "架構", "策略", "計劃", "重要"
            ]},
            # Normal (3-5)
            "normal": {"weight": 4, "keywords": [
                "create", "update", "test", "implement", "add", "modify",
                "創建", "更新", "測試", "實現", "添加", "修改", "完成"
            ]},
            # Low (1-2)
            "low": {"weight": 2, "keywords": [
                "debug", "temp", "temporary", "log", "print", "comment",
                "調試", "臨時", "日誌", "打印", "註釋", "記錄"
            ]}
        }
        
        # 類型識別模式
        self.type_patterns = {
            MemoryType.FILE_OPERATION: [
                r"(create|創建|新建).*file",
                r"(modify|修改|編輯).*file",
                r"(delete|刪除|移除).*file",
                r"file.*(created|modified|deleted)",
                r"(寫入|讀取|保存).*文件"
            ],
            MemoryType.DECISION_MAKING: [
                r"(decide|決定|選擇).*",
                r"(design|設計).*",
                r"(strategy|策略|方案).*",
                r"(architecture|架構).*",
                r"應該.*還是.*"
            ],
            MemoryType.PROBLEM_SOLVING: [
                r"(solve|解決).*problem",
                r"(fix|修復).*",
                r"(debug|調試).*",
                r"問題.*解決",
                r"(error|錯誤).*fixed"
            ],
            MemoryType.STATUS_UPDATE: [
                r"(complete|完成).*",
                r"(progress|進度).*",
                r"(status|狀態).*",
                r"(update|更新).*",
                r"階段.*完成"
            ],
            MemoryType.CONVERSATION: [
                r"(discuss|討論).*",
                r"(conversation|對話).*",
                r"(meeting|會議).*",
                r"(chat|聊天).*",
                r"用戶.*說"
            ]
        }
        
    def init_database(self):
        """初始化數據庫"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance_score INTEGER NOT NULL,
                importance_level TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                keywords TEXT NOT NULL,
                context TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_importance_score ON memories(importance_score);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp);
        ''')
        
        conn.commit()
        conn.close()
        
    def classify_memory(self, content: str, source: str, context: Dict[str, Any] = None) -> MemoryEntry:
        """分類記憶條目"""
        if context is None:
            context = {}
            
        # 生成ID
        memory_id = f"mem_{int(datetime.now().timestamp())}_{hash(content) % 10000}"
        
        # 計算重要性分數
        importance_score = self._calculate_importance_score(content, context)
        
        # 確定重要性級別
        importance_level = self._determine_importance_level(importance_score)
        
        # 識別記憶類型
        memory_type = self._identify_memory_type(content, context)
        
        # 提取關鍵詞
        keywords = self._extract_keywords(content)
        
        # 創建記憶條目
        memory_entry = MemoryEntry(
            id=memory_id,
            content=content,
            source=source,
            timestamp=datetime.now().isoformat(),
            importance_score=importance_score,
            importance_level=importance_level,
            memory_type=memory_type,
            keywords=keywords,
            context=context,
            metadata={
                "classification_time": datetime.now().isoformat(),
                "classifier_version": "1.0"
            }
        )
        
        # 保存到數據庫
        self._save_memory(memory_entry)
        
        logger.info(f"記憶分類完成: {importance_level.emoji} {memory_type.emoji} {memory_id}")
        
        return memory_entry
        
    def _calculate_importance_score(self, content: str, context: Dict[str, Any]) -> int:
        """計算重要性分數 (1-10)"""
        score = 3  # 基礎分數
        content_lower = content.lower()
        
        # 基於關鍵詞的分數調整
        for category, config in self.importance_keywords.items():
            for keyword in config["keywords"]:
                if keyword.lower() in content_lower:
                    score = max(score, config["weight"])
                    break
                    
        # 基於上下文的分數調整
        if context:
            # 如果是錯誤相關
            if context.get("error") or context.get("exception"):
                score = max(score, 9)
                
            # 如果是決策相關
            if context.get("decision") or context.get("design"):
                score = max(score, 7)
                
            # 如果是文件操作
            if context.get("file_operation"):
                score = max(score, 4)
                
        # 基於內容長度的微調
        if len(content) > 500:
            score += 1  # 長內容通常更重要
        elif len(content) < 50:
            score -= 1  # 短內容通常不太重要
            
        # 確保分數在1-10範圍內
        return max(1, min(10, score))
        
    def _determine_importance_level(self, score: int) -> ImportanceLevel:
        """確定重要性級別"""
        for level in ImportanceLevel:
            if level.min_score <= score <= level.max_score:
                return level
        return ImportanceLevel.NORMAL
        
    def _identify_memory_type(self, content: str, context: Dict[str, Any]) -> MemoryType:
        """識別記憶類型"""
        content_lower = content.lower()
        
        # 基於上下文的類型判斷
        if context:
            if context.get("file_operation"):
                return MemoryType.FILE_OPERATION
            if context.get("decision") or context.get("design"):
                return MemoryType.DECISION_MAKING
            if context.get("error") or context.get("problem"):
                return MemoryType.PROBLEM_SOLVING
            if context.get("status") or context.get("progress"):
                return MemoryType.STATUS_UPDATE
                
        # 基於模式匹配的類型判斷
        for memory_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return memory_type
                    
        # 默認為對話類型
        return MemoryType.CONVERSATION
        
    def _extract_keywords(self, content: str) -> List[str]:
        """提取關鍵詞"""
        # 簡單的關鍵詞提取（可以後續改進為更複雜的NLP方法）
        keywords = []
        
        # 提取所有重要性關鍵詞
        content_lower = content.lower()
        for category, config in self.importance_keywords.items():
            for keyword in config["keywords"]:
                if keyword.lower() in content_lower:
                    keywords.append(keyword)
                    
        # 提取技術關鍵詞
        tech_keywords = [
            "python", "javascript", "react", "vue", "node", "api", "database",
            "git", "github", "docker", "kubernetes", "aws", "azure",
            "mcp", "rag", "ai", "ml", "supermemory", "kilocode"
        ]
        
        for keyword in tech_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
                
        return list(set(keywords))  # 去重
        
    def _save_memory(self, memory: MemoryEntry):
        """保存記憶到數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (id, content, source, timestamp, importance_score, importance_level, 
             memory_type, keywords, context, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.id,
            memory.content,
            memory.source,
            memory.timestamp,
            memory.importance_score,
            memory.importance_level.label,
            memory.memory_type.code,
            json.dumps(memory.keywords, ensure_ascii=False),
            json.dumps(memory.context, ensure_ascii=False),
            json.dumps(memory.metadata, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        
    def query_memories(self, 
                      importance_level: Optional[ImportanceLevel] = None,
                      memory_type: Optional[MemoryType] = None,
                      keywords: Optional[List[str]] = None,
                      limit: int = 50) -> List[MemoryEntry]:
        """查詢記憶"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if importance_level:
            query += " AND importance_level = ?"
            params.append(importance_level.label)
            
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type.code)
            
        if keywords:
            for keyword in keywords:
                query += " AND keywords LIKE ?"
                params.append(f"%{keyword}%")
                
        query += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            # 重建MemoryEntry對象
            importance_level_obj = next(
                level for level in ImportanceLevel 
                if level.label == row[5]
            )
            memory_type_obj = next(
                mtype for mtype in MemoryType 
                if mtype.code == row[6]
            )
            
            memory = MemoryEntry(
                id=row[0],
                content=row[1],
                source=row[2],
                timestamp=row[3],
                importance_score=row[4],
                importance_level=importance_level_obj,
                memory_type=memory_type_obj,
                keywords=json.loads(row[7]),
                context=json.loads(row[8]),
                metadata=json.loads(row[9])
            )
            memories.append(memory)
            
        conn.close()
        return memories
        
    def get_statistics(self) -> Dict[str, Any]:
        """獲取分類統計"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 總記憶數
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]
        
        # 按重要性級別統計
        cursor.execute("""
            SELECT importance_level, COUNT(*) 
            FROM memories 
            GROUP BY importance_level
        """)
        importance_stats = dict(cursor.fetchall())
        
        # 按類型統計
        cursor.execute("""
            SELECT memory_type, COUNT(*) 
            FROM memories 
            GROUP BY memory_type
        """)
        type_stats = dict(cursor.fetchall())
        
        # 按分數統計
        cursor.execute("""
            SELECT importance_score, COUNT(*) 
            FROM memories 
            GROUP BY importance_score 
            ORDER BY importance_score DESC
        """)
        score_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_memories": total_memories,
            "importance_distribution": importance_stats,
            "type_distribution": type_stats,
            "score_distribution": score_stats,
            "database_path": self.db_path
        }

# 全局分類器實例
classifier = IntelligentClassifier()

# 便捷函數
def classify_memory(content: str, source: str, context: Dict[str, Any] = None) -> MemoryEntry:
    """分類記憶條目"""
    return classifier.classify_memory(content, source, context)

def query_memories_by_importance(importance_level: ImportanceLevel, limit: int = 20) -> List[MemoryEntry]:
    """按重要性查詢記憶"""
    return classifier.query_memories(importance_level=importance_level, limit=limit)

def query_memories_by_type(memory_type: MemoryType, limit: int = 20) -> List[MemoryEntry]:
    """按類型查詢記憶"""
    return classifier.query_memories(memory_type=memory_type, limit=limit)

if __name__ == "__main__":
    # 測試智能分類器
    print("🧠 智能分類器測試")
    
    # 測試不同類型的記憶
    test_memories = [
        {
            "content": "系統出現嚴重錯誤，需要立即修復",
            "source": "error_log",
            "context": {"error": True, "severity": "high"}
        },
        {
            "content": "設計新的架構方案，考慮使用微服務架構",
            "source": "design_meeting",
            "context": {"decision": True, "design": True}
        },
        {
            "content": "創建了新的Python文件 test.py",
            "source": "file_system",
            "context": {"file_operation": True}
        },
        {
            "content": "調試輸出：變量值為123",
            "source": "debug_log",
            "context": {"debug": True}
        }
    ]
    
    # 分類測試記憶
    for test_memory in test_memories:
        memory = classify_memory(**test_memory)
        print(f"{memory.importance_level.emoji} {memory.memory_type.emoji} "
              f"分數:{memory.importance_score} - {memory.content[:30]}...")
              
    # 顯示統計信息
    stats = classifier.get_statistics()
    print(f"\n📊 分類統計:")
    print(f"   總記憶數: {stats['total_memories']}")
    print(f"   重要性分布: {stats['importance_distribution']}")
    print(f"   類型分布: {stats['type_distribution']}")
    
    print("✅ 智能分類器測試完成")

