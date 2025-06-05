"""
后端API路由模块 - PPT智能体

提供PPT智能体相关的API端点，将请求转发给服务层进行处理。
"""

from flask import Blueprint, request, jsonify, send_file
import json
import os
from ..services.ppt_service import PPTTaskService

ppt_agent_bp = Blueprint('ppt_agent', __name__)
ppt_service = PPTTaskService()

@ppt_agent_bp.route('/generate_ppt', methods=['POST'])
def generate_ppt():
    """
    生成PPT演示文稿
    """
    data = request.json
    topic = data.get('topic', '')
    content = data.get('content')
    template = data.get('template', '专业简历.pptx')
    
    result = ppt_service.create_ppt_from_text(topic, content, template)
    
    # 返回文件路径，前端可以通过另一个接口下载
    return jsonify({
        "status": "success",
        "file_path": result.get("ppt_path", ""),
        "slides_count": result.get("slides_count", 0)
    })

@ppt_agent_bp.route('/mindmap_to_ppt', methods=['POST'])
def mindmap_to_ppt():
    """
    将思维导图转换为PPT
    """
    data = request.json
    title = data.get('title', '思维导图演示文稿')
    mindmap_data = data.get('mindmap_data', {})
    template = data.get('template', '专业简历.pptx')
    
    result = ppt_service.create_ppt_from_mindmap(title, mindmap_data, template)
    
    # 返回文件路径，前端可以通过另一个接口下载
    return jsonify({
        "status": "success",
        "file_path": result.get("ppt_path", ""),
        "slides_count": result.get("slides_count", 0)
    })

@ppt_agent_bp.route('/get_templates', methods=['GET'])
def get_templates():
    """
    获取可用的PPT模板列表
    """
    templates = ppt_service.get_available_templates()
    return jsonify(templates)

@ppt_agent_bp.route('/get_recent_ppts', methods=['GET'])
def get_recent_ppts():
    """
    获取最近生成的PPT列表
    """
    limit = request.args.get('limit', 10, type=int)
    ppts = ppt_service.get_recent_ppts(limit)
    return jsonify(ppts)

@ppt_agent_bp.route('/download_ppt/<path:filename>', methods=['GET'])
def download_ppt(filename):
    """
    下载生成的PPT文件
    """
    directory = os.path.dirname(filename)
    file_name = os.path.basename(filename)
    return send_file(filename, as_attachment=True, download_name=file_name)
