#!/usr/bin/env python3
"""
THE FORGE - Unified Chat Interface for ChatGPT 2.0
===================================================

Merges existing chat components into a single interface with hierarchical
memory support, enabling seamless transitions across conversations and
persistent context-sharing between chats and Codex sessions.

Features:
- Unified chat interface
- Hierarchical memory integration
- Codex integration for documentation
- Plugin system integration
- Cross-session context sharing
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

# Import forge modules
from forge_memory import get_memory, HierarchicalMemory, PersistentContextManager
from forge_codex import get_codex, CodexSystem
from forge_collaboration import get_collaboration, CollaborationSystem
from forge_plugins import get_plugins, PluginSystem

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a chat message"""
    id: str = ""
    role: str = "user"  # user, assistant, system
    content: str = ""
    timestamp: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.id:
            import hashlib
            self.id = hashlib.sha256(
                f"{self.content}{self.timestamp}".encode()
            ).hexdigest()[:16]


@dataclass
class ChatSession:
    """Represents a chat session"""
    id: str
    created_at: str
    updated_at: str
    title: Optional[str] = None
    messages: List[ChatMessage] = field(default_factory=list)
    codex_session_id: Optional[str] = None
    shared_context_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedChatInterface:
    """
    Unified Chat Interface for ChatGPT 2.0
    
    Provides:
    - Single interface for all chat interactions
    - Hierarchical memory support
    - Codex integration for documentation
    - Cross-session context sharing
    - Plugin system integration
    """
    
    def __init__(self):
        # Initialize subsystems
        self.memory = get_memory()
        self.codex = get_codex()
        self.collaboration = get_collaboration()
        self.plugins = get_plugins()
        
        # Session management
        self.sessions: Dict[str, ChatSession] = {}
        self.active_session: Optional[str] = None
        
        # Context manager for persistent sharing
        self.context_manager = PersistentContextManager(self.memory)
        
        # Message handlers
        self.message_handlers: List[Callable] = []
        
        # Register with collaboration system
        self.collaboration.register_module(
            "unified_chat",
            capabilities=["chat", "memory", "codex_integration"]
        )
        
        logger.info("✅ Unified Chat Interface initialized")
    
    def create_session(
        self, 
        title: Optional[str] = None,
        link_codex: bool = True
    ) -> ChatSession:
        """Create a new chat session"""
        import hashlib
        
        now = datetime.utcnow().isoformat()
        session_id = hashlib.sha256(now.encode()).hexdigest()[:16]
        
        # Create memory session
        self.memory.create_session(session_id)
        
        # Create codex session if linked
        codex_session_id = None
        if link_codex:
            codex_session_id = f"codex_{session_id[:8]}"
            self.memory.link_codex_session(session_id, codex_session_id)
        
        session = ChatSession(
            id=session_id,
            created_at=now,
            updated_at=now,
            title=title or f"Session {session_id[:8]}",
            codex_session_id=codex_session_id
        )
        
        self.sessions[session_id] = session
        self.active_session = session_id
        
        # Execute plugin hook
        self.plugins.execute_hook("on_session_start", {
            "session_id": session_id,
            "codex_linked": link_codex
        })
        
        logger.info(f"🆕 Created session: {session.title} ({session_id})")
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def set_active_session(self, session_id: str) -> bool:
        """Set the active session"""
        if session_id in self.sessions:
            self.active_session = session_id
            return True
        return False
    
    def send_message(
        self, 
        content: str,
        role: str = "user",
        session_id: Optional[str] = None,
        use_memory: bool = True,
        use_codex: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Send a message in a chat session"""
        
        # Use active session if not specified
        if not session_id:
            if not self.active_session:
                session = self.create_session()
                session_id = session.id
            else:
                session_id = self.active_session
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Create message
        message = ChatMessage(
            role=role,
            content=content,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        # Execute pre-processing hook
        hook_data = self.plugins.execute_hook("before_process", {
            "message": asdict(message),
            "session_id": session_id
        })
        
        # Update session
        session.messages.append(message)
        session.updated_at = datetime.utcnow().isoformat()
        
        # Store in memory
        if use_memory:
            self.memory.update_session_context(
                session_id,
                {"role": role, "content": content}
            )
        
        # Execute post-processing hook
        self.plugins.execute_hook("after_process", {
            "message": asdict(message),
            "session_id": session_id
        })
        
        # Notify handlers
        for handler in self.message_handlers:
            try:
                handler(message, session)
            except Exception as e:
                logger.error(f"❌ Handler error: {e}")
        
        return message
    
    def get_response(
        self, 
        user_message: str,
        session_id: Optional[str] = None,
        include_memory: bool = True,
        include_codex: bool = True
    ) -> ChatMessage:
        """Get an AI response to a user message"""
        
        # Send user message
        self.send_message(user_message, role="user", session_id=session_id)
        
        if not session_id:
            session_id = self.active_session
        
        session = self.sessions.get(session_id)
        
        # Build context
        context = self._build_context(session_id, include_memory, include_codex)
        
        # Generate response (placeholder - would integrate with actual model)
        response_content = self._generate_response(user_message, context, session)
        
        # Send assistant message
        response = self.send_message(
            response_content,
            role="assistant",
            session_id=session_id,
            metadata={"context_used": bool(context)}
        )
        
        return response
    
    def _build_context(
        self, 
        session_id: str,
        include_memory: bool,
        include_codex: bool
    ) -> Dict[str, Any]:
        """Build context for response generation"""
        context = {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if include_memory:
            # Get recent memories
            session = self.sessions.get(session_id)
            if session and session.messages:
                recent_content = " ".join(
                    m.content for m in session.messages[-5:]
                )
                memories = self.memory.retrieve(
                    recent_content, 
                    session_id,
                    max_results=5
                )
                context["memories"] = [
                    {"content": m.content, "relevance": m.relevance_score}
                    for m in memories
                ]
            
            # Get shared context
            shared = self.memory.get_shared_context(session_id)
            context["shared_context"] = shared
        
        if include_codex:
            # Search Codex for relevant documentation
            session = self.sessions.get(session_id)
            if session and session.messages:
                last_message = session.messages[-1].content
                codex_results = self.codex.search(last_message, max_results=3)
                context["codex_results"] = [
                    {
                        "title": r.document.title,
                        "highlights": r.highlights[:2],
                        "relevance": r.relevance_score
                    }
                    for r in codex_results
                ]
        
        return context
    
    def _generate_response(
        self, 
        user_message: str,
        context: Dict[str, Any],
        session: Optional[ChatSession]
    ) -> str:
        """Generate a response (placeholder for actual model integration)"""
        
        response_parts = [
            f"Processing: {user_message}\n"
        ]
        
        # Add context information
        if context.get("memories"):
            response_parts.append("\n📚 Relevant memories found:")
            for m in context["memories"]:
                response_parts.append(f"  - {m['content'][:50]}...")
        
        if context.get("codex_results"):
            response_parts.append("\n📖 Relevant documentation found:")
            for r in context["codex_results"]:
                response_parts.append(f"  - {r['title']}")
        
        response_parts.append("\n\nIn production, this would use Kimi K2 with:")
        response_parts.append("- Full context from memory system")
        response_parts.append("- Relevant Codex documentation")
        response_parts.append("- Plugin enhancements")
        response_parts.append("- Cross-session learning")
        
        return "\n".join(response_parts)
    
    def search_history(
        self, 
        query: str,
        session_id: Optional[str] = None,
        max_results: int = 10
    ) -> List[ChatMessage]:
        """Search chat history"""
        results = []
        query_lower = query.lower()
        
        sessions_to_search = (
            [self.sessions[session_id]] if session_id and session_id in self.sessions
            else list(self.sessions.values())
        )
        
        for session in sessions_to_search:
            for message in session.messages:
                if query_lower in message.content.lower():
                    results.append(message)
                    if len(results) >= max_results:
                        return results
        
        return results
    
    def link_to_codex(self, session_id: str, codex_session_id: str):
        """Link a chat session to a Codex session"""
        if session_id in self.sessions:
            self.sessions[session_id].codex_session_id = codex_session_id
            self.memory.link_codex_session(session_id, codex_session_id)
            logger.info(f"🔗 Linked session {session_id} to Codex {codex_session_id}")
    
    def create_shared_context(self, name: str) -> str:
        """Create a shared context for multiple sessions"""
        context_id = self.context_manager.create_shared_context(name)
        logger.info(f"📦 Created shared context: {name} ({context_id})")
        return context_id
    
    def join_shared_context(self, session_id: str, context_id: str):
        """Join a session to a shared context"""
        self.context_manager.join_context(context_id, session_id)
        if session_id in self.sessions:
            self.sessions[session_id].shared_context_id = context_id
    
    def add_message_handler(self, handler: Callable):
        """Add a handler for new messages"""
        self.message_handlers.append(handler)
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a conversation"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        user_messages = [m for m in session.messages if m.role == "user"]
        assistant_messages = [m for m in session.messages if m.role == "assistant"]
        
        return {
            "session_id": session_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "total_messages": len(session.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "codex_linked": session.codex_session_id is not None,
            "shared_context": session.shared_context_id
        }
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export a session for backup/transfer"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        return {
            "session": asdict(session) if hasattr(session, '__dataclass_fields__') else {
                "id": session.id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "title": session.title,
                "messages": [asdict(m) for m in session.messages],
                "codex_session_id": session.codex_session_id,
                "shared_context_id": session.shared_context_id,
                "metadata": session.metadata
            },
            "memory_context": self.memory.get_shared_context(session_id),
            "exported_at": datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get interface statistics"""
        total_messages = sum(len(s.messages) for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_session": self.active_session,
            "total_messages": total_messages,
            "memory_stats": self.memory.get_stats(),
            "codex_stats": self.codex.get_stats(),
            "plugin_stats": self.plugins.get_stats(),
            "collaboration_stats": self.collaboration.get_stats()
        }


# Global instance
_chat_interface: Optional[UnifiedChatInterface] = None


def get_chat_interface() -> UnifiedChatInterface:
    """Get or create the global chat interface"""
    global _chat_interface
    if _chat_interface is None:
        _chat_interface = UnifiedChatInterface()
    return _chat_interface


def main():
    """Demo: Unified Chat Interface for ChatGPT 2.0"""
    print("\n" + "=" * 70)
    print("💬 THE FORGE - Unified Chat Interface for ChatGPT 2.0")
    print("=" * 70 + "\n")
    
    # Initialize interface
    chat = get_chat_interface()
    
    # Create a session
    session = chat.create_session(title="Demo Conversation")
    print(f"Created session: {session.title} ({session.id})")
    
    # Add some Codex documents for context
    chat.codex.add_document(
        title="Video Editing Best Practices",
        content="# Video Editing\n\nBest practices for professional video editing...",
        doc_type="markdown",
        tags=["video", "editing", "guide"]
    )
    
    # Send messages
    print("\n📝 Sending messages...")
    
    chat.send_message("Hello, I need help with video editing")
    response = chat.get_response(
        "What are the best practices for video timeline management?"
    )
    
    print(f"\n🤖 Response:\n{response.content}")
    
    # Search history
    print("\n🔍 Searching history for 'video':")
    results = chat.search_history("video")
    for r in results:
        print(f"  [{r.role}] {r.content[:50]}...")
    
    # Create shared context
    print("\n📦 Creating shared context...")
    context_id = chat.create_shared_context("video_project")
    chat.join_shared_context(session.id, context_id)
    
    # Get conversation summary
    print("\n📊 Conversation Summary:")
    summary = chat.get_conversation_summary(session.id)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Get overall stats
    print("\n📈 Interface Statistics:")
    stats = chat.get_stats()
    print(f"  Sessions: {stats['total_sessions']}")
    print(f"  Messages: {stats['total_messages']}")
    print(f"  Memory entries: {stats['memory_stats']['total_memories']}")
    print(f"  Codex documents: {stats['codex_stats']['total_documents']}")
    
    print("\n" + "=" * 70)
    print("✅ Unified Chat Interface Demo Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
