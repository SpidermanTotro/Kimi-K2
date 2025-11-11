"""
Unit tests for Interaction module
"""

import pytest
from kimi_k2.interaction import (
    ConversationManager,
    PersonalizationEngine,
    MemoryModule
)


class TestConversationManager:
    """Test suite for ConversationManager."""
    
    def test_create_session(self):
        """Test session creation."""
        manager = ConversationManager()
        result = manager.create_session("session_1", metadata={"topic": "AI"})
        
        assert result["status"] == "success"
        assert result["session_id"] == "session_1"
        assert "created_at" in result
    
    def test_duplicate_session(self):
        """Test creating duplicate session."""
        manager = ConversationManager()
        manager.create_session("session_1")
        result = manager.create_session("session_1")
        
        assert result["status"] == "error"
    
    def test_add_user_to_session(self):
        """Test adding user to session."""
        manager = ConversationManager()
        manager.create_session("session_1")
        result = manager.add_user_to_session("session_1", "user_1")
        
        assert result["status"] == "success"
        assert result["user_id"] == "user_1"
        assert result["total_users"] == 1
    
    def test_add_message(self):
        """Test adding message."""
        manager = ConversationManager()
        manager.create_session("session_1")
        manager.add_user_to_session("session_1", "user_1")
        
        result = manager.add_message("session_1", "user_1", "Hello", "user")
        
        assert result["status"] == "success"
        assert "message_id" in result
        assert "timestamp" in result
    
    def test_get_session_history(self):
        """Test getting session history."""
        manager = ConversationManager()
        manager.create_session("session_1")
        manager.add_user_to_session("session_1", "user_1")
        manager.add_message("session_1", "user_1", "Message 1", "user")
        manager.add_message("session_1", "user_1", "Message 2", "user")
        
        result = manager.get_session_history("session_1")
        
        assert result["status"] == "success"
        assert result["total_messages"] == 2
        assert len(result["messages"]) == 2
    
    def test_get_stats(self):
        """Test manager statistics."""
        manager = ConversationManager()
        manager.create_session("session_1")
        manager.create_session("session_2")
        manager.add_user_to_session("session_1", "user_1")
        
        stats = manager.get_stats()
        
        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 2
        assert stats["total_users"] == 1


class TestPersonalizationEngine:
    """Test suite for PersonalizationEngine."""
    
    def test_create_profile(self):
        """Test profile creation."""
        engine = PersonalizationEngine()
        result = engine.create_profile("user_1", preferences={"lang": "en"})
        
        assert result["status"] == "success"
        assert result["user_id"] == "user_1"
    
    def test_update_preferences(self):
        """Test updating preferences."""
        engine = PersonalizationEngine()
        engine.create_profile("user_1", preferences={"lang": "en"})
        
        result = engine.update_preferences("user_1", {"theme": "dark"})
        
        assert result["status"] == "success"
        assert "lang" in result["preferences"]
        assert "theme" in result["preferences"]
    
    def test_record_interaction(self):
        """Test recording interaction."""
        engine = PersonalizationEngine()
        engine.create_profile("user_1")
        
        result = engine.record_interaction(
            "user_1",
            "query",
            {"topics": ["AI", "ML"]}
        )
        
        assert result["status"] == "success"
        assert result["interaction_recorded"] is True
    
    def test_learned_preferences(self):
        """Test preference learning."""
        engine = PersonalizationEngine()
        engine.create_profile("user_1")
        
        # Record multiple interactions
        engine.record_interaction("user_1", "query", {"topics": ["AI"]})
        engine.record_interaction("user_1", "query", {"topics": ["AI", "ML"]})
        
        prefs = engine.get_preferences("user_1")
        
        assert "learned_preferences" in prefs
        assert "preferred_topics" in prefs["learned_preferences"]
        assert "AI" in prefs["learned_preferences"]["preferred_topics"]
    
    def test_export_import_profile(self):
        """Test profile export and import."""
        engine = PersonalizationEngine()
        engine.create_profile("user_1", preferences={"test": "value"})
        
        # Export
        exported = engine.export_profile("user_1")
        assert exported is not None
        
        # Import to new user
        result = engine.import_profile("user_2", exported)
        assert result["status"] == "success"


class TestMemoryModule:
    """Test suite for MemoryModule."""
    
    def test_store_memory(self):
        """Test storing memory."""
        memory = MemoryModule()
        result = memory.store_memory(
            "user_1",
            "Test memory",
            category="test",
            tags=["tag1", "tag2"]
        )
        
        assert result["status"] == "success"
        assert "memory_id" in result
    
    def test_recall_by_category(self):
        """Test recalling memories by category."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Memory 1", category="work")
        memory.store_memory("user_1", "Memory 2", category="personal")
        memory.store_memory("user_1", "Memory 3", category="work")
        
        result = memory.recall_memories("user_1", category="work")
        
        assert result["count"] == 2
        assert all(m["category"] == "work" for m in result["memories"])
    
    def test_recall_by_tags(self):
        """Test recalling memories by tags."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Memory 1", tags=["ai", "ml"])
        memory.store_memory("user_1", "Memory 2", tags=["web"])
        memory.store_memory("user_1", "Memory 3", tags=["ai"])
        
        result = memory.recall_memories("user_1", tags=["ai"])
        
        assert result["count"] == 2
    
    def test_search_memories(self):
        """Test searching memories."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Python programming tutorial")
        memory.store_memory("user_1", "JavaScript basics")
        memory.store_memory("user_1", "Advanced Python techniques")
        
        result = memory.search_memories("user_1", "python")
        
        assert result["count"] == 2
        assert all("python" in m["content"].lower() for m in result["memories"])
    
    def test_consolidate_memories(self):
        """Test memory consolidation."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Memory 1", category="work")
        memory.store_memory("user_1", "Memory 2", category="work")
        memory.store_memory("user_1", "Memory 3", category="personal")
        
        result = memory.consolidate_memories("user_1")
        
        assert result["status"] == "success"
        assert result["categories"] == 2
        assert "work" in result["consolidated"]
        assert "personal" in result["consolidated"]
    
    def test_get_memory_stats(self):
        """Test memory statistics."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Memory 1", category="cat1")
        memory.store_memory("user_1", "Memory 2", category="cat2")
        memory.store_memory("user_1", "Memory 3", category="cat1")
        
        stats = memory.get_memory_stats("user_1")
        
        assert stats["total_memories"] == 3
        assert stats["categories"] == 2
        assert "cat1" in stats["category_list"]
        assert "cat2" in stats["category_list"]
    
    def test_clear_memories(self):
        """Test clearing memories."""
        memory = MemoryModule()
        memory.store_memory("user_1", "Memory 1", category="test")
        memory.store_memory("user_1", "Memory 2", category="test")
        
        result = memory.clear_memories("user_1")
        
        assert result["status"] == "success"
        assert result["cleared_count"] == 2
        
        stats = memory.get_memory_stats("user_1")
        assert stats["total_memories"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
