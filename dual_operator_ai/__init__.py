"""
Dual Operator AI System

A modular framework for combining the functionalities and perspectives of multiple users
into a cohesive, dynamic AI system. This system enables two operators to interact with
a single AI entity that adapts to both their preferences and decision-making styles.
"""

__version__ = "1.0.0"

from .core.dual_operator_engine import DualOperatorEngine
from .core.user_profile import UserProfile
from .core.context_manager import ContextManager
from .core.decision_fusion import DecisionFusionEngine

__all__ = [
    "DualOperatorEngine",
    "UserProfile",
    "ContextManager",
    "DecisionFusionEngine",
]
