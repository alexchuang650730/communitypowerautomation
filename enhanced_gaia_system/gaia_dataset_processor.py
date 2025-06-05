#!/usr/bin/env python3
"""
GAIA數據集處理器

此模塊負責從Hugging Face下載真實的GAIA數據集，
並提供數據處理和分析功能。
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from huggingface_hub import snapshot_download, login
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GAIADatasetProcessor:
    """GAIA數據集處理器"""
    
    def __init__(self, data_dir: str = "./gaia_data"):
        """
        初始化GAIA數據集處理器
        
        Args:
            data_dir: 數據存儲目錄
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Hugging Face token - 使用環境變量
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', '')
        
        logger.info(f"GAIA數據集處理器初始化完成，數據目錄: {self.data_dir}")
    
    def login_huggingface(self):
        """登錄Hugging Face"""
        try:
            login(token=self.hf_token)
            logger.info("✅ Hugging Face登錄成功")
            return True
        except Exception as e:
            logger.error(f"❌ Hugging Face登錄失敗: {str(e)}")
            return False
    
    def download_gaia_dataset(self):
        """下載GAIA數據集"""
        try:
            logger.info("🔄 開始下載GAIA數據集...")
            
            # 登錄Hugging Face
            if not self.login_huggingface():
                return False
            
            # 下載數據集
            snapshot_download(
                repo_id="gaia-benchmark/GAIA",
                repo_type="dataset",
                local_dir=str(self.data_dir),
                local_dir_use_symlinks=True,
            )
            
            logger.info("✅ GAIA數據集下載完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ GAIA數據集下載失敗: {str(e)}")
            return False
    
    def load_gaia_data(self, level: str = "1") -> List[Dict[str, Any]]:
        """
        載入GAIA測試數據
        
        Args:
            level: GAIA測試級別 (1, 2, 3)
            
        Returns:
            測試數據列表
        """
        try:
            # 查找數據文件 - 所有數據都在metadata.jsonl中
            validation_file = self.data_dir / "2023" / "validation" / "metadata.jsonl"
            test_file = self.data_dir / "2023" / "test" / "metadata.jsonl"
            
            # 優先使用validation數據，如果不存在則使用test數據
            data_file = validation_file if validation_file.exists() else test_file
            
            if not data_file.exists():
                logger.warning(f"⚠️ 找不到數據文件")
                return []
            
            # 讀取JSONL文件並過濾指定級別
            data = []
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        # 過濾指定級別的數據
                        if str(item.get('Level', '')) == str(level):
                            data.append(item)
            
            logger.info(f"✅ 載入Level {level}數據: {len(data)}個問題")
            return data
            
        except Exception as e:
            logger.error(f"❌ 載入GAIA數據失敗: {str(e)}")
            return []
    
    def get_question_by_id(self, task_id: str, level: str = "1") -> Optional[Dict[str, Any]]:
        """
        根據ID獲取特定問題
        
        Args:
            task_id: 任務ID
            level: GAIA測試級別
            
        Returns:
            問題數據或None
        """
        data = self.load_gaia_data(level)
        for item in data:
            if item.get('task_id') == task_id:
                return item
        return None
    
    def analyze_dataset(self, level: str = "1") -> Dict[str, Any]:
        """
        分析數據集統計信息
        
        Args:
            level: GAIA測試級別
            
        Returns:
            統計信息字典
        """
        data = self.load_gaia_data(level)
        
        if not data:
            return {"error": "無法載入數據"}
        
        # 統計信息
        stats = {
            "total_questions": len(data),
            "level": level,
            "question_types": {},
            "file_types": {},
            "has_files": 0,
            "no_files": 0
        }
        
        for item in data:
            # 統計文件類型
            files = item.get('file_name', '')
            if files:
                stats["has_files"] += 1
                # 分析文件類型
                if isinstance(files, str):
                    file_ext = files.split('.')[-1].lower() if '.' in files else 'unknown'
                    stats["file_types"][file_ext] = stats["file_types"].get(file_ext, 0) + 1
            else:
                stats["no_files"] += 1
        
        return stats
    
    def export_questions_for_testing(self, level: str = "1", output_file: str = None) -> str:
        """
        導出問題用於測試
        
        Args:
            level: GAIA測試級別
            output_file: 輸出文件路徑
            
        Returns:
            輸出文件路徑
        """
        data = self.load_gaia_data(level)
        
        if not data:
            logger.error("❌ 無法載入數據進行導出")
            return ""
        
        # 準備測試格式的數據
        test_data = []
        for item in data:
            test_item = {
                "task_id": item.get('task_id', ''),
                "question": item.get('Question', ''),
                "answer": item.get('Final answer', ''),
                "level": item.get('Level', level),
                "file_name": item.get('file_name', ''),
                "annotator_metadata": item.get('Annotator Metadata', {})
            }
            test_data.append(test_item)
        
        # 輸出文件
        if output_file is None:
            output_file = self.data_dir / f"gaia_level_{level}_test_data.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 測試數據已導出到: {output_file}")
        return str(output_file)
    
    def validate_dataset(self) -> bool:
        """驗證數據集完整性"""
        try:
            logger.info("🔍 驗證GAIA數據集完整性...")
            
            # 檢查基本目錄結構
            required_dirs = ["2023/validation", "2023/test"]
            for dir_path in required_dirs:
                full_path = self.data_dir / dir_path
                if not full_path.exists():
                    logger.error(f"❌ 缺少目錄: {full_path}")
                    return False
            
            # 檢查各級別數據文件
            total_questions = 0
            for level in ["1", "2", "3"]:
                data = self.load_gaia_data(level)
                if data:
                    total_questions += len(data)
                    logger.info(f"✅ Level {level}: {len(data)}個問題")
                else:
                    logger.warning(f"⚠️ Level {level}: 無數據")
            
            logger.info(f"✅ 數據集驗證完成，總計 {total_questions} 個問題")
            return total_questions > 0
            
        except Exception as e:
            logger.error(f"❌ 數據集驗證失敗: {str(e)}")
            return False

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GAIA數據集處理器')
    parser.add_argument('--action', choices=['download', 'analyze', 'export', 'validate'], 
                       default='download', help='執行動作')
    parser.add_argument('--level', choices=['1', '2', '3'], default='1', help='GAIA測試級別')
    parser.add_argument('--data-dir', default='./gaia_data', help='數據目錄')
    parser.add_argument('--output', help='輸出文件路徑')
    
    args = parser.parse_args()
    
    # 創建處理器
    processor = GAIADatasetProcessor(args.data_dir)
    
    if args.action == 'download':
        print("📥 下載GAIA數據集...")
        success = processor.download_gaia_dataset()
        if success:
            print("✅ 下載完成")
            processor.validate_dataset()
        else:
            print("❌ 下載失敗")
    
    elif args.action == 'analyze':
        print(f"📊 分析Level {args.level}數據集...")
        stats = processor.analyze_dataset(args.level)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.action == 'export':
        print(f"📤 導出Level {args.level}測試數據...")
        output_file = processor.export_questions_for_testing(args.level, args.output)
        if output_file:
            print(f"✅ 導出完成: {output_file}")
        else:
            print("❌ 導出失敗")
    
    elif args.action == 'validate':
        print("🔍 驗證數據集...")
        is_valid = processor.validate_dataset()
        if is_valid:
            print("✅ 數據集驗證通過")
        else:
            print("❌ 數據集驗證失敗")

if __name__ == "__main__":
    main()

