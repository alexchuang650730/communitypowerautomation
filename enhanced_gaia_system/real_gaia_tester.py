#!/usr/bin/env python3
"""
真實GAIA測試執行器

使用真實的GAIA數據集進行API測試，並與標準答案對比計算準確率
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import google.generativeai as genai

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealGAIATester:
    """真實GAIA測試器"""
    
    def __init__(self, gaia_data_file: str):
        """
        初始化測試器
        
        Args:
            gaia_data_file: GAIA測試數據文件路徑
        """
        self.gaia_data_file = Path(gaia_data_file)
        self.test_data = self._load_test_data()
        self.results = []
        
        # API配置
        self.setup_apis()
        
        logger.info(f"真實GAIA測試器初始化完成，載入 {len(self.test_data)} 個問題")
    
    def setup_apis(self):
        """設置API配置"""
        # Gemini API
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            logger.info("✅ Gemini API已配置")
        
        # Claude API
        self.claude_api_key = os.environ.get('CLAUDE_API_KEY')
        if self.claude_api_key:
            logger.info("✅ Claude API已配置")
    
    def _load_test_data(self) -> List[Dict[str, Any]]:
        """載入測試數據"""
        try:
            with open(self.gaia_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"❌ 載入測試數據失敗: {str(e)}")
            return []
    
    def call_gemini_api(self, question: str) -> str:
        """調用Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(question)
            return response.text
        except Exception as e:
            return f"Gemini API錯誤: {str(e)}"
    
    def call_claude_api(self, question: str) -> str:
        """調用Claude API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.claude_api_key,
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": question}
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                return f"Claude API錯誤: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Claude API錯誤: {str(e)}"
    
    def sequential_thinking(self, question: str) -> str:
        """使用Sequential thinking處理問題"""
        prompt = f"""
請使用逐步推理的方法來回答以下問題：

問題: {question}

請按照以下步驟進行：
1. 問題分析：理解問題要求什麼
2. 信息收集：確定需要什麼信息
3. 逐步推理：一步一步解決問題
4. 驗證答案：檢查答案是否合理
5. 最終答案：提供簡潔的最終答案

請提供詳細的推理過程，最後給出明確的答案。
"""
        
        # 優先使用Gemini API
        if self.gemini_api_key:
            return self.call_gemini_api(prompt)
        elif self.claude_api_key:
            return self.call_claude_api(prompt)
        else:
            return "無可用的API"
    
    def webagent_search(self, question: str) -> str:
        """使用WebAgent進行搜索增強"""
        prompt = f"""
作為一個WebAgent，請幫助回答以下問題。假設你可以搜索網絡並獲取最新信息：

問題: {question}

請按照以下步驟：
1. 分析問題需要什麼類型的信息
2. 模擬搜索相關信息
3. 基於搜索結果進行分析
4. 提供準確的答案

請提供詳細的分析過程和最終答案。
"""
        
        # 優先使用Gemini API
        if self.gemini_api_key:
            return self.call_gemini_api(prompt)
        elif self.claude_api_key:
            return self.call_claude_api(prompt)
        else:
            return "無可用的API"
    
    def classify_question_type(self, question: str) -> str:
        """分類問題類型"""
        question_lower = question.lower()
        
        # 需要搜索的問題
        if any(keyword in question_lower for keyword in [
            'wikipedia', 'latest', 'recent', 'current', 'published', 
            'website', 'arxiv', 'google', 'search'
        ]):
            return 'web_search'
        
        # 需要複雜推理的問題
        elif any(keyword in question_lower for keyword in [
            'calculate', 'how many', 'what is', 'compare', 'analyze'
        ]):
            return 'sequential_thinking'
        
        # 一般問題
        else:
            return 'general'
    
    def answer_question(self, question: str, question_type: str = None) -> str:
        """回答問題"""
        if question_type is None:
            question_type = self.classify_question_type(question)
        
        if question_type == 'sequential_thinking':
            return self.sequential_thinking(question)
        elif question_type == 'web_search':
            return self.webagent_search(question)
        else:
            # 一般問題直接使用API
            if self.gemini_api_key:
                return self.call_gemini_api(question)
            elif self.claude_api_key:
                return self.call_claude_api(question)
            else:
                return "無可用的API"
    
    def evaluate_answer(self, predicted: str, expected: str) -> bool:
        """評估答案是否正確"""
        # 簡單的字符串匹配評估
        predicted_clean = predicted.strip().lower()
        expected_clean = expected.strip().lower()
        
        # 直接匹配
        if expected_clean in predicted_clean:
            return True
        
        # 數字匹配
        try:
            pred_num = float(predicted_clean)
            exp_num = float(expected_clean)
            return abs(pred_num - exp_num) < 0.01
        except:
            pass
        
        return False
    
    def run_test(self, max_questions: int = 10, start_index: int = 0) -> Dict[str, Any]:
        """運行測試"""
        logger.info(f"🧠 開始真實GAIA測試，測試 {max_questions} 個問題...")
        
        correct_count = 0
        total_count = 0
        
        # 選擇測試問題
        test_questions = self.test_data[start_index:start_index + max_questions]
        
        for i, item in enumerate(test_questions):
            total_count += 1
            question = item['question']
            expected_answer = item['answer']
            task_id = item['task_id']
            
            print(f"\n📝 測試 {i+1}/{len(test_questions)}: {task_id}")
            print(f"❓ 問題: {question}")
            
            # 分類問題類型
            question_type = self.classify_question_type(question)
            print(f"🔍 問題類型: {question_type}")
            
            # 開始計時
            start_time = time.time()
            
            # 獲取答案
            predicted_answer = self.answer_question(question, question_type)
            
            # 結束計時
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"✅ AI答案: {predicted_answer[:200]}...")
            print(f"🎯 標準答案: {expected_answer}")
            
            # 評估答案
            is_correct = self.evaluate_answer(predicted_answer, expected_answer)
            if is_correct:
                correct_count += 1
                print(f"📊 評估: ✅ 正確")
            else:
                print(f"📊 評估: ❌ 錯誤")
            
            print(f"⏱️ 執行時間: {execution_time:.2f}秒")
            
            # 保存結果
            result = {
                'task_id': task_id,
                'question': question,
                'question_type': question_type,
                'predicted_answer': predicted_answer,
                'expected_answer': expected_answer,
                'is_correct': is_correct,
                'execution_time': execution_time
            }
            self.results.append(result)
        
        # 計算成功率
        success_rate = (correct_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n🎉 測試完成！")
        print(f"📊 成功率: {success_rate:.2f}% ({correct_count}/{total_count})")
        
        return {
            'success_rate': success_rate,
            'correct_count': correct_count,
            'total_count': total_count,
            'results': self.results
        }
    
    def save_results(self, output_file: str = None):
        """保存測試結果"""
        if output_file is None:
            timestamp = int(time.time())
            output_file = f"real_gaia_test_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 測試結果已保存到: {output_file}")
        return output_file

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='真實GAIA測試執行器')
    parser.add_argument('--data-file', required=True, help='GAIA測試數據文件')
    parser.add_argument('--max-questions', type=int, default=10, help='最大測試問題數')
    parser.add_argument('--start-index', type=int, default=0, help='開始索引')
    parser.add_argument('--output', help='結果輸出文件')
    
    args = parser.parse_args()
    
    # 創建測試器
    tester = RealGAIATester(args.data_file)
    
    # 運行測試
    results = tester.run_test(args.max_questions, args.start_index)
    
    # 保存結果
    output_file = tester.save_results(args.output)
    
    print(f"\n✅ 真實GAIA測試完成，結果已保存到: {output_file}")

if __name__ == "__main__":
    main()

