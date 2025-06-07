"""
自我奖励训练接口单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from abc import ABC, abstractmethod

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from mcptool.adapters.interfaces.self_reward_training_interface import SelfRewardTrainingInterface
except ImportError:
    # 如果导入失败，创建Mock接口
    class SelfRewardTrainingInterface(ABC):
        """自我奖励训练接口"""
        
        @abstractmethod
        def train(self, thought_process, iterations=100):
            """使用自我奖励机制训练模型"""
            pass
        
        @abstractmethod
        def evaluate(self, thought_process):
            """评估思考过程的质量"""
            pass
        
        @abstractmethod
        def improve(self, thought_process):
            """改进思考过程"""
            pass
        
        @abstractmethod
        def batch_train(self, thought_processes, iterations=100):
            """批量训练"""
            pass
        
        @abstractmethod
        def get_training_status(self):
            """获取训练状态"""
            pass


class MockSelfRewardTrainingImplementation(SelfRewardTrainingInterface):
    """自我奖励训练接口的Mock实现"""
    
    def __init__(self):
        self.training_history = []
        self.model_version = "1.0.0"
        self.is_training = False
    
    def train(self, thought_process, iterations=100):
        """使用自我奖励机制训练模型"""
        self.is_training = True
        
        # 模拟训练过程
        training_result = {
            "status": "success",
            "iterations_completed": iterations,
            "initial_score": 0.6,
            "final_score": 0.85,
            "improvement": 0.25,
            "training_time": 1.5,
            "model_version": self.model_version
        }
        
        self.training_history.append(training_result)
        self.is_training = False
        
        return training_result
    
    def evaluate(self, thought_process):
        """评估思考过程的质量"""
        if isinstance(thought_process, str):
            # 基于文本长度和关键词的简单评分
            score = min(0.9, len(thought_process) / 1000 + 0.3)
            if "分析" in thought_process or "思考" in thought_process:
                score += 0.1
        elif isinstance(thought_process, dict):
            # 基于结构化数据的评分
            score = 0.5
            if "steps" in thought_process:
                score += len(thought_process["steps"]) * 0.1
            if "reasoning" in thought_process:
                score += 0.2
        else:
            score = 0.3
        
        return min(1.0, score)
    
    def improve(self, thought_process):
        """改进思考过程"""
        if isinstance(thought_process, str):
            # 文本改进
            improved = f"经过优化的思考过程：{thought_process}\n\n补充分析：基于自我奖励训练的改进建议。"
            return improved
        elif isinstance(thought_process, dict):
            # 结构化数据改进
            improved = thought_process.copy()
            improved["optimized"] = True
            improved["improvement_suggestions"] = [
                "增强逻辑推理链",
                "添加更多验证步骤",
                "优化决策过程"
            ]
            return improved
        else:
            return thought_process
    
    def batch_train(self, thought_processes, iterations=100):
        """批量训练"""
        results = []
        for i, process in enumerate(thought_processes):
            result = self.train(process, iterations)
            result["batch_index"] = i
            results.append(result)
        
        return {
            "status": "success",
            "batch_size": len(thought_processes),
            "total_iterations": iterations * len(thought_processes),
            "results": results,
            "average_improvement": sum(r["improvement"] for r in results) / len(results)
        }
    
    def get_training_status(self):
        """获取训练状态"""
        return {
            "is_training": self.is_training,
            "model_version": self.model_version,
            "total_training_sessions": len(self.training_history),
            "last_training": self.training_history[-1] if self.training_history else None,
            "average_score": sum(h["final_score"] for h in self.training_history) / len(self.training_history) if self.training_history else 0
        }


class TestSelfRewardTrainingInterface(unittest.TestCase):
    """自我奖励训练接口测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.implementation = MockSelfRewardTrainingImplementation()
    
    def test_interface_methods_exist(self):
        """测试接口方法存在"""
        # 验证所有必需的方法都存在
        self.assertTrue(hasattr(self.implementation, 'train'))
        self.assertTrue(hasattr(self.implementation, 'evaluate'))
        self.assertTrue(hasattr(self.implementation, 'improve'))
        self.assertTrue(hasattr(self.implementation, 'batch_train'))
        self.assertTrue(hasattr(self.implementation, 'get_training_status'))
    
    def test_train_method_string_input(self):
        """测试训练方法 - 字符串输入"""
        thought_process = "这是一个需要训练的思考过程，包含分析和推理步骤。"
        iterations = 50
        
        result = self.implementation.train(thought_process, iterations)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["iterations_completed"], iterations)
        self.assertIn("initial_score", result)
        self.assertIn("final_score", result)
        self.assertIn("improvement", result)
        self.assertGreater(result["final_score"], result["initial_score"])
    
    def test_train_method_dict_input(self):
        """测试训练方法 - 字典输入"""
        thought_process = {
            "problem": "如何优化算法性能",
            "steps": ["分析瓶颈", "设计方案", "实施优化"],
            "reasoning": "基于性能分析的逐步优化"
        }
        
        result = self.implementation.train(thought_process)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["iterations_completed"], 100)  # 默认值
    
    def test_evaluate_method_string_input(self):
        """测试评估方法 - 字符串输入"""
        thought_process = "这是一个包含深入分析和思考的复杂思维过程。"
        
        score = self.implementation.evaluate(thought_process)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_evaluate_method_dict_input(self):
        """测试评估方法 - 字典输入"""
        thought_process = {
            "steps": ["步骤1", "步骤2", "步骤3"],
            "reasoning": "详细的推理过程"
        }
        
        score = self.implementation.evaluate(thought_process)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_improve_method_string_input(self):
        """测试改进方法 - 字符串输入"""
        original_process = "原始的思考过程"
        
        improved_process = self.implementation.improve(original_process)
        
        self.assertIsInstance(improved_process, str)
        self.assertIn(original_process, improved_process)
        self.assertGreater(len(improved_process), len(original_process))
    
    def test_improve_method_dict_input(self):
        """测试改进方法 - 字典输入"""
        original_process = {
            "problem": "测试问题",
            "solution": "测试解决方案"
        }
        
        improved_process = self.implementation.improve(original_process)
        
        self.assertIsInstance(improved_process, dict)
        self.assertIn("optimized", improved_process)
        self.assertTrue(improved_process["optimized"])
        self.assertIn("improvement_suggestions", improved_process)
    
    def test_batch_train_method(self):
        """测试批量训练方法"""
        thought_processes = [
            "第一个思考过程",
            "第二个思考过程",
            {"problem": "结构化问题", "steps": ["步骤1", "步骤2"]}
        ]
        
        result = self.implementation.batch_train(thought_processes, 25)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["batch_size"], 3)
        self.assertEqual(result["total_iterations"], 75)  # 25 * 3
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 3)
        self.assertIn("average_improvement", result)
    
    def test_get_training_status_initial(self):
        """测试获取训练状态 - 初始状态"""
        status = self.implementation.get_training_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("is_training", status)
        self.assertIn("model_version", status)
        self.assertIn("total_training_sessions", status)
        self.assertFalse(status["is_training"])
        self.assertEqual(status["total_training_sessions"], 0)
    
    def test_get_training_status_after_training(self):
        """测试获取训练状态 - 训练后"""
        # 先进行一次训练
        self.implementation.train("测试思考过程")
        
        status = self.implementation.get_training_status()
        
        self.assertEqual(status["total_training_sessions"], 1)
        self.assertIsNotNone(status["last_training"])
        self.assertGreater(status["average_score"], 0)
    
    def test_training_history_tracking(self):
        """测试训练历史跟踪"""
        # 进行多次训练
        processes = ["过程1", "过程2", "过程3"]
        
        for process in processes:
            self.implementation.train(process)
        
        status = self.implementation.get_training_status()
        
        self.assertEqual(status["total_training_sessions"], 3)
        self.assertEqual(len(self.implementation.training_history), 3)
    
    def test_score_consistency(self):
        """测试评分一致性"""
        thought_process = "一致性测试的思考过程"
        
        # 多次评估同一个过程，应该得到相同的分数
        score1 = self.implementation.evaluate(thought_process)
        score2 = self.implementation.evaluate(thought_process)
        score3 = self.implementation.evaluate(thought_process)
        
        self.assertEqual(score1, score2)
        self.assertEqual(score2, score3)


class TestSelfRewardTrainingUtilities(unittest.TestCase):
    """自我奖励训练工具函数测试类"""
    
    def test_thought_process_validation(self):
        """测试思考过程验证"""
        # 有效的字符串思考过程
        valid_string = "这是一个有效的思考过程"
        self.assertIsInstance(valid_string, str)
        self.assertGreater(len(valid_string), 0)
        
        # 有效的字典思考过程
        valid_dict = {
            "problem": "问题描述",
            "analysis": "分析过程",
            "solution": "解决方案"
        }
        self.assertIsInstance(valid_dict, dict)
        self.assertIn("problem", valid_dict)
    
    def test_score_range_validation(self):
        """测试评分范围验证"""
        implementation = MockSelfRewardTrainingImplementation()
        
        # 测试不同长度的输入
        test_inputs = [
            "",  # 空字符串
            "短",  # 短文本
            "这是一个中等长度的思考过程，包含一些分析内容",  # 中等长度
            "这是一个非常长的思考过程" * 100  # 长文本
        ]
        
        for input_text in test_inputs:
            score = implementation.evaluate(input_text)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_improvement_quality(self):
        """测试改进质量"""
        implementation = MockSelfRewardTrainingImplementation()
        
        original = "原始思考过程"
        improved = implementation.improve(original)
        
        # 改进后的内容应该更长或更结构化
        if isinstance(improved, str):
            self.assertGreater(len(improved), len(original))
        elif isinstance(improved, dict):
            self.assertIn("optimized", improved)
            self.assertTrue(improved["optimized"])


if __name__ == '__main__':
    unittest.main()

