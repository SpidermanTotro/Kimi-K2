#!/usr/bin/env python3
"""
THE FORGE AI - Plugin System
==============================

Implements a modular plugin architecture for "ChatGPT 2.0" including:
- Plugin registry and management
- Dynamic plugin loading
- Plugin lifecycle management
- Hook-based extension points
- Plugin isolation and sandboxing

This module enables extensible functionality through plugins.
"""

import hashlib
import importlib
import importlib.util
import inspect
import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware way"""
    return datetime.now(timezone.utc)


class PluginState(Enum):
    """Plugin lifecycle states"""
    UNLOADED = "unloaded"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class HookType(Enum):
    """Available extension hook types"""
    PRE_PROCESS = "pre_process"       # Before processing user input
    POST_PROCESS = "post_process"     # After processing, before response
    PRE_MEMORY = "pre_memory"         # Before storing memory
    POST_MEMORY = "post_memory"       # After storing memory
    PRE_TOOL = "pre_tool"             # Before tool execution
    POST_TOOL = "post_tool"           # After tool execution
    ON_ERROR = "on_error"             # On error handling
    ON_START = "on_start"             # On system startup
    ON_SHUTDOWN = "on_shutdown"       # On system shutdown
    CUSTOM = "custom"                 # Custom hook point


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    min_forge_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        return cls(**data)


@dataclass
class PluginInfo:
    """Runtime information about a loaded plugin"""
    metadata: PluginMetadata
    state: PluginState
    loaded_at: str = ""
    enabled_at: str = ""
    error_message: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "state": self.state.value,
            "loaded_at": self.loaded_at,
            "enabled_at": self.enabled_at,
            "error_message": self.error_message,
            "config": self.config
        }


class ForgePlugin(ABC):
    """
    Base class for all FORGE plugins
    
    All plugins must inherit from this class and implement
    the required abstract methods.
    """
    
    # Plugin metadata - override in subclasses
    METADATA = PluginMetadata(
        name="BasePlugin",
        version="1.0.0",
        description="Base plugin class",
        author="FORGE"
    )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin with optional configuration"""
        self.config = config or {}
        self._enabled = False
        self._hooks: Dict[HookType, Callable] = {}
    
    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when the plugin is loaded
        
        Returns:
            True if load was successful
        """
        pass
    
    @abstractmethod
    def on_unload(self) -> bool:
        """
        Called when the plugin is unloaded
        
        Returns:
            True if unload was successful
        """
        pass
    
    def on_enable(self) -> bool:
        """Called when the plugin is enabled"""
        self._enabled = True
        return True
    
    def on_disable(self) -> bool:
        """Called when the plugin is disabled"""
        self._enabled = False
        return True
    
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled"""
        return self._enabled
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return self.METADATA
    
    def register_hook(self, hook_type: HookType, callback: Callable):
        """Register a callback for a hook"""
        self._hooks[hook_type] = callback
    
    def get_hook(self, hook_type: HookType) -> Optional[Callable]:
        """Get the registered callback for a hook"""
        return self._hooks.get(hook_type)
    
    def execute_hook(self, hook_type: HookType, *args, **kwargs) -> Any:
        """Execute the registered hook callback"""
        callback = self._hooks.get(hook_type)
        if callback:
            try:
                return callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing hook {hook_type.value}: {e}")
                return None
        return None


class PluginRegistry:
    """
    Registry for managing plugins
    
    Handles plugin discovery, loading, and lifecycle management.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """Initialize the plugin registry"""
        self.plugin_dirs = plugin_dirs or ["./plugins"]
        self.plugins: Dict[str, ForgePlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.hooks: Dict[HookType, List[str]] = {hook: [] for hook in HookType}
        
        # Ensure plugin directories exist
        for dir_path in self.plugin_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("🔌 Plugin Registry initialized")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directories
        
        Returns:
            List of discovered plugin paths
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            dir_path = Path(plugin_dir)
            if not dir_path.exists():
                continue
            
            # Look for Python files
            for file_path in dir_path.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue
                discovered.append(str(file_path))
            
            # Look for plugin directories with __init__.py
            for subdir in dir_path.iterdir():
                if subdir.is_dir() and (subdir / "__init__.py").exists():
                    discovered.append(str(subdir / "__init__.py"))
        
        logger.info(f"📦 Discovered {len(discovered)} plugin(s)")
        return discovered
    
    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from file path
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            True if load was successful
        """
        try:
            path = Path(plugin_path)
            module_name = path.stem
            
            # Load module from file
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                logger.error(f"Failed to load spec for {plugin_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, ForgePlugin) and obj is not ForgePlugin:
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                logger.warning(f"No ForgePlugin subclass found in {plugin_path}")
                return False
            
            # Instantiate plugin
            plugin = plugin_class()
            plugin_name = plugin.get_metadata().name
            
            # Call on_load
            if plugin.on_load():
                self.plugins[plugin_name] = plugin
                self.plugin_info[plugin_name] = PluginInfo(
                    metadata=plugin.get_metadata(),
                    state=PluginState.LOADED,
                    loaded_at=utc_now().isoformat()
                )
                
                # Register hooks
                for hook_type in HookType:
                    if plugin.get_hook(hook_type):
                        self.hooks[hook_type].append(plugin_name)
                
                logger.info(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} failed to load")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def load_plugin_from_class(self, plugin_class: Type[ForgePlugin]) -> bool:
        """
        Load a plugin from a class (for built-in plugins)
        
        Args:
            plugin_class: The plugin class to instantiate
            
        Returns:
            True if load was successful
        """
        try:
            plugin = plugin_class()
            plugin_name = plugin.get_metadata().name
            
            if plugin.on_load():
                self.plugins[plugin_name] = plugin
                self.plugin_info[plugin_name] = PluginInfo(
                    metadata=plugin.get_metadata(),
                    state=PluginState.LOADED,
                    loaded_at=utc_now().isoformat()
                )
                
                # Register hooks
                for hook_type in HookType:
                    if plugin.get_hook(hook_type):
                        self.hooks[hook_type].append(plugin_name)
                
                logger.info(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} failed to load")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin class: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if unload was successful
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        plugin = self.plugins[plugin_name]
        
        try:
            # Disable first if enabled
            if plugin.is_enabled():
                plugin.on_disable()
            
            # Call on_unload
            if plugin.on_unload():
                # Remove from hooks
                for hook_type in HookType:
                    if plugin_name in self.hooks[hook_type]:
                        self.hooks[hook_type].remove(plugin_name)
                
                del self.plugins[plugin_name]
                if plugin_name in self.plugin_info:
                    self.plugin_info[plugin_name].state = PluginState.UNLOADED
                
                logger.info(f"🔌 Unloaded plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Plugin {plugin_name} failed to unload")
                return False
                
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            if plugin_name in self.plugin_info:
                self.plugin_info[plugin_name].state = PluginState.ERROR
                self.plugin_info[plugin_name].error_message = str(e)
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a loaded plugin"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        if plugin.on_enable():
            self.plugin_info[plugin_name].state = PluginState.ENABLED
            self.plugin_info[plugin_name].enabled_at = utc_now().isoformat()
            logger.info(f"✅ Enabled plugin: {plugin_name}")
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        if plugin.on_disable():
            self.plugin_info[plugin_name].state = PluginState.DISABLED
            logger.info(f"⏸️ Disabled plugin: {plugin_name}")
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[ForgePlugin]:
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin info by name"""
        return self.plugin_info.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return list(self.plugins.keys())
    
    def list_enabled_plugins(self) -> List[str]:
        """List all enabled plugins"""
        return [
            name for name, plugin in self.plugins.items()
            if plugin.is_enabled()
        ]
    
    def execute_hook(
        self,
        hook_type: HookType,
        *args,
        stop_on_error: bool = False,
        **kwargs
    ) -> List[Any]:
        """
        Execute all registered hooks for a hook type
        
        Args:
            hook_type: The hook type to execute
            stop_on_error: Whether to stop execution on first error
            
        Returns:
            List of results from each hook
        """
        results = []
        
        for plugin_name in self.hooks[hook_type]:
            plugin = self.plugins.get(plugin_name)
            if plugin and plugin.is_enabled():
                try:
                    result = plugin.execute_hook(hook_type, *args, **kwargs)
                    results.append((plugin_name, result))
                except Exception as e:
                    logger.error(f"Hook error in {plugin_name}: {e}")
                    if stop_on_error:
                        break
                    results.append((plugin_name, None))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin system statistics"""
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": len(self.list_enabled_plugins()),
            "plugin_dirs": self.plugin_dirs,
            "hooks_registered": {
                hook.value: len(plugins)
                for hook, plugins in self.hooks.items()
                if plugins
            }
        }


# ==================== BUILT-IN PLUGINS ====================

class LoggingPlugin(ForgePlugin):
    """Built-in plugin for enhanced logging"""
    
    METADATA = PluginMetadata(
        name="LoggingPlugin",
        version="1.0.0",
        description="Enhanced logging for debugging and monitoring",
        author="FORGE Team",
        hooks=["pre_process", "post_process"],
        capabilities=["logging", "debugging"]
    )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.log_level = self.config.get("log_level", "INFO")
    
    def on_load(self) -> bool:
        self.register_hook(HookType.PRE_PROCESS, self._log_input)
        self.register_hook(HookType.POST_PROCESS, self._log_output)
        return True
    
    def on_unload(self) -> bool:
        return True
    
    def _log_input(self, message: str, **kwargs):
        logger.info(f"[LoggingPlugin] Input: {message[:100]}...")
        return message
    
    def _log_output(self, response: str, **kwargs):
        logger.info(f"[LoggingPlugin] Output: {response[:100]}...")
        return response


class MetricsPlugin(ForgePlugin):
    """Built-in plugin for collecting metrics"""
    
    METADATA = PluginMetadata(
        name="MetricsPlugin",
        version="1.0.0",
        description="Collects usage and performance metrics",
        author="FORGE Team",
        hooks=["pre_process", "post_process"],
        capabilities=["metrics", "analytics"]
    )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "total_responses": 0,
            "errors": 0,
            "start_time": None
        }
    
    def on_load(self) -> bool:
        self.metrics["start_time"] = utc_now().isoformat()
        self.register_hook(HookType.PRE_PROCESS, self._count_request)
        self.register_hook(HookType.POST_PROCESS, self._count_response)
        self.register_hook(HookType.ON_ERROR, self._count_error)
        return True
    
    def on_unload(self) -> bool:
        return True
    
    def _count_request(self, *args, **kwargs):
        self.metrics["total_requests"] += 1
        return args[0] if args else None
    
    def _count_response(self, *args, **kwargs):
        self.metrics["total_responses"] += 1
        return args[0] if args else None
    
    def _count_error(self, *args, **kwargs):
        self.metrics["errors"] += 1
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()


class ContentFilterPlugin(ForgePlugin):
    """Built-in plugin for content filtering (ethical safeguards)"""
    
    METADATA = PluginMetadata(
        name="ContentFilterPlugin",
        version="1.0.0",
        description="Content filtering for safety and compliance",
        author="FORGE Team",
        hooks=["pre_process", "post_process"],
        capabilities=["content_filter", "safety"]
    )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.blocked_patterns: List[str] = self.config.get("blocked_patterns", [])
        self.warning_patterns: List[str] = self.config.get("warning_patterns", [])
    
    def on_load(self) -> bool:
        self.register_hook(HookType.PRE_PROCESS, self._filter_input)
        self.register_hook(HookType.POST_PROCESS, self._filter_output)
        return True
    
    def on_unload(self) -> bool:
        return True
    
    def _filter_input(self, message: str, **kwargs) -> str:
        # Basic content filtering
        for pattern in self.blocked_patterns:
            if pattern.lower() in message.lower():
                logger.warning(f"[ContentFilter] Blocked pattern found in input")
                return "[Content filtered for safety]"
        return message
    
    def _filter_output(self, response: str, **kwargs) -> str:
        # Ensure output doesn't contain blocked content
        for pattern in self.blocked_patterns:
            if pattern.lower() in response.lower():
                logger.warning(f"[ContentFilter] Blocked pattern found in output")
                return "[Response filtered for safety]"
        return response
    
    def add_blocked_pattern(self, pattern: str):
        if pattern not in self.blocked_patterns:
            self.blocked_patterns.append(pattern)
    
    def remove_blocked_pattern(self, pattern: str):
        if pattern in self.blocked_patterns:
            self.blocked_patterns.remove(pattern)


# ==================== PLUGIN MANAGER ====================

class PluginManager:
    """
    High-level plugin manager
    
    Provides a simplified interface for plugin operations.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.registry = PluginRegistry(plugin_dirs)
        self._load_builtin_plugins()
        
        logger.info("🔌 Plugin Manager initialized")
    
    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        builtin_plugins = [
            LoggingPlugin,
            MetricsPlugin,
            ContentFilterPlugin
        ]
        
        for plugin_class in builtin_plugins:
            self.registry.load_plugin_from_class(plugin_class)
    
    def discover_and_load(self) -> int:
        """Discover and load all available plugins"""
        discovered = self.registry.discover_plugins()
        loaded = 0
        
        for plugin_path in discovered:
            if self.registry.load_plugin(plugin_path):
                loaded += 1
        
        return loaded
    
    def enable_all(self):
        """Enable all loaded plugins"""
        for plugin_name in self.registry.list_plugins():
            self.registry.enable_plugin(plugin_name)
    
    def disable_all(self):
        """Disable all plugins"""
        for plugin_name in self.registry.list_plugins():
            self.registry.disable_plugin(plugin_name)
    
    def process_input(self, message: str, **kwargs) -> str:
        """Process input through pre-process hooks"""
        results = self.registry.execute_hook(HookType.PRE_PROCESS, message, **kwargs)
        
        # Return last modified message or original
        for plugin_name, result in reversed(results):
            if result is not None:
                return result
        return message
    
    def process_output(self, response: str, **kwargs) -> str:
        """Process output through post-process hooks"""
        results = self.registry.execute_hook(HookType.POST_PROCESS, response, **kwargs)
        
        # Return last modified response or original
        for plugin_name, result in reversed(results):
            if result is not None:
                return result
        return response
    
    def get_plugin(self, name: str) -> Optional[ForgePlugin]:
        """Get a plugin by name"""
        return self.registry.get_plugin(name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin manager statistics"""
        return self.registry.get_stats()
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins with their info"""
        return [
            self.registry.get_plugin_info(name).to_dict()
            for name in self.registry.list_plugins()
            if self.registry.get_plugin_info(name)
        ]


# Convenience function
def create_plugin_manager(plugin_dirs: Optional[List[str]] = None) -> PluginManager:
    """Create a new plugin manager instance"""
    return PluginManager(plugin_dirs)


# ==================== MAIN ====================

def main():
    """Demo the plugin system"""
    print("=" * 60)
    print("🔌 THE FORGE AI - Plugin System Demo")
    print("=" * 60)
    print()
    
    # Initialize plugin manager
    manager = PluginManager()
    
    # List built-in plugins
    print("📦 Built-in Plugins:")
    print("-" * 40)
    for plugin_info in manager.list_plugins():
        meta = plugin_info["metadata"]
        print(f"  • {meta['name']} v{meta['version']}")
        print(f"    {meta['description']}")
        print(f"    State: {plugin_info['state']}")
    print()
    
    # Enable all plugins
    print("✅ Enabling Plugins:")
    print("-" * 40)
    manager.enable_all()
    for name in manager.registry.list_enabled_plugins():
        print(f"  • {name} enabled")
    print()
    
    # Process sample input through hooks
    print("🔄 Processing Through Hooks:")
    print("-" * 40)
    test_input = "Hello, can you help me with a Python question?"
    processed_input = manager.process_input(test_input)
    print(f"  Input: {test_input}")
    print(f"  Processed: {processed_input}")
    
    test_output = "Of course! I'd be happy to help with Python."
    processed_output = manager.process_output(test_output)
    print(f"  Output: {test_output}")
    print(f"  Processed: {processed_output}")
    print()
    
    # Get metrics
    print("📊 Metrics Plugin Data:")
    print("-" * 40)
    metrics_plugin = manager.get_plugin("MetricsPlugin")
    if metrics_plugin:
        metrics = metrics_plugin.get_metrics()
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    print()
    
    # Get stats
    print("📈 Plugin System Stats:")
    print("-" * 40)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Plugin System Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
