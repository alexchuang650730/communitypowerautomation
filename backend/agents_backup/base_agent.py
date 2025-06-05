"""
智能体基类模块

定义所有智能体的基础接口和共享功能
"""

from abc import ABC, abstractmethod
import logging
import uuid
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseAgent(ABC):
    """智能体基类，定义所有智能体的通用接口和功能"""
    
    def __init__(self, agent_id: str = None, name: str = "未命名智能体", description: str = ""):
        """
        初始化智能体
        
        参数:
            agent_id: 智能体ID，如果不提供则自动生成
            name: 智能体名称
            description: 智能体描述
        """
        self.agent_id = agent_id if agent_id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{self.agent_id}")
        self.logger.info(f"初始化智能体: {self.name}")
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据并返回结果
        
        参数:
            input_data: 输入数据字典
            
        返回:
            处理结果字典
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        获取智能体能力列表
        
        返回:
            能力描述列表
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据是否有效
        
        参数:
            input_data: 输入数据字典
            
        返回:
            数据是否有效
        """
        # 基础验证逻辑，子类可以重写此方法进行特定验证
        return True
    
    def preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理输入数据
        
        参数:
            input_data: 输入数据字典
            
        返回:
            预处理后的数据字典
        """
        # 基础预处理逻辑，子类可以重写此方法进行特定预处理
        return input_data
    
    def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理结果数据
        
        参数:
            result: 处理结果字典
            
        返回:
            后处理后的结果字典
        """
        # 基础后处理逻辑，子类可以重写此方法进行特定后处理
        return result
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整的处理流程
        
        参数:
            input_data: 输入数据字典
            
        返回:
            处理结果字典
        """
        self.logger.info(f"开始执行: {self.name}")
        
        # 验证输入
        if not self.validate_input(input_data):
            self.logger.error("输入数据验证失败")
            return {"status": "error", "message": "输入数据验证失败"}
        
        try:
            # 预处理
            preprocessed_data = self.preprocess(input_data)
            
            # 核心处理
            result = self.process(preprocessed_data)
            
            # 后处理
            final_result = self.postprocess(result)
            
            self.logger.info(f"执行完成: {self.name}")
            return {"status": "success", "data": final_result}
        
        except Exception as e:
            self.logger.error(f"执行出错: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        返回:
            智能体信息字典
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "capabilities": self.get_capabilities()
        }
