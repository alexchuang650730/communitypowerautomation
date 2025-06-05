#!/usr/bin/env python3
"""
RLFactory与SRT（Self-Reward Training）集成测试

测试RLFactory强化学习工厂与SRT自我奖励训练系统的集成功能，
验证两个系统在思维过程优化、模型训练和性能提升方面的协同工作。

作者: PowerAutomation团队
版本: 1.0.0
日期: 2025-06-04
"""

import asyncio
import pytest
import sys
import os
import json
import time
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from rl_factory.adapters.rl_factory_aligner import RLFactoryAligner
    from mcptool.adapters.srt.srt_adapter import SRTAdapter
    from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP
    RL_FACTORY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RLFactory or SRT components not available: {e}")
    RL_FACTORY_AVAILABLE = False


class TestRLFactorySRTIntegration:
    """RLFactory与SRT（Self-Reward Training）集成测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_context = {
            "user_id": "test_user",
            "session_id": "test_session_001",
            "environment": "test",
            "timestamp": time.time()
        }
        
        # 初始化组件
        if RL_FACTORY_AVAILABLE:
            self.rl_factory = RLFactoryAligner()
            self.srt_adapter = SRTAdapter()
            self.workflow_engine = IntelligentWorkflowEngineMCP()
        else:
            # 使用Mock对象进行测试
            self.rl_factory = Mock()
            self.srt_adapter = Mock()
            self.workflow_engine = Mock()
        
        # 测试数据
        self.sample_thought_processes = [
            "分析用户需求：用户希望自动化数据处理流程。首先识别数据源，然后确定处理步骤，最后输出结果。",
            "问题解决思路：遇到API调用失败，需要检查网络连接、验证API密钥、确认请求格式，并实施重试机制。",
            "工作流优化：当前流程耗时过长，可以通过并行处理、缓存机制和算法优化来提升性能。"
        ]
    
    def teardown_method(self):
        """测试后置清理"""
        if hasattr(self.srt_adapter, 'shutdown'):
            self.srt_adapter.shutdown()
    
    @pytest.mark.asyncio
    async def test_srt_basic_training(self):
        """测试SRT基础训练功能"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化SRT适配器
        config = {
            "learning_rate": 0.001,
            "batch_size": 16,
            "max_iterations": 50
        }
        
        init_success = self.srt_adapter.initialize(config)
        assert init_success, "SRT适配器初始化失败"
        
        # 测试单个思维过程训练
        thought_process = self.sample_thought_processes[0]
        training_result = self.srt_adapter.train(thought_process, iterations=10)
        
        # 验证训练结果
        assert "iterations" in training_result
        assert "improvements" in training_result
        assert "final_reward" in training_result
        assert training_result["iterations"] == 10
        assert isinstance(training_result["final_reward"], float)
        assert 0.0 <= training_result["final_reward"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_srt_batch_training(self):
        """测试SRT批量训练功能"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化SRT适配器
        config = {"learning_rate": 0.001, "batch_size": 8}
        self.srt_adapter.initialize(config)
        
        # 批量训练
        batch_result = self.srt_adapter.batch_train(
            self.sample_thought_processes, 
            batch_size=2
        )
        
        # 验证批量训练结果
        assert "batches" in batch_result
        assert "samples" in batch_result
        assert "batch_results" in batch_result
        assert "average_reward" in batch_result
        assert batch_result["samples"] == len(self.sample_thought_processes)
        assert isinstance(batch_result["average_reward"], float)
    
    @pytest.mark.asyncio
    async def test_srt_evaluation(self):
        """测试SRT思维过程评估功能"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化SRT适配器
        config = {"learning_rate": 0.001}
        self.srt_adapter.initialize(config)
        
        # 评估思维过程
        for thought_process in self.sample_thought_processes:
            score = self.srt_adapter.evaluate(thought_process)
            
            # 验证评估结果
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_srt_improvement(self):
        """测试SRT思维过程改进功能"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化SRT适配器
        config = {"learning_rate": 0.001}
        self.srt_adapter.initialize(config)
        
        # 改进思维过程
        original_thought = self.sample_thought_processes[0]
        improved_thought = self.srt_adapter.improve(original_thought)
        
        # 验证改进结果
        assert improved_thought is not None
        assert isinstance(improved_thought, (str, dict))
        
        # 如果返回字典，应包含改进信息
        if isinstance(improved_thought, dict):
            assert "improved_text" in improved_thought or "suggestions" in improved_thought
    
    @pytest.mark.asyncio
    async def test_rl_factory_srt_integration(self):
        """测试RLFactory与SRT的核心集成功能"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 模拟RLFactory生成的思维过程
        rl_generated_thought = {
            "action": "analyze_task",
            "reasoning": "基于历史数据分析，选择最优工具组合",
            "confidence": 0.85,
            "context": self.test_context
        }
        
        # 使用SRT评估RLFactory生成的思维
        srt_config = {"learning_rate": 0.001}
        self.srt_adapter.initialize(srt_config)
        
        # 评估思维质量
        quality_score = self.srt_adapter.evaluate(rl_generated_thought)
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0
        
        # 如果质量不够高，使用SRT改进
        if quality_score < 0.8:
            improved_thought = self.srt_adapter.improve(rl_generated_thought)
            
            # 重新评估改进后的思维
            improved_score = self.srt_adapter.evaluate(improved_thought)
            
            # 验证改进效果
            assert improved_score >= quality_score, "SRT改进应该提升思维质量"
    
    @pytest.mark.asyncio
    async def test_feedback_loop_integration(self):
        """测试RLFactory与SRT的反馈循环集成"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化组件
        srt_config = {"learning_rate": 0.002}
        self.srt_adapter.initialize(srt_config)
        
        # 模拟反馈循环
        feedback_data = []
        
        for i in range(3):  # 模拟3轮反馈循环
            # 1. RLFactory生成决策
            rl_decision = {
                "iteration": i,
                "selected_tool": f"tool_{i}",
                "reasoning": f"基于第{i}轮学习，选择最优工具",
                "confidence": 0.7 + i * 0.1
            }
            
            # 2. SRT评估决策质量
            quality_score = self.srt_adapter.evaluate(rl_decision)
            
            # 3. 记录反馈数据
            feedback_data.append({
                "iteration": i,
                "decision": rl_decision,
                "quality_score": quality_score,
                "timestamp": time.time()
            })
            
            # 4. 如果质量不够，使用SRT训练改进
            if quality_score < 0.8:
                training_result = self.srt_adapter.train(rl_decision, iterations=5)
                feedback_data[-1]["training_applied"] = True
                feedback_data[-1]["training_result"] = training_result
        
        # 验证反馈循环效果
        assert len(feedback_data) == 3
        
        # 检查质量分数趋势（应该有改进）
        scores = [item["quality_score"] for item in feedback_data]
        assert all(isinstance(score, float) for score in scores)
        assert all(0.0 <= score <= 1.0 for score in scores)
    
    @pytest.mark.asyncio
    async def test_workflow_engine_integration(self):
        """测试与智能工作流引擎的集成"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 模拟工作流请求
        workflow_request = {
            "action": "optimize_workflow",
            "user_request": "提升数据处理效率",
            "context": {
                "current_performance": "3.2s",
                "target_performance": "1.5s",
                "available_tools": ["pandas", "numpy", "dask"]
            }
        }
        
        # 通过工作流引擎处理请求
        if hasattr(self.workflow_engine, 'process'):
            result = await self.workflow_engine.process(workflow_request)
            
            # 验证工作流结果
            assert isinstance(result, dict)
            assert "status" in result
        
        # 使用SRT评估工作流决策质量
        srt_config = {"learning_rate": 0.001}
        self.srt_adapter.initialize(srt_config)
        
        workflow_reasoning = {
            "decision": "使用dask进行并行处理",
            "reasoning": "基于数据量大小和性能要求，dask最适合",
            "expected_improvement": "50%性能提升"
        }
        
        quality_score = self.srt_adapter.evaluate(workflow_reasoning)
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0
    
    def test_performance_metrics_collection(self):
        """测试性能指标收集"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 获取SRT性能指标
        if hasattr(self.srt_adapter, 'get_performance_metrics'):
            srt_metrics = self.srt_adapter.get_performance_metrics()
            
            # 验证指标结构
            assert isinstance(srt_metrics, dict)
            
            # 检查关键指标
            expected_metrics = ["training_time", "evaluation_accuracy", "improvement_rate"]
            for metric in expected_metrics:
                if metric in srt_metrics:
                    assert isinstance(srt_metrics[metric], (int, float, list))
        
        # 获取RLFactory性能指标
        if hasattr(self.rl_factory, 'get_performance_metrics'):
            rl_metrics = self.rl_factory.get_performance_metrics()
            assert isinstance(rl_metrics, dict)
    
    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复机制"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 测试无效输入处理
        with pytest.raises((ValueError, TypeError, RuntimeError)):
            self.srt_adapter.evaluate(None)
        
        with pytest.raises((ValueError, TypeError, RuntimeError)):
            self.srt_adapter.train("", iterations=-1)
        
        # 测试空输入处理
        try:
            result = self.srt_adapter.evaluate("")
            # 如果没有抛出异常，结果应该是有效的
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
        except (ValueError, TypeError):
            # 抛出异常也是可接受的
            pass
    
    def test_integration_health_check(self):
        """测试集成健康检查"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 检查SRT适配器健康状态
        srt_health = self.srt_adapter.health_check()
        assert isinstance(srt_health, dict)
        assert "status" in srt_health
        assert srt_health["status"] in ["ok", "warning", "error"]
        
        # 检查RLFactory健康状态
        if hasattr(self.rl_factory, 'health_check'):
            rl_health = self.rl_factory.health_check()
            assert isinstance(rl_health, dict)
    
    def test_configuration_management(self):
        """测试配置管理"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 测试不同配置参数
        configs = [
            {"learning_rate": 0.001, "batch_size": 16},
            {"learning_rate": 0.01, "batch_size": 32},
            {"learning_rate": 0.0001, "batch_size": 8}
        ]
        
        for config in configs:
            # 重新初始化适配器
            success = self.srt_adapter.initialize(config)
            assert success, f"配置初始化失败: {config}"
            
            # 验证配置生效
            if hasattr(self.srt_adapter, 'get_config'):
                current_config = self.srt_adapter.get_config()
                assert isinstance(current_config, dict)
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """测试并发操作"""
        if not RL_FACTORY_AVAILABLE:
            pytest.skip("RLFactory/SRT components not available")
        
        # 初始化SRT适配器
        config = {"learning_rate": 0.001}
        self.srt_adapter.initialize(config)
        
        # 并发评估多个思维过程
        tasks = []
        for thought in self.sample_thought_processes:
            task = asyncio.create_task(
                asyncio.to_thread(self.srt_adapter.evaluate, thought)
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证并发结果
        for result in results:
            if not isinstance(result, Exception):
                assert isinstance(result, float)
                assert 0.0 <= result <= 1.0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])

