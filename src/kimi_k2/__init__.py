"""Kimi K2 - Open Agentic Intelligence"""

__version__ = "0.1.0"

from .animation import ClayamationAssistant, AnimationAssistant
from .commands import CommandSystem, ForgeAI
from .models import OptimizedGPT, TransformerModel

__all__ = [
    "ClayamationAssistant",
    "AnimationAssistant",
    "CommandSystem",
    "ForgeAI",
    "OptimizedGPT",
    "TransformerModel",
]
