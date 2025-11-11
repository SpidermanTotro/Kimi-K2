"""
Contextual Chat Module
Enhanced chat with context awareness and conversation flow
"""

from typing import Dict, List, Optional, Any
from ..client import KimiClient


class ContextualChat:
    """
    Contextual chat with enhanced conversation understanding.
    
    Provides:
    - Context-aware responses
    - Conversation history tracking
    - Topic detection and switching
    - Sentiment awareness
    """
    
    def __init__(self, client: Optional[KimiClient] = None):
        """
        Initialize the contextual chat module.
        
        Args:
            client: Kimi K2 client instance
        """
        self.client = client or KimiClient()
        self.context_window: List[Dict[str, str]] = []
        self.current_topic: Optional[str] = None
    
    def chat_with_context(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        maintain_history: bool = True,
    ) -> Dict[str, Any]:
        """
        Chat with contextual awareness.
        
        Args:
            user_message: User's message
            context: Additional context (user info, preferences, etc.)
            maintain_history: Whether to maintain conversation history
            
        Returns:
            Response with context metadata
        """
        # Build context string
        context_parts = []
        
        if context:
            if "user_info" in context:
                context_parts.append(f"User information: {context['user_info']}")
            if "preferences" in context:
                context_parts.append(f"User preferences: {context['preferences']}")
            if "location" in context:
                context_parts.append(f"User location: {context['location']}")
        
        # Add conversation history
        if maintain_history and self.context_window:
            recent_history = self.context_window[-5:]  # Last 5 exchanges
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_history
            ])
            context_parts.append(f"Recent conversation:\n{history_str}")
        
        # Build system prompt with context
        system_prompt = "You are Kimi, an AI assistant created by Moonshot AI."
        if context_parts:
            system_prompt += "\n\nContext:\n" + "\n\n".join(context_parts)
        
        # Get response
        response = self.client.simple_chat(user_message, system_prompt=system_prompt)
        
        # Update history
        if maintain_history:
            self.context_window.append({"role": "user", "content": user_message})
            self.context_window.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "context_used": context is not None,
            "history_length": len(self.context_window),
            "topic": self.current_topic
        }
    
    def detect_topic_change(self, user_message: str) -> Dict[str, Any]:
        """
        Detect if the user is changing topics.
        
        Args:
            user_message: User's message
            
        Returns:
            Topic change information
        """
        if not self.context_window:
            return {
                "topic_changed": False,
                "previous_topic": None,
                "new_topic": None
            }
        
        recent_context = " ".join([
            msg["content"] for msg in self.context_window[-4:]
        ])
        
        prompt = f"""Given the recent conversation context and the new user message, determine if the user is changing topics.

Recent context: {recent_context}

New message: {user_message}

Respond in this format:
- Topic changed: Yes/No
- Previous topic: [topic name or "none"]
- New topic: [topic name or "same"]"""
        
        response = self.client.simple_chat(prompt)
        
        # Simple parsing (in production, use structured output)
        topic_changed = "yes" in response.lower().split("\n")[0]
        
        if topic_changed:
            self.current_topic = user_message[:50]  # Simplified
        
        return {
            "topic_changed": topic_changed,
            "analysis": response,
            "previous_topic": self.current_topic
        }
    
    def summarize_conversation(self) -> str:
        """
        Summarize the current conversation.
        
        Returns:
            Summary of the conversation
        """
        if not self.context_window:
            return "No conversation history available."
        
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.context_window
        ])
        
        prompt = f"""Please provide a concise summary of the following conversation:

{conversation}

Include:
1. Main topics discussed
2. Key points or decisions
3. Any unresolved questions"""
        
        summary = self.client.simple_chat(prompt)
        return summary
    
    def clear_context(self):
        """Clear the conversation context."""
        self.context_window = []
        self.current_topic = None
    
    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current context.
        
        Returns:
            Context statistics
        """
        return {
            "message_count": len(self.context_window),
            "user_messages": len([m for m in self.context_window if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.context_window if m["role"] == "assistant"]),
            "current_topic": self.current_topic,
        }
