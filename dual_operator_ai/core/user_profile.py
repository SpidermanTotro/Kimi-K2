"""
User Profile Module

Manages individual user profiles, preferences, and characteristics for the dual-operator AI system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class UserProfile:
    """
    Represents an individual user's profile with preferences and characteristics.
    
    Attributes:
        user_id: Unique identifier for the user
        name: User's display name
        preferences: Dictionary of user preferences
        strengths: List of user's strengths and expertise areas
        communication_style: Preferred communication style
        decision_weight: Weight given to this user's preferences (0.0 to 1.0)
        context_history: Historical context from this user's interactions
        created_at: Timestamp when profile was created
        updated_at: Timestamp of last profile update
    """
    
    user_id: str
    name: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    communication_style: str = "balanced"
    decision_weight: float = 0.5
    context_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_preferences(self, new_preferences: Dict[str, Any]) -> None:
        """
        Update user preferences with new values.
        
        Args:
            new_preferences: Dictionary of preference updates
        """
        self.preferences.update(new_preferences)
        self.updated_at = datetime.now()
    
    def add_strength(self, strength: str) -> None:
        """
        Add a strength or expertise area to the user's profile.
        
        Args:
            strength: Description of the strength to add
        """
        if strength not in self.strengths:
            self.strengths.append(strength)
            self.updated_at = datetime.now()
    
    def add_context(self, context: Dict[str, Any]) -> None:
        """
        Add a context entry to the user's interaction history.
        
        Args:
            context: Context dictionary with interaction information
        """
        context['timestamp'] = datetime.now().isoformat()
        self.context_history.append(context)
        self.updated_at = datetime.now()
        
        # Keep only the last 100 context entries to manage memory
        if len(self.context_history) > 100:
            self.context_history = self.context_history[-100:]
    
    def set_decision_weight(self, weight: float) -> None:
        """
        Set the decision weight for this user.
        
        Args:
            weight: Weight value between 0.0 and 1.0
            
        Raises:
            ValueError: If weight is not between 0.0 and 1.0
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Decision weight must be between 0.0 and 1.0")
        self.decision_weight = weight
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user profile to dictionary format.
        
        Returns:
            Dictionary representation of the user profile
        """
        return {
            'user_id': self.user_id,
            'name': self.name,
            'preferences': self.preferences,
            'strengths': self.strengths,
            'communication_style': self.communication_style,
            'decision_weight': self.decision_weight,
            'context_history': self.context_history,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """
        Create a UserProfile instance from a dictionary.
        
        Args:
            data: Dictionary containing user profile data
            
        Returns:
            UserProfile instance
        """
        profile = cls(
            user_id=data['user_id'],
            name=data['name'],
            preferences=data.get('preferences', {}),
            strengths=data.get('strengths', []),
            communication_style=data.get('communication_style', 'balanced'),
            decision_weight=data.get('decision_weight', 0.5),
            context_history=data.get('context_history', [])
        )
        
        if 'created_at' in data:
            profile.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            profile.updated_at = datetime.fromisoformat(data['updated_at'])
            
        return profile
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save user profile to a JSON file.
        
        Args:
            filepath: Path to the file where profile should be saved
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'UserProfile':
        """
        Load user profile from a JSON file.
        
        Args:
            filepath: Path to the file containing the profile
            
        Returns:
            UserProfile instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
