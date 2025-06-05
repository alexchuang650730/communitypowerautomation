"""
Kilo Code适配器实现

此模块实现了Kilo Code适配器，用于将Kilo Code的功能集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时最小化对原有代码的修改。
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
import requests

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("KILO_CODE_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("KILO_CODE_LOG_FILE", None)
)
logger = logging.getLogger("kilo_code_adapter")

class KiloCodeAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Kilo Code适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Kilo Code服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性。
    """
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        """
        初始化Kilo Code适配器
        
        Args:
            api_key: Kilo Code API密钥，如果为None则从环境变量获取
            server_url: Kilo Code服务器URL，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.environ.get("KILO_CODE_API_KEY")
        self.server_url = server_url or os.environ.get("KILO_CODE_SERVER_URL", "https://api.kilocode.ai/v1")
        self.timeout = int(os.environ.get("KILO_CODE_TIMEOUT", "30"))
        
        if not self.api_key:
            logger.warning("No API key provided for Kilo Code adapter")
        
        logger.info(f"Initialized Kilo Code adapter with server URL: {self.server_url}")
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # 初始化能力标志
        self._capabilities = {
            "code_generation": True,
            "code_interpretation": True,
            "task_decomposition": True,
            "code_optimization": True,
            "complexity_analysis": True
        }
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        使用配置信息初始化适配器
        
        Args:
            config: 配置信息字典
            
        Returns:
            初始化是否成功
        """
        try:
            # 更新配置
            if "api_key" in config:
                self.api_key = config["api_key"]
                self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
            
            if "server_url" in config:
                self.server_url = config["server_url"]
            
            if "timeout" in config:
                self.timeout = config["timeout"]
            
            if "capabilities" in config:
                self._capabilities.update(config["capabilities"])
            
            # 验证连接
            health_status = self.health_check()
            if health_status.get("status") == "ok":
                logger.info("Kilo Code adapter initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize Kilo Code adapter: {health_status.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Kilo Code adapter: {str(e)}")
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        获取适配器支持的能力
        
        Returns:
            支持的能力字典，键为能力名称，值为是否支持
        """
        return self._capabilities.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """
        检查适配器健康状态
        
        Returns:
            健康状态信息字典
        """
        try:
            response = self.session.get(
                f"{self.server_url}/health",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "Kilo Code service is healthy",
                    "details": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Kilo Code service returned status code {response.status_code}",
                    "details": response.text
                }
                
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Kilo Code service: {str(e)}",
                "details": None
            }
    
    def shutdown(self) -> bool:
        """
        关闭适配器，释放资源
        
        Returns:
            关闭是否成功
        """
        try:
            self.session.close()
            logger.info("Kilo Code adapter shut down successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down Kilo Code adapter: {str(e)}")
            return False
    
    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                     mode: str = "standard") -> str:
        """
        根据提示生成代码
        
        Args:
            prompt: 代码生成提示
            context: 上下文信息
            mode: 生成模式，可选值包括 "standard", "optimized", "explained"
            
        Returns:
            生成的代码字符串
            
        Raises:
            ValueError: 如果提示为空或模式无效
            RuntimeError: 如果API调用失败
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        
        if mode not in ["standard", "optimized", "explained"]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of: standard, optimized, explained")
        
        try:
            payload = {
                "prompt": prompt,
                "mode": mode
            }
            
            if context:
                payload["context"] = context
            
            logger.debug(f"Generating code with prompt: {prompt[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("code", "")
            else:
                error_msg = f"Failed to generate code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def interpret_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        解释代码
        
        Args:
            code: 需要解释的代码
            context: 上下文信息
            
        Returns:
            包含代码解释的字典
            
        Raises:
            ValueError: 如果代码为空
            RuntimeError: 如果API调用失败
        """
        if not code:
            raise ValueError("Code cannot be empty")
        
        try:
            payload = {
                "code": code
            }
            
            if context:
                payload["context"] = context
            
            logger.debug(f"Interpreting code: {code[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/interpret",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to interpret code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def decompose_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        分解任务
        
        Args:
            task_description: 任务描述
            
        Returns:
            分解后的子任务列表
            
        Raises:
            ValueError: 如果任务描述为空
            RuntimeError: 如果API调用失败
        """
        if not task_description:
            raise ValueError("Task description cannot be empty")
        
        try:
            payload = {
                "task": task_description
            }
            
            logger.debug(f"Decomposing task: {task_description[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/decompose",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("subtasks", [])
            else:
                error_msg = f"Failed to decompose task: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def batch_generate(self, prompts: List[str], context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        批量生成代码
        
        Args:
            prompts: 代码生成提示列表
            context: 共享上下文信息
            
        Returns:
            生成的代码字符串列表
            
        Raises:
            ValueError: 如果提示列表为空
            RuntimeError: 如果API调用失败
        """
        if not prompts:
            raise ValueError("Prompts list cannot be empty")
        
        try:
            payload = {
                "prompts": prompts
            }
            
            if context:
                payload["context"] = context
            
            logger.debug(f"Batch generating code for {len(prompts)} prompts...")
            
            response = self.session.post(
                f"{self.server_url}/batch_generate",
                json=payload,
                timeout=self.timeout * 2  # 批处理给予更长的超时时间
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("codes", [])
            else:
                error_msg = f"Failed to batch generate code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def optimize_code(self, code: str, optimization_level: str = "medium") -> str:
        """
        优化代码
        
        Args:
            code: 需要优化的代码
            optimization_level: 优化级别，可选值包括 "low", "medium", "high"
            
        Returns:
            优化后的代码
            
        Raises:
            ValueError: 如果代码为空或优化级别无效
            RuntimeError: 如果API调用失败
        """
        if not code:
            raise ValueError("Code cannot be empty")
        
        if optimization_level not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid optimization level: {optimization_level}. Must be one of: low, medium, high")
        
        try:
            payload = {
                "code": code,
                "level": optimization_level
            }
            
            logger.debug(f"Optimizing code with level {optimization_level}: {code[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/optimize",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("optimized_code", "")
            else:
                error_msg = f"Failed to optimize code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """
        分析代码复杂度
        
        Args:
            code: 需要分析的代码
            
        Returns:
            包含复杂度分析的字典
            
        Raises:
            ValueError: 如果代码为空
            RuntimeError: 如果API调用失败
        """
        if not code:
            raise ValueError("Code cannot be empty")
        
        try:
            payload = {
                "code": code
            }
            
            logger.debug(f"Analyzing complexity of code: {code[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/analyze_complexity",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Failed to analyze code complexity: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def suggest_improvements(self, code: str) -> List[Dict[str, Any]]:
        """
        提供代码改进建议
        
        Args:
            code: 需要分析的代码
            
        Returns:
            改进建议列表
            
        Raises:
            ValueError: 如果代码为空
            RuntimeError: 如果API调用失败
        """
        if not code:
            raise ValueError("Code cannot be empty")
        
        try:
            payload = {
                "code": code
            }
            
            logger.debug(f"Suggesting improvements for code: {code[:50]}...")
            
            response = self.session.post(
                f"{self.server_url}/suggest_improvements",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("suggestions", [])
            else:
                error_msg = f"Failed to suggest code improvements: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
