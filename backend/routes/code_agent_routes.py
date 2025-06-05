"""
后端API路由模块 - 代码智能体

提供代码智能体相关的API端点，将请求转发给MCP规划器进行处理。
"""

from flask import Blueprint, request, jsonify
import json
from ...agents.code_agent.code_agent import CodeAgent

code_agent_bp = Blueprint('code_agent', __name__)
code_agent = CodeAgent()

@code_agent_bp.route('/analyze_code', methods=['POST'])
def analyze_code():
    """
    分析代码内容
    """
    data = request.json
    code_content = data.get('code_content', '')
    language = data.get('language')
    analysis_type = data.get('analysis_type', 'general')
    
    result = code_agent.analyze_code(code_content, language, analysis_type)
    return jsonify(result)

@code_agent_bp.route('/solve_problem', methods=['POST'])
def solve_problem():
    """
    解决代码问题
    """
    data = request.json
    problem_description = data.get('problem_description', '')
    code_content = data.get('code_content')
    language = data.get('language')
    
    result = code_agent.solve_problem(problem_description, code_content, language)
    return jsonify(result)

@code_agent_bp.route('/update_github', methods=['POST'])
def update_github():
    """
    更新GitHub仓库中的文件
    """
    data = request.json
    repo_url = data.get('repo_url', '')
    file_path = data.get('file_path', '')
    changes = data.get('changes', '')
    commit_message = data.get('commit_message', 'Update file')
    
    result = code_agent.update_github(repo_url, file_path, changes, commit_message)
    return jsonify(result)
