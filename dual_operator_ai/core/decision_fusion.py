"""
Decision Fusion Engine Module

Merges decision-making processes from multiple users based on their preferences,
strengths, and configured weights.
"""

from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json


class FusionStrategy(Enum):
    """Strategies for fusing decisions from multiple users."""
    WEIGHTED_AVERAGE = "weighted_average"
    CONSENSUS = "consensus"
    EXPERTISE_BASED = "expertise_based"
    ADAPTIVE = "adaptive"
    PRIORITIZED = "prioritized"


class DecisionFusionEngine:
    """
    Fuses decision-making processes from multiple users.
    
    This engine combines inputs, preferences, and decisions from multiple users
    to produce a unified output that respects both users' perspectives.
    """
    
    def __init__(self, fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE):
        """
        Initialize the decision fusion engine.
        
        Args:
            fusion_strategy: Strategy to use for fusing decisions
        """
        self.fusion_strategy = fusion_strategy
        self.decision_history: List[Dict[str, Any]] = []
        self.custom_fusion_functions: Dict[str, Callable] = {}
        
    def fuse_preferences(
        self,
        user1_prefs: Dict[str, Any],
        user2_prefs: Dict[str, Any],
        user1_weight: float = 0.5,
        user2_weight: float = 0.5
    ) -> Dict[str, Any]:
        """
        Fuse preferences from two users.
        
        Args:
            user1_prefs: First user's preferences
            user2_prefs: Second user's preferences
            user1_weight: Weight for first user (0.0 to 1.0)
            user2_weight: Weight for second user (0.0 to 1.0)
            
        Returns:
            Fused preferences dictionary
        """
        fused = {}
        all_keys = set(user1_prefs.keys()) | set(user2_prefs.keys())
        
        for key in all_keys:
            val1 = user1_prefs.get(key)
            val2 = user2_prefs.get(key)
            
            if val1 is None:
                fused[key] = val2
            elif val2 is None:
                fused[key] = val1
            else:
                # Handle different types of preferences
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Numeric values: weighted average
                    fused[key] = val1 * user1_weight + val2 * user2_weight
                elif isinstance(val1, bool) and isinstance(val2, bool):
                    # Boolean values: use weighted decision
                    fused[key] = (val1 * user1_weight + val2 * user2_weight) >= 0.5
                elif isinstance(val1, str) and isinstance(val2, str):
                    # String values: combine or choose based on weight
                    if val1 == val2:
                        fused[key] = val1
                    else:
                        fused[key] = val1 if user1_weight >= user2_weight else val2
                elif isinstance(val1, list) and isinstance(val2, list):
                    # List values: merge unique items
                    fused[key] = list(set(val1 + val2))
                elif isinstance(val1, dict) and isinstance(val2, dict):
                    # Nested dictionaries: recursive fusion
                    fused[key] = self.fuse_preferences(val1, val2, user1_weight, user2_weight)
                else:
                    # Default: prefer higher weighted user
                    fused[key] = val1 if user1_weight >= user2_weight else val2
        
        return fused
    
    def fuse_decisions(
        self,
        decisions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fuse multiple decisions based on the configured strategy.
        
        Args:
            decisions: List of decision dictionaries from different users
            context: Optional context for the decision
            
        Returns:
            Fused decision dictionary
        """
        if not decisions:
            return {}
        
        if len(decisions) == 1:
            return decisions[0]
        
        fused_decision = {}
        
        if self.fusion_strategy == FusionStrategy.WEIGHTED_AVERAGE:
            fused_decision = self._weighted_average_fusion(decisions)
        elif self.fusion_strategy == FusionStrategy.CONSENSUS:
            fused_decision = self._consensus_fusion(decisions)
        elif self.fusion_strategy == FusionStrategy.EXPERTISE_BASED:
            fused_decision = self._expertise_based_fusion(decisions, context)
        elif self.fusion_strategy == FusionStrategy.ADAPTIVE:
            fused_decision = self._adaptive_fusion(decisions, context)
        elif self.fusion_strategy == FusionStrategy.PRIORITIZED:
            fused_decision = self._prioritized_fusion(decisions)
        
        # Record decision in history
        self.decision_history.append({
            'decisions': decisions,
            'fused_decision': fused_decision,
            'strategy': self.fusion_strategy.value,
            'context': context
        })
        
        return fused_decision
    
    def _weighted_average_fusion(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fuse decisions using weighted average approach.
        
        Args:
            decisions: List of decisions with 'weight' and 'content' keys
            
        Returns:
            Fused decision
        """
        total_weight = sum(d.get('weight', 1.0) for d in decisions)
        fused = {'content': {}, 'weights_used': {}}
        
        # Collect all unique keys
        all_keys = set()
        for decision in decisions:
            if 'content' in decision:
                all_keys.update(decision['content'].keys())
        
        # Fuse each key
        for key in all_keys:
            values = []
            weights = []
            for decision in decisions:
                if 'content' in decision and key in decision['content']:
                    values.append(decision['content'][key])
                    weights.append(decision.get('weight', 1.0))
            
            if values:
                if all(isinstance(v, (int, float)) for v in values):
                    # Numeric: weighted average
                    fused['content'][key] = sum(v * w for v, w in zip(values, weights)) / sum(weights)
                else:
                    # Non-numeric: choose by highest weight
                    max_weight_idx = weights.index(max(weights))
                    fused['content'][key] = values[max_weight_idx]
        
        return fused
    
    def _consensus_fusion(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fuse decisions requiring consensus (agreement between users).
        
        Args:
            decisions: List of decisions
            
        Returns:
            Fused decision with consensus items
        """
        if not decisions:
            return {'content': {}, 'consensus_level': 0.0}
        
        fused = {'content': {}, 'consensus_items': [], 'divergent_items': []}
        
        # Find common keys
        common_keys = set(decisions[0].get('content', {}).keys())
        for decision in decisions[1:]:
            common_keys &= set(decision.get('content', {}).keys())
        
        consensus_count = 0
        for key in common_keys:
            values = [d['content'][key] for d in decisions if 'content' in d and key in d['content']]
            
            # Check if all values are the same
            if len(set(str(v) for v in values)) == 1:
                fused['content'][key] = values[0]
                fused['consensus_items'].append(key)
                consensus_count += 1
            else:
                fused['divergent_items'].append({
                    'key': key,
                    'values': values
                })
        
        fused['consensus_level'] = consensus_count / max(len(common_keys), 1)
        return fused
    
    def _expertise_based_fusion(
        self,
        decisions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fuse decisions based on user expertise in the relevant domain.
        
        Args:
            decisions: List of decisions with 'expertise' field
            context: Context containing domain information
            
        Returns:
            Fused decision favoring expert opinions
        """
        domain = context.get('domain', 'general') if context else 'general'
        fused = {'content': {}, 'expert_contributions': {}}
        
        # Assign expertise scores
        for decision in decisions:
            user_id = decision.get('user_id', 'unknown')
            expertise_areas = decision.get('expertise', [])
            
            # Calculate expertise score for this domain
            expertise_score = 1.0  # Default
            if domain in expertise_areas:
                expertise_score = 2.0
            elif any(domain in area for area in expertise_areas):
                expertise_score = 1.5
            
            decision['expertise_score'] = expertise_score
        
        # Fuse based on expertise
        all_keys = set()
        for decision in decisions:
            if 'content' in decision:
                all_keys.update(decision['content'].keys())
        
        for key in all_keys:
            best_score = 0
            best_value = None
            expert_user = None
            
            for decision in decisions:
                if 'content' in decision and key in decision['content']:
                    score = decision.get('expertise_score', 1.0)
                    if score > best_score:
                        best_score = score
                        best_value = decision['content'][key]
                        expert_user = decision.get('user_id', 'unknown')
            
            if best_value is not None:
                fused['content'][key] = best_value
                fused['expert_contributions'][key] = expert_user
        
        return fused
    
    def _adaptive_fusion(
        self,
        decisions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adaptively fuse decisions based on context and past performance.
        
        Args:
            decisions: List of decisions
            context: Context for adaptation
            
        Returns:
            Adaptively fused decision
        """
        # Use historical performance to adjust weights
        fused = {'content': {}, 'adaptation_info': {}}
        
        # For now, use a combination of weighted and expertise-based
        # In a full implementation, this would learn from feedback
        weighted_result = self._weighted_average_fusion(decisions)
        expertise_result = self._expertise_based_fusion(decisions, context)
        
        # Blend results
        fused['content'] = weighted_result.get('content', {})
        
        # Override with expertise-based where confidence is high
        for key, value in expertise_result.get('content', {}).items():
            if key in expertise_result.get('expert_contributions', {}):
                fused['content'][key] = value
        
        return fused
    
    def _prioritized_fusion(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fuse decisions based on explicit priorities.
        
        Args:
            decisions: List of decisions with 'priority' field
            
        Returns:
            Fused decision favoring higher priority items
        """
        # Sort by priority
        sorted_decisions = sorted(
            decisions,
            key=lambda d: d.get('priority', 0),
            reverse=True
        )
        
        fused = {'content': {}, 'priority_order': []}
        
        for decision in sorted_decisions:
            user_id = decision.get('user_id', 'unknown')
            priority = decision.get('priority', 0)
            
            if 'content' in decision:
                # Add content, with higher priority overwriting lower
                for key, value in decision['content'].items():
                    if key not in fused['content']:
                        fused['content'][key] = value
                        fused['priority_order'].append({
                            'key': key,
                            'user_id': user_id,
                            'priority': priority
                        })
        
        return fused
    
    def register_custom_fusion(self, name: str, fusion_func: Callable) -> None:
        """
        Register a custom fusion function.
        
        Args:
            name: Name for the custom fusion strategy
            fusion_func: Function that takes decisions list and returns fused decision
        """
        self.custom_fusion_functions[name] = fusion_func
    
    def apply_custom_fusion(
        self,
        name: str,
        decisions: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply a registered custom fusion function.
        
        Args:
            name: Name of the custom fusion strategy
            decisions: List of decisions to fuse
            **kwargs: Additional arguments for the fusion function
            
        Returns:
            Fused decision
            
        Raises:
            ValueError: If fusion function is not registered
        """
        if name not in self.custom_fusion_functions:
            raise ValueError(f"Custom fusion function '{name}' not registered")
        
        return self.custom_fusion_functions[name](decisions, **kwargs)
    
    def get_decision_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Get the audit trail of all decisions made.
        
        Returns:
            List of decision records
        """
        return self.decision_history
    
    def clear_decision_history(self) -> None:
        """Clear the decision history."""
        self.decision_history.clear()
