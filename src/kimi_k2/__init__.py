"""
Kimi-K2 Linux-style Command System and Forge AI Extension

This package provides:
1. Linux-style command emulation for advanced file management
2. Forge-like AI extension for creative tasks (book writing, NPC dialogue, quest scripting)
"""

__version__ = "0.1.0"
__author__ = "Kimi-K2 Team"

from .linux_commands import CommandSystem
from .forge_ai import ForgeAI

__all__ = ["CommandSystem", "ForgeAI"]
