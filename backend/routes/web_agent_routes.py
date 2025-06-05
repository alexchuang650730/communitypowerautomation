"""
后端API路由模块 - 网页智能体

提供网页智能体相关的API端点，将请求转发给MCP规划器进行处理。
"""

from flask import Blueprint, request, jsonify
import json
from ...agents.web_agent.web_agent import WebAgent

web_agent_bp = Blueprint('web_agent', __name__)
web_agent = WebAgent()

@web_agent_bp.route('/extract_data', methods=['POST'])
def extract_data():
    """
    从指定网页提取数据
    """
    data = request.json
    url = data.get('url', '')
    extraction_query = data.get('extraction_query', '')
    
    result = web_agent.extract_data(url, extraction_query)
    return jsonify(result)

@web_agent_bp.route('/automate_task', methods=['POST'])
def automate_task():
    """
    在指定网页执行自动化任务
    """
    data = request.json
    url = data.get('url', '')
    task = data.get('task', '')
    
    result = web_agent.automate_task(url, task)
    return jsonify(result)

@web_agent_bp.route('/analyze_content', methods=['POST'])
def analyze_content():
    """
    分析指定网页的内容
    """
    data = request.json
    url = data.get('url', '')
    analysis_type = data.get('analysis_type', 'general')
    analysis_query = data.get('analysis_query', '')
    
    result = web_agent.analyze_content(url, analysis_type, analysis_query)
    return jsonify(result)
