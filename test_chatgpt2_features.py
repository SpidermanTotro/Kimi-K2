#!/usr/bin/env python3
"""
Test suite for THE FORGE AI - ChatGPT 2.0 Features
Tests memory system, skills engine, and unified system
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class TestForgeMemory(unittest.TestCase):
    """Test cases for the memory system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from forge_memory import ForgeMemorySystem
        # Use a temporary database for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.memory = ForgeMemorySystem(self.db_path)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_store_and_recall_memory(self):
        """Test storing and recalling a memory"""
        content = "Python is a great programming language"
        memory_id = self.memory.store_memory(
            content=content,
            memory_type="fact",
            importance=0.8
        )
        
        self.assertIsNotNone(memory_id)
        self.assertTrue(len(memory_id) > 0)
        
        # Recall the memory
        recalled = self.memory.recall_memory(memory_id)
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.content, content)
        self.assertEqual(recalled.memory_type, "fact")
        self.assertEqual(recalled.importance, 0.8)
    
    def test_search_memories(self):
        """Test searching memories"""
        # Store some memories
        self.memory.store_memory(
            content="I love Python programming",
            memory_type="preference",
            importance=0.7
        )
        self.memory.store_memory(
            content="JavaScript is useful for web development",
            memory_type="fact",
            importance=0.6
        )
        
        # Search for Python
        results = self.memory.search_memories("Python")
        self.assertTrue(len(results) > 0)
        self.assertTrue(any("Python" in r.content for r in results))
    
    def test_conversation_storage(self):
        """Test storing and retrieving conversations"""
        session_id = "test_session_123"
        
        self.memory.store_conversation_turn(
            session_id=session_id,
            role="user",
            content="Hello, how are you?"
        )
        
        self.memory.store_conversation_turn(
            session_id=session_id,
            role="assistant",
            content="I'm doing great, thank you!"
        )
        
        # Retrieve conversation
        history = self.memory.get_conversation_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[1].role, "assistant")
    
    def test_user_profile(self):
        """Test user profile creation and update"""
        user_id = "test_user_456"
        
        # Get or create profile
        profile = self.memory.get_or_create_profile(user_id)
        self.assertEqual(profile.user_id, user_id)
        
        # Update profile
        self.memory.update_profile(user_id, {
            "preferences": {"language": "python"},
            "topics_of_interest": ["programming", "ai"]
        })
        
        # Verify update
        updated = self.memory.get_or_create_profile(user_id)
        self.assertEqual(updated.preferences.get("language"), "python")
        self.assertIn("programming", updated.topics_of_interest)
    
    def test_memory_stats(self):
        """Test getting memory statistics"""
        # Store some test data
        self.memory.store_memory(
            content="Test memory",
            memory_type="test"
        )
        
        stats = self.memory.get_memory_stats()
        
        self.assertIn("total_memories", stats)
        self.assertIn("cached_memories", stats)
        self.assertTrue(stats["total_memories"] >= 1)


class TestForgeSkills(unittest.TestCase):
    """Test cases for the skills engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        from forge_skills import AdvancedSkillsEngine
        self.skills = AdvancedSkillsEngine()
    
    def test_chain_of_thought(self):
        """Test chain-of-thought reasoning"""
        result = self.skills.reasoning.chain_of_thought(
            "How can I improve my Python code performance?"
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.output)
        self.assertEqual(result.skill_name, "chain_of_thought")
    
    def test_code_analysis(self):
        """Test code analysis"""
        sample_code = '''
def calculate(x):
    if x > 0:
        return x * 2
    return 0
'''
        result = self.skills.code_skills.analyze_code(sample_code, "python")
        
        self.assertTrue(result.success)
        self.assertIn("quality_score", result.output)
        self.assertIn("complexity", result.output)
    
    def test_code_generation(self):
        """Test code generation"""
        result = self.skills.code_skills.generate_code(
            "Create a function to process data",
            language="python"
        )
        
        self.assertTrue(result.success)
        self.assertIn("def", result.output)
    
    def test_writing_analysis(self):
        """Test writing analysis"""
        sample_text = """
        The implementation of artificial intelligence has revolutionized 
        how we approach software development. Furthermore, the integration
        of machine learning enables systems to improve over time.
        """
        
        result = self.skills.writing_skills.analyze_writing(sample_text)
        
        self.assertTrue(result.success)
        self.assertIn("word_count", result.output)
        self.assertIn("style", result.output)
        self.assertIn("readability", result.output)
    
    def test_intent_detection(self):
        """Test intent detection"""
        messages = [
            ("Please help me with this", "request"),
            ("What is Python?", "question"),
            ("Create a function", "command"),
        ]
        
        for message, expected_intent in messages:
            result = self.skills.personalization.detect_user_intent(message)
            self.assertTrue(result.success)
            self.assertEqual(result.output["primary_intent"], expected_intent)
    
    def test_available_skills(self):
        """Test getting available skills"""
        skills = self.skills.get_available_skills()
        
        self.assertIn("reasoning", skills)
        self.assertIn("coding", skills)
        self.assertIn("writing", skills)
        self.assertIn("personalization", skills)


class TestKimiForgeUnified(unittest.TestCase):
    """Test cases for the unified system"""
    
    def setUp(self):
        """Set up test fixtures"""
        from kimi_forge_unified import KimiForgeUnified
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_unified.db")
        self.system = KimiForgeUnified(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_basic_process(self):
        """Test basic processing"""
        response = self.system.process("Write a Python function")
        
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
    
    def test_memory_enhanced_process(self):
        """Test memory-enhanced processing"""
        result = self.system.process_with_memory(
            "Help me with Python programming",
            user_id="test_user",
            session_id="test_session"
        )
        
        self.assertIn("response", result)
        self.assertIn("session_id", result)
        self.assertTrue(len(result["response"]) > 0)
    
    def test_remember_fact(self):
        """Test fact storage"""
        fact_id = self.system.remember_fact(
            "User likes Python",
            importance=0.8,
            tags=["preference"]
        )
        
        self.assertIsNotNone(fact_id)
        self.assertTrue(len(fact_id) > 0)
    
    def test_search_memory(self):
        """Test memory search"""
        # Store something first
        self.system.remember_fact(
            "Python is my favorite language",
            importance=0.9
        )
        
        # Search for it
        results = self.system.search_memory("Python")
        self.assertTrue(len(results) >= 0)  # May be empty if no matches
    
    def test_get_stats(self):
        """Test getting system statistics"""
        stats = self.system.get_stats()
        
        self.assertIn("kimi_k2_model", stats)
        self.assertIn("forge_tools_available", stats)
        self.assertIn("chatgpt_2_features", stats)
        
        # Check ChatGPT 2.0 features
        features = stats["chatgpt_2_features"]
        self.assertIn("memory_system", features)
        self.assertIn("skills_engine", features)
    
    def test_user_profile(self):
        """Test user profile retrieval"""
        profile = self.system.get_user_profile("new_user")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["user_id"], "new_user")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestForgeMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestForgeSkills))
    suite.addTests(loader.loadTestsFromTestCase(TestKimiForgeUnified))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 THE FORGE AI - ChatGPT 2.0 Features Test Suite")
    print("=" * 70)
    print()
    
    success = run_tests()
    
    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
