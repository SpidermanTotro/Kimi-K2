"""Tests for collaboration server functionality."""

import pytest
import asyncio

from kimi_k2.collaboration.server import CollaborationServer, User, CollaborationSession
from kimi_k2.core.config import CollaborationConfig


class TestCollaborationServer:
    """Test collaboration server functionality."""
    
    @pytest.fixture
    def collab_server(self):
        """Create collaboration server for testing."""
        config = CollaborationConfig(
            server_host="localhost",
            server_port=8080,
            max_users=5
        )
        return CollaborationServer(config)
        
    def test_server_initialization(self, collab_server):
        """Test server initialization."""
        assert collab_server is not None
        assert not collab_server.running
        
    @pytest.mark.asyncio
    async def test_server_start_stop(self, collab_server):
        """Test starting and stopping server."""
        await collab_server.start()
        assert collab_server.running
        
        await collab_server.stop()
        assert not collab_server.running
        
    @pytest.mark.asyncio
    async def test_connect_user(self, collab_server):
        """Test connecting a user."""
        user = await collab_server.connect_user("user1", "Alice")
        
        assert user.id == "user1"
        assert user.name == "Alice"
        assert "user1" in collab_server.users
        
    @pytest.mark.asyncio
    async def test_disconnect_user(self, collab_server):
        """Test disconnecting a user."""
        await collab_server.connect_user("user1", "Alice")
        await collab_server.disconnect_user("user1")
        
        assert "user1" not in collab_server.users
        
    @pytest.mark.asyncio
    async def test_max_users_limit(self, collab_server):
        """Test maximum users limit is enforced."""
        # Connect max users
        for i in range(collab_server.config.max_users):
            await collab_server.connect_user(f"user{i}", f"User{i}")
            
        # Try to connect one more
        with pytest.raises(RuntimeError):
            await collab_server.connect_user("extra", "Extra User")


class TestCollaborationSession:
    """Test collaboration session functionality."""
    
    @pytest.fixture
    def collab_server(self):
        """Create collaboration server for testing."""
        config = CollaborationConfig()
        return CollaborationServer(config)
        
    @pytest.mark.asyncio
    async def test_create_session(self, collab_server):
        """Test creating a session."""
        await collab_server.connect_user("user1", "Alice")
        session = collab_server.create_session("session1", "Test Session", "user1")
        
        assert session.id == "session1"
        assert session.name == "Test Session"
        assert "user1" in session.users
        
    @pytest.mark.asyncio
    async def test_create_session_invalid_user(self, collab_server):
        """Test creating session with invalid user raises error."""
        with pytest.raises(ValueError):
            collab_server.create_session("session1", "Test", "nonexistent")
            
    @pytest.mark.asyncio
    async def test_join_session(self, collab_server):
        """Test joining a session."""
        await collab_server.connect_user("user1", "Alice")
        await collab_server.connect_user("user2", "Bob")
        
        collab_server.create_session("session1", "Test", "user1")
        collab_server.join_session("session1", "user2")
        
        session = collab_server.sessions["session1"]
        assert len(session.users) == 2
        assert "user2" in session.users
        
    @pytest.mark.asyncio
    async def test_leave_session(self, collab_server):
        """Test leaving a session."""
        await collab_server.connect_user("user1", "Alice")
        await collab_server.connect_user("user2", "Bob")
        
        collab_server.create_session("session1", "Test", "user1")
        collab_server.join_session("session1", "user2")
        collab_server.leave_session("session1", "user2")
        
        session = collab_server.sessions["session1"]
        assert "user2" not in session.users
        
    @pytest.mark.asyncio
    async def test_empty_session_deleted(self, collab_server):
        """Test empty sessions are automatically deleted."""
        await collab_server.connect_user("user1", "Alice")
        
        collab_server.create_session("session1", "Test", "user1")
        collab_server.leave_session("session1", "user1")
        
        assert "session1" not in collab_server.sessions


class TestSharedState:
    """Test shared state functionality."""
    
    @pytest.fixture
    def collab_server(self):
        """Create collaboration server for testing."""
        config = CollaborationConfig()
        return CollaborationServer(config)
        
    @pytest.mark.asyncio
    async def test_update_shared_state(self, collab_server):
        """Test updating shared state."""
        await collab_server.connect_user("user1", "Alice")
        collab_server.create_session("session1", "Test", "user1")
        
        collab_server.update_shared_state("session1", "key1", "value1")
        
        session = collab_server.sessions["session1"]
        assert session.shared_state["key1"] == "value1"
        
    @pytest.mark.asyncio
    async def test_update_shared_state_invalid_session(self, collab_server):
        """Test updating state for invalid session raises error."""
        with pytest.raises(ValueError):
            collab_server.update_shared_state("nonexistent", "key", "value")
            
    @pytest.mark.asyncio
    async def test_multiple_state_updates(self, collab_server):
        """Test multiple state updates."""
        await collab_server.connect_user("user1", "Alice")
        collab_server.create_session("session1", "Test", "user1")
        
        collab_server.update_shared_state("session1", "key1", "value1")
        collab_server.update_shared_state("session1", "key2", "value2")
        
        session = collab_server.sessions["session1"]
        assert len(session.shared_state) == 2


class TestSessionUsers:
    """Test session user management."""
    
    @pytest.fixture
    def collab_server(self):
        """Create collaboration server for testing."""
        config = CollaborationConfig()
        return CollaborationServer(config)
        
    @pytest.mark.asyncio
    async def test_get_session_users(self, collab_server):
        """Test getting users in a session."""
        await collab_server.connect_user("user1", "Alice")
        await collab_server.connect_user("user2", "Bob")
        
        collab_server.create_session("session1", "Test", "user1")
        collab_server.join_session("session1", "user2")
        
        users = collab_server.get_session_users("session1")
        
        assert len(users) == 2
        user_names = [u.name for u in users]
        assert "Alice" in user_names
        assert "Bob" in user_names
        
    @pytest.mark.asyncio
    async def test_get_users_invalid_session(self, collab_server):
        """Test getting users for invalid session raises error."""
        with pytest.raises(ValueError):
            collab_server.get_session_users("nonexistent")
            
    @pytest.mark.asyncio
    async def test_user_removal_from_sessions(self, collab_server):
        """Test disconnecting user removes from all sessions."""
        await collab_server.connect_user("user1", "Alice")
        await collab_server.connect_user("user2", "Bob")
        
        collab_server.create_session("session1", "Test1", "user1")
        collab_server.create_session("session2", "Test2", "user1")
        collab_server.join_session("session1", "user2")
        collab_server.join_session("session2", "user2")
        
        await collab_server.disconnect_user("user2")
        
        # Check user2 removed from both sessions
        assert "user2" not in collab_server.sessions["session1"].users
        assert "user2" not in collab_server.sessions["session2"].users
