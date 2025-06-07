#!/usr/bin/env python3
"""
RAG整合模塊 (RAG Integration Module)
PowerAutomation 記憶系統的語義檢索層

提供向量化、語義檢索和RAG整合功能
"""

import os
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import hashlib

# 嘗試導入向量化相關庫
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers未安裝，將使用簡化的向量化方法")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ faiss未安裝，將使用簡化的相似度搜索")

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VectorizedMemory:
    """向量化記憶"""
    memory_id: str
    content: str
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: str

class SimpleVectorizer:
    """簡化的向量化器（當專業庫不可用時）"""
    
    def __init__(self):
        self.vocab = {}
        self.vector_size = 128
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """簡單的文本向量化"""
        vectors = []
        
        for text in texts:
            # 簡單的字符級向量化
            vector = np.zeros(self.vector_size)
            
            # 基於字符頻率的向量化
            for i, char in enumerate(text[:self.vector_size]):
                vector[i] = ord(char) / 1000.0
                
            # 歸一化
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
                
            vectors.append(vector)
            
        return np.array(vectors)

class RAGIntegration:
    """RAG整合管理器"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.vector_db_path = "memory-system/rag-integration/vectors.json"
        self.index_path = "memory-system/rag-integration/faiss.index"
        
        # 初始化向量化模型
        self._init_vectorizer()
        
        # 初始化向量數據庫
        self.vectors_db = self._load_vectors_db()
        self.faiss_index = self._load_faiss_index()
        
    def _init_vectorizer(self):
        """初始化向量化器"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.vectorizer = SentenceTransformer(self.model_name)
                self.vector_size = self.vectorizer.get_sentence_embedding_dimension()
                logger.info(f"✅ 使用SentenceTransformer: {self.model_name}")
            except Exception as e:
                logger.warning(f"SentenceTransformer初始化失敗: {e}")
                self.vectorizer = SimpleVectorizer()
                self.vector_size = self.vectorizer.vector_size
        else:
            self.vectorizer = SimpleVectorizer()
            self.vector_size = self.vectorizer.vector_size
            logger.info("✅ 使用簡化向量化器")
            
    def _load_vectors_db(self) -> Dict[str, VectorizedMemory]:
        """加載向量數據庫"""
        os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
        
        if os.path.exists(self.vector_db_path):
            try:
                with open(self.vector_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                vectors_db = {}
                for memory_id, memory_data in data.items():
                    vectors_db[memory_id] = VectorizedMemory(
                        memory_id=memory_data['memory_id'],
                        content=memory_data['content'],
                        vector=memory_data['vector'],
                        metadata=memory_data['metadata'],
                        created_at=memory_data['created_at']
                    )
                    
                logger.info(f"✅ 加載向量數據庫: {len(vectors_db)} 條記錄")
                return vectors_db
                
            except Exception as e:
                logger.error(f"加載向量數據庫失敗: {e}")
                
        return {}
        
    def _save_vectors_db(self):
        """保存向量數據庫"""
        try:
            data = {}
            for memory_id, vectorized_memory in self.vectors_db.items():
                data[memory_id] = {
                    'memory_id': vectorized_memory.memory_id,
                    'content': vectorized_memory.content,
                    'vector': vectorized_memory.vector,
                    'metadata': vectorized_memory.metadata,
                    'created_at': vectorized_memory.created_at
                }
                
            with open(self.vector_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ 保存向量數據庫: {len(data)} 條記錄")
            
        except Exception as e:
            logger.error(f"保存向量數據庫失敗: {e}")
            
    def _load_faiss_index(self):
        """加載FAISS索引"""
        if not FAISS_AVAILABLE:
            return None
            
        try:
            if os.path.exists(self.index_path):
                index = faiss.read_index(self.index_path)
                logger.info(f"✅ 加載FAISS索引: {index.ntotal} 條記錄")
                return index
        except Exception as e:
            logger.error(f"加載FAISS索引失敗: {e}")
            
        # 創建新索引
        try:
            index = faiss.IndexFlatIP(self.vector_size)  # 內積相似度
            logger.info("✅ 創建新FAISS索引")
            return index
        except Exception as e:
            logger.error(f"創建FAISS索引失敗: {e}")
            return None
            
    def _save_faiss_index(self):
        """保存FAISS索引"""
        if self.faiss_index and FAISS_AVAILABLE:
            try:
                faiss.write_index(self.faiss_index, self.index_path)
                logger.info("✅ 保存FAISS索引")
            except Exception as e:
                logger.error(f"保存FAISS索引失敗: {e}")
                
    def vectorize_memory(self, memory_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """向量化記憶"""
        try:
            # 生成向量
            if SENTENCE_TRANSFORMERS_AVAILABLE and hasattr(self.vectorizer, 'encode'):
                vector = self.vectorizer.encode([content])[0].tolist()
            else:
                vector = self.vectorizer.encode([content])[0].tolist()
                
            # 創建向量化記憶
            vectorized_memory = VectorizedMemory(
                memory_id=memory_id,
                content=content,
                vector=vector,
                metadata=metadata or {},
                created_at=datetime.now().isoformat()
            )
            
            # 存儲到向量數據庫
            self.vectors_db[memory_id] = vectorized_memory
            
            # 添加到FAISS索引
            if self.faiss_index:
                vector_array = np.array([vector], dtype=np.float32)
                self.faiss_index.add(vector_array)
                
            logger.info(f"✅ 記憶向量化完成: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"記憶向量化失敗: {e}")
            return False
            
    def semantic_search(self, query: str, top_k: int = 10, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """語義搜索"""
        try:
            # 向量化查詢
            if SENTENCE_TRANSFORMERS_AVAILABLE and hasattr(self.vectorizer, 'encode'):
                query_vector = self.vectorizer.encode([query])[0]
            else:
                query_vector = self.vectorizer.encode([query])[0]
                
            results = []
            
            if self.faiss_index and self.faiss_index.ntotal > 0:
                # 使用FAISS搜索
                query_array = np.array([query_vector], dtype=np.float32)
                scores, indices = self.faiss_index.search(query_array, min(top_k, self.faiss_index.ntotal))
                
                memory_ids = list(self.vectors_db.keys())
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(memory_ids) and score >= threshold:
                        results.append((memory_ids[idx], float(score)))
                        
            else:
                # 使用簡單相似度計算
                for memory_id, vectorized_memory in self.vectors_db.items():
                    similarity = self._cosine_similarity(query_vector, vectorized_memory.vector)
                    if similarity >= threshold:
                        results.append((memory_id, similarity))
                        
                # 按相似度排序
                results.sort(key=lambda x: x[1], reverse=True)
                results = results[:top_k]
                
            logger.info(f"✅ 語義搜索完成: 查詢='{query}', 結果={len(results)}條")
            return results
            
        except Exception as e:
            logger.error(f"語義搜索失敗: {e}")
            return []
            
    def get_similar_memories(self, memory_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """獲取相似記憶"""
        if memory_id not in self.vectors_db:
            return []
            
        target_memory = self.vectors_db[memory_id]
        return self.semantic_search(target_memory.content, top_k + 1, threshold=0.3)[1:]  # 排除自己
        
    def update_memory_vector(self, memory_id: str, new_content: str, metadata: Dict[str, Any] = None) -> bool:
        """更新記憶向量"""
        # 先刪除舊向量
        if memory_id in self.vectors_db:
            del self.vectors_db[memory_id]
            
        # 重新向量化
        return self.vectorize_memory(memory_id, new_content, metadata)
        
    def delete_memory_vector(self, memory_id: str) -> bool:
        """刪除記憶向量"""
        try:
            if memory_id in self.vectors_db:
                del self.vectors_db[memory_id]
                logger.info(f"✅ 刪除記憶向量: {memory_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"刪除記憶向量失敗: {e}")
            return False
            
    def rebuild_index(self) -> bool:
        """重建FAISS索引"""
        try:
            if not FAISS_AVAILABLE:
                logger.warning("FAISS不可用，跳過索引重建")
                return True
                
            # 創建新索引
            self.faiss_index = faiss.IndexFlatIP(self.vector_size)
            
            # 添加所有向量
            if self.vectors_db:
                vectors = []
                for vectorized_memory in self.vectors_db.values():
                    vectors.append(vectorized_memory.vector)
                    
                vectors_array = np.array(vectors, dtype=np.float32)
                self.faiss_index.add(vectors_array)
                
            logger.info(f"✅ 重建FAISS索引: {len(self.vectors_db)} 條記錄")
            return True
            
        except Exception as e:
            logger.error(f"重建索引失敗: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """獲取RAG統計信息"""
        return {
            "total_vectors": len(self.vectors_db),
            "vector_size": self.vector_size,
            "model_name": self.model_name,
            "faiss_available": FAISS_AVAILABLE,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "faiss_index_size": self.faiss_index.ntotal if self.faiss_index else 0
        }
        
    def save_all(self):
        """保存所有數據"""
        self._save_vectors_db()
        self._save_faiss_index()
        
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """計算餘弦相似度"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"計算相似度失敗: {e}")
            return 0.0

# 全局實例
rag_integration = RAGIntegration()

if __name__ == "__main__":
    # 測試RAG整合功能
    rag = RAGIntegration()
    
    # 測試向量化
    test_memories = [
        ("mem1", "實現記憶存儲模塊，提供高效的數據存儲功能"),
        ("mem2", "創建智能分類器，自動判斷記憶的重要性"),
        ("mem3", "開發RAG整合系統，支持語義檢索"),
        ("mem4", "修復MCP適配器的註冊問題"),
        ("mem5", "實現ZIP加密的token管理系統")
    ]
    
    print("🧪 測試RAG整合功能...")
    
    # 向量化測試記憶
    for memory_id, content in test_memories:
        success = rag.vectorize_memory(memory_id, content, {"test": True})
        if success:
            print(f"✅ 向量化成功: {memory_id}")
        else:
            print(f"❌ 向量化失敗: {memory_id}")
            
    # 測試語義搜索
    query = "記憶存儲和數據管理"
    results = rag.semantic_search(query, top_k=3)
    print(f"\n🔍 語義搜索結果 (查詢: '{query}'):")
    for memory_id, score in results:
        print(f"  {memory_id}: {score:.3f}")
        
    # 測試相似記憶查找
    similar = rag.get_similar_memories("mem1", top_k=2)
    print(f"\n🔗 相似記憶 (基於 mem1):")
    for memory_id, score in similar:
        print(f"  {memory_id}: {score:.3f}")
        
    # 獲取統計信息
    stats = rag.get_statistics()
    print(f"\n📊 RAG統計信息: {stats}")
    
    # 保存數據
    rag.save_all()
    print("💾 數據已保存")

