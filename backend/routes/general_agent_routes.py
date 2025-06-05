"""
后端API路由模块 - 通用智能体

提供通用智能体相关的API端点，将请求转发给MCP规划器进行处理。
"""

from flask import Blueprint, request, jsonify
import json
from ...agents.general_agent.general_agent import GeneralAgent

general_agent_bp = Blueprint('general_agent', __name__)
general_agent = GeneralAgent()

@general_agent_bp.route('/chat', methods=['POST'])
def chat():
    """
    与通用智能体进行对话
    """
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id')
    context = data.get('context', {})
    
    response = general_agent.chat(query, session_id, context)
    return jsonify(response)

@general_agent_bp.route('/execute_task', methods=['POST'])
def execute_task():
    """
    执行指定任务
    """
    data = request.json
    task = data.get('task', '')
    session_id = data.get('session_id')
    parameters = data.get('parameters', {})
    
    response = general_agent.execute_task(task, session_id, parameters)
    return jsonify(response)

@general_agent_bp.route('/create_project', methods=['POST'])
def create_project():
    """
    创建项目
    """
    data = request.json
    project_name = data.get('project_name', '')
    project_description = data.get('project_description', '')
    session_id = data.get('session_id')
    parameters = data.get('parameters', {})
    
    response = general_agent.create_project(project_name, project_description, session_id, parameters)
    return jsonify(response)
