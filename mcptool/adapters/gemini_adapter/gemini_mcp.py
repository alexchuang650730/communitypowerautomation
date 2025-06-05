"""
Gemini API适配器实现

此模块实现了基于Google Gemini API的Kilo Code适配器，用于将Gemini的大模型能力集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时最小化对原有代码的修改。
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("GEMINI_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("GEMINI_LOG_FILE", None)
)
logger = logging.getLogger("gemini_adapter")

class GeminiAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Gemini适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Google Gemini服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Gemini适配器
        
        Args:
            api_key: Gemini API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided for Gemini adapter")
        
        # 初始化Gemini模型
        self.model = None
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        
        logger.info(f"Initialized Gemini adapter with model: {self.model_name}")
        
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
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
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
            
            if "model" in config:
                self.model_name = config["model"]
            
            if "temperature" in config:
                self.generation_config["temperature"] = config["temperature"]
            
            if "max_output_tokens" in config:
                self.generation_config["max_output_tokens"] = config["max_output_tokens"]
            
            if "capabilities" in config:
                self._capabilities.update(config["capabilities"])
            
            # 初始化Gemini API
            genai.configure(api_key=self.api_key)
            
            # 创建模型实例
            self.model = genai.GenerativeModel(self.model_name)
            
            # 验证连接
            health_status = self.health_check()
            if health_status.get("status") == "ok":
                logger.info("Gemini adapter initialized successfully")
                return True
            else:
                logger.error(f"Failed to initialize Gemini adapter: {health_status.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Gemini adapter: {str(e)}")
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
            
            if not self.model:
                # 初始化API和模型
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            
            # 简单的健康检查请求
            response = self.model.generate_content("Hello, are you working?")
            
            if response and hasattr(response, 'text'):
                return {
                    "status": "ok",
                    "message": "Gemini service is healthy",
                    "details": {
                        "model": self.model_name,
                        "response": response.text[:50] + "..." if len(response.text) > 50 else response.text
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Gemini service returned an invalid response",
                    "details": str(response)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to connect to Gemini service: {str(e)}",
                "details": None
            }
    
    def shutdown(self) -> bool:
        """
        关闭适配器，释放资源
        
        Returns:
            关闭是否成功
        """
        try:
            # Gemini模型不需要显式关闭
            self.model = None
            logger.info("Gemini adapter shut down successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down Gemini adapter: {str(e)}")
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
            full_prompt = self._build_code_generation_prompt(prompt, context, mode)
            
            logger.debug(f"Generating code with prompt: {prompt[:50]}...")
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                top_p=self.generation_config["top_p"],
                top_k=self.generation_config["top_k"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取代码块
                code = self._extract_code_from_response(response.text)
                return code
            else:
                error_msg = f"Failed to generate code: Invalid response from Gemini API"
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
            prompt = f"""
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
                prompt += f"\n\nAdditional context:\n{context_str}"
            
            logger.debug(f"Interpreting code: {code[:50]}...")
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取JSON
                interpretation = self._extract_json_from_response(response.text)
                return interpretation
            else:
                error_msg = f"Failed to interpret code: Invalid response from Gemini API"
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
            prompt = f"""
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
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取JSON
                subtasks = self._extract_json_from_response(response.text)
                if isinstance(subtasks, list):
                    return subtasks
                else:
                    return []
            else:
                error_msg = f"Failed to decompose task: Invalid response from Gemini API"
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
            prompt = f"""
Please optimize the following code. Optimization level: {optimization_level.upper()}

Original code:
```
{code}
```

{self._get_optimization_instructions(optimization_level)}

Return only the optimized code without any explanations or additional text.
"""
            
            logger.debug(f"Optimizing code with level {optimization_level}: {code[:50]}...")
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取代码块
                optimized_code = self._extract_code_from_response(response.text)
                return optimized_code
            else:
                error_msg = f"Failed to optimize code: Invalid response from Gemini API"
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
            prompt = f"""
Please analyze the time and space complexity of the following code:

```
{code}
```

Format your response as a JSON object with the following structure:
{{
  "time_complexity": "Time complexity in Big O notation",
  "space_complexity": "Space complexity in Big O notation",
  "details": {{
    "loops": "Number of loops",
    "nested_depth": "Maximum nesting depth",
    "recursive": "Whether the code is recursive (true/false)",
    "algorithm_type": "Type of algorithm (e.g., sorting, searching)",
    "best_case_time": "Best case time complexity",
    "average_case_time": "Average case time complexity",
    "worst_case_time": "Worst case time complexity",
    "stability": "For sorting algorithms, whether it's stable",
    "in_place": "Whether the algorithm is in-place (true/false)"
  }}
}}
"""
            
            logger.debug(f"Analyzing complexity of code: {code[:50]}...")
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取JSON
                analysis = self._extract_json_from_response(response.text)
                return analysis
            else:
                error_msg = f"Failed to analyze complexity: Invalid response from Gemini API"
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
            code: 需要改进的代码
            
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
            prompt = f"""
Please suggest improvements for the following code:

```
{code}
```

Format your response as a JSON array with the following structure:
[
  {{
    "type": "Improvement type (e.g., 'performance', 'readability', 'security')",
    "description": "Detailed description of the improvement",
    "code_snippet": "Example code snippet implementing the improvement"
  }}
]
"""
            
            logger.debug(f"Suggesting improvements for code: {code[:50]}...")
            
            # 调用Gemini API
            generation_config = genai.GenerationConfig(
                temperature=self.generation_config["temperature"],
                max_output_tokens=self.generation_config["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response and hasattr(response, 'text'):
                # 提取JSON
                suggestions = self._extract_json_from_response(response.text)
                if isinstance(suggestions, list):
                    return suggestions
                else:
                    return []
            else:
                error_msg = f"Failed to suggest improvements: Invalid response from Gemini API"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _build_code_generation_prompt(self, prompt: str, context: Optional[Dict[str, Any]], mode: str) -> str:
        """
        构建代码生成提示
        
        Args:
            prompt: 原始提示
            context: 上下文信息
            mode: 生成模式
            
        Returns:
            完整的提示字符串
        """
        # 基础提示
        if mode == "standard":
            full_prompt = f"""
Generate code for the following task:

{prompt}

Return only the code without any explanations or additional text.
"""
        elif mode == "optimized":
            full_prompt = f"""
Generate optimized code for the following task:

{prompt}

The code should be:
1. Efficient in terms of time and space complexity
2. Well-structured and maintainable
3. Following best practices for the language
4. Properly documented with comments

Return only the code without any explanations or additional text.
"""
        elif mode == "explained":
            full_prompt = f"""
Generate well-commented and explained code for the following task:

{prompt}

The code should:
1. Include detailed comments explaining the logic
2. Have proper documentation for functions/methods
3. Include explanations for complex parts
4. Follow best practices for the language

Return only the code with comments, without any additional text.
"""
        
        # 添加上下文信息
        if context:
            context_str = json.dumps(context, indent=2)
            full_prompt += f"\n\nAdditional context:\n{context_str}"
        
        return full_prompt
    
    def _get_optimization_instructions(self, level: str) -> str:
        """
        获取优化指令
        
        Args:
            level: 优化级别
            
        Returns:
            优化指令字符串
        """
        if level == "low":
            return """
For LOW optimization level:
- Fix obvious inefficiencies
- Improve variable names and formatting
- Add basic comments
- Keep the original algorithm and structure
"""
        elif level == "medium":
            return """
For MEDIUM optimization level:
- Improve algorithm efficiency where possible
- Optimize loops and conditionals
- Use appropriate data structures
- Add comprehensive comments
- Improve code structure and organization
"""
        elif level == "high":
            return """
For HIGH optimization level:
- Implement the most efficient algorithm
- Optimize for both time and space complexity
- Use advanced language features when appropriate
- Add detailed documentation
- Ensure code is robust with proper error handling
- Consider edge cases and performance implications
"""
        
        return ""
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """
        从响应文本中提取代码
        
        Args:
            response_text: 响应文本
            
        Returns:
            提取的代码字符串
        """
        # 尝试提取代码块
        import re
        code_blocks = re.findall(r'```(?:\w*\n)?(.*?)```', response_text, re.DOTALL)
        
        if code_blocks:
            return code_blocks[0].strip()
        
        # 如果没有代码块，返回整个响应
        return response_text.strip()
    
    def _extract_json_from_response(self, response_text: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        从响应文本中提取JSON
        
        Args:
            response_text: 响应文本
            
        Returns:
            提取的JSON对象
        """
        # 尝试提取JSON块
        import re
        json_blocks = re.findall(r'```(?:json\n)?(.*?)```', response_text, re.DOTALL)
        
        if json_blocks:
            try:
                return json.loads(json_blocks[0].strip())
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析整个响应
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # 如果无法解析JSON，返回空字典
            logger.error(f"Failed to parse JSON from response: {response_text[:100]}...")
            return {}
