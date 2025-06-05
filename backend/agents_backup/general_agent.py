"""
通用智能体模块

实现对话、任务执行和项目管理功能。
集成MCP模块进行优化和增强。
"""

import os
import json
from datetime import datetime
from ..core.mcp.context_matching_optimization_mcp import ContextMatchingOptimizationMCP
from ..core.mcp.content_template_optimization_mcp import ContentTemplateOptimizationMCP
from ..core.mcp.prompt_optimization_mcp import PromptOptimizationMCP
from ..core.mcp.project_memory_optimization_mcp import ProjectMemoryOptimizationMCP
from ..development_tools.thought_action_recorder import ThoughtActionRecorder

class GeneralAgent:
    def __init__(self):
        # 初始化MCP模块
        self.context_matching_mcp = ContextMatchingOptimizationMCP()
        self.content_template_mcp = ContentTemplateOptimizationMCP()
        self.prompt_optimization_mcp = PromptOptimizationMCP()
        self.project_memory_mcp = ProjectMemoryOptimizationMCP()
        
        # 初始化思考与操作记录器
        self.recorder = ThoughtActionRecorder()
        
        # 初始化会话ID
        self.session_id = None
    
    def _start_session(self):
        """启动新的会话"""
        self.session_id = self.recorder.start_session("general_agent")
        return self.session_id
    
    def _record_thought(self, thought):
        """记录思考过程"""
        if self.session_id:
            self.recorder.record_thought(self.session_id, thought)
    
    def _record_action(self, action, params=None, result=None):
        """记录执行的操作"""
        if self.session_id:
            self.recorder.record_action(self.session_id, action, params, result)
    
    def chat(self, query, session_id=None, context=None):
        """
        与通用智能体进行对话
        
        参数:
        - query: 用户问题
        - session_id: 会话ID（可选）
        - context: 上下文信息（可选）
        
        返回:
        - 对话响应
        """
        if session_id:
            self.session_id = session_id
        else:
            self._start_session()
        
        self._record_thought(f"收到用户问题: {query}")
        
        # 使用上下文匹配优化MCP解析用户问题
        self._record_thought("使用上下文匹配优化MCP解析用户问题")
        parsed_query = self.context_matching_mcp.optimize({
            "type": "chat_query",
            "query": query,
            "context": context or {}
        })
        
        # 使用提示词优化MCP生成最佳回答
        self._record_thought("使用提示词优化MCP生成最佳回答")
        optimized_prompt = self.prompt_optimization_mcp.optimize({
            "type": "chat_prompt",
            "parsed_query": parsed_query
        })
        
        # 使用内容模板优化MCP生成回答内容
        self._record_thought("使用内容模板优化MCP生成回答内容")
        response_content = self.content_template_mcp.optimize({
            "type": "chat_response",
            "optimized_prompt": optimized_prompt
        })
        
        # 记录操作和结果
        self._record_action("generate_response", {
            "query": query,
            "optimized_prompt": optimized_prompt
        }, response_content)
        
        # 构建响应
        response = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def execute_task(self, task, session_id=None, parameters=None):
        """
        执行指定任务
        
        参数:
        - task: 任务描述
        - session_id: 会话ID（可选）
        - parameters: 任务参数（可选）
        
        返回:
        - 任务执行结果
        """
        if session_id:
            self.session_id = session_id
        else:
            self._start_session()
        
        self._record_thought(f"收到任务执行请求: {task}")
        
        # 使用上下文匹配优化MCP解析任务
        self._record_thought("使用上下文匹配优化MCP解析任务")
        parsed_task = self.context_matching_mcp.optimize({
            "type": "task_parsing",
            "task": task,
            "parameters": parameters or {}
        })
        
        # 使用项目记忆优化MCP生成任务执行计划
        self._record_thought("使用项目记忆优化MCP生成任务执行计划")
        task_plan = self.project_memory_mcp.optimize({
            "type": "task_planning",
            "parsed_task": parsed_task
        })
        
        # 记录操作和结果
        self._record_action("plan_task", {
            "task": task,
            "parsed_task": parsed_task
        }, task_plan)
        
        # 模拟任务执行
        self._record_thought("开始执行任务")
        
        # 构建响应
        response = {
            "role": "assistant",
            "content": f"我将帮助您完成"{task}"任务。\n\n我已经开始处理这个任务，以下是我的计划：\n\n1. 分析任务需求\n2. 收集必要信息\n3. 执行任务步骤\n4. 验证结果\n\n我现在正在执行第一步...",
            "actions": [
                {"type": "task_started", "name": task, "id": f"task-{datetime.now().timestamp()}"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def create_project(self, project_name, project_description, session_id=None, parameters=None):
        """
        创建项目
        
        参数:
        - project_name: 项目名称
        - project_description: 项目描述
        - session_id: 会话ID（可选）
        - parameters: 项目参数（可选）
        
        返回:
        - 项目创建结果
        """
        if session_id:
            self.session_id = session_id
        else:
            self._start_session()
        
        self._record_thought(f"收到项目创建请求: {project_name}")
        
        # 使用上下文匹配优化MCP解析项目需求
        self._record_thought("使用上下文匹配优化MCP解析项目需求")
        parsed_project = self.context_matching_mcp.optimize({
            "type": "project_parsing",
            "project_name": project_name,
            "project_description": project_description,
            "parameters": parameters or {}
        })
        
        # 使用项目记忆优化MCP生成项目结构
        self._record_thought("使用项目记忆优化MCP生成项目结构")
        project_structure = self.project_memory_mcp.optimize({
            "type": "project_structure",
            "parsed_project": parsed_project
        })
        
        # 使用内容模板优化MCP生成项目组件
        self._record_thought("使用内容模板优化MCP生成项目组件")
        project_components = self.content_template_mcp.optimize({
            "type": "project_components",
            "project_structure": project_structure
        })
        
        # 记录操作和结果
        self._record_action("create_project", {
            "project_name": project_name,
            "project_description": project_description
        }, project_structure)
        
        # 构建响应
        response = {
            "role": "assistant",
            "content": f"我将为您创建"{project_name}"项目。\n\n这个项目将包含以下组件：\n\n1. 需求分析文档\n2. 设计方案\n3. 实施计划\n4. 测试策略\n\n我已经开始准备项目文档，您可以在项目面板中查看进度。",
            "actions": [
                {"type": "project_created", "name": project_name, "id": f"proj-{datetime.now().timestamp()}"}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return response
