#!/usr/bin/env python3
"""
Memory Manager for Kimi K2

This module provides memory management capabilities for handling
long-context conversations and user personalization.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages conversation memory and user profiles for Kimi K2."""
    
    def __init__(self, backend: str = 'file', config_path: Optional[str] = None):
        """Initialize the memory manager.
        
        Args:
            backend: Storage backend ('file', 'database', 'redis')
            config_path: Path to configuration file
        """
        self.backend = backend
        self.config = self._load_config(config_path)
        self.storage_path = Path(self.config.get('storage', {}).get('path', './data/memory'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'storage': {'path': './data/memory', 'max_history': 1000},
            'personalization': {'enabled': True}
        }
    
    def store_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Store a conversation message.
        
        Args:
            user_id: User identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)
        
        history_file = user_dir / 'history.json'
        
        # Load existing history
        history = []
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        
        # Add new message
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        history.append(message)
        
        # Apply max history limit
        max_history = self.config.get('storage', {}).get('max_history', 1000)
        if len(history) > max_history:
            history = history[-max_history:]
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_history(
        self,
        user_id: str,
        limit: Optional[int] = None,
        since: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve conversation history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages to retrieve
            since: ISO timestamp to filter messages after
            
        Returns:
            List of messages
        """
        history_file = self.storage_path / user_id / 'history.json'
        
        if not history_file.exists():
            return []
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        # Filter by timestamp if provided
        if since:
            history = [
                msg for msg in history
                if msg['timestamp'] >= since
            ]
        
        # Apply limit
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_profile(self, user_id: str) -> Dict:
        """Get user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary
        """
        profile_file = self.storage_path / user_id / 'profile.json'
        
        if not profile_file.exists():
            return self._create_default_profile(user_id)
        
        with open(profile_file, 'r') as f:
            return json.load(f)
    
    def _create_default_profile(self, user_id: str) -> Dict:
        """Create a default user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Default profile dictionary
        """
        profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'preferences': {
                'language': 'en',
                'expertise_level': 'intermediate',
                'preferred_format': 'balanced',
                'interests': []
            },
            'stats': {
                'total_messages': 0,
                'last_active': datetime.now().isoformat()
            }
        }
        
        # Save profile directly without calling update_profile to avoid recursion
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)
        
        profile_file = user_dir / 'profile.json'
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        return profile
    
    def update_profile(self, user_id: str, profile_updates: Dict):
        """Update user profile.
        
        Args:
            user_id: User identifier
            profile_updates: Dictionary of profile updates
        """
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)
        
        profile_file = user_dir / 'profile.json'
        
        # Load existing profile or create new one
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                profile = json.load(f)
        else:
            profile = self._create_default_profile(user_id)
        
        # Update profile with new values
        profile.update(profile_updates)
        profile['updated_at'] = datetime.now().isoformat()
        
        # Save updated profile
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def get_personalized_context(self, user_id: str) -> Dict:
        """Get personalized context for the user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Personalized context dictionary
        """
        profile = self.get_profile(user_id)
        history = self.get_history(user_id, limit=10)
        
        return {
            'profile': profile,
            'recent_history': history,
            'context_summary': self._generate_context_summary(history),
            'personalization_hints': self._generate_hints(profile)
        }
    
    def _generate_context_summary(self, history: List[Dict]) -> str:
        """Generate a summary of conversation context.
        
        Args:
            history: Conversation history
            
        Returns:
            Summary string
        """
        # Simple summary - in production, use a summarization model
        if not history:
            return "No previous conversation history."
        
        recent_topics = []
        for msg in history[-5:]:
            if msg['role'] == 'user':
                # Extract first sentence or first 50 chars
                content = msg['content']
                summary = content.split('.')[0][:50]
                recent_topics.append(summary)
        
        return f"Recent topics: {', '.join(recent_topics)}"
    
    def _generate_hints(self, profile: Dict) -> List[str]:
        """Generate personalization hints based on profile.
        
        Args:
            profile: User profile
            
        Returns:
            List of personalization hints
        """
        hints = []
        prefs = profile.get('preferences', {})
        
        if prefs.get('expertise_level') == 'expert':
            hints.append("Use technical language and skip basic explanations")
        elif prefs.get('expertise_level') == 'beginner':
            hints.append("Provide detailed explanations and examples")
        
        if prefs.get('preferred_format') == 'concise':
            hints.append("Keep responses brief and to the point")
        elif prefs.get('preferred_format') == 'detailed':
            hints.append("Provide comprehensive, detailed responses")
        
        interests = prefs.get('interests', [])
        if interests:
            hints.append(f"User is interested in: {', '.join(interests)}")
        
        return hints
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user.
        
        Args:
            user_id: User identifier
        """
        history_file = self.storage_path / user_id / 'history.json'
        if history_file.exists():
            history_file.unlink()
