"""
工作流驱动集成验证脚本
版本: 1.0.0
更新日期: 2025-06-01
"""

import os
import sys
import time
import logging
import threading
import unittest
import pytest
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 导入核心组件
from mcptool.adapters.intelligent_workflow_engine_mcp import get_instance as get_workflow_driver
from agents.general_agent.general_agent_features import get_instance as get_features

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_workflow_integration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("WorkflowIntegrationTest")

class WorkflowIntegrationTest:
    """工作流驱动集成测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        # 获取项目根目录
        self.project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 初始化核心组件
        self.workflow_driver = get_workflow_driver(self.project_root)
        self.features = get_features()
        
        # 初始化测试结果
        self.test_results = {
            "test_workflow": None,
            "rollback_workflow": None,
            "github_release_workflow": None
        }
        
        # 初始化事件接收标志
        self.event_received = threading.Event()
        
        # 初始化直接回调标志
        self.direct_callback_received = {
            "test_workflow": threading.Event(),
            "rollback_workflow": threading.Event(),
            "github_release_workflow": threading.Event()
        }
        
        # 注册事件监听器
        self._register_event_listeners()
        
        # 设置工作流驱动为测试模式
        self.workflow_driver.set_test_mode(True)
        
        logger.info("工作流集成测试初始化完成")
    
    def _register_event_listeners(self):
        """注册事件监听器"""
        # 注册工作流完成事件监听器
        self.workflow_driver.register_event_listener("workflow_completed", self._on_workflow_completed)
        
        # 注册直接回调
        self._register_direct_callbacks()
        
        logger.info("已注册事件监听器")
    
    def _register_direct_callbacks(self):
        """注册直接回调，绕过事件系统"""
        # 保存原始方法引用
        original_test_workflow = self.workflow_driver._run_test_workflow
        original_rollback_workflow = self.workflow_driver._run_rollback_workflow
        original_github_release_workflow = self.workflow_driver._run_github_release_workflow
        
        # 包装测试工作流方法
        def wrapped_test_workflow(*args, **kwargs):
            try:
                result = original_test_workflow(*args, **kwargs)
                # 直接设置测试结果
                self.test_results["test_workflow"] = self.workflow_driver.get_workflow_data()
                # 设置直接回调标志
                self.direct_callback_received["test_workflow"].set()
                logger.info("测试工作流直接回调已触发")
                return result
            except Exception as e:
                logger.error(f"测试工作流执行异常: {str(e)}")
                raise
        
        # 包装回滚工作流方法
        def wrapped_rollback_workflow(*args, **kwargs):
            try:
                result = original_rollback_workflow(*args, **kwargs)
                # 直接设置测试结果
                self.test_results["rollback_workflow"] = self.workflow_driver.get_workflow_data()
                # 设置直接回调标志
                self.direct_callback_received["rollback_workflow"].set()
                logger.info("回滚工作流直接回调已触发")
                return result
            except Exception as e:
                logger.error(f"回滚工作流执行异常: {str(e)}")
                raise
        
        # 包装GitHub Release工作流方法
        def wrapped_github_release_workflow(*args, **kwargs):
            try:
                result = original_github_release_workflow(*args, **kwargs)
                # 直接设置测试结果
                self.test_results["github_release_workflow"] = self.workflow_driver.get_workflow_data()
                # 设置直接回调标志
                self.direct_callback_received["github_release_workflow"].set()
                logger.info("GitHub Release工作流直接回调已触发")
                return result
            except Exception as e:
                logger.error(f"GitHub Release工作流执行异常: {str(e)}")
                raise
        
        # 替换原始方法
        self.workflow_driver._run_test_workflow = wrapped_test_workflow
        self.workflow_driver._run_rollback_workflow = wrapped_rollback_workflow
        self.workflow_driver._run_github_release_workflow = wrapped_github_release_workflow
        
        logger.info("已注册直接回调")
    
    def _on_workflow_completed(self, event_data):
        """工作流完成事件处理"""
        logger.info(f"收到工作流完成事件: {event_data.get('workflow_data', {}).get('status', {})}")
        
        # 获取工作流数据
        workflow_data = event_data.get("workflow_data", {})
        
        # 根据当前节点判断工作流类型
        nodes = workflow_data.get("nodes", [])
        if not nodes:
            logger.warning("工作流节点为空")
            return
        
        # 查找触发器节点
        trigger_node = None
        for node in nodes:
            if node.get("type") == "trigger":
                trigger_node = node
                break
        
        if not trigger_node:
            logger.warning("未找到触发器节点")
            return
        
        # 根据触发器节点名称判断工作流类型
        node_name = trigger_node.get("name", "")
        
        if "测试工作流" in node_name:
            logger.info("收到测试工作流完成事件")
            self.test_results["test_workflow"] = workflow_data
        elif "回滚工作流" in node_name:
            logger.info("收到回滚工作流完成事件")
            self.test_results["rollback_workflow"] = workflow_data
        elif "GitHub Release" in node_name:
            logger.info("收到GitHub Release工作流完成事件")
            self.test_results["github_release_workflow"] = workflow_data
        else:
            logger.warning(f"未知工作流类型: {node_name}")
            return
        
        # 设置事件接收标志
        self.event_received.set()
    
    def run_test_workflow(self):
        """运行测试工作流"""
        logger.info("开始运行测试工作流")
        
        # 重置事件接收标志
        self.event_received.clear()
        self.direct_callback_received["test_workflow"].clear()
        self.test_results["test_workflow"] = None
        
        # 启动测试工作流
        self.workflow_driver.start_test_workflow("unit", "test_module")
        
        # 等待工作流完成
        max_wait_time = 30  # 最大等待时间（秒）
        wait_interval = 0.5  # 轮询间隔（秒）
        total_waited = 0
        
        while self.workflow_driver.workflow_status["is_running"] and total_waited < max_wait_time:
            time.sleep(wait_interval)
            total_waited += wait_interval
        
        # 确保工作流线程已完成并且事件已被处理
        if hasattr(self.workflow_driver, 'workflow_thread') and self.workflow_driver.workflow_thread:
            self.workflow_driver.workflow_thread.join(timeout=5)
        
        # 等待事件接收或直接回调或超时
        event_received = self.event_received.wait(timeout=2)
        direct_callback_received = self.direct_callback_received["test_workflow"].wait(timeout=2)
        
        logger.info(f"测试工作流执行完成，事件接收: {event_received}，直接回调: {direct_callback_received}")
        
        # 轮询检查测试结果
        for _ in range(10):
            if self.test_results["test_workflow"]:
                break
            time.sleep(0.5)
        
        # 验证测试工作流结果
        workflow_data = self.test_results["test_workflow"]
        if not workflow_data:
            logger.error("未收到测试工作流完成事件或直接回调")
            return False
        
        nodes = workflow_data["nodes"]
        if not nodes or len(nodes) < 3:
            logger.error(f"测试工作流节点数量不足: {len(nodes)}")
            return False
        
        # 验证节点状态
        success_count = sum(1 for node in nodes if node["status"] == "success")
        logger.info(f"测试工作流成功节点数: {success_count}/{len(nodes)}")
        
        return success_count >= 2
    
    def run_rollback_workflow(self):
        """运行回滚工作流"""
        logger.info("开始运行回滚工作流")
        
        # 重置事件接收标志
        self.event_received.clear()
        self.direct_callback_received["rollback_workflow"].clear()
        self.test_results["rollback_workflow"] = None
        
        # 启动回滚工作流
        self.workflow_driver.start_rollback_workflow("集成测试回滚", None)
        
        # 等待工作流完成
        max_wait_time = 30  # 最大等待时间（秒）
        wait_interval = 0.5  # 轮询间隔（秒）
        total_waited = 0
        
        while self.workflow_driver.workflow_status["is_running"] and total_waited < max_wait_time:
            time.sleep(wait_interval)
            total_waited += wait_interval
        
        # 确保工作流线程已完成并且事件已被处理
        if hasattr(self.workflow_driver, 'workflow_thread') and self.workflow_driver.workflow_thread:
            self.workflow_driver.workflow_thread.join(timeout=5)
        
        # 等待事件接收或直接回调或超时
        event_received = self.event_received.wait(timeout=2)
        direct_callback_received = self.direct_callback_received["rollback_workflow"].wait(timeout=2)
        
        logger.info(f"回滚工作流执行完成，事件接收: {event_received}，直接回调: {direct_callback_received}")
        
        # 轮询检查测试结果
        for _ in range(10):
            if self.test_results["rollback_workflow"]:
                break
            time.sleep(0.5)
        
        # 验证回滚工作流结果
        workflow_data = self.test_results["rollback_workflow"]
        if not workflow_data:
            logger.error("未收到回滚工作流完成事件或直接回调")
            return False
        
        nodes = workflow_data["nodes"]
        if not nodes or len(nodes) < 3:
            logger.error(f"回滚工作流节点数量不足: {len(nodes)}")
            return False
        
        # 验证节点状态
        success_count = sum(1 for node in nodes if node["status"] == "success")
        logger.info(f"回滚工作流成功节点数: {success_count}/{len(nodes)}")
        
        return success_count >= 2
    
    def run_github_release_workflow(self):
        """运行GitHub Release工作流"""
        logger.info("开始运行GitHub Release工作流")
        
        # 重置事件接收标志
        self.event_received.clear()
        self.direct_callback_received["github_release_workflow"].clear()
        self.test_results["github_release_workflow"] = None
        
        # 使用有效的测试URL替代实际不存在的URL
        test_version = "v1.0.0-test"
        test_url = "https://example.com/test-release"
        
        # 启动GitHub Release工作流
        self.workflow_driver.start_github_release_workflow(test_version, test_url)
        
        # 等待工作流完成
        max_wait_time = 30  # 最大等待时间（秒）
        wait_interval = 0.5  # 轮询间隔（秒）
        total_waited = 0
        
        while self.workflow_driver.workflow_status["is_running"] and total_waited < max_wait_time:
            time.sleep(wait_interval)
            total_waited += wait_interval
        
        # 确保工作流线程已完成并且事件已被处理
        if hasattr(self.workflow_driver, 'workflow_thread') and self.workflow_driver.workflow_thread:
            self.workflow_driver.workflow_thread.join(timeout=5)
        
        # 等待事件接收或直接回调或超时
        event_received = self.event_received.wait(timeout=2)
        direct_callback_received = self.direct_callback_received["github_release_workflow"].wait(timeout=2)
        
        logger.info(f"GitHub Release工作流执行完成，事件接收: {event_received}，直接回调: {direct_callback_received}")
        
        # 轮询检查测试结果
        for _ in range(10):
            if self.test_results["github_release_workflow"]:
                break
            time.sleep(0.5)
        
        # 验证GitHub Release工作流结果
        workflow_data = self.test_results["github_release_workflow"]
        if not workflow_data:
            logger.error("未收到GitHub Release工作流完成事件或直接回调")
            return False
        
        nodes = workflow_data["nodes"]
        if not nodes or len(nodes) < 3:
            logger.error(f"GitHub Release工作流节点数量不足: {len(nodes)}")
            return False
        
        # 验证节点状态
        success_count = sum(1 for node in nodes if node["status"] == "success")
        logger.info(f"GitHub Release工作流成功节点数: {success_count}/{len(nodes)}")
        
        return success_count >= 2
    
    def verify_feature_integration(self):
        """验证特性集成"""
        logger.info("开始验证特性集成")
        
        # 验证四大核心能力
        core_capabilities = self.features.get_core_capabilities()
        if len(core_capabilities) != 4:
            logger.error(f"核心能力数量不正确: {len(core_capabilities)}")
            return False
        
        # 验证自动化测试能力
        if "automated_testing" not in core_capabilities:
            logger.error("缺少自动化测试能力")
            return False
        
        # 验证版本回滚能力
        if "version_rollback" not in core_capabilities:
            logger.error("缺少版本回滚能力")
            return False
        
        # 验证工作节点可视化
        ui_features = self.features.get_ui_features()
        if "work_node_visualizer" not in ui_features:
            logger.error("缺少工作节点可视化特性")
            return False
        
        # 验证检查点管理
        memory_features = self.features.get_memory_features()
        if "checkpoint_management" not in memory_features:
            logger.error("缺少检查点管理特性")
            return False
        
        logger.info("特性集成验证通过")
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始运行所有测试")
        
        results = {
            "feature_integration": self.verify_feature_integration(),
            "test_workflow": self.run_test_workflow(),
            "rollback_workflow": self.run_rollback_workflow(),
            "github_release_workflow": self.run_github_release_workflow()
        }
        
        # 计算总体结果
        results["overall"] = all(results.values())
        
        logger.info(f"所有测试结果: {results}")
        return results


# 创建测试实例
@pytest.fixture
def workflow_test_instance():
    """创建工作流测试实例"""
    return WorkflowIntegrationTest()

def test_feature_integration(workflow_test_instance):
    """测试特性集成"""
    assert workflow_test_instance.verify_feature_integration() == True

def test_test_workflow(workflow_test_instance):
    """测试测试工作流执行"""
    assert workflow_test_instance.run_test_workflow() == True

def test_rollback_workflow(workflow_test_instance):
    """测试回滚工作流执行"""
    assert workflow_test_instance.run_rollback_workflow() == True

def test_github_release_workflow(workflow_test_instance):
    """测试GitHub Release工作流执行"""
    assert workflow_test_instance.run_github_release_workflow() == True

def test_all_workflows(workflow_test_instance):
    """测试所有工作流"""
    results = workflow_test_instance.run_all_tests()
    assert results["overall"] == True
