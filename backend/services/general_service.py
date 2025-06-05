"""
通用智能体服务模块

提供通用智能体相关的服务功能，包括会话管理、任务执行和项目管理。
"""

import os
import json
import uuid
from datetime import datetime
from powerautomation_integration.agents.general.general_agent import GeneralAgent

class GeneralService:
    def __init__(self):
        self.data_dir = os.path.join(os.getcwd(), 'data', 'general_agent')
        self.sessions_dir = os.path.join(self.data_dir, 'sessions')
        self.tasks_dir = os.path.join(self.data_dir, 'tasks')
        self.projects_dir = os.path.join(self.data_dir, 'projects')
        
        # 创建必要的目录
        for directory in [self.data_dir, self.sessions_dir, self.tasks_dir, self.projects_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # 初始化通用智能体
        self.general_agent = GeneralAgent()
    
    def create_session(self):
        """
        创建新的会话
        
        返回:
        - 会话ID
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return session_id
    
    def get_sessions(self):
        """
        获取所有会话
        
        返回:
        - 会话列表
        """
        sessions = []
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_file = os.path.join(self.sessions_dir, filename)
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append({
                        "id": session_data["id"],
                        "created_at": session_data["created_at"],
                        "updated_at": session_data["updated_at"],
                        "message_count": len(session_data["messages"])
                    })
        
        return sessions
    
    def get_session(self, session_id):
        """
        获取指定会话的详细信息
        
        参数:
        - session_id: 会话ID
        
        返回:
        - 会话详细信息
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        return session_data
    
    def add_message(self, session_id, message):
        """
        向会话添加消息
        
        参数:
        - session_id: 会话ID
        - message: 消息内容
        
        返回:
        - 更新后的会话
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # 如果是用户消息，使用通用智能体处理
        if message.get("role") == "user":
            response = self.general_agent.chat(
                query=message.get("content", ""),
                session_id=session_id,
                context={"messages": session_data["messages"]}
            )
            
            # 添加用户消息
            session_data["messages"].append(message)
            
            # 添加智能体响应
            session_data["messages"].append(response)
        else:
            # 直接添加消息
            session_data["messages"].append(message)
        
        session_data["updated_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return session_data
    
    def create_task(self, task_name, task_description, parameters=None):
        """
        创建新的任务
        
        参数:
        - task_name: 任务名称
        - task_description: 任务描述
        - parameters: 任务参数
        
        返回:
        - 任务ID和执行结果
        """
        task_id = str(uuid.uuid4())
        
        # 使用通用智能体执行任务
        result = self.general_agent.execute_task(
            task=task_description,
            session_id=None,
            parameters=parameters
        )
        
        # 保存任务信息
        task_data = {
            "id": task_id,
            "name": task_name,
            "description": task_description,
            "parameters": parameters or {},
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "steps": [],
            "result": result
        }
        
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        return {"task_id": task_id, "result": result}
    
    def update_task_status(self, task_id, status, step=None):
        """
        更新任务状态
        
        参数:
        - task_id: 任务ID
        - status: 新状态
        - step: 任务步骤
        
        返回:
        - 更新后的任务
        """
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        
        if not os.path.exists(task_file):
            raise FileNotFoundError(f"Task {task_id} not found")
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
        
        task_data["status"] = status
        task_data["updated_at"] = datetime.now().isoformat()
        
        if step:
            task_data["steps"].append({
                "description": step,
                "timestamp": datetime.now().isoformat()
            })
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        return task_data
    
    def create_project(self, project_name, project_description, parameters=None):
        """
        创建新的项目
        
        参数:
        - project_name: 项目名称
        - project_description: 项目描述
        - parameters: 项目参数
        
        返回:
        - 项目ID和创建结果
        """
        project_id = str(uuid.uuid4())
        
        # 使用通用智能体创建项目
        result = self.general_agent.create_project(
            project_name=project_name,
            project_description=project_description,
            parameters=parameters
        )
        
        # 保存项目信息
        project_data = {
            "id": project_id,
            "name": project_name,
            "description": project_description,
            "parameters": parameters or {},
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "components": [],
            "result": result
        }
        
        project_file = os.path.join(self.projects_dir, f"{project_id}.json")
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        return {"project_id": project_id, "result": result}
    
    def add_project_component(self, project_id, component_name, component_type, content=None):
        """
        向项目添加组件
        
        参数:
        - project_id: 项目ID
        - component_name: 组件名称
        - component_type: 组件类型
        - content: 组件内容
        
        返回:
        - 更新后的项目
        """
        project_file = os.path.join(self.projects_dir, f"{project_id}.json")
        
        if not os.path.exists(project_file):
            raise FileNotFoundError(f"Project {project_id} not found")
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        component_id = str(uuid.uuid4())
        component = {
            "id": component_id,
            "name": component_name,
            "type": component_type,
            "content": content or {},
            "created_at": datetime.now().isoformat()
        }
        
        project_data["components"].append(component)
        project_data["updated_at"] = datetime.now().isoformat()
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        return project_data
