# ChatGPT 2.0 Integration Guide

## THE FORGE - Unified Framework for ChatGPT 2.0

This document provides comprehensive documentation for the ChatGPT 2.0 unified framework integration, including usage examples for end-users and developers.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Codex System](#codex-system)
5. [Memory System](#memory-system)
6. [Collaboration System](#collaboration-system)
7. [Plugin System](#plugin-system)
8. [System Manager](#system-manager)
9. [Unified Chat Interface](#unified-chat-interface)
10. [API Reference](#api-reference)
11. [Examples](#examples)

---

## Overview

The ChatGPT 2.0 unified framework integrates several key components:

- **Codex System**: Documentation browsing, querying, and content editing
- **Memory System**: Hierarchical memory with persistent context sharing
- **Collaboration System**: Inter-module communication and task coordination
- **Plugin System**: Extensible plugin architecture
- **System Manager**: Centralized version tracking and system-wide updates
- **Unified Chat Interface**: Single interface merging all chat capabilities

### Key Features

- ✅ Hierarchical memory (short-term, working, long-term)
- ✅ Persistent context sharing between sessions
- ✅ Cross-session learning and adaptation
- ✅ Codex integration for documentation
- ✅ Plugin-based extensibility
- ✅ Event-driven collaboration
- ✅ Centralized version management
- ✅ System-wide health monitoring and updates

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unified Chat Interface                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐ │
│  │   Memory    │  │   Codex     │  │     Collaboration        │ │
│  │   System    │  │   System    │  │        System            │ │
│  ├─────────────┤  ├─────────────┤  ├──────────────────────────┤ │
│  │ Short-term  │  │ Index       │  │ Event Bus                │ │
│  │ Working     │  │ Editor      │  │ Shared State             │ │
│  │ Long-term   │  │ Browser     │  │ Task Coordinator         │ │
│  └─────────────┘  └─────────────┘  └──────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Plugin System                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │   │
│  │  │ Hook     │  │ Plugin   │  │ Plugin   │                │   │
│  │  │ Registry │  │ Loader   │  │ Manager  │                │   │
│  │  └──────────┘  └──────────┘  └──────────┘                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_chatgpt2_integration.py
```

### Quick Start

```python
from forge_unified_chat import get_chat_interface

# Initialize the unified interface
chat = get_chat_interface()

# Create a session
session = chat.create_session(title="My Conversation")

# Send a message and get response
response = chat.get_response("Help me with video editing")
print(response.content)
```

---

## Codex System

The Codex System provides documentation browsing, querying, and content editing capabilities.

### Features

- Full-text search and indexing
- Section-level navigation
- Document versioning
- Content editing with history
- Integration with reasoning workflows

### Usage

```python
from forge_codex import get_codex

codex = get_codex()

# Add a document
doc = codex.add_document(
    title="Video Editing Guide",
    content="# Professional Video Editing\n\n...",
    doc_type="markdown",
    tags=["video", "guide"]
)

# Search for documents
results = codex.search("video editing tips")
for result in results:
    print(f"- {result.document.title} (relevance: {result.relevance_score})")

# Edit a document
codex.edit_document(
    doc_id=doc.id,
    edit_type="append",
    new_content="\n## Additional Tips\n..."
)

# Browse documents
structure = codex.browse()
print(f"Total documents: {len(structure['documents'])}")

# Get statistics
stats = codex.get_stats()
print(f"Indexed words: {stats['indexed_words']}")
```

### Document Types

- `markdown`: Markdown documentation with section parsing
- `code`: Source code with function/class detection
- `text`: Plain text documents
- `config`: Configuration files (JSON, YAML)

---

## Memory System

The Memory System implements hierarchical memory with three tiers:

1. **Short-term memory**: Recent interactions within a session
2. **Working memory**: Active context being processed
3. **Long-term memory**: Consolidated knowledge across sessions

### Features

- Automatic memory consolidation
- Persistent storage
- Context sharing between sessions
- Relevance-based retrieval

### Usage

```python
from forge_memory import get_memory

memory = get_memory()

# Create a session
session_id = memory.create_session()

# Add memories
memory.add_memory(
    content="User prefers Python code examples",
    session_id=session_id,
    tags=["preference", "python"]
)

# Retrieve relevant memories
results = memory.retrieve("python programming", session_id)
for mem in results:
    print(f"- {mem.content} (relevance: {mem.relevance_score})")

# Link to Codex session
codex_session = "codex_123"
memory.link_codex_session(session_id, codex_session)

# Get shared context
context = memory.get_shared_context(session_id)
print(f"Codex session: {context['codex_session_id']}")

# Consolidate to long-term
memory.consolidate_to_long_term(memory_id)
```

### Persistent Context Manager

```python
from forge_memory import get_memory, PersistentContextManager

memory = get_memory()
context_manager = PersistentContextManager(memory)

# Create shared context
context_id = context_manager.create_shared_context("project_alpha")

# Join multiple sessions
context_manager.join_context(context_id, session1_id)
context_manager.join_context(context_id, session2_id)

# Share data
context_manager.share_data(context_id, "key", "value")
```

---

## Collaboration System

The Collaboration System enables inter-module communication and coordination.

### Components

- **Event Bus**: Publish/subscribe messaging
- **Shared State**: Namespaced key-value storage
- **Task Coordinator**: Task scheduling and dependencies
- **Module Registry**: Module discovery and health

### Usage

```python
from forge_collaboration import get_collaboration, EventType

collab = get_collaboration()

# Register a module
module = collab.register_module(
    "my_module",
    capabilities=["process", "analyze"]
)

# Subscribe to events
def handle_message(event):
    print(f"Received: {event.payload}")

collab.subscribe(EventType.MESSAGE.value, handle_message)

# Send messages
collab.send_message("my_module", "other_module", {"action": "sync"})

# Shared state
collab.set_state("namespace", "key", "value", "my_module")
value = collab.get_state("namespace", "key")

# Create and manage tasks
task = collab.create_task(
    name="Process Data",
    owner="my_module",
    input_data={"file": "data.json"}
)

collab.task_coordinator.start_task(task.id)
collab.task_coordinator.complete_task(task.id, {"result": "success"})

# Cleanup
collab.shutdown()
```

---

## Plugin System

The Plugin System provides extensibility through hooks and plugins.

### Core Hooks

| Hook Name | Description |
|-----------|-------------|
| `before_process` | Called before processing a request |
| `after_process` | Called after processing a request |
| `before_memory_store` | Called before storing in memory |
| `after_memory_retrieve` | Called after retrieving from memory |
| `before_codex_search` | Called before searching Codex |
| `after_codex_search` | Called after searching Codex |
| `on_session_start` | Called when a session starts |
| `on_session_end` | Called when a session ends |
| `on_error` | Called when an error occurs |

### Creating a Plugin

```python
# plugins/my_plugin/plugin.json
{
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "Example plugin",
    "author": "Developer",
    "hooks": ["before_process", "after_process"],
    "capabilities": ["enhance"],
    "entry_point": "main.py"
}

# plugins/my_plugin/main.py
from forge_plugins import PluginBase, PluginInfo

class MyPlugin(PluginBase):
    def __init__(self):
        self._info = PluginInfo(
            name="My Plugin",
            version="1.0.0",
            hooks=["before_process"],
            capabilities=["enhance"]
        )
    
    def get_info(self):
        return self._info
    
    def initialize(self, context):
        print("Plugin initialized")
        return True
    
    def shutdown(self):
        return True
    
    def on_hook(self, hook_name, data):
        if hook_name == "before_process":
            data["enhanced"] = True
        return data
```

### Using the Plugin System

```python
from forge_plugins import get_plugins

plugins = get_plugins()

# Discover and load plugins
discovered = plugins.discover()
loaded = plugins.load_all()

# Execute hooks
result = plugins.execute_hook("before_process", {"data": "test"})

# Find plugins by capability
found = plugins.find_plugins_by_capability("enhance")

# Get statistics
stats = plugins.get_stats()
```

---

## System Manager

The System Manager provides centralized version tracking and system-wide updates.

### Features

- Unified version tracking across all modules
- System-wide health monitoring
- Coordinated updates
- Diagnostics and rollback support

### Usage

```python
from forge_system_manager import get_system_manager

manager = get_system_manager()

# Get system status
status = manager.get_system_status()
print(f"Version: {status['version']}")
print(f"Health: {status['health']['overall_status']}")

# Get all module versions
for name, version in status['modules'].items():
    print(f"  {name}: v{version}")

# Update all systems
result = manager.update_all_systems()
print(f"Updated: {len(result['modules_updated'])} modules")

# Run diagnostics
diagnostics = manager.run_diagnostics()
print(f"Total Capabilities: {diagnostics['system_info']['total_capabilities']}")
```

### Version Compatibility

```python
from forge_system_manager import SystemVersionManager

version_manager = SystemVersionManager()

# Check module version
version = version_manager.get_version("forge_memory")
print(f"Memory System: v{version}")

# Check compatibility
is_compatible = version_manager.check_compatibility("forge_memory", "1.5.0")
```

### Health Monitoring

```python
from forge_system_manager import SystemHealthChecker, SystemVersionManager

version_manager = SystemVersionManager()
health_checker = SystemHealthChecker(version_manager)

# Perform health check
health = health_checker.check_health()
print(f"Overall Status: {health.overall_status}")

for module, status in health.modules_status.items():
    print(f"  {module}: {status}")
```

---

## Unified Chat Interface

The Unified Chat Interface merges all components into a single interface.

### Features

- Session management
- Memory integration
- Codex integration
- Plugin execution
- Cross-session context

### Usage

```python
from forge_unified_chat import get_chat_interface

chat = get_chat_interface()

# Create session with Codex linking
session = chat.create_session(
    title="Project Discussion",
    link_codex=True
)

# Send message
message = chat.send_message(
    content="I need help with video editing",
    role="user"
)

# Get AI response with context
response = chat.get_response(
    user_message="What are the best practices?",
    include_memory=True,
    include_codex=True
)

# Search history
results = chat.search_history("video")

# Create shared context for multiple sessions
context_id = chat.create_shared_context("video_project")
chat.join_shared_context(session.id, context_id)

# Export session
export_data = chat.export_session(session.id)

# Get statistics
stats = chat.get_stats()
```

---

## API Reference

### Memory API

| Method | Description |
|--------|-------------|
| `create_session(session_id)` | Create a new session |
| `add_memory(content, session_id, memory_type, tags)` | Add a memory entry |
| `retrieve(query, session_id, max_results)` | Retrieve relevant memories |
| `consolidate_to_long_term(memory_id)` | Promote to long-term |
| `link_codex_session(chat_session, codex_session)` | Link sessions |
| `get_shared_context(session_id)` | Get shared context |
| `get_stats()` | Get system statistics |

### Codex API

| Method | Description |
|--------|-------------|
| `add_document(title, content, doc_type, tags)` | Add a document |
| `search(query, filters, max_results)` | Search documents |
| `edit_document(doc_id, edit_type, old_content, new_content)` | Edit content |
| `browse(path)` | Browse documents |
| `view(doc_id)` | View a document |
| `get_stats()` | Get statistics |

### Collaboration API

| Method | Description |
|--------|-------------|
| `register_module(name, capabilities)` | Register a module |
| `send_message(source, target, message)` | Send a message |
| `request(source, target, type, data)` | Send a request |
| `respond(source, target, correlation_id, response)` | Send response |
| `create_task(name, owner, input_data)` | Create a task |
| `set_state(namespace, key, value, source)` | Set shared state |
| `get_state(namespace, key, default)` | Get shared state |
| `subscribe(event_type, handler)` | Subscribe to events |
| `get_stats()` | Get statistics |

### Plugin API

| Method | Description |
|--------|-------------|
| `discover()` | Discover plugins |
| `load_all()` | Load all plugins |
| `load_plugin(plugin_id)` | Load specific plugin |
| `unload_plugin(plugin_id)` | Unload a plugin |
| `execute_hook(hook_name, data)` | Execute a hook |
| `find_plugins_by_capability(capability)` | Find by capability |
| `get_stats()` | Get statistics |

---

## Examples

### Example 1: Complete Workflow

```python
from forge_unified_chat import get_chat_interface

# Initialize
chat = get_chat_interface()

# Create session
session = chat.create_session(title="Video Project")

# Add documentation to Codex
chat.codex.add_document(
    title="Video Editing Guide",
    content="# Professional Video Editing\n\nLearn video editing...",
    tags=["video", "guide"]
)

# Have a conversation
chat.send_message("I'm working on a video project")
response = chat.get_response("What tools should I use?")
print(response.content)

# Search previous conversations
results = chat.search_history("video")
for msg in results:
    print(f"[{msg.role}]: {msg.content[:50]}...")

# Get summary
summary = chat.get_conversation_summary(session.id)
print(f"Total messages: {summary['total_messages']}")
```

### Example 2: Cross-Session Context

```python
from forge_unified_chat import get_chat_interface

chat = get_chat_interface()

# Create first session
session1 = chat.create_session(title="Session 1")
context_id = chat.create_shared_context("shared_project")
chat.join_shared_context(session1.id, context_id)

# Add to memory
chat.memory.add_memory(
    content="Project uses Python 3.10",
    session_id=session1.id,
    memory_type="long_term"
)

# Create second session with same context
session2 = chat.create_session(title="Session 2")
chat.join_shared_context(session2.id, context_id)

# Second session can access shared memories
memories = chat.memory.retrieve("Python", session2.id)
```

### Example 3: Plugin Development

```python
from forge_plugins import PluginBase, PluginInfo, get_plugins

class LoggingPlugin(PluginBase):
    def __init__(self):
        self._info = PluginInfo(
            name="Logging Plugin",
            version="1.0.0",
            hooks=["before_process", "after_process"],
            capabilities=["logging"]
        )
        self.log = []
    
    def get_info(self):
        return self._info
    
    def initialize(self, context):
        print("Logging plugin started")
        return True
    
    def shutdown(self):
        print(f"Logged {len(self.log)} events")
        return True
    
    def on_hook(self, hook_name, data):
        self.log.append({
            "hook": hook_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        return data

# Register manually (for testing)
plugins = get_plugins()
plugins.hooks.add_handler(
    "before_process", 
    "logging_plugin",
    lambda data: print(f"Processing: {data}")
)
```

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test_chatgpt2_integration.py

# Run specific test class
python -m pytest test_chatgpt2_integration.py::TestHierarchicalMemory

# Run with verbose output
python -m pytest test_chatgpt2_integration.py -v
```

---

## Troubleshooting

### Common Issues

1. **Memory not persisting**: Ensure storage directory is writable
2. **Codex search returns empty**: Verify documents are indexed
3. **Plugin not loading**: Check plugin.json format and entry_point
4. **Events not received**: Ensure event bus is started

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## License

This project is licensed under the Modified MIT License. See LICENSE file for details.
