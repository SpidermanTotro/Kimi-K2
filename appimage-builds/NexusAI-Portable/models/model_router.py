"""
NEXUS AI - Model Router
Smart model selection based on task type and requirements
"""

from typing import Dict, Any, Optional
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class ModelRouter:
    """
    Intelligently routes tasks to the most appropriate model
    """
    
    # Task type to model mapping
    TASK_MODEL_MAP = {
        # Reasoning tasks - use o1 models
        "math": config.DEFAULT_REASONING_MODEL,
        "logic": config.DEFAULT_REASONING_MODEL,
        "problem_solving": config.DEFAULT_REASONING_MODEL,
        "analysis": config.DEFAULT_REASONING_MODEL,
        "debugging": config.DEFAULT_REASONING_MODEL,
        
        # Coding tasks - use GPT-4
        "code": config.DEFAULT_CODE_MODEL,
        "programming": config.DEFAULT_CODE_MODEL,
        "code_review": config.DEFAULT_CODE_MODEL,
        
        # Vision tasks - use GPT-4 Vision
        "vision": config.DEFAULT_VISION_MODEL,
        "image": config.DEFAULT_VISION_MODEL,
        "image_analysis": config.DEFAULT_VISION_MODEL,
        
        # General chat - use default chat model
        "chat": config.DEFAULT_CHAT_MODEL,
        "conversation": config.DEFAULT_CHAT_MODEL,
        "general": config.DEFAULT_CHAT_MODEL,
        
        # Creative tasks - use GPT-4 Turbo
        "creative": config.GPT_4_TURBO,
        "writing": config.GPT_4_TURBO,
        "brainstorming": config.GPT_4_TURBO,
    }
    
    @staticmethod
    def select_model(
        task_type: Optional[str] = None,
        user_preference: Optional[str] = None,
        requires_reasoning: bool = False,
        requires_vision: bool = False,
        requires_code: bool = False
    ) -> str:
        """
        Select the best model for the task
        
        Args:
            task_type: Type of task (math, code, chat, etc.)
            user_preference: User's preferred model
            requires_reasoning: Task requires deep reasoning
            requires_vision: Task requires image understanding
            requires_code: Task requires code execution
        
        Returns:
            Model name to use
        """
        # User preference takes priority
        if user_preference:
            logger.info(f"Using user-preferred model: {user_preference}")
            return user_preference
        
        # Capability-based selection
        if requires_vision:
            logger.info(f"Vision required, using: {config.DEFAULT_VISION_MODEL}")
            return config.DEFAULT_VISION_MODEL
        
        if requires_reasoning:
            logger.info(f"Reasoning required, using: {config.DEFAULT_REASONING_MODEL}")
            return config.DEFAULT_REASONING_MODEL
        
        if requires_code:
            logger.info(f"Code execution required, using: {config.DEFAULT_CODE_MODEL}")
            return config.DEFAULT_CODE_MODEL
        
        # Task type-based selection
        if task_type:
            model = ModelRouter.TASK_MODEL_MAP.get(task_type.lower())
            if model:
                logger.info(f"Task type '{task_type}' mapped to model: {model}")
                return model
        
        # Default fallback
        logger.info(f"Using default chat model: {config.DEFAULT_CHAT_MODEL}")
        return config.DEFAULT_CHAT_MODEL
    
    @staticmethod
    def get_model_capabilities(model: str) -> Dict[str, bool]:
        """
        Get capabilities of a specific model
        
        Args:
            model: Model name
        
        Returns:
            Dict of capabilities
        """
        capabilities = {
            "reasoning": False,
            "vision": False,
            "function_calling": False,
            "code_execution": False,
            "long_context": False,
        }
        
        # o1 models
        if model in [config.O1, config.O1_PREVIEW, config.O1_MINI]:
            capabilities["reasoning"] = True
            capabilities["long_context"] = True
        
        # GPT-4 Vision
        elif model == config.GPT_4_VISION:
            capabilities["vision"] = True
            capabilities["function_calling"] = True
        
        # GPT-4 models
        elif model in [config.GPT_4, config.GPT_4_TURBO]:
            capabilities["function_calling"] = True
            capabilities["code_execution"] = True
            capabilities["long_context"] = True
        
        # GPT-3.5
        elif model == config.GPT_35_TURBO:
            capabilities["function_calling"] = True
        
        return capabilities
    
    @staticmethod
    def estimate_cost(
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Estimate cost for a model call
        
        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        
        Returns:
            Estimated cost in USD
        """
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            config.O1: {"input": 15.00, "output": 60.00},
            config.O1_PREVIEW: {"input": 15.00, "output": 60.00},
            config.O1_MINI: {"input": 3.00, "output": 12.00},
            config.GPT_4_TURBO: {"input": 10.00, "output": 30.00},
            config.GPT_4: {"input": 30.00, "output": 60.00},
            config.GPT_4_VISION: {"input": 10.00, "output": 30.00},
            config.GPT_35_TURBO: {"input": 0.50, "output": 1.50},
        }
        
        if model not in pricing:
            return 0.0
        
        input_cost = (prompt_tokens / 1_000_000) * pricing[model]["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing[model]["output"]
        
        return input_cost + output_cost
    
    @staticmethod
    def recommend_model(
        task_description: str,
        budget_conscious: bool = False
    ) -> Dict[str, Any]:
        """
        Recommend a model based on task description
        
        Args:
            task_description: Description of the task
            budget_conscious: Prefer cheaper models
        
        Returns:
            Dict with recommended model and reasoning
        """
        task_lower = task_description.lower()
        
        # Keywords for different capabilities
        reasoning_keywords = ["solve", "calculate", "analyze", "reason", "logic", "math", "problem"]
        vision_keywords = ["image", "picture", "photo", "visual", "see", "look"]
        code_keywords = ["code", "program", "script", "function", "debug", "implement"]
        
        requires_reasoning = any(kw in task_lower for kw in reasoning_keywords)
        requires_vision = any(kw in task_lower for kw in vision_keywords)
        requires_code = any(kw in task_lower for kw in code_keywords)
        
        # Select model
        if requires_vision:
            model = config.GPT_4_VISION
            reason = "Task requires image understanding"
        elif requires_reasoning and not budget_conscious:
            model = config.O1_MINI if budget_conscious else config.O1_PREVIEW
            reason = "Task requires deep reasoning"
        elif requires_code:
            model = config.GPT_4
            reason = "Task requires code generation/execution"
        else:
            model = config.GPT_4_TURBO if not budget_conscious else config.GPT_35_TURBO
            reason = "General purpose task"
        
        return {
            "model": model,
            "reason": reason,
            "capabilities": ModelRouter.get_model_capabilities(model),
            "budget_friendly": budget_conscious
        }

__all__ = ['ModelRouter']