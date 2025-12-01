"""
NEXUS AI - Reasoning Model Handler
Handles OpenAI's o1 reasoning models (o1, o1-preview, o1-mini)
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class ReasoningHandler:
    """
    Handler for OpenAI's o1 reasoning models
    Supports: o1, o1-preview, o1-mini
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        reasoning_effort: str = "medium"
    ):
        """
        Initialize reasoning handler
        
        Args:
            model: Model name (o1, o1-preview, o1-mini)
            reasoning_effort: Level of reasoning effort
        """
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = model or config.DEFAULT_REASONING_MODEL
        self.reasoning_effort = reasoning_effort
        
        logger.info(f"Initialized ReasoningHandler with model: {self.model}")
    
    def reason(
        self,
        prompt: str,
        max_tokens: int = 4096,
        reasoning_effort: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Use o1 model for deep reasoning
        
        Args:
            prompt: The problem to reason about
            max_tokens: Maximum completion tokens
            reasoning_effort: Override default reasoning effort
        
        Returns:
            Dict with answer, reasoning trace, and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=max_tokens
            )
            
            result = {
                "answer": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            # Add reasoning tokens if available
            if hasattr(response.usage, 'completion_tokens_details'):
                details = response.usage.completion_tokens_details
                if hasattr(details, 'reasoning_tokens'):
                    result["usage"]["reasoning_tokens"] = details.reasoning_tokens
            
            logger.debug(f"Reasoning completion: {result['usage']['total_tokens']} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Reasoning error: {str(e)}")
            return {
                "error": str(e),
                "answer": f"Reasoning error: {str(e)}"
            }
    
    def solve_problem(
        self,
        problem: str,
        context: str = "",
        step_by_step: bool = True
    ) -> Dict[str, Any]:
        """
        Solve a complex problem with step-by-step reasoning
        
        Args:
            problem: The problem to solve
            context: Additional context
            step_by_step: Request step-by-step explanation
        
        Returns:
            Dict with solution and reasoning
        """
        full_prompt = f"{context}\n\n{problem}" if context else problem
        
        if step_by_step:
            enhanced_prompt = f"""Solve this problem step-by-step:

{full_prompt}

Please:
1. Break down the problem
2. Show your reasoning process
3. Provide a clear answer
4. Explain any assumptions
"""
        else:
            enhanced_prompt = full_prompt
        
        return self.reason(enhanced_prompt)
    
    def analyze_code(
        self,
        code: str,
        task: str = "analyze"
    ) -> Dict[str, Any]:
        """
        Analyze code with deep reasoning
        
        Args:
            code: Code to analyze
            task: Type of analysis (analyze, debug, optimize, review)
        
        Returns:
            Dict with analysis results
        """
        task_prompts = {
            "analyze": "Analyze this code thoroughly. Explain what it does, identify potential issues, and suggest improvements:",
            "debug": "Debug this code. Find all bugs, explain why they occur, and provide fixes:",
            "optimize": "Optimize this code. Identify performance bottlenecks and suggest optimizations:",
            "review": "Review this code. Check for correctness, security, best practices, and maintainability:"
        }
        
        prompt = f"""{task_prompts.get(task, task_prompts['analyze'])}

```python
{code}
```

Provide a detailed analysis with specific recommendations.
"""
        
        return self.reason(prompt)
    
    def solve_math(
        self,
        problem: str,
        show_work: bool = True
    ) -> Dict[str, Any]:
        """
        Solve mathematical problems with reasoning
        
        Args:
            problem: Math problem to solve
            show_work: Show step-by-step work
        
        Returns:
            Dict with solution and work shown
        """
        if show_work:
            prompt = f"""Solve this mathematical problem step-by-step:

{problem}

Show all your work:
1. Identify what's being asked
2. List known information
3. Show each calculation step
4. Verify your answer
5. State the final answer clearly
"""
        else:
            prompt = problem
        
        return self.reason(prompt)
    
    def reason_about_data(
        self,
        data_description: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Reason about data and answer questions
        
        Args:
            data_description: Description of the data
            question: Question about the data
        
        Returns:
            Dict with reasoning and answer
        """
        prompt = f"""Given this data:

{data_description}

Question: {question}

Analyze the data carefully and provide a well-reasoned answer.
"""
        
        return self.reason(prompt)
    
    def compare_options(
        self,
        options: List[str],
        criteria: str
    ) -> Dict[str, Any]:
        """
        Compare multiple options using reasoning
        
        Args:
            options: List of options to compare
            criteria: Criteria for comparison
        
        Returns:
            Dict with comparison and recommendation
        """
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""Compare these options based on the given criteria:

Options:
{options_text}

Criteria: {criteria}

Analyze each option thoroughly and provide:
1. Pros and cons of each option
2. How each meets the criteria
3. Your recommendation with reasoning
"""
        
        return self.reason(prompt)

__all__ = ['ReasoningHandler']