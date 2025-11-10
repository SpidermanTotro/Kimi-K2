"""Core framework initialization and module management."""

from typing import Optional, Dict, Any
from pathlib import Path
import logging

from kimi_k2.core.config import Config


logger = logging.getLogger(__name__)


class Framework:
    """Main framework class that manages all modules."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the framework with configuration.
        
        Args:
            config: Framework configuration. If None, uses default configuration.
        """
        self.config = config or Config.default()
        self._modules: Dict[str, Any] = {}
        self._initialized = False
        
    def initialize(self) -> None:
        """Initialize all enabled modules."""
        if self._initialized:
            logger.warning("Framework already initialized")
            return
            
        logger.info("Initializing Kimi-K2 Framework v1.0.0")
        
        # Initialize modules based on configuration
        if self.config.animation.enabled:
            self._init_animation_module()
            
        if self.config.commands.enabled:
            self._init_commands_module()
            
        if self.config.models.enabled:
            self._init_models_module()
            
        if self.config.collaboration.enabled:
            self._init_collaboration_module()
            
        self._initialized = True
        logger.info("Framework initialization complete")
        
    def _init_animation_module(self) -> None:
        """Initialize animation suite module."""
        from kimi_k2.animation.suite import AnimationSuite
        self._modules['animation'] = AnimationSuite(self.config.animation)
        logger.info("Animation suite initialized")
        
    def _init_commands_module(self) -> None:
        """Initialize commands module."""
        from kimi_k2.commands.interface import CommandInterface
        self._modules['commands'] = CommandInterface(self.config.commands)
        logger.info("Command interface initialized")
        
    def _init_models_module(self) -> None:
        """Initialize AI models module."""
        from kimi_k2.models.manager import ModelManager
        self._modules['models'] = ModelManager(self.config.models)
        logger.info("Model manager initialized")
        
    def _init_collaboration_module(self) -> None:
        """Initialize collaboration module."""
        from kimi_k2.collaboration.server import CollaborationServer
        self._modules['collaboration'] = CollaborationServer(self.config.collaboration)
        logger.info("Collaboration server initialized")
        
    def get_module(self, name: str) -> Any:
        """Get a module by name.
        
        Args:
            name: Module name (animation, commands, models, collaboration)
            
        Returns:
            The requested module instance
            
        Raises:
            KeyError: If module not found or not enabled
        """
        if not self._initialized:
            raise RuntimeError("Framework not initialized. Call initialize() first.")
            
        if name not in self._modules:
            raise KeyError(f"Module '{name}' not found or not enabled")
            
        return self._modules[name]
    
    def shutdown(self) -> None:
        """Shutdown all modules and cleanup resources."""
        logger.info("Shutting down framework")
        
        for name, module in self._modules.items():
            if hasattr(module, 'shutdown'):
                module.shutdown()
                logger.info(f"Module '{name}' shutdown complete")
                
        self._modules.clear()
        self._initialized = False
        logger.info("Framework shutdown complete")
