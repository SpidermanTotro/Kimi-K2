"""
Context Manager Module

Manages conversation context and history for multiple users in the dual-operator AI system.
Handles long-context understanding and multimodal input aggregation.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class ContextEntry:
    """
    Represents a single context entry in the conversation history.
    
    Attributes:
        user_id: ID of the user who created this context
        role: Role in conversation (user, assistant, system, tool)
        content: Content of the message
        modality: Type of content (text, image, audio, video, etc.)
        metadata: Additional metadata about the context
        timestamp: When this context was created
    """
    
    user_id: Optional[str]
    role: str
    content: Any
    modality: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context entry to dictionary format."""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'modality': self.modality,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class ContextManager:
    """
    Manages conversation context for multiple users with long-context support.
    
    This class handles:
    - Context aggregation from multiple users
    - Long-context maintenance and pruning
    - Multimodal input support
    - Context retrieval and summarization
    """
    
    def __init__(self, max_context_length: int = 100000):
        """
        Initialize the context manager.
        
        Args:
            max_context_length: Maximum number of tokens/entries to maintain
        """
        self.max_context_length = max_context_length
        self.context_history: List[ContextEntry] = []
        self.user_contexts: Dict[str, List[ContextEntry]] = {}
        self.shared_context: List[ContextEntry] = []
        
    def add_context(
        self,
        user_id: Optional[str],
        role: str,
        content: Any,
        modality: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        shared: bool = True
    ) -> None:
        """
        Add a new context entry.
        
        Args:
            user_id: ID of the user creating this context
            role: Role in conversation
            content: Content of the message
            modality: Type of content
            metadata: Additional metadata
            shared: Whether this context is shared between users
        """
        entry = ContextEntry(
            user_id=user_id,
            role=role,
            content=content,
            modality=modality,
            metadata=metadata or {}
        )
        
        self.context_history.append(entry)
        
        if shared:
            self.shared_context.append(entry)
        
        if user_id:
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = []
            self.user_contexts[user_id].append(entry)
        
        # Prune if necessary
        self._prune_context()
    
    def get_context_for_user(
        self,
        user_id: str,
        include_shared: bool = True,
        max_entries: Optional[int] = None
    ) -> List[ContextEntry]:
        """
        Get context relevant for a specific user.
        
        Args:
            user_id: ID of the user
            include_shared: Whether to include shared context
            max_entries: Maximum number of entries to return
            
        Returns:
            List of context entries
        """
        context = []
        
        if include_shared:
            context.extend(self.shared_context)
        
        if user_id in self.user_contexts:
            # Add user-specific context that's not already in shared
            for entry in self.user_contexts[user_id]:
                if entry not in context:
                    context.append(entry)
        
        # Sort by timestamp
        context.sort(key=lambda x: x.timestamp)
        
        if max_entries:
            context = context[-max_entries:]
        
        return context
    
    def get_combined_context(
        self,
        user_ids: Optional[List[str]] = None,
        max_entries: Optional[int] = None
    ) -> List[ContextEntry]:
        """
        Get combined context from multiple users.
        
        Args:
            user_ids: List of user IDs to include (None for all)
            max_entries: Maximum number of entries to return
            
        Returns:
            Combined list of context entries
        """
        if user_ids is None:
            context = self.context_history
        else:
            context = []
            for user_id in user_ids:
                if user_id in self.user_contexts:
                    context.extend(self.user_contexts[user_id])
            # Add shared context
            for entry in self.shared_context:
                if entry not in context:
                    context.append(entry)
        
        # Sort by timestamp and deduplicate
        seen = set()
        unique_context = []
        for entry in sorted(context, key=lambda x: x.timestamp):
            entry_id = id(entry)
            if entry_id not in seen:
                seen.add(entry_id)
                unique_context.append(entry)
        
        if max_entries:
            unique_context = unique_context[-max_entries:]
        
        return unique_context
    
    def get_context_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of the current context.
        
        Args:
            user_id: Optional user ID to get user-specific summary
            
        Returns:
            Dictionary containing context summary statistics
        """
        if user_id:
            context = self.get_context_for_user(user_id)
        else:
            context = self.context_history
        
        modality_counts = {}
        role_counts = {}
        
        for entry in context:
            modality_counts[entry.modality] = modality_counts.get(entry.modality, 0) + 1
            role_counts[entry.role] = role_counts.get(entry.role, 0) + 1
        
        return {
            'total_entries': len(context),
            'modality_counts': modality_counts,
            'role_counts': role_counts,
            'users': list(self.user_contexts.keys()),
            'shared_entries': len(self.shared_context)
        }
    
    def format_for_llm(
        self,
        user_id: Optional[str] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Format context for LLM input (OpenAI-compatible format).
        
        Args:
            user_id: Optional user ID to get user-specific context
            include_metadata: Whether to include metadata in messages
            
        Returns:
            List of message dictionaries
        """
        if user_id:
            context = self.get_context_for_user(user_id)
        else:
            context = self.context_history
        
        messages = []
        for entry in context:
            message = {
                'role': entry.role,
                'content': entry.content
            }
            
            if include_metadata:
                message['metadata'] = entry.metadata
                if entry.user_id:
                    message['user_id'] = entry.user_id
            
            messages.append(message)
        
        return messages
    
    def _prune_context(self) -> None:
        """
        Prune context history if it exceeds max_context_length.
        Keeps the most recent entries and important context.
        """
        if len(self.context_history) > self.max_context_length:
            # Keep the first few entries (system prompts, important context)
            # and the most recent entries
            keep_start = min(10, len(self.context_history) // 10)
            keep_recent = self.max_context_length - keep_start
            
            self.context_history = (
                self.context_history[:keep_start] +
                self.context_history[-keep_recent:]
            )
            
            # Update user contexts
            remaining_entries = set(self.context_history)
            for user_id in self.user_contexts:
                self.user_contexts[user_id] = [
                    e for e in self.user_contexts[user_id]
                    if e in remaining_entries
                ]
            
            # Update shared context
            self.shared_context = [
                e for e in self.shared_context
                if e in remaining_entries
            ]
    
    def clear_context(self, user_id: Optional[str] = None) -> None:
        """
        Clear context history.
        
        Args:
            user_id: Optional user ID to clear only that user's context
        """
        if user_id:
            self.user_contexts[user_id] = []
            # Remove user's entries from history
            self.context_history = [
                e for e in self.context_history
                if e.user_id != user_id
            ]
        else:
            self.context_history.clear()
            self.user_contexts.clear()
            self.shared_context.clear()
    
    def save_context(self, filepath: str) -> None:
        """
        Save context history to a file.
        
        Args:
            filepath: Path to save the context
        """
        data = {
            'context_history': [e.to_dict() for e in self.context_history],
            'max_context_length': self.max_context_length
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_context(self, filepath: str) -> None:
        """
        Load context history from a file.
        
        Args:
            filepath: Path to load the context from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.max_context_length = data.get('max_context_length', 100000)
        self.context_history.clear()
        self.user_contexts.clear()
        self.shared_context.clear()
        
        for entry_data in data.get('context_history', []):
            entry = ContextEntry(
                user_id=entry_data.get('user_id'),
                role=entry_data['role'],
                content=entry_data['content'],
                modality=entry_data.get('modality', 'text'),
                metadata=entry_data.get('metadata', {}),
                timestamp=datetime.fromisoformat(entry_data['timestamp'])
            )
            self.context_history.append(entry)
            
            if entry.user_id:
                if entry.user_id not in self.user_contexts:
                    self.user_contexts[entry.user_id] = []
                self.user_contexts[entry.user_id].append(entry)
