"""
Personalization Engine
Manages user preferences and customization
"""

from typing import Dict, List, Optional, Any
import json


class PersonalizationEngine:
    """
    Manages user personalization and preferences.
    
    Features:
    - User profile management
    - Preference learning
    - Adaptive responses
    - Custom settings
    """
    
    def __init__(self):
        """Initialize the personalization engine."""
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
    
    def create_profile(
        self,
        user_id: str,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a user profile.
        
        Args:
            user_id: User identifier
            preferences: Optional initial preferences
            
        Returns:
            Profile creation result
        """
        if user_id in self.user_profiles:
            return {
                "status": "error",
                "message": f"Profile for {user_id} already exists"
            }
        
        self.user_profiles[user_id] = {
            "user_id": user_id,
            "preferences": preferences or {},
            "interaction_history": [],
            "learned_preferences": {},
            "custom_settings": {}
        }
        
        return {
            "status": "success",
            "user_id": user_id,
            "profile_created": True
        }
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        merge: bool = True,
    ) -> Dict[str, Any]:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: Preferences to update
            merge: Whether to merge with existing preferences
            
        Returns:
            Update result
        """
        if user_id not in self.user_profiles:
            self.create_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        if merge:
            profile["preferences"].update(preferences)
        else:
            profile["preferences"] = preferences
        
        return {
            "status": "success",
            "user_id": user_id,
            "preferences": profile["preferences"]
        }
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences
        """
        if user_id not in self.user_profiles:
            return {"status": "error", "message": "User profile not found"}
        
        return {
            "status": "success",
            "user_id": user_id,
            "preferences": self.user_profiles[user_id]["preferences"],
            "learned_preferences": self.user_profiles[user_id]["learned_preferences"]
        }
    
    def record_interaction(
        self,
        user_id: str,
        interaction_type: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Record user interaction for learning.
        
        Args:
            user_id: User identifier
            interaction_type: Type of interaction
            data: Interaction data
            
        Returns:
            Recording result
        """
        if user_id not in self.user_profiles:
            self.create_profile(user_id)
        
        profile = self.user_profiles[user_id]
        
        interaction = {
            "type": interaction_type,
            "data": data,
            "timestamp": str(len(profile["interaction_history"]))
        }
        
        profile["interaction_history"].append(interaction)
        
        # Simple preference learning
        self._update_learned_preferences(user_id, interaction_type, data)
        
        return {
            "status": "success",
            "user_id": user_id,
            "interaction_recorded": True
        }
    
    def _update_learned_preferences(
        self,
        user_id: str,
        interaction_type: str,
        data: Dict[str, Any],
    ):
        """
        Update learned preferences based on interactions.
        
        Args:
            user_id: User identifier
            interaction_type: Type of interaction
            data: Interaction data
        """
        profile = self.user_profiles[user_id]
        learned = profile["learned_preferences"]
        
        # Track interaction type frequency
        if "interaction_types" not in learned:
            learned["interaction_types"] = {}
        
        if interaction_type not in learned["interaction_types"]:
            learned["interaction_types"][interaction_type] = 0
        
        learned["interaction_types"][interaction_type] += 1
        
        # Learn from specific data patterns
        if "topics" in data:
            if "preferred_topics" not in learned:
                learned["preferred_topics"] = {}
            
            for topic in data["topics"]:
                if topic not in learned["preferred_topics"]:
                    learned["preferred_topics"][topic] = 0
                learned["preferred_topics"][topic] += 1
    
    def get_adaptive_settings(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get adaptive settings based on user profile and context.
        
        Args:
            user_id: User identifier
            context: Optional context information
            
        Returns:
            Adaptive settings
        """
        if user_id not in self.user_profiles:
            return {
                "status": "error",
                "message": "User profile not found"
            }
        
        profile = self.user_profiles[user_id]
        settings = {
            **profile["preferences"],
            **profile["custom_settings"]
        }
        
        # Add learned preferences
        if profile["learned_preferences"]:
            settings["learned"] = profile["learned_preferences"]
        
        return {
            "status": "success",
            "user_id": user_id,
            "settings": settings,
            "interaction_count": len(profile["interaction_history"])
        }
    
    def set_custom_setting(
        self,
        user_id: str,
        setting_name: str,
        setting_value: Any,
    ) -> Dict[str, Any]:
        """
        Set a custom setting for a user.
        
        Args:
            user_id: User identifier
            setting_name: Setting name
            setting_value: Setting value
            
        Returns:
            Operation result
        """
        if user_id not in self.user_profiles:
            self.create_profile(user_id)
        
        profile = self.user_profiles[user_id]
        profile["custom_settings"][setting_name] = setting_value
        
        return {
            "status": "success",
            "user_id": user_id,
            "setting": setting_name,
            "value": setting_value
        }
    
    def export_profile(self, user_id: str) -> Optional[str]:
        """
        Export user profile as JSON.
        
        Args:
            user_id: User identifier
            
        Returns:
            JSON string of profile data
        """
        if user_id not in self.user_profiles:
            return None
        
        return json.dumps(self.user_profiles[user_id], indent=2)
    
    def import_profile(self, user_id: str, profile_json: str) -> Dict[str, Any]:
        """
        Import user profile from JSON.
        
        Args:
            user_id: User identifier
            profile_json: JSON string of profile data
            
        Returns:
            Import result
        """
        try:
            profile_data = json.loads(profile_json)
            self.user_profiles[user_id] = profile_data
            
            return {
                "status": "success",
                "user_id": user_id,
                "imported": True
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"Invalid JSON: {str(e)}"
            }
