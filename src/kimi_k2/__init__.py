"""Kimi-K2 Unified Framework - Core package initialization."""

__version__ = "1.0.0"
__author__ = "Kimi Team"
__description__ = "Unified AI Framework for Animation, Commands, and GPT Models"

from kimi_k2.core.framework import Framework
from kimi_k2.core.config import Config

__all__ = ["Framework", "Config", "__version__"]
