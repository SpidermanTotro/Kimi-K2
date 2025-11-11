"""
Advanced Reasoning Module
Provides chain-of-thought reasoning and problem decomposition
"""

from typing import Dict, List, Optional, Any
from ..client import KimiClient


class AdvancedReasoning:
    """
    Advanced reasoning capabilities for complex problem solving.
    
    Implements:
    - Chain-of-thought reasoning
    - Problem decomposition
    - Step-by-step analysis
    - Multi-hop reasoning
    """
    
    def __init__(self, client: Optional[KimiClient] = None):
        """
        Initialize the reasoning module.
        
        Args:
            client: Kimi K2 client instance
        """
        self.client = client or KimiClient()
    
    def chain_of_thought(
        self,
        problem: str,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform chain-of-thought reasoning on a problem.
        
        Args:
            problem: The problem to solve
            domain: Optional domain context (math, logic, coding, etc.)
            
        Returns:
            Dictionary with reasoning steps and final answer
        """
        domain_context = f" in the {domain} domain" if domain else ""
        
        prompt = f"""Please solve the following problem{domain_context} using step-by-step reasoning.

Problem: {problem}

Please provide:
1. Your thought process step-by-step
2. Any intermediate conclusions
3. The final answer

Format your response clearly with numbered steps."""
        
        response = self.client.simple_chat(prompt)
        
        return {
            "problem": problem,
            "domain": domain,
            "reasoning": response,
            "type": "chain_of_thought"
        }
    
    def decompose_problem(
        self,
        complex_problem: str,
    ) -> Dict[str, Any]:
        """
        Decompose a complex problem into smaller sub-problems.
        
        Args:
            complex_problem: The complex problem to decompose
            
        Returns:
            Dictionary with sub-problems and solving strategy
        """
        prompt = f"""Please decompose the following complex problem into smaller, manageable sub-problems.

Problem: {complex_problem}

For each sub-problem:
1. State the sub-problem clearly
2. Explain why it's important
3. Suggest an approach to solve it
4. Indicate dependencies on other sub-problems

Finally, provide a recommended order to solve these sub-problems."""
        
        response = self.client.simple_chat(prompt)
        
        return {
            "original_problem": complex_problem,
            "decomposition": response,
            "type": "problem_decomposition"
        }
    
    def multi_hop_reasoning(
        self,
        question: str,
        context: List[str],
    ) -> Dict[str, Any]:
        """
        Perform multi-hop reasoning across multiple pieces of context.
        
        Args:
            question: The question to answer
            context: List of context passages
            
        Returns:
            Dictionary with reasoning path and answer
        """
        context_str = "\n\n".join([f"Context {i+1}: {c}" for i, c in enumerate(context)])
        
        prompt = f"""Given the following contexts, please answer the question using multi-hop reasoning.
You may need to connect information from multiple contexts.

{context_str}

Question: {question}

Please:
1. Identify which contexts are relevant
2. Show how you connect information across contexts
3. Provide the final answer with supporting evidence"""
        
        response = self.client.simple_chat(prompt)
        
        return {
            "question": question,
            "num_contexts": len(context),
            "reasoning": response,
            "type": "multi_hop_reasoning"
        }
    
    def analyze_step_by_step(
        self,
        task: str,
        requirements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a task step-by-step with detailed planning.
        
        Args:
            task: The task to analyze
            requirements: Optional list of requirements or constraints
            
        Returns:
            Dictionary with step-by-step analysis
        """
        req_str = ""
        if requirements:
            req_str = "\n\nRequirements:\n" + "\n".join([f"- {r}" for r in requirements])
        
        prompt = f"""Please analyze the following task step-by-step:

Task: {task}{req_str}

Please provide:
1. Initial assessment of the task
2. Required steps in order
3. Potential challenges for each step
4. Resources or tools needed
5. Success criteria"""
        
        response = self.client.simple_chat(prompt)
        
        return {
            "task": task,
            "requirements": requirements,
            "analysis": response,
            "type": "step_by_step_analysis"
        }
