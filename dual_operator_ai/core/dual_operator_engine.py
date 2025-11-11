"""
Dual Operator Engine

Main engine that coordinates the entire dual-operator AI system, integrating
all components including user profiles, context management, and decision fusion.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .user_profile import UserProfile
from .context_manager import ContextManager
from .decision_fusion import DecisionFusionEngine, FusionStrategy


class DualOperatorEngine:
    """
    Main engine for the dual-operator AI system.
    
    This class coordinates:
    - User profile management
    - Context aggregation and management
    - Decision fusion
    - AI model integration
    - Audit and transparency features
    """
    
    def __init__(
        self,
        user1_profile: UserProfile,
        user2_profile: UserProfile,
        fusion_strategy: FusionStrategy = FusionStrategy.ADAPTIVE,
        max_context_length: int = 100000
    ):
        """
        Initialize the dual operator engine.
        
        Args:
            user1_profile: Profile for the first user
            user2_profile: Profile for the second user
            fusion_strategy: Strategy for fusing decisions
            max_context_length: Maximum context length to maintain
        """
        self.user1 = user1_profile
        self.user2 = user2_profile
        self.context_manager = ContextManager(max_context_length)
        self.decision_engine = DecisionFusionEngine(fusion_strategy)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.metadata: Dict[str, Any] = {}
        
    def process_input(
        self,
        user_id: str,
        content: Any,
        modality: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process input from a user.
        
        Args:
            user_id: ID of the user providing input
            content: Input content
            modality: Type of input (text, image, audio, etc.)
            metadata: Additional metadata
            
        Returns:
            Processing result dictionary
        """
        # Validate user
        if user_id not in [self.user1.user_id, self.user2.user_id]:
            raise ValueError(f"Unknown user_id: {user_id}")
        
        # Add to context
        self.context_manager.add_context(
            user_id=user_id,
            role="user",
            content=content,
            modality=modality,
            metadata=metadata,
            shared=True
        )
        
        # Update user profile with context
        user_profile = self.user1 if user_id == self.user1.user_id else self.user2
        user_profile.add_context({
            'content': content,
            'modality': modality,
            'metadata': metadata
        })
        
        return {
            'status': 'success',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_response(
        self,
        target_user_id: Optional[str] = None,
        include_both_perspectives: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response considering both users' perspectives.
        
        Args:
            target_user_id: Specific user to generate response for (None for both)
            include_both_perspectives: Whether to include both users' perspectives
            
        Returns:
            Response dictionary with content and metadata
        """
        # Get fused preferences
        fused_preferences = self.decision_engine.fuse_preferences(
            self.user1.preferences,
            self.user2.preferences,
            self.user1.decision_weight,
            self.user2.decision_weight
        )
        
        # Get context for response generation
        if target_user_id:
            context = self.context_manager.get_context_for_user(target_user_id)
        else:
            context = self.context_manager.get_combined_context(
                [self.user1.user_id, self.user2.user_id]
            )
        
        # Format context for LLM
        formatted_context = self.context_manager.format_for_llm(target_user_id)
        
        # Create response metadata
        response = {
            'session_id': self.session_id,
            'fused_preferences': fused_preferences,
            'context_entries': len(context),
            'formatted_messages': formatted_context,
            'timestamp': datetime.now().isoformat(),
            'target_user': target_user_id,
            'perspectives_included': {
                'user1': self.user1.name,
                'user2': self.user2.name
            } if include_both_perspectives else {'user': target_user_id}
        }
        
        # Add to shared context
        self.context_manager.add_context(
            user_id=None,
            role="assistant",
            content=response,
            modality="structured",
            shared=True
        )
        
        return response
    
    def make_collaborative_decision(
        self,
        decision_context: Dict[str, Any],
        user1_input: Optional[Dict[str, Any]] = None,
        user2_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a collaborative decision based on inputs from both users.
        
        Args:
            decision_context: Context for the decision
            user1_input: First user's input/preference for this decision
            user2_input: Second user's input/preference for this decision
            
        Returns:
            Fused decision with audit trail
        """
        decisions = []
        
        if user1_input:
            decisions.append({
                'user_id': self.user1.user_id,
                'content': user1_input,
                'weight': self.user1.decision_weight,
                'expertise': self.user1.strengths,
                'priority': user1_input.get('priority', 1)
            })
        
        if user2_input:
            decisions.append({
                'user_id': self.user2.user_id,
                'content': user2_input,
                'weight': self.user2.decision_weight,
                'expertise': self.user2.strengths,
                'priority': user2_input.get('priority', 1)
            })
        
        # Fuse the decisions
        fused_decision = self.decision_engine.fuse_decisions(
            decisions,
            context=decision_context
        )
        
        # Add metadata
        fused_decision['session_id'] = self.session_id
        fused_decision['timestamp'] = datetime.now().isoformat()
        fused_decision['decision_context'] = decision_context
        
        return fused_decision
    
    def get_audit_trail(self) -> Dict[str, Any]:
        """
        Get comprehensive audit trail of all decisions and interactions.
        
        Returns:
            Audit trail dictionary with all tracked information
        """
        return {
            'session_id': self.session_id,
            'users': {
                'user1': {
                    'id': self.user1.user_id,
                    'name': self.user1.name,
                    'weight': self.user1.decision_weight,
                    'strengths': self.user1.strengths
                },
                'user2': {
                    'id': self.user2.user_id,
                    'name': self.user2.name,
                    'weight': self.user2.decision_weight,
                    'strengths': self.user2.strengths
                }
            },
            'context_summary': self.context_manager.get_context_summary(),
            'decision_history': self.decision_engine.get_decision_audit_trail(),
            'fusion_strategy': self.decision_engine.fusion_strategy.value,
            'metadata': self.metadata
        }
    
    def export_session(self, filepath: str) -> None:
        """
        Export the entire session to a file.
        
        Args:
            filepath: Path to export the session
        """
        session_data = {
            'session_id': self.session_id,
            'user1': self.user1.to_dict(),
            'user2': self.user2.to_dict(),
            'audit_trail': self.get_audit_trail(),
            'metadata': self.metadata,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def get_context_for_llm(
        self,
        user_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get formatted context for LLM API calls.
        
        Args:
            user_id: Optional specific user ID
            system_prompt: Optional system prompt to prepend
            
        Returns:
            List of message dictionaries ready for LLM API
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        else:
            # Default system prompt for dual-operator mode
            messages.append({
                'role': 'system',
                'content': f"You are an AI assistant serving two users: {self.user1.name} and {self.user2.name}. "
                          f"Consider both of their perspectives, preferences, and expertise when responding. "
                          f"{self.user1.name}'s strengths: {', '.join(self.user1.strengths)}. "
                          f"{self.user2.name}'s strengths: {', '.join(self.user2.strengths)}."
            })
        
        # Add conversation context
        context_messages = self.context_manager.format_for_llm(user_id)
        messages.extend(context_messages)
        
        return messages
    
    def update_user_weights(
        self,
        user1_weight: Optional[float] = None,
        user2_weight: Optional[float] = None
    ) -> None:
        """
        Update decision weights for users.
        
        Args:
            user1_weight: New weight for user 1
            user2_weight: New weight for user 2
        """
        if user1_weight is not None:
            self.user1.set_decision_weight(user1_weight)
        if user2_weight is not None:
            self.user2.set_decision_weight(user2_weight)
    
    def get_personalized_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized context view for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Personalized context dictionary
        """
        user_profile = self.user1 if user_id == self.user1.user_id else self.user2
        other_user = self.user2 if user_id == self.user1.user_id else self.user1
        
        return {
            'user': user_profile.to_dict(),
            'partner': {
                'id': other_user.user_id,
                'name': other_user.name,
                'strengths': other_user.strengths
            },
            'context': self.context_manager.get_context_for_user(user_id),
            'shared_context_entries': len(self.context_manager.shared_context)
        }
