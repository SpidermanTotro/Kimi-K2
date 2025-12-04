#!/usr/bin/env python3
"""
THE FORGE - Memory System for ChatGPT 2.0
==========================================

Implements hierarchical memory support enabling seamless transitions across 
conversations and persistent context-sharing between chats and Codex sessions.

Features:
- Hierarchical memory with short-term, working, and long-term memory
- Persistent context sharing across sessions
- Memory consolidation and retrieval
- Cross-session learning and adaptation
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    content: str
    memory_type: str  # 'short_term', 'working', 'long_term'
    session_id: str
    timestamp: str
    relevance_score: float = 1.0
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.content}{self.timestamp}".encode()
            ).hexdigest()[:16]


@dataclass 
class ConversationContext:
    """Represents context for a conversation session"""
    session_id: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, str]] = field(default_factory=list)
    active_memories: List[str] = field(default_factory=list)
    codex_session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HierarchicalMemory:
    """
    Hierarchical Memory System
    
    Implements three-tier memory architecture:
    1. Short-term memory: Recent interactions within a session
    2. Working memory: Active context being processed
    3. Long-term memory: Consolidated knowledge across sessions
    """
    
    def __init__(self, storage_path: str = ".forge_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Memory tiers
        self.short_term: Dict[str, List[MemoryEntry]] = {}  # session_id -> entries
        self.working: Dict[str, MemoryEntry] = {}  # id -> entry
        self.long_term: Dict[str, MemoryEntry] = {}  # id -> entry
        
        # Session contexts
        self.contexts: Dict[str, ConversationContext] = {}
        
        # Load persistent memory
        self._load_persistent_memory()
        
        logger.info("✅ Hierarchical Memory System initialized")
    
    def _load_persistent_memory(self):
        """Load long-term memory from storage"""
        memory_file = self.storage_path / "long_term_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get('memories', []):
                        entry = MemoryEntry(**entry_data)
                        self.long_term[entry.id] = entry
                logger.info(f"📚 Loaded {len(self.long_term)} long-term memories")
            except Exception as e:
                logger.warning(f"⚠️ Could not load memories: {e}")
    
    def _save_persistent_memory(self):
        """Save long-term memory to storage"""
        memory_file = self.storage_path / "long_term_memory.json"
        try:
            data = {
                'memories': [asdict(entry) for entry in self.long_term.values()],
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Could not save memories: {e}")
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new conversation session"""
        if not session_id:
            session_id = hashlib.sha256(
                datetime.utcnow().isoformat().encode()
            ).hexdigest()[:16]
        
        now = datetime.utcnow().isoformat()
        self.contexts[session_id] = ConversationContext(
            session_id=session_id,
            created_at=now,
            updated_at=now
        )
        self.short_term[session_id] = []
        
        logger.info(f"🆕 Created session: {session_id}")
        return session_id
    
    def add_memory(
        self, 
        content: str, 
        session_id: str,
        memory_type: str = 'short_term',
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """Add a new memory entry"""
        
        entry = MemoryEntry(
            id="",
            content=content,
            memory_type=memory_type,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        
        if memory_type == 'short_term':
            if session_id not in self.short_term:
                self.short_term[session_id] = []
            self.short_term[session_id].append(entry)
            
            # Limit short-term memory per session
            if len(self.short_term[session_id]) > 100:
                self._consolidate_to_working(session_id)
                
        elif memory_type == 'working':
            self.working[entry.id] = entry
            
        elif memory_type == 'long_term':
            self.long_term[entry.id] = entry
            self._save_persistent_memory()
        
        return entry
    
    def _consolidate_to_working(self, session_id: str):
        """Consolidate short-term memories to working memory"""
        if session_id not in self.short_term:
            return
            
        # Take older memories and consolidate
        to_consolidate = self.short_term[session_id][:-50]  # Keep last 50
        self.short_term[session_id] = self.short_term[session_id][-50:]
        
        for entry in to_consolidate:
            entry.memory_type = 'working'
            self.working[entry.id] = entry
        
        logger.info(f"📦 Consolidated {len(to_consolidate)} memories to working memory")
    
    def consolidate_to_long_term(self, memory_id: str):
        """Promote a memory to long-term storage"""
        if memory_id in self.working:
            entry = self.working.pop(memory_id)
            entry.memory_type = 'long_term'
            self.long_term[entry.id] = entry
            self._save_persistent_memory()
            logger.info(f"💾 Consolidated memory to long-term: {memory_id}")
    
    def retrieve(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        include_types: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[MemoryEntry]:
        """Retrieve relevant memories based on query"""
        include_types = include_types or ['short_term', 'working', 'long_term']
        results = []
        query_lower = query.lower()
        
        # Search short-term memory for session
        if 'short_term' in include_types and session_id:
            if session_id in self.short_term:
                for entry in self.short_term[session_id]:
                    if self._matches(entry, query_lower):
                        entry.access_count += 1
                        results.append(entry)
        
        # Search working memory
        if 'working' in include_types:
            for entry in self.working.values():
                if session_id and entry.session_id != session_id:
                    continue
                if self._matches(entry, query_lower):
                    entry.access_count += 1
                    results.append(entry)
        
        # Search long-term memory
        if 'long_term' in include_types:
            for entry in self.long_term.values():
                if self._matches(entry, query_lower):
                    entry.access_count += 1
                    results.append(entry)
        
        # Sort by relevance and access count
        results.sort(key=lambda x: (x.relevance_score, x.access_count), reverse=True)
        
        return results[:max_results]
    
    def _matches(self, entry: MemoryEntry, query: str) -> bool:
        """Check if memory entry matches query"""
        # Simple keyword matching (can be enhanced with embeddings)
        content_lower = entry.content.lower()
        query_words = query.split()
        
        matches = sum(1 for word in query_words if word in content_lower)
        entry.relevance_score = matches / len(query_words) if query_words else 0
        
        return matches > 0 or any(tag.lower() in query for tag in entry.tags)
    
    def get_session_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get context for a session"""
        return self.contexts.get(session_id)
    
    def update_session_context(
        self, 
        session_id: str, 
        message: Dict[str, str],
        codex_session_id: Optional[str] = None
    ):
        """Update session context with new message"""
        if session_id not in self.contexts:
            self.create_session(session_id)
        
        ctx = self.contexts[session_id]
        ctx.messages.append(message)
        ctx.updated_at = datetime.utcnow().isoformat()
        
        if codex_session_id:
            ctx.codex_session_id = codex_session_id
        
        # Add to short-term memory
        self.add_memory(
            content=message.get('content', ''),
            session_id=session_id,
            memory_type='short_term',
            metadata={'role': message.get('role', 'user')}
        )
    
    def link_codex_session(self, chat_session_id: str, codex_session_id: str):
        """Link a chat session to a Codex session for context sharing"""
        if chat_session_id in self.contexts:
            self.contexts[chat_session_id].codex_session_id = codex_session_id
            logger.info(f"🔗 Linked chat {chat_session_id} to Codex {codex_session_id}")
    
    def get_shared_context(self, session_id: str) -> Dict[str, Any]:
        """Get shared context between chat and Codex sessions"""
        if session_id not in self.contexts:
            return {}
        
        ctx = self.contexts[session_id]
        
        # Get recent memories
        recent_memories = self.short_term.get(session_id, [])[-20:]
        
        # Get working memory for session
        working_memories = [
            m for m in self.working.values() 
            if m.session_id == session_id
        ]
        
        return {
            'session_id': session_id,
            'codex_session_id': ctx.codex_session_id,
            'recent_messages': ctx.messages[-10:],
            'recent_memories': [asdict(m) for m in recent_memories],
            'working_memories': [asdict(m) for m in working_memories],
            'long_term_count': len(self.long_term)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_short_term = sum(len(m) for m in self.short_term.values())
        
        return {
            'sessions': len(self.contexts),
            'short_term_memories': total_short_term,
            'working_memories': len(self.working),
            'long_term_memories': len(self.long_term),
            'total_memories': total_short_term + len(self.working) + len(self.long_term)
        }


class PersistentContextManager:
    """
    Manages persistent context sharing between chats and Codex sessions.
    
    Enables seamless transitions across conversations while maintaining
    shared state and knowledge.
    """
    
    def __init__(self, memory: HierarchicalMemory):
        self.memory = memory
        self.shared_contexts: Dict[str, Dict[str, Any]] = {}
    
    def create_shared_context(self, name: str) -> str:
        """Create a named shared context that can be accessed by multiple sessions"""
        context_id = hashlib.sha256(f"{name}{datetime.utcnow()}".encode()).hexdigest()[:16]
        
        self.shared_contexts[context_id] = {
            'name': name,
            'created_at': datetime.utcnow().isoformat(),
            'sessions': [],
            'data': {},
            'memories': []
        }
        
        return context_id
    
    def join_context(self, context_id: str, session_id: str):
        """Join a session to a shared context"""
        if context_id in self.shared_contexts:
            if session_id not in self.shared_contexts[context_id]['sessions']:
                self.shared_contexts[context_id]['sessions'].append(session_id)
                logger.info(f"🤝 Session {session_id} joined context {context_id}")
    
    def share_data(self, context_id: str, key: str, value: Any):
        """Share data within a context"""
        if context_id in self.shared_contexts:
            self.shared_contexts[context_id]['data'][key] = value
    
    def get_shared_data(self, context_id: str) -> Dict[str, Any]:
        """Get all shared data for a context"""
        if context_id in self.shared_contexts:
            return self.shared_contexts[context_id]['data']
        return {}
    
    def broadcast_memory(self, context_id: str, memory: MemoryEntry):
        """Broadcast a memory to all sessions in a shared context"""
        if context_id in self.shared_contexts:
            self.shared_contexts[context_id]['memories'].append(asdict(memory))
            
            # Add memory to all sessions in context
            for session_id in self.shared_contexts[context_id]['sessions']:
                self.memory.add_memory(
                    content=memory.content,
                    session_id=session_id,
                    memory_type='working',
                    tags=['shared', f'context:{context_id}']
                )


# Global memory instance for the application
_memory_instance: Optional[HierarchicalMemory] = None


def get_memory() -> HierarchicalMemory:
    """Get or create the global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = HierarchicalMemory()
    return _memory_instance


def main():
    """Demo: Memory System for ChatGPT 2.0"""
    print("\n" + "=" * 60)
    print("🧠 THE FORGE - Memory System for ChatGPT 2.0")
    print("=" * 60 + "\n")
    
    # Initialize memory system
    memory = get_memory()
    
    # Create a session
    session_id = memory.create_session()
    print(f"Created session: {session_id}\n")
    
    # Add some memories
    memory.add_memory(
        content="User is working on a Python project",
        session_id=session_id,
        tags=['python', 'project']
    )
    
    memory.add_memory(
        content="User prefers detailed explanations",
        session_id=session_id,
        tags=['preference', 'style']
    )
    
    # Update session context
    memory.update_session_context(
        session_id,
        {'role': 'user', 'content': 'Help me with video editing'}
    )
    
    memory.update_session_context(
        session_id,
        {'role': 'assistant', 'content': 'I can help with video editing using THE FORGE'}
    )
    
    # Link to a Codex session
    codex_session = "codex_" + session_id[:8]
    memory.link_codex_session(session_id, codex_session)
    
    # Retrieve memories
    print("Retrieving memories for 'python project':")
    results = memory.retrieve("python project", session_id)
    for r in results:
        print(f"  - {r.content} (relevance: {r.relevance_score:.2f})")
    
    # Get shared context
    print("\nShared context:")
    context = memory.get_shared_context(session_id)
    print(f"  Session: {context['session_id']}")
    print(f"  Codex Session: {context['codex_session_id']}")
    print(f"  Recent Messages: {len(context['recent_messages'])}")
    print(f"  Recent Memories: {len(context['recent_memories'])}")
    
    # Get stats
    print("\nMemory System Stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Memory System Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
