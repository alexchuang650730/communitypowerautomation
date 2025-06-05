"""
PPT任务管理器服务模块

提供PPT任务管理的服务层接口，连接智能体与API层
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 更新引用路径，从agents目录导入
from powerautomation_integration.agents.ppt.ppt_agent import PPTAgent

class PPTTaskService:
    """PPT任务服务类，负责处理PPT相关任务请求"""
    
    def __init__(self):
        """初始化PPT任务服务"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ppt_agent = PPTAgent()
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_ppt_from_text(self, title: str, content: str, template_name: str = "专业简历.pptx") -> Dict[str, Any]:
        """
        从文本内容创建PPT
        
        参数:
            title: PPT标题
            content: 文本内容
            template_name: 模板名称
            
        返回:
            处理结果字典
        """
        self.logger.info(f"从文本创建PPT: {title}")
        
        input_data = {
            "task_type": "text_to_ppt",
            "title": title,
            "content": content,
            "template_name": template_name
        }
        
        return self.ppt_agent.execute(input_data)
    
    def create_ppt_from_mindmap(self, title: str, mindmap_data: Dict[str, Any], template_name: str = "专业简历.pptx") -> Dict[str, Any]:
        """
        从思维导图创建PPT
        
        参数:
            title: PPT标题
            mindmap_data: 思维导图数据
            template_name: 模板名称
            
        返回:
            处理结果字典
        """
        self.logger.info(f"从思维导图创建PPT: {title}")
        
        input_data = {
            "task_type": "mindmap_to_ppt",
            "title": title,
            "mindmap_data": mindmap_data,
            "template_name": template_name
        }
        
        return self.ppt_agent.execute(input_data)
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        获取可用的PPT模板列表
        
        返回:
            模板信息列表
        """
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "templates")
        templates = []
        
        try:
            for filename in os.listdir(template_dir):
                if filename.endswith('.pptx'):
                    template_path = os.path.join(template_dir, filename)
                    template_info = {
                        "name": filename,
                        "path": template_path,
                        "size": os.path.getsize(template_path),
                        "last_modified": datetime.fromtimestamp(os.path.getmtime(template_path)).isoformat()
                    }
                    templates.append(template_info)
        except Exception as e:
            self.logger.error(f"获取模板列表失败: {str(e)}")
        
        return templates
    
    def get_recent_ppts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近生成的PPT列表
        
        参数:
            limit: 返回结果数量限制
            
        返回:
            PPT信息列表
        """
        ppts = []
        
        try:
            files = os.listdir(self.output_dir)
            pptx_files = [f for f in files if f.endswith('.pptx')]
            
            # 按修改时间排序
            pptx_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)), reverse=True)
            
            # 限制数量
            pptx_files = pptx_files[:limit]
            
            for filename in pptx_files:
                file_path = os.path.join(self.output_dir, filename)
                ppt_info = {
                    "name": filename,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                ppts.append(ppt_info)
        except Exception as e:
            self.logger.error(f"获取最近PPT列表失败: {str(e)}")
        
        return ppts
