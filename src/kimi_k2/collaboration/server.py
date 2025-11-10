"""Multi-user collaboration server."""

from typing import Dict, List, Any, Optional, Set
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime

from kimi_k2.core.config import CollaborationConfig


logger = logging.getLogger(__name__)


@dataclass
class User:
    """Represents a connected user."""
    id: str
    name: str
    connected_at: datetime
    active_module: Optional[str] = None


@dataclass
class CollaborationSession:
    """Represents a collaboration session."""
    id: str
    name: str
    created_at: datetime
    users: Set[str]
    shared_state: Dict[str, Any]


class CollaborationServer:
    """Server for multi-user collaboration."""
    
    def __init__(self, config: CollaborationConfig):
        """Initialize collaboration server.
        
        Args:
            config: Collaboration configuration
        """
        self.config = config
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, CollaborationSession] = {}
        self.running = False
        
        logger.info(f"Collaboration server initialized on {config.server_host}:{config.server_port}")
        
    async def start(self) -> None:
        """Start the collaboration server."""
        if self.running:
            logger.warning("Server already running")
            return
            
        logger.info("Starting collaboration server")
        self.running = True
        
        # Placeholder for actual server startup
        await asyncio.sleep(0.1)
        logger.info("Collaboration server started")
        
    async def stop(self) -> None:
        """Stop the collaboration server."""
        if not self.running:
            return
            
        logger.info("Stopping collaboration server")
        self.running = False
        
        # Disconnect all users
        for user_id in list(self.users.keys()):
            await self.disconnect_user(user_id)
            
        logger.info("Collaboration server stopped")
        
    async def connect_user(self, user_id: str, user_name: str) -> User:
        """Connect a new user.
        
        Args:
            user_id: Unique user identifier
            user_name: User display name
            
        Returns:
            Connected user object
        """
        if len(self.users) >= self.config.max_users:
            raise RuntimeError(f"Maximum users ({self.config.max_users}) reached")
            
        user = User(
            id=user_id,
            name=user_name,
            connected_at=datetime.now()
        )
        
        self.users[user_id] = user
        logger.info(f"User connected: {user_name} ({user_id})")
        
        return user
        
    async def disconnect_user(self, user_id: str) -> None:
        """Disconnect a user.
        
        Args:
            user_id: User identifier
        """
        if user_id not in self.users:
            return
            
        user = self.users[user_id]
        
        # Remove from all sessions
        for session in self.sessions.values():
            if user_id in session.users:
                session.users.remove(user_id)
                
        del self.users[user_id]
        logger.info(f"User disconnected: {user.name} ({user_id})")
        
    def create_session(self, session_id: str, session_name: str, creator_id: str) -> CollaborationSession:
        """Create a new collaboration session.
        
        Args:
            session_id: Unique session identifier
            session_name: Session display name
            creator_id: ID of user creating the session
            
        Returns:
            Created session object
        """
        if creator_id not in self.users:
            raise ValueError(f"User not found: {creator_id}")
            
        session = CollaborationSession(
            id=session_id,
            name=session_name,
            created_at=datetime.now(),
            users={creator_id},
            shared_state={}
        )
        
        self.sessions[session_id] = session
        logger.info(f"Session created: {session_name} ({session_id})")
        
        return session
        
    def join_session(self, session_id: str, user_id: str) -> None:
        """Add a user to a session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
            
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
            
        session = self.sessions[session_id]
        session.users.add(user_id)
        
        user = self.users[user_id]
        logger.info(f"User {user.name} joined session {session.name}")
        
    def leave_session(self, session_id: str, user_id: str) -> None:
        """Remove a user from a session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
        """
        if session_id not in self.sessions:
            return
            
        session = self.sessions[session_id]
        
        if user_id in session.users:
            session.users.remove(user_id)
            user = self.users.get(user_id)
            if user:
                logger.info(f"User {user.name} left session {session.name}")
                
        # Delete empty sessions
        if not session.users:
            del self.sessions[session_id]
            logger.info(f"Deleted empty session: {session.name}")
            
    def update_shared_state(self, session_id: str, key: str, value: Any) -> None:
        """Update shared state in a session.
        
        Args:
            session_id: Session identifier
            key: State key
            value: State value
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
            
        session = self.sessions[session_id]
        session.shared_state[key] = value
        logger.debug(f"Updated shared state in session {session.name}: {key}")
        
    def get_session_users(self, session_id: str) -> List[User]:
        """Get all users in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of users in the session
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
            
        session = self.sessions[session_id]
        return [self.users[user_id] for user_id in session.users if user_id in self.users]
        
    def shutdown(self) -> None:
        """Cleanup collaboration server resources."""
        logger.info("Shutting down collaboration server")
        
        # This is sync, so we can't await stop()
        self.running = False
        self.users.clear()
        self.sessions.clear()
