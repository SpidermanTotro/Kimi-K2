#!/usr/bin/env python3
"""
Plugin Loader for Kimi K2

This module provides the core functionality for loading and managing
plugins in the Kimi K2 system.
"""

import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Plugin:
    """Base class for all Kimi K2 plugins."""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """Initialize the plugin.
        
        Args:
            name: Plugin name
            config: Plugin configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.enabled = True
        
    def initialize(self) -> bool:
        """Initialize the plugin.
        
        Returns:
            True if initialization successful, False otherwise
        """
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main functionality.
        
        Returns:
            Plugin execution result
        """
        raise NotImplementedError("Plugin must implement execute method")
    
    def cleanup(self):
        """Cleanup plugin resources."""
        pass
    
    def get_info(self) -> Dict:
        """Get plugin information.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {
            "name": self.name,
            "enabled": self.enabled,
            "config": self.config
        }


class PluginLoader:
    """Plugin loader and manager for Kimi K2."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        """Initialize the plugin loader.
        
        Args:
            plugin_dir: Directory containing plugins
        """
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_registry: Dict[str, Dict] = {}
        self._load_registry()
        
    def _load_registry(self):
        """Load the plugin registry."""
        registry_path = self.plugin_dir / "core" / "registry.json"
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                self.plugin_registry = json.load(f)
    
    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Plugin instance if successful, None otherwise
        """
        if plugin_name in self.plugins:
            logger.info(f"Plugin {plugin_name} already loaded")
            return self.plugins[plugin_name]
        
        # Check if plugin is in registry
        if plugin_name not in self.plugin_registry:
            logger.error(f"Plugin {plugin_name} not found in registry")
            return None
        
        plugin_info = self.plugin_registry[plugin_name]
        plugin_path = self.plugin_dir / plugin_info.get("path", "")
        
        if not plugin_path.exists():
            logger.error(f"Plugin path {plugin_path} does not exist")
            return None
        
        try:
            # Load plugin module
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                plugin_path / "__init__.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Create plugin instance
                plugin_class = getattr(module, plugin_info.get("class", "Plugin"))
                plugin = plugin_class(
                    name=plugin_name,
                    config=plugin_info.get("config", {})
                )
                
                # Initialize plugin
                if plugin.initialize():
                    self.plugins[plugin_name] = plugin
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                    return plugin
                else:
                    logger.error(f"Failed to initialize plugin: {plugin_name}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            return None
    
    def unload_plugin(self, plugin_name: str):
        """Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
        """
        if plugin_name in self.plugins:
            self.plugins[plugin_name].cleanup()
            del self.plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
    
    def list_plugins(self) -> List[str]:
        """List all available plugins.
        
        Returns:
            List of plugin names
        """
        return list(self.plugin_registry.keys())
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self.plugins.get(plugin_name)
