"""
Conversation Manager
Handles multi-user sessions and conversation flow
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class ConversationManager:
    """
    Manages multi-user conversation sessions.
    
    Features:
    - Session management
    - Multi-user support
    - Message threading
    - Conversation state tracking
    """
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.active_users: Dict[str, List[str]] = {}
    
    def create_session(
        self,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional session metadata
            
        Returns:
            Session information
        """
        if session_id in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} already exists"
            }
        
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "users": [],
            "metadata": metadata or {},
            "state": "active"
        }
        
        return {
            "status": "success",
            "session_id": session_id,
            "created_at": self.sessions[session_id]["created_at"]
        }
    
    def add_user_to_session(
        self,
        session_id: str,
        user_id: str,
        user_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a user to a session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            user_info: Optional user information
            
        Returns:
            Operation result
        """
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found"
            }
        
        session = self.sessions[session_id]
        
        if user_id not in session["users"]:
            session["users"].append(user_id)
            
            # Track active sessions for user
            if user_id not in self.active_users:
                self.active_users[user_id] = []
            self.active_users[user_id].append(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "user_id": user_id,
            "total_users": len(session["users"])
        }
    
    def add_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        message_type: str = "user",
    ) -> Dict[str, Any]:
        """
        Add a message to a session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            message: Message content
            message_type: Message type ('user', 'assistant', 'system')
            
        Returns:
            Message information
        """
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found"
            }
        
        session = self.sessions[session_id]
        
        message_obj = {
            "id": len(session["messages"]),
            "session_id": session_id,
            "user_id": user_id,
            "content": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
        session["messages"].append(message_obj)
        
        return {
            "status": "success",
            "message_id": message_obj["id"],
            "timestamp": message_obj["timestamp"]
        }
    
    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages
            user_id: Optional filter by user
            
        Returns:
            Session history
        """
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found"
            }
        
        session = self.sessions[session_id]
        messages = session["messages"]
        
        if user_id:
            messages = [m for m in messages if m["user_id"] == user_id]
        
        if limit:
            messages = messages[-limit:]
        
        return {
            "status": "success",
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(session["messages"]),
            "filtered_count": len(messages)
        }
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        return self.active_users.get(user_id, [])
    
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Operation result
        """
        if session_id not in self.sessions:
            return {
                "status": "error",
                "message": f"Session {session_id} not found"
            }
        
        self.sessions[session_id]["state"] = "closed"
        self.sessions[session_id]["closed_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "session_id": session_id,
            "message_count": len(self.sessions[session_id]["messages"])
        }
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export session as JSON.
        
        Args:
            session_id: Session identifier
            
        Returns:
            JSON string of session data
        """
        if session_id not in self.sessions:
            return None
        
        return json.dumps(self.sessions[session_id], indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics.
        
        Returns:
            Statistics about sessions and users
        """
        active_sessions = len([s for s in self.sessions.values() if s["state"] == "active"])
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_users": len(self.active_users),
            "total_messages": sum(len(s["messages"]) for s in self.sessions.values())
        }
