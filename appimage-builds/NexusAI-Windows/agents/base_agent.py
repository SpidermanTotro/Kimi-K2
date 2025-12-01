"""
NEXUS AI - Base Agent
Abstract base class for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from models.gpt_handler import GPTHandler
from models.reasoning_handler import ReasoningHandler
from config.settings import config
from config.prompts import SystemPrompts
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    """Base class for all Nexus AI agents"""
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        use_reasoning: bool = False,
        model: Optional[str] = None
    ):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            role: Agent role/description
            system_prompt: System prompt for the agent
            use_reasoning: Use reasoning model (o1) instead of GPT
            model: Specific model to use
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.use_reasoning = use_reasoning
        
        # Initialize model handler
        if use_reasoning:
            self.model = ReasoningHandler(model=model or config.DEFAULT_REASONING_MODEL)
            logger.info(f"Agent '{name}' using reasoning model")
        else:
            self.model = GPTHandler(model=model or config.DEFAULT_CHAT_MODEL)
            logger.info(f"Agent '{name}' using chat model")
        
        self.tools = []
        self.memory = []
        
        logger.info(f"Initialized agent: {name} ({role})")
    
    @abstractmethod
    def process(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a task and return results
        Must be implemented by each agent
        
        Args:
            task: Task description
            context: Additional context
        
        Returns:
            Dict with processing results
        """
        pass
    
    def add_to_memory(self, entry: Dict[str, Any]):
        """
        Add entry to agent's memory
        
        Args:
            entry: Memory entry dict
        """
        self.memory.append(entry)
        
        # Keep last 20 entries
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
        
        logger.debug(f"Added memory entry to {self.name}")
    
    def get_memory_context(self, limit: int = 5) -> str:
        """
        Get memory as context string
        
        Args:
            limit: Number of recent entries to include
        
        Returns:
            Formatted memory context
        """
        if not self.memory:
            return ""
        
        context = "\n\nRecent interactions:\n"
        for entry in self.memory[-limit:]:
            context += f"- {entry.get('summary', str(entry))}\n"
        return context
    
    def clear_memory(self):
        """Clear agent's memory"""
        self.memory = []
        logger.info(f"Cleared memory for {self.name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics
        
        Returns:
            Dict with agent stats
        """
        return {
            "name": self.name,
            "role": self.role,
            "memory_entries": len(self.memory),
            "uses_reasoning": self.use_reasoning,
            "tools_available": len(self.tools)
        }
    
    def __str__(self):
        return f"{self.name} ({self.role})"
    
    def __repr__(self):
        return f"<Agent: {self.name}>"

__all__ = ['BaseAgent']