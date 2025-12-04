#!/usr/bin/env python3
"""
THE FORGE - Collaboration System for ChatGPT 2.0
=================================================

Implements collaboration features for cross-functional alignment and
system-wide coordination between different modules.

Features:
- Inter-module communication
- Shared state management
- Event broadcasting
- Task coordination
- Workflow orchestration
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from enum import Enum
import threading
from queue import Queue

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of collaboration events"""
    MODULE_STARTED = "module_started"
    MODULE_STOPPED = "module_stopped"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    STATE_CHANGED = "state_changed"
    MESSAGE = "message"
    REQUEST = "request"
    RESPONSE = "response"


@dataclass
class CollaborationEvent:
    """Represents a collaboration event"""
    id: str = ""
    event_type: str = ""
    source_module: str = ""
    target_module: Optional[str] = None  # None = broadcast
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.source_module}{self.timestamp}{self.event_type}".encode()
            ).hexdigest()[:16]
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Task:
    """Represents a coordinated task"""
    id: str = ""
    name: str = ""
    owner_module: str = ""
    status: str = "pending"  # pending, running, completed, failed
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.name}{self.owner_module}{datetime.utcnow()}".encode()
            ).hexdigest()[:16]
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class ModuleInfo:
    """Information about a registered module"""
    name: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    status: str = "unknown"  # unknown, starting, running, stopping, stopped
    registered_at: str = ""
    last_heartbeat: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.utcnow().isoformat()


class EventBus:
    """
    Event bus for module communication.
    
    Provides:
    - Publish/subscribe pattern
    - Event filtering
    - Async event delivery
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}  # event_type -> handlers
        self.module_subscribers: Dict[str, List[Callable]] = {}  # module -> handlers
        self.event_queue: Queue = Queue()
        self.event_history: List[CollaborationEvent] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[CollaborationEvent], None]
    ):
        """Subscribe to events of a specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.debug(f"📫 Subscribed to {event_type}")
    
    def subscribe_module(
        self, 
        module_name: str, 
        handler: Callable[[CollaborationEvent], None]
    ):
        """Subscribe to events targeted at a specific module"""
        if module_name not in self.module_subscribers:
            self.module_subscribers[module_name] = []
        self.module_subscribers[module_name].append(handler)
    
    def publish(self, event: CollaborationEvent):
        """Publish an event"""
        self.event_queue.put(event)
        self.event_history.append(event)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
    
    def _process_events(self):
        """Process events from the queue"""
        import queue
        while self._running:
            try:
                event = self.event_queue.get(timeout=0.1)
                self._deliver_event(event)
            except queue.Empty:
                pass  # Expected when queue is empty, continue loop
            except Exception as e:
                logger.error(f"❌ Event processing error: {e}")
    
    def _deliver_event(self, event: CollaborationEvent):
        """Deliver event to subscribers"""
        # Type-based delivery
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"❌ Handler error: {e}")
        
        # Module-targeted delivery
        if event.target_module:
            if event.target_module in self.module_subscribers:
                for handler in self.module_subscribers[event.target_module]:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"❌ Handler error: {e}")
    
    def start(self):
        """Start event processing"""
        self._running = True
        self._thread = threading.Thread(target=self._process_events, daemon=True)
        self._thread.start()
        logger.info("📬 Event bus started")
    
    def stop(self):
        """Stop event processing"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        logger.info("📭 Event bus stopped")
    
    def get_history(
        self, 
        event_type: Optional[str] = None,
        source_module: Optional[str] = None,
        limit: int = 100
    ) -> List[CollaborationEvent]:
        """Get event history with optional filtering"""
        events = self.event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source_module:
            events = [e for e in events if e.source_module == source_module]
        
        return events[-limit:]


class SharedState:
    """
    Shared state management across modules.
    
    Provides:
    - Key-value storage
    - Namespaced access
    - State synchronization
    - Change notifications
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.state: Dict[str, Dict[str, Any]] = {}  # namespace -> data
        self._lock = threading.Lock()
    
    def set(self, namespace: str, key: str, value: Any, source: str = "system"):
        """Set a value in shared state"""
        with self._lock:
            if namespace not in self.state:
                self.state[namespace] = {}
            
            old_value = self.state[namespace].get(key)
            self.state[namespace][key] = value
            
            # Notify if changed
            if old_value != value:
                self.event_bus.publish(CollaborationEvent(
                    event_type=EventType.STATE_CHANGED.value,
                    source_module=source,
                    payload={
                        'namespace': namespace,
                        'key': key,
                        'old_value': old_value,
                        'new_value': value
                    }
                ))
    
    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get a value from shared state"""
        with self._lock:
            if namespace in self.state:
                return self.state[namespace].get(key, default)
            return default
    
    def get_namespace(self, namespace: str) -> Dict[str, Any]:
        """Get all data in a namespace"""
        with self._lock:
            return self.state.get(namespace, {}).copy()
    
    def delete(self, namespace: str, key: str, source: str = "system"):
        """Delete a value from shared state"""
        with self._lock:
            if namespace in self.state and key in self.state[namespace]:
                old_value = self.state[namespace].pop(key)
                
                self.event_bus.publish(CollaborationEvent(
                    event_type=EventType.STATE_CHANGED.value,
                    source_module=source,
                    payload={
                        'namespace': namespace,
                        'key': key,
                        'old_value': old_value,
                        'new_value': None,
                        'deleted': True
                    }
                ))
    
    def clear_namespace(self, namespace: str, source: str = "system"):
        """Clear all data in a namespace"""
        with self._lock:
            if namespace in self.state:
                self.state[namespace] = {}
                
                self.event_bus.publish(CollaborationEvent(
                    event_type=EventType.STATE_CHANGED.value,
                    source_module=source,
                    payload={
                        'namespace': namespace,
                        'cleared': True
                    }
                ))


class TaskCoordinator:
    """
    Task coordination and workflow orchestration.
    
    Provides:
    - Task scheduling
    - Dependency management
    - Progress tracking
    - Error handling
    """
    
    def __init__(self, event_bus: EventBus, shared_state: SharedState):
        self.event_bus = event_bus
        self.shared_state = shared_state
        self.tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
    
    def create_task(
        self, 
        name: str, 
        owner_module: str,
        input_data: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """Create a new coordinated task"""
        task = Task(
            name=name,
            owner_module=owner_module,
            input_data=input_data or {},
            dependencies=dependencies or []
        )
        
        with self._lock:
            self.tasks[task.id] = task
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.TASK_CREATED.value,
            source_module=owner_module,
            payload={'task_id': task.id, 'task_name': name}
        ))
        
        logger.info(f"📋 Task created: {name} ({task.id})")
        return task
    
    def start_task(self, task_id: str) -> bool:
        """Start a task if dependencies are met"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            # Check dependencies
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    dep_task = self.tasks[dep_id]
                    if dep_task.status != 'completed':
                        logger.warning(f"⏳ Task {task_id} waiting for dependency {dep_id}")
                        return False
            
            task.status = 'running'
            task.started_at = datetime.utcnow().isoformat()
        
        logger.info(f"▶️ Task started: {task.name}")
        return True
    
    def complete_task(
        self, 
        task_id: str, 
        output_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark a task as completed"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = 'completed'
            task.completed_at = datetime.utcnow().isoformat()
            task.output_data = output_data or {}
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.TASK_COMPLETED.value,
            source_module=task.owner_module,
            payload={'task_id': task_id, 'output': output_data}
        ))
        
        logger.info(f"✅ Task completed: {task.name}")
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        with self._lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = 'failed'
            task.completed_at = datetime.utcnow().isoformat()
            task.error_message = error
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.TASK_FAILED.value,
            source_module=task.owner_module,
            payload={'task_id': task_id, 'error': error}
        ))
        
        logger.error(f"❌ Task failed: {task.name} - {error}")
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self, owner_module: Optional[str] = None) -> List[Task]:
        """Get all pending tasks"""
        tasks = [t for t in self.tasks.values() if t.status == 'pending']
        if owner_module:
            tasks = [t for t in tasks if t.owner_module == owner_module]
        return tasks
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
        for task in self.tasks.values():
            stats[task.status] = stats.get(task.status, 0) + 1
        return stats


class ModuleRegistry:
    """
    Registry for managing module registration and discovery.
    
    Provides:
    - Module registration
    - Capability discovery
    - Health monitoring
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.modules: Dict[str, ModuleInfo] = {}
        self._lock = threading.Lock()
    
    def register(
        self, 
        name: str, 
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ModuleInfo:
        """Register a module"""
        module = ModuleInfo(
            name=name,
            version=version,
            capabilities=capabilities or [],
            status='running',
            metadata=metadata or {}
        )
        
        with self._lock:
            self.modules[name] = module
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.MODULE_STARTED.value,
            source_module=name,
            payload={'name': name, 'version': version, 'capabilities': capabilities}
        ))
        
        logger.info(f"📦 Module registered: {name} v{version}")
        return module
    
    def unregister(self, name: str):
        """Unregister a module"""
        with self._lock:
            if name in self.modules:
                self.modules[name].status = 'stopped'
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.MODULE_STOPPED.value,
            source_module=name,
            payload={'name': name}
        ))
        
        logger.info(f"📦 Module unregistered: {name}")
    
    def heartbeat(self, name: str):
        """Update module heartbeat"""
        with self._lock:
            if name in self.modules:
                self.modules[name].last_heartbeat = datetime.utcnow().isoformat()
    
    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Get module info"""
        return self.modules.get(name)
    
    def find_by_capability(self, capability: str) -> List[ModuleInfo]:
        """Find modules with a specific capability"""
        return [
            m for m in self.modules.values()
            if capability in m.capabilities and m.status == 'running'
        ]
    
    def get_all_modules(self) -> List[ModuleInfo]:
        """Get all registered modules"""
        return list(self.modules.values())


class CollaborationSystem:
    """
    Main collaboration system integrating all components.
    
    Provides unified interface for:
    - Module communication
    - State sharing
    - Task coordination
    - Workflow orchestration
    """
    
    def __init__(self, storage_path: str = ".forge_collaboration"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.event_bus = EventBus()
        self.shared_state = SharedState(self.event_bus)
        self.task_coordinator = TaskCoordinator(self.event_bus, self.shared_state)
        self.module_registry = ModuleRegistry(self.event_bus)
        
        # Start event processing
        self.event_bus.start()
        
        logger.info("✅ Collaboration System initialized")
    
    def register_module(
        self, 
        name: str, 
        capabilities: Optional[List[str]] = None
    ) -> ModuleInfo:
        """Register a module with the collaboration system"""
        return self.module_registry.register(name, capabilities=capabilities)
    
    def send_message(
        self, 
        source: str, 
        target: Optional[str],
        message: Dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        """Send a message between modules"""
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.MESSAGE.value,
            source_module=source,
            target_module=target,
            payload=message,
            correlation_id=correlation_id
        ))
    
    def request(
        self, 
        source: str, 
        target: str,
        request_type: str,
        data: Dict[str, Any]
    ) -> str:
        """Send a request to a module"""
        correlation_id = hashlib.sha256(
            f"{source}{target}{datetime.utcnow()}".encode()
        ).hexdigest()[:16]
        
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.REQUEST.value,
            source_module=source,
            target_module=target,
            payload={'type': request_type, 'data': data},
            correlation_id=correlation_id
        ))
        
        return correlation_id
    
    def respond(
        self, 
        source: str, 
        target: str,
        correlation_id: str,
        response: Dict[str, Any]
    ):
        """Send a response to a request"""
        self.event_bus.publish(CollaborationEvent(
            event_type=EventType.RESPONSE.value,
            source_module=source,
            target_module=target,
            payload=response,
            correlation_id=correlation_id
        ))
    
    def create_task(
        self, 
        name: str, 
        owner: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a coordinated task"""
        return self.task_coordinator.create_task(name, owner, input_data)
    
    def set_state(self, namespace: str, key: str, value: Any, source: str):
        """Set shared state"""
        self.shared_state.set(namespace, key, value, source)
    
    def get_state(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get shared state"""
        return self.shared_state.get(namespace, key, default)
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[CollaborationEvent], None]
    ):
        """Subscribe to events"""
        self.event_bus.subscribe(event_type, handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collaboration system statistics"""
        return {
            'modules': len(self.module_registry.modules),
            'active_modules': len([m for m in self.module_registry.modules.values() if m.status == 'running']),
            'tasks': self.task_coordinator.get_task_stats(),
            'events_in_history': len(self.event_bus.event_history),
            'state_namespaces': len(self.shared_state.state)
        }
    
    def shutdown(self):
        """Shutdown the collaboration system"""
        self.event_bus.stop()
        logger.info("🛑 Collaboration System shutdown")


# Global collaboration instance
_collaboration_instance: Optional[CollaborationSystem] = None


def get_collaboration() -> CollaborationSystem:
    """Get or create the global collaboration instance"""
    global _collaboration_instance
    if _collaboration_instance is None:
        _collaboration_instance = CollaborationSystem()
    return _collaboration_instance


def main():
    """Demo: Collaboration System for ChatGPT 2.0"""
    print("\n" + "=" * 60)
    print("🤝 THE FORGE - Collaboration System for ChatGPT 2.0")
    print("=" * 60 + "\n")
    
    # Initialize collaboration system
    collab = get_collaboration()
    
    # Register modules
    memory_module = collab.register_module(
        "memory", 
        capabilities=["store", "retrieve", "consolidate"]
    )
    print(f"Registered module: {memory_module.name}")
    
    codex_module = collab.register_module(
        "codex",
        capabilities=["search", "browse", "edit"]
    )
    print(f"Registered module: {codex_module.name}")
    
    # Set shared state
    collab.set_state("session", "current_user", "demo_user", "memory")
    collab.set_state("session", "mode", "collaborative", "codex")
    
    print("\nShared state set")
    print(f"  current_user: {collab.get_state('session', 'current_user')}")
    print(f"  mode: {collab.get_state('session', 'mode')}")
    
    # Create and manage tasks
    task = collab.create_task(
        name="Process document",
        owner="codex",
        input_data={"doc_id": "doc123"}
    )
    print(f"\nCreated task: {task.name} ({task.id})")
    
    collab.task_coordinator.start_task(task.id)
    print(f"Task status: {task.status}")
    
    collab.task_coordinator.complete_task(task.id, {"processed": True})
    print(f"Task status: {task.status}")
    
    # Subscribe to events
    def handle_event(event: CollaborationEvent):
        print(f"  Event received: {event.event_type} from {event.source_module}")
    
    collab.subscribe(EventType.MESSAGE.value, handle_event)
    
    # Send messages
    print("\nSending message:")
    collab.send_message("memory", "codex", {"action": "sync", "data": {}})
    
    # Get stats
    print("\nCollaboration System Stats:")
    stats = collab.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    collab.shutdown()
    
    print("\n" + "=" * 60)
    print("✅ Collaboration System Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
