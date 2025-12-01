"""
NEXUS AI - Code Agent
Specialized agent for writing, debugging, and executing code
"""

from agents.base_agent import BaseAgent
from tools.code_executor import CodeExecutor
from config.prompts import SystemPrompts
from config.settings import config
from typing import Dict, Any, Optional
from utils.logger import get_logger
import re

logger = get_logger(__name__)

class CodeAgent(BaseAgent):
    """Agent specialized in writing and executing code"""
    
    def __init__(self):
        super().__init__(
            name="Code Agent",
            role="Programmer & Code Executor",
            system_prompt=SystemPrompts.CODE_AGENT,
            use_reasoning=False,
            model=config.DEFAULT_CODE_MODEL
        )
        self.executor = CodeExecutor(timeout=config.CODE_EXECUTION_TIMEOUT)
        logger.info("CodeAgent initialized with code executor")
    
    def process(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process coding task: write and/or execute code
        
        Args:
            task: Coding task description
            context: Additional context
        
        Returns:
            Dict with code, explanation, and execution results
        """
        logger.info(f"Processing coding task: {task[:100]}...")
        
        # Build prompt
        prompt = f"{self.system_prompt}\n\nTask: {task}"
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        # Add memory context
        memory_context = self.get_memory_context()
        if memory_context:
            prompt += memory_context
        
        # Get code from model
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(messages)
        
        content = response["content"]
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        
        result = {
            "agent": self.name,
            "explanation": content,
            "code_blocks": code_blocks,
            "execution_results": []
        }
        
        # Execute code blocks if any
        if code_blocks:
            logger.info(f"Executing {len(code_blocks)} code blocks")
            for i, code in enumerate(code_blocks):
                exec_result = self.executor.execute(code)
                result["execution_results"].append({
                    "block_number": i + 1,
                    "code": code,
                    **exec_result
                })
        
        # Add to memory
        self.add_to_memory({
            "task": task,
            "summary": f"Wrote and executed {len(code_blocks)} code blocks",
            "success": all(r["success"] for r in result["execution_results"]) if code_blocks else True
        })
        
        logger.info("Coding task completed")
        return result
    
    def debug_code(self, code: str, error: str) -> Dict[str, Any]:
        """
        Debug code with error message
        
        Args:
            code: Code with error
            error: Error message
        
        Returns:
            Dict with debugging results
        """
        logger.info("Debugging code")
        
        prompt = f"""{SystemPrompts.DEBUGGING_PROMPT}

Code with error:
```python
{code}
```

Error message:
{error}

Please:
1. Identify the bug
2. Explain why it occurs
3. Provide the fixed code
4. Explain the fix
"""
        
        return self.process(prompt)
    
    def optimize_code(self, code: str) -> Dict[str, Any]:
        """
        Optimize code for performance
        
        Args:
            code: Code to optimize
        
        Returns:
            Dict with optimization results
        """
        logger.info("Optimizing code")
        
        prompt = f"""{SystemPrompts.OPTIMIZATION_PROMPT}

Code to optimize:
```python
{code}
```

Please:
1. Identify performance bottlenecks
2. Suggest optimizations
3. Provide optimized code
4. Explain improvements
"""
        
        return self.process(prompt)
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """
        Review code for quality and best practices
        
        Args:
            code: Code to review
        
        Returns:
            Dict with review results
        """
        logger.info("Reviewing code")
        
        prompt = f"""Review this code for:
1. Correctness
2. Security
3. Best practices
4. Readability
5. Maintainability

Code:
```python
{code}
```

Provide specific, actionable feedback.
"""
        
        return self.process(prompt)
    
    def explain_code(self, code: str) -> Dict[str, Any]:
        """
        Explain what code does
        
        Args:
            code: Code to explain
        
        Returns:
            Dict with explanation
        """
        logger.info("Explaining code")
        
        prompt = f"""Explain this code in detail:

```python
{code}
```

Please explain:
1. What it does
2. How it works
3. Key concepts used
4. Potential improvements
"""
        
        return self.process(prompt)
    
    def _extract_code_blocks(self, text: str) -> list:
        """
        Extract Python code blocks from markdown
        
        Args:
            text: Text containing code blocks
        
        Returns:
            List of code strings
        """
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        logger.debug(f"Extracted {len(matches)} code blocks")
        return matches

__all__ = ['CodeAgent']