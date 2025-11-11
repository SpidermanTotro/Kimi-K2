"""
Plugin System Module

Provides a modular plugin system for extending the dual-operator AI with
custom tools, workflows, and integrations.
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import importlib
import inspect


class Plugin(ABC):
    """
    Base class for all plugins.
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
        """
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the plugin's main functionality.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Plugin execution result
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up resources when plugin is unloaded."""
        pass


class PluginManager:
    """
    Manages plugins for the dual-operator AI system.
    
    This manager handles plugin loading, initialization, execution,
    and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        
    def register_plugin(
        self,
        plugin: Plugin,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a plugin with the manager.
        
        Args:
            plugin: Plugin instance to register
            config: Optional configuration for the plugin
            
        Raises:
            ValueError: If plugin with same name already exists
        """
        plugin_name = plugin.name
        
        if plugin_name in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' is already registered")
        
        # Initialize plugin
        plugin_config = config or {}
        plugin.initialize(plugin_config)
        
        # Store plugin and config
        self.plugins[plugin_name] = plugin
        self.plugin_configs[plugin_name] = plugin_config
        
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Raises:
            KeyError: If plugin is not registered
        """
        if plugin_name not in self.plugins:
            raise KeyError(f"Plugin '{plugin_name}' is not registered")
        
        # Cleanup plugin
        plugin = self.plugins[plugin_name]
        plugin.cleanup()
        
        # Remove plugin
        del self.plugins[plugin_name]
        del self.plugin_configs[plugin_name]
    
    def get_plugin(self, plugin_name: str) -> Plugin:
        """
        Get a registered plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance
            
        Raises:
            KeyError: If plugin is not registered
        """
        if plugin_name not in self.plugins:
            raise KeyError(f"Plugin '{plugin_name}' is not registered")
        
        return self.plugins[plugin_name]
    
    def execute_plugin(
        self,
        plugin_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a plugin.
        
        Args:
            plugin_name: Name of the plugin to execute
            *args: Positional arguments for plugin
            **kwargs: Keyword arguments for plugin
            
        Returns:
            Plugin execution result
        """
        plugin = self.get_plugin(plugin_name)
        return plugin.execute(*args, **kwargs)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'type': type(plugin).__name__
            }
            for plugin in self.plugins.values()
        ]
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback.
        
        Args:
            hook_name: Name of the hook
            callback: Callback function to register
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Trigger all callbacks for a hook.
        
        Args:
            hook_name: Name of the hook to trigger
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
            
        Returns:
            List of callback results
        """
        if hook_name not in self.hooks:
            return []
        
        results = []
        for callback in self.hooks[hook_name]:
            result = callback(*args, **kwargs)
            results.append(result)
        
        return results
    
    def load_plugin_from_module(
        self,
        module_path: str,
        class_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Load a plugin from a Python module.
        
        Args:
            module_path: Python module path (e.g., 'mypackage.plugins.myplugin')
            class_name: Name of the plugin class
            config: Optional configuration for the plugin
            
        Raises:
            ImportError: If module cannot be imported
            AttributeError: If class is not found in module
            TypeError: If class is not a Plugin subclass
        """
        # Import module
        module = importlib.import_module(module_path)
        
        # Get plugin class
        plugin_class = getattr(module, class_name)
        
        # Verify it's a Plugin subclass
        if not inspect.isclass(plugin_class) or not issubclass(plugin_class, Plugin):
            raise TypeError(f"{class_name} is not a Plugin subclass")
        
        # Instantiate and register
        plugin_instance = plugin_class()
        self.register_plugin(plugin_instance, config)


class WorkflowPlugin(Plugin):
    """
    Base class for workflow plugins.
    
    Workflow plugins define multi-step processes that can be executed
    in the dual-operator AI system.
    """
    
    def __init__(self):
        """Initialize workflow plugin."""
        self.steps: List[Callable] = []
        self.current_step = 0
        
    def add_step(self, step_func: Callable) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step_func: Function representing a workflow step
        """
        self.steps.append(step_func)
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the workflow.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Final workflow result
        """
        results = []
        self.current_step = 0
        context = kwargs.copy()
        
        for step in self.steps:
            # Pass previous result if the step accepts it
            if self.current_step > 0 and results:
                context['previous_result'] = results[-1]
            
            result = step(*args, **context)
            results.append(result)
            self.current_step += 1
        
        return results[-1] if results else None
    
    def reset(self) -> None:
        """Reset the workflow to the beginning."""
        self.current_step = 0


class ToolPlugin(Plugin):
    """
    Base class for tool plugins.
    
    Tool plugins provide specific capabilities that can be called by the AI.
    """
    
    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get the tool definition for LLM tool calling.
        
        Returns:
            Tool definition dictionary in OpenAI format
        """
        pass
    
    def format_result(self, result: Any) -> str:
        """
        Format the tool result for LLM consumption.
        
        Args:
            result: Raw tool result
            
        Returns:
            Formatted result string
        """
        if isinstance(result, dict):
            import json
            return json.dumps(result, indent=2)
        return str(result)
