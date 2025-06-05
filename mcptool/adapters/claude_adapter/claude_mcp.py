"""
Claude适配器实现

此模块实现了基于Anthropic Claude API的适配器，用于将Claude的大模型能力集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时支持与Gemini和Kilo Code适配器的协同工作。
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
import requests

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("CLAUDE_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("CLAUDE_LOG_FILE", None)
)
logger = logging.getLogger("claude_adapter")

class ClaudeAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Claude适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Anthropic Claude服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性和与其他适配器的协同工作。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化Claude适配器
        
        Args:
            api_key: Claude API密钥，如果为None则从环境变量获取
            base_url: Claude API基础URL，如果为None则使用默认值
        """
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        self.base_url = base_url or os.environ.get("CLAUDE_BASE_URL", "https://api.anthropic.com")
        self.model = os.environ.get("CLAUDE_MODEL", "claude-3-opus-20240229")
        self.timeout = int(os.environ.get("CLAUDE_TIMEOUT", "60"))
        
        if not self.api_key:
            logger.warning("No API key provided for Claude adapter")
        
        logger.info(f"Initialized Claude adapter with model: {self.model}")
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        })
        
        # 初始化能力标志
        self._capabilities = {
            "code_generation": True,
            "code_interpretation": True,
            "task_decomposition": True,
            "code_optimization": True,
            "complexity_analysis": True
        }
        
        # 初始化生成参数
        self.generation_config = {
            "temperature": 0.2,
            "max_tokens": 4000,
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
                self.session.headers.update({"x-api-key": self.api_key})
            
            if "base_url" in config:
                self.base_url = config["base_url"]
            
            if "model" in config:
                self.model = config["model"]
            
            if "timeout" in config:
                self.timeout = config["timeout"]
            
            if "temperature" in config:
                self.generation_config["temperature"] = config["temperature"]
            
            if "max_tokens" in config:
                self.generation_config["max_tokens"] = config["max_tokens"]
            
            if "capabilities" in config:
                self._capabilities.update(config["capabilities"])
            
            # 验证连接
            health_status = self.health_check()
            if health_status.get("status") == "ok":
                logger.info("Claude adapter initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize Claude adapter: {health_status.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Claude adapter: {str(e)}")
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
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API key not provided",
                    "details": None
                }
            
            # 构建简单的请求
            payload = {
                "model": self.model,
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "Hello, are you working? Please respond with a simple confirmation."}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                return {
                    "status": "ok",
                    "message": "Claude service is healthy",
                    "details": {
                        "model": self.model,
                        "response": content[:50] + "..." if len(content) > 50 else content
                    }
                }
            else:
                error_message = f"Claude service returned status code {response.status_code}"
                try:
                    error_details = response.json()
                    error_message += f": {error_details.get('error', {}).get('message', '')}"
                except:
                    error_message += f": {response.text}"
                
                return {
                    "status": "error",
                    "message": error_message,
                    "details": None
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Claude service: {str(e)}",
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
            logger.info("Claude adapter shut down successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down Claude adapter: {str(e)}")
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
            # 构建提示
            system_prompt = "You are an expert programmer. "
            
            if mode == "standard":
                system_prompt += "Generate clean, efficient code based on the user's requirements."
            elif mode == "optimized":
                system_prompt += "Generate highly optimized code with excellent performance characteristics."
            elif mode == "explained":
                system_prompt += "Generate well-commented code with detailed explanations of the implementation."
            
            user_prompt = prompt
            
            if context:
                context_str = json.dumps(context, indent=2)
                user_prompt += f"\n\nAdditional context:\n{context_str}"
            
            # 添加明确的代码格式指令
            user_prompt += "\n\nPlease provide only the code without any additional explanations or markdown formatting."
            
            logger.debug(f"Generating code with prompt: {prompt[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取代码块
                code = self._extract_code_from_response(content)
                return code
            else:
                error_msg = f"Failed to generate code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
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
            # 构建提示
            system_prompt = "You are an expert code analyst. Analyze the provided code and provide a detailed explanation."
            
            user_prompt = f"""
Please analyze and interpret the following code. Provide a detailed explanation including:
1. A high-level description of what the code does
2. Time and space complexity analysis
3. Any potential issues or bugs
4. Suggestions for improvement

Code to interpret:
```
{code}
```

Format your response as a JSON object with the following structure:
{{
  "description": "High-level description of the code",
  "complexity": {{
    "time": "Time complexity (Big O notation)",
    "space": "Space complexity (Big O notation)"
  }},
  "issues": [
    "Issue 1",
    "Issue 2"
  ],
  "suggestions": [
    "Suggestion 1",
    "Suggestion 2"
  ]
}}
"""
            
            if context:
                context_str = json.dumps(context, indent=2)
                user_prompt += f"\n\nAdditional context:\n{context_str}"
            
            logger.debug(f"Interpreting code: {code[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取JSON
                interpretation = self._extract_json_from_response(content)
                return interpretation
            else:
                error_msg = f"Failed to interpret code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
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
            # 构建提示
            system_prompt = "You are an expert project planner. Break down complex tasks into manageable subtasks."
            
            user_prompt = f"""
Please decompose the following task into smaller, manageable subtasks:

Task: {task_description}

Format your response as a JSON array with the following structure:
[
  {{
    "id": 1,
    "description": "Subtask 1 description",
    "estimated_time": "Estimated time (e.g., '30m', '2h')"
  }},
  {{
    "id": 2,
    "description": "Subtask 2 description",
    "estimated_time": "Estimated time (e.g., '30m', '2h')"
  }}
]

Provide a comprehensive breakdown that covers all aspects of the task.
"""
            
            logger.debug(f"Decomposing task: {task_description[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取JSON
                subtasks = self._extract_json_from_response(content)
                if isinstance(subtasks, list):
                    return subtasks
                else:
                    return []
            else:
                error_msg = f"Failed to decompose task: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
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
        
        results = []
        
        for prompt in prompts:
            try:
                code = self.generate_code(prompt, context)
                results.append(code)
            except Exception as e:
                logger.error(f"Error generating code for prompt '{prompt[:30]}...': {str(e)}")
                results.append("")  # 添加空字符串作为占位符
        
        return results
    
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
            # 构建提示
            system_prompt = "You are an expert code optimizer. Optimize the provided code according to the specified level."
            
            optimization_instructions = {
                "low": "Make basic optimizations that improve readability and maintainability without significant structural changes.",
                "medium": "Make moderate optimizations that improve performance and efficiency while maintaining the original structure.",
                "high": "Make aggressive optimizations that maximize performance, even if it requires significant restructuring."
            }
            
            user_prompt = f"""
Please optimize the following code. Optimization level: {optimization_level.upper()}

Original code:
```
{code}
```

{optimization_instructions[optimization_level]}

Return only the optimized code without any explanations or additional text.
"""
            
            logger.debug(f"Optimizing code with level {optimization_level}: {code[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取代码块
                optimized_code = self._extract_code_from_response(content)
                return optimized_code
            else:
                error_msg = f"Failed to optimize code: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
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
            # 构建提示
            system_prompt = "You are an expert in algorithm analysis. Analyze the time and space complexity of the provided code."
            
            user_prompt = f"""
Please analyze the time and space complexity of the following code:

```
{code}
```

Format your response as a JSON object with the following structure:
{{
  "time_complexity": "Time complexity in Big O notation",
  "space_complexity": "Space complexity in Big O notation",
  "details": {{
    "worst_case": "Worst case complexity explanation",
    "average_case": "Average case complexity explanation",
    "best_case": "Best case complexity explanation"
  }},
  "bottlenecks": [
    "Bottleneck 1",
    "Bottleneck 2"
  ]
}}
"""
            
            logger.debug(f"Analyzing complexity of code: {code[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取JSON
                analysis = self._extract_json_from_response(content)
                return analysis
            else:
                error_msg = f"Failed to analyze code complexity: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
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
            # 构建提示
            system_prompt = "You are an expert code reviewer. Provide detailed suggestions for improving the provided code."
            
            user_prompt = f"""
Please review the following code and suggest improvements:

```
{code}
```

Format your response as a JSON array with the following structure:
[
  {{
    "type": "Improvement type (e.g., 'Performance', 'Readability', 'Security')",
    "description": "Detailed description of the improvement",
    "code_snippet": "Example code snippet implementing the improvement"
  }}
]
"""
            
            logger.debug(f"Suggesting improvements for code: {code[:50]}...")
            
            # 构建API请求
            payload = {
                "model": self.model,
                "max_tokens": self.generation_config["max_tokens"],
                "temperature": self.generation_config["temperature"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/messages",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [{}])[0].get("text", "")
                
                # 提取JSON
                suggestions = self._extract_json_from_response(content)
                if isinstance(suggestions, list):
                    return suggestions
                else:
                    return []
            else:
                error_msg = f"Failed to suggest code improvements: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """
        从响应文本中提取代码块
        
        Args:
            response_text: 响应文本
            
        Returns:
            提取的代码
        """
        # 尝试提取Markdown代码块
        import re
        code_block_pattern = r"```(?:\w+)?\s*([\s\S]*?)\s*```"
        matches = re.findall(code_block_pattern, response_text)
        
        if matches:
            # 返回第一个代码块
            return matches[0].strip()
        else:
            # 如果没有代码块，返回原始文本
            return response_text.strip()
    
    def _extract_json_from_response(self, response_text: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        从响应文本中提取JSON
        
        Args:
            response_text: 响应文本
            
        Returns:
            提取的JSON对象
        """
        # 尝试提取JSON
        import re
        import json
        
        # 尝试直接解析整个响应
        try:
            return json.loads(response_text)
        except:
            pass
        
        # 尝试提取JSON块
        json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_block_pattern, response_text)
        
        if matches:
            try:
                # 尝试解析第一个JSON块
                return json.loads(matches[0])
            except:
                pass
        
        # 尝试提取{...}或[...]格式的JSON
        json_pattern = r"(\{[\s\S]*\}|\[[\s\S]*\])"
        matches = re.findall(json_pattern, response_text)
        
        if matches:
            try:
                # 尝试解析第一个匹配项
                return json.loads(matches[0])
            except:
                pass
        
        # 如果所有尝试都失败，返回空字典
        logger.warning("Failed to extract JSON from response")
        return {}
