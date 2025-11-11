"""
Test Suite for Dual Operator AI System

Basic tests for core functionality.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_operator_ai.core import (
    UserProfile,
    ContextManager,
    DecisionFusionEngine,
    FusionStrategy,
    DualOperatorEngine
)


class TestUserProfile(unittest.TestCase):
    """Test UserProfile functionality."""
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        user = UserProfile(
            user_id="test_user",
            name="Test User",
            preferences={"key": "value"},
            strengths=["strength1"],
            decision_weight=0.7
        )
        
        self.assertEqual(user.user_id, "test_user")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.preferences["key"], "value")
        self.assertEqual(user.decision_weight, 0.7)
    
    def test_update_preferences(self):
        """Test updating user preferences."""
        user = UserProfile(user_id="test", name="Test")
        user.update_preferences({"new_key": "new_value"})
        
        self.assertIn("new_key", user.preferences)
        self.assertEqual(user.preferences["new_key"], "new_value")
    
    def test_add_strength(self):
        """Test adding strengths."""
        user = UserProfile(user_id="test", name="Test")
        user.add_strength("coding")
        
        self.assertIn("coding", user.strengths)
    
    def test_decision_weight_validation(self):
        """Test decision weight validation."""
        user = UserProfile(user_id="test", name="Test")
        
        with self.assertRaises(ValueError):
            user.set_decision_weight(1.5)
        
        with self.assertRaises(ValueError):
            user.set_decision_weight(-0.1)
        
        # Valid weights should work
        user.set_decision_weight(0.5)
        self.assertEqual(user.decision_weight, 0.5)


class TestContextManager(unittest.TestCase):
    """Test ContextManager functionality."""
    
    def setUp(self):
        """Set up test context manager."""
        self.manager = ContextManager(max_context_length=100)
    
    def test_add_context(self):
        """Test adding context entries."""
        self.manager.add_context(
            user_id="user1",
            role="user",
            content="Hello",
            modality="text"
        )
        
        self.assertEqual(len(self.manager.context_history), 1)
        self.assertEqual(self.manager.context_history[0].content, "Hello")
    
    def test_get_user_context(self):
        """Test retrieving user-specific context."""
        self.manager.add_context("user1", "user", "Message 1")
        self.manager.add_context("user2", "user", "Message 2")
        
        user1_context = self.manager.get_context_for_user("user1")
        
        # Should include shared context plus user-specific
        self.assertTrue(len(user1_context) > 0)
    
    def test_combined_context(self):
        """Test getting combined context."""
        self.manager.add_context("user1", "user", "Message 1")
        self.manager.add_context("user2", "user", "Message 2")
        
        combined = self.manager.get_combined_context(["user1", "user2"])
        
        self.assertEqual(len(combined), 2)
    
    def test_context_summary(self):
        """Test context summary generation."""
        self.manager.add_context("user1", "user", "Text message", modality="text")
        self.manager.add_context("user1", "assistant", "Response", modality="text")
        
        summary = self.manager.get_context_summary()
        
        self.assertEqual(summary['total_entries'], 2)
        self.assertIn('text', summary['modality_counts'])


class TestDecisionFusionEngine(unittest.TestCase):
    """Test DecisionFusionEngine functionality."""
    
    def setUp(self):
        """Set up test fusion engine."""
        self.engine = DecisionFusionEngine(FusionStrategy.WEIGHTED_AVERAGE)
    
    def test_fuse_preferences_numeric(self):
        """Test fusing numeric preferences."""
        prefs1 = {"temperature": 0.7, "detail": 5}
        prefs2 = {"temperature": 0.3, "detail": 3}
        
        fused = self.engine.fuse_preferences(prefs1, prefs2, 0.5, 0.5)
        
        self.assertEqual(fused["temperature"], 0.5)
        self.assertEqual(fused["detail"], 4.0)
    
    def test_fuse_preferences_string(self):
        """Test fusing string preferences."""
        prefs1 = {"style": "formal"}
        prefs2 = {"style": "casual"}
        
        # Higher weight should win for strings
        fused = self.engine.fuse_preferences(prefs1, prefs2, 0.7, 0.3)
        
        self.assertEqual(fused["style"], "formal")
    
    def test_weighted_average_fusion(self):
        """Test weighted average decision fusion."""
        decisions = [
            {
                'user_id': 'user1',
                'weight': 0.6,
                'content': {'choice': 1, 'priority': 'high'}
            },
            {
                'user_id': 'user2',
                'weight': 0.4,
                'content': {'choice': 2, 'priority': 'low'}
            }
        ]
        
        result = self.engine.fuse_decisions(decisions)
        
        self.assertIn('content', result)
    
    def test_consensus_fusion(self):
        """Test consensus-based fusion."""
        engine = DecisionFusionEngine(FusionStrategy.CONSENSUS)
        
        decisions = [
            {'content': {'agreed_item': 'value', 'disputed': 'a'}},
            {'content': {'agreed_item': 'value', 'disputed': 'b'}}
        ]
        
        result = engine.fuse_decisions(decisions)
        
        self.assertIn('consensus_items', result)
        self.assertIn('divergent_items', result)


class TestDualOperatorEngine(unittest.TestCase):
    """Test DualOperatorEngine functionality."""
    
    def setUp(self):
        """Set up test dual operator engine."""
        self.user1 = UserProfile(
            user_id="alice",
            name="Alice",
            strengths=["technical"],
            decision_weight=0.6
        )
        
        self.user2 = UserProfile(
            user_id="bob",
            name="Bob",
            strengths=["creative"],
            decision_weight=0.4
        )
        
        self.engine = DualOperatorEngine(
            user1_profile=self.user1,
            user2_profile=self.user2
        )
    
    def test_process_input(self):
        """Test processing user input."""
        result = self.engine.process_input(
            user_id="alice",
            content="Test message",
            modality="text"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['user_id'], "alice")
    
    def test_generate_response(self):
        """Test response generation."""
        self.engine.process_input("alice", "Question?")
        
        response = self.engine.generate_response()
        
        self.assertIn('fused_preferences', response)
        self.assertIn('session_id', response)
    
    def test_collaborative_decision(self):
        """Test collaborative decision making."""
        decision = self.engine.make_collaborative_decision(
            decision_context={"domain": "test"},
            user1_input={"option": "A", "priority": 1},
            user2_input={"option": "B", "priority": 2}
        )
        
        self.assertIn('content', decision)
        self.assertIn('session_id', decision)
    
    def test_audit_trail(self):
        """Test audit trail generation."""
        self.engine.process_input("alice", "Input 1")
        self.engine.process_input("bob", "Input 2")
        
        audit = self.engine.get_audit_trail()
        
        self.assertIn('session_id', audit)
        self.assertIn('users', audit)
        self.assertIn('context_summary', audit)
    
    def test_context_for_llm(self):
        """Test LLM context formatting."""
        self.engine.process_input("alice", "Hello")
        
        messages = self.engine.get_context_for_llm()
        
        # Should include system prompt + user message
        self.assertGreater(len(messages), 1)
        self.assertEqual(messages[0]['role'], 'system')


if __name__ == '__main__':
    unittest.main()
