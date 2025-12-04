#!/usr/bin/env python3
"""
THE FORGE - Plugin System for ChatGPT 2.0
==========================================

Implements a scalable plugin system for extending functionality across
Codex-assisted components and system modules.

Features:
- Plugin discovery and loading
- Plugin lifecycle management
- Hook system for extensibility
- Dependency resolution
- Hot-reload support
"""

import json
import os
import hashlib
import importlib
import importlib.util
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from abc import ABC, abstractmethod
import inspect

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Information about a plugin"""
    id: str = ""
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    entry_point: str = ""
    enabled: bool = True
    loaded: bool = False
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.name}{self.version}".encode()
            ).hexdigest()[:16]


class PluginBase(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin information"""
        pass
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the plugin"""
        pass
    
    def on_hook(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a hook invocation"""
        return data


@dataclass
class HookPoint:
    """Represents a hook point in the system"""
    name: str
    description: str = ""
    handlers: List[Callable] = field(default_factory=list)
    priority_order: List[str] = field(default_factory=list)  # Plugin IDs in order


class HookRegistry:
    """
    Registry for hook points and handlers.
    
    Provides:
    - Hook registration
    - Handler management
    - Ordered execution
    """
    
    def __init__(self):
        self.hooks: Dict[str, HookPoint] = {}
        self.plugin_handlers: Dict[str, Dict[str, Callable]] = {}  # plugin_id -> hook_name -> handler
    
    def register_hook(self, name: str, description: str = ""):
        """Register a new hook point"""
        if name not in self.hooks:
            self.hooks[name] = HookPoint(name=name, description=description)
            logger.debug(f"🪝 Registered hook: {name}")
    
    def add_handler(
        self, 
        hook_name: str, 
        plugin_id: str,
        handler: Callable,
        priority: int = 100
    ):
        """Add a handler for a hook"""
        if hook_name not in self.hooks:
            self.register_hook(hook_name)
        
        hook = self.hooks[hook_name]
        hook.handlers.append(handler)
        
        # Track plugin handlers
        if plugin_id not in self.plugin_handlers:
            self.plugin_handlers[plugin_id] = {}
        self.plugin_handlers[plugin_id][hook_name] = handler
        
        # Update priority order
        hook.priority_order.append(plugin_id)
        hook.priority_order.sort(key=lambda x: priority)
    
    def remove_handlers(self, plugin_id: str):
        """Remove all handlers for a plugin"""
        if plugin_id in self.plugin_handlers:
            for hook_name, handler in self.plugin_handlers[plugin_id].items():
                if hook_name in self.hooks:
                    hook = self.hooks[hook_name]
                    if handler in hook.handlers:
                        hook.handlers.remove(handler)
                    if plugin_id in hook.priority_order:
                        hook.priority_order.remove(plugin_id)
            del self.plugin_handlers[plugin_id]
    
    def execute(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all handlers for a hook"""
        if hook_name not in self.hooks:
            return data
        
        hook = self.hooks[hook_name]
        result = data
        
        for handler in hook.handlers:
            try:
                result = handler(result)
                if result is None:
                    result = data
            except Exception as e:
                logger.error(f"❌ Hook handler error: {e}")
        
        return result
    
    def get_hook_info(self) -> List[Dict[str, Any]]:
        """Get information about all hooks"""
        return [
            {
                'name': h.name,
                'description': h.description,
                'handler_count': len(h.handlers),
                'plugins': h.priority_order
            }
            for h in self.hooks.values()
        ]


class PluginLoader:
    """
    Plugin loading and lifecycle management.
    
    Provides:
    - Plugin discovery
    - Dynamic loading
    - Dependency resolution
    - Lifecycle management
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.load_order: List[str] = []
    
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins"""
        discovered = []
        
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return discovered
        
        # Look for plugin manifest files
        for manifest_path in self.plugins_dir.glob("*/plugin.json"):
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                info = PluginInfo(
                    name=manifest.get('name', 'Unknown'),
                    version=manifest.get('version', '1.0.0'),
                    description=manifest.get('description', ''),
                    author=manifest.get('author', ''),
                    dependencies=manifest.get('dependencies', []),
                    hooks=manifest.get('hooks', []),
                    capabilities=manifest.get('capabilities', []),
                    entry_point=manifest.get('entry_point', 'main.py')
                )
                
                self.plugin_info[info.id] = info
                discovered.append(info)
                
            except Exception as e:
                logger.warning(f"⚠️ Could not read plugin manifest: {manifest_path}: {e}")
        
        logger.info(f"🔍 Discovered {len(discovered)} plugins")
        return discovered
    
    def resolve_dependencies(self, plugin_ids: List[str]) -> List[str]:
        """Resolve plugin dependencies and return load order"""
        resolved = []
        unresolved = set(plugin_ids)
        
        while unresolved:
            made_progress = False
            
            for plugin_id in list(unresolved):
                if plugin_id not in self.plugin_info:
                    unresolved.remove(plugin_id)
                    continue
                
                info = self.plugin_info[plugin_id]
                deps_met = all(
                    dep in resolved 
                    for dep in info.dependencies
                )
                
                if deps_met:
                    resolved.append(plugin_id)
                    unresolved.remove(plugin_id)
                    made_progress = True
            
            if not made_progress and unresolved:
                # Circular dependency or missing dependency
                logger.error(f"❌ Cannot resolve dependencies for: {unresolved}")
                break
        
        return resolved
    
    def load_plugin(self, plugin_id: str, context: Dict[str, Any]) -> bool:
        """Load a single plugin"""
        if plugin_id not in self.plugin_info:
            logger.error(f"❌ Plugin not found: {plugin_id}")
            return False
        
        info = self.plugin_info[plugin_id]
        
        if not info.enabled:
            logger.info(f"⏭️ Plugin disabled: {info.name}")
            return False
        
        try:
            # Find plugin directory
            plugin_dir = None
            for d in self.plugins_dir.iterdir():
                if d.is_dir():
                    manifest_path = d / "plugin.json"
                    if manifest_path.exists():
                        with open(manifest_path) as f:
                            manifest = json.load(f)
                        if manifest.get('name') == info.name:
                            plugin_dir = d
                            break
            
            if not plugin_dir:
                logger.error(f"❌ Plugin directory not found: {info.name}")
                return False
            
            # Load the plugin module
            entry_path = plugin_dir / info.entry_point
            if not entry_path.exists():
                logger.error(f"❌ Plugin entry point not found: {entry_path}")
                return False
            
            spec = importlib.util.spec_from_file_location(info.name, entry_path)
            if spec is None or spec.loader is None:
                logger.error(f"❌ Could not load plugin spec: {info.name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"❌ No PluginBase subclass found in: {info.name}")
                return False
            
            # Instantiate and initialize
            plugin = plugin_class()
            if plugin.initialize(context):
                self.plugins[plugin_id] = plugin
                info.loaded = True
                self.load_order.append(plugin_id)
                logger.info(f"✅ Loaded plugin: {info.name} v{info.version}")
                return True
            else:
                info.error = "Initialization failed"
                return False
            
        except Exception as e:
            info.error = str(e)
            logger.error(f"❌ Failed to load plugin {info.name}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        info = self.plugin_info[plugin_id]
        
        try:
            plugin.shutdown()
            del self.plugins[plugin_id]
            info.loaded = False
            if plugin_id in self.load_order:
                self.load_order.remove(plugin_id)
            logger.info(f"📤 Unloaded plugin: {info.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {info.name}: {e}")
            return False
    
    def get_loaded_plugins(self) -> List[PluginInfo]:
        """Get list of loaded plugins"""
        return [
            info for info in self.plugin_info.values()
            if info.loaded
        ]


class PluginSystem:
    """
    Main plugin system integrating all components.
    
    Provides unified interface for:
    - Plugin management
    - Hook system
    - Capability extension
    """
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.loader = PluginLoader(plugins_dir)
        self.hooks = HookRegistry()
        self.context: Dict[str, Any] = {}
        
        # Register core hooks
        self._register_core_hooks()
        
        logger.info("✅ Plugin System initialized")
    
    def _register_core_hooks(self):
        """Register core hook points"""
        core_hooks = [
            ("before_process", "Called before processing a request"),
            ("after_process", "Called after processing a request"),
            ("before_memory_store", "Called before storing in memory"),
            ("after_memory_retrieve", "Called after retrieving from memory"),
            ("before_codex_search", "Called before searching Codex"),
            ("after_codex_search", "Called after searching Codex"),
            ("before_codex_edit", "Called before editing Codex content"),
            ("after_codex_edit", "Called after editing Codex content"),
            ("on_session_start", "Called when a session starts"),
            ("on_session_end", "Called when a session ends"),
            ("on_error", "Called when an error occurs"),
            ("on_collaboration_event", "Called on collaboration events"),
        ]
        
        for name, description in core_hooks:
            self.hooks.register_hook(name, description)
    
    def set_context(self, key: str, value: Any):
        """Set context value available to plugins"""
        self.context[key] = value
    
    def discover(self) -> List[PluginInfo]:
        """Discover available plugins"""
        return self.loader.discover_plugins()
    
    def load_all(self) -> int:
        """Load all discovered plugins"""
        plugins = self.discover()
        
        if not plugins:
            return 0
        
        # Resolve dependencies
        plugin_ids = [p.id for p in plugins]
        load_order = self.loader.resolve_dependencies(plugin_ids)
        
        loaded = 0
        for plugin_id in load_order:
            if self.loader.load_plugin(plugin_id, self.context):
                # Register plugin hooks
                plugin = self.loader.plugins[plugin_id]
                info = self.loader.plugin_info[plugin_id]
                
                for hook_name in info.hooks:
                    def create_handler(p, h):
                        return lambda data: p.on_hook(h, data)
                    
                    self.hooks.add_handler(
                        hook_name,
                        plugin_id,
                        create_handler(plugin, hook_name)
                    )
                
                loaded += 1
        
        return loaded
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin"""
        return self.loader.load_plugin(plugin_id, self.context)
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin"""
        # Remove hooks first
        self.hooks.remove_handlers(plugin_id)
        return self.loader.unload_plugin(plugin_id)
    
    def execute_hook(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a hook with data"""
        return self.hooks.execute(hook_name, data)
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities provided by plugins"""
        capabilities: Dict[str, List[str]] = {}
        
        for plugin_id, info in self.loader.plugin_info.items():
            if info.loaded:
                for cap in info.capabilities:
                    if cap not in capabilities:
                        capabilities[cap] = []
                    capabilities[cap].append(info.name)
        
        return capabilities
    
    def find_plugins_by_capability(self, capability: str) -> List[PluginInfo]:
        """Find plugins that provide a capability"""
        return [
            info for info in self.loader.plugin_info.values()
            if info.loaded and capability in info.capabilities
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin system statistics"""
        all_plugins = list(self.loader.plugin_info.values())
        loaded = [p for p in all_plugins if p.loaded]
        
        return {
            'total_plugins': len(all_plugins),
            'loaded_plugins': len(loaded),
            'disabled_plugins': len([p for p in all_plugins if not p.enabled]),
            'failed_plugins': len([p for p in all_plugins if p.error]),
            'registered_hooks': len(self.hooks.hooks),
            'active_handlers': sum(len(h.handlers) for h in self.hooks.hooks.values()),
            'capabilities': self.get_capabilities()
        }
    
    def shutdown(self):
        """Shutdown the plugin system"""
        # Unload in reverse order
        for plugin_id in reversed(self.loader.load_order[:]):
            self.unload_plugin(plugin_id)
        logger.info("🛑 Plugin System shutdown")


class ExamplePlugin(PluginBase):
    """Example plugin implementation"""
    
    def __init__(self):
        self._info = PluginInfo(
            name="Example Plugin",
            version="1.0.0",
            description="An example plugin demonstrating the plugin system",
            author="THE FORGE",
            hooks=["before_process", "after_process"],
            capabilities=["example", "demo"]
        )
    
    def get_info(self) -> PluginInfo:
        return self._info
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        logger.info("🔌 Example Plugin initialized")
        return True
    
    def shutdown(self) -> bool:
        logger.info("🔌 Example Plugin shutdown")
        return True
    
    def on_hook(self, hook_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(f"🪝 Example Plugin handling hook: {hook_name}")
        return data


# Global plugin system instance
_plugin_instance: Optional[PluginSystem] = None


def get_plugins() -> PluginSystem:
    """Get or create the global plugin system instance"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = PluginSystem()
    return _plugin_instance


def main():
    """Demo: Plugin System for ChatGPT 2.0"""
    print("\n" + "=" * 60)
    print("🔌 THE FORGE - Plugin System for ChatGPT 2.0")
    print("=" * 60 + "\n")
    
    # Initialize plugin system
    plugins = get_plugins()
    
    # Set context
    plugins.set_context("app_name", "THE FORGE")
    plugins.set_context("version", "2.0.0")
    
    # Show registered hooks
    print("📋 Core Hooks:")
    for hook_info in plugins.hooks.get_hook_info():
        print(f"  - {hook_info['name']}: {hook_info['description']}")
    
    # Create example plugin directory and manifest
    example_dir = Path("plugins/example")
    example_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "name": "Example Plugin",
        "version": "1.0.0",
        "description": "Example plugin for demo",
        "author": "THE FORGE",
        "dependencies": [],
        "hooks": ["before_process", "after_process"],
        "capabilities": ["example"],
        "entry_point": "main.py"
    }
    
    with open(example_dir / "plugin.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create plugin code
    plugin_code = '''
from forge_plugins import PluginBase, PluginInfo
import logging

logger = logging.getLogger(__name__)

class DemoPlugin(PluginBase):
    def __init__(self):
        self._info = PluginInfo(
            name="Example Plugin",
            version="1.0.0",
            description="Demo plugin",
            hooks=["before_process"],
            capabilities=["example"]
        )
    
    def get_info(self):
        return self._info
    
    def initialize(self, context):
        logger.info("Demo plugin initialized")
        return True
    
    def shutdown(self):
        return True
    
    def on_hook(self, hook_name, data):
        data["plugin_processed"] = True
        return data
'''
    
    with open(example_dir / "main.py", 'w') as f:
        f.write(plugin_code)
    
    # Discover plugins
    print("\n🔍 Discovering plugins...")
    discovered = plugins.discover()
    for p in discovered:
        print(f"  Found: {p.name} v{p.version}")
    
    # Load plugins
    print("\n📦 Loading plugins...")
    loaded = plugins.load_all()
    print(f"  Loaded {loaded} plugins")
    
    # Execute a hook
    print("\n🪝 Executing hook 'before_process'...")
    data = {"request": "test request"}
    result = plugins.execute_hook("before_process", data)
    print(f"  Input: {data}")
    print(f"  Output: {result}")
    
    # Get capabilities
    print("\n🎯 Plugin Capabilities:")
    capabilities = plugins.get_capabilities()
    for cap, providers in capabilities.items():
        print(f"  {cap}: {providers}")
    
    # Get stats
    print("\n📊 Plugin System Stats:")
    stats = plugins.get_stats()
    for key, value in stats.items():
        if key != 'capabilities':
            print(f"  {key}: {value}")
    
    # Cleanup
    plugins.shutdown()
    
    # Remove example plugin directory
    import shutil
    shutil.rmtree("plugins", ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("✅ Plugin System Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
