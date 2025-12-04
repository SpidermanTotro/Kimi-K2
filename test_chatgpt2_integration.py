#!/usr/bin/env python3
"""
THE FORGE - Test Suite for ChatGPT 2.0 Integration
===================================================

Comprehensive test cases to validate new integrations and system upgrades,
ensuring stability and scalability of the unified framework.
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from forge_memory import HierarchicalMemory, MemoryEntry, PersistentContextManager, get_memory
from forge_codex import CodexSystem, CodexDocument, CodexQuery, get_codex
from forge_collaboration import CollaborationSystem, EventType, CollaborationEvent, get_collaboration
from forge_plugins import PluginSystem, PluginInfo, HookRegistry, get_plugins


class TestHierarchicalMemory(unittest.TestCase):
    """Test cases for the Hierarchical Memory System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = HierarchicalMemory(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_session(self):
        """Test session creation"""
        session_id = self.memory.create_session()
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.memory.contexts)
    
    def test_add_memory(self):
        """Test adding memories"""
        session_id = self.memory.create_session()
        
        entry = self.memory.add_memory(
            content="Test memory content",
            session_id=session_id,
            memory_type="short_term",
            tags=["test"]
        )
        
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.content, "Test memory content")
        self.assertEqual(entry.session_id, session_id)
    
    def test_memory_retrieval(self):
        """Test memory retrieval"""
        session_id = self.memory.create_session()
        
        self.memory.add_memory(
            content="Python programming tutorial",
            session_id=session_id,
            tags=["python", "programming"]
        )
        
        self.memory.add_memory(
            content="Video editing guide",
            session_id=session_id,
            tags=["video", "editing"]
        )
        
        results = self.memory.retrieve("python", session_id)
        self.assertGreater(len(results), 0)
        self.assertIn("python", results[0].content.lower())
    
    def test_memory_consolidation(self):
        """Test memory consolidation to working memory"""
        session_id = self.memory.create_session()
        
        # Add many memories to trigger consolidation
        for i in range(110):
            self.memory.add_memory(
                content=f"Memory content {i}",
                session_id=session_id
            )
        
        # Check that some moved to working memory
        self.assertLess(len(self.memory.short_term[session_id]), 110)
        self.assertGreater(len(self.memory.working), 0)
    
    def test_long_term_persistence(self):
        """Test long-term memory persistence"""
        session_id = self.memory.create_session()
        
        entry = self.memory.add_memory(
            content="Important persistent memory",
            session_id=session_id,
            memory_type="long_term"
        )
        
        # Create new memory instance
        new_memory = HierarchicalMemory(storage_path=self.temp_dir)
        
        # Check persistence
        self.assertIn(entry.id, new_memory.long_term)
    
    def test_codex_session_linking(self):
        """Test linking chat and Codex sessions"""
        chat_session = self.memory.create_session()
        codex_session = "codex_123"
        
        self.memory.link_codex_session(chat_session, codex_session)
        
        context = self.memory.contexts[chat_session]
        self.assertEqual(context.codex_session_id, codex_session)
    
    def test_shared_context(self):
        """Test shared context retrieval"""
        session_id = self.memory.create_session()
        
        self.memory.add_memory(
            content="Shared context test",
            session_id=session_id
        )
        
        shared = self.memory.get_shared_context(session_id)
        self.assertEqual(shared["session_id"], session_id)
        self.assertIn("recent_memories", shared)


class TestCodexSystem(unittest.TestCase):
    """Test cases for the Codex System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.codex = CodexSystem(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_document(self):
        """Test adding a document"""
        doc = self.codex.add_document(
            title="Test Document",
            content="This is test content for the document.",
            doc_type="text",
            tags=["test"]
        )
        
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.title, "Test Document")
        self.assertIn(doc.id, self.codex.index.documents)
    
    def test_search_documents(self):
        """Test searching documents"""
        self.codex.add_document(
            title="Python Guide",
            content="Learn Python programming from basics to advanced.",
            tags=["python", "programming"]
        )
        
        self.codex.add_document(
            title="Video Editing",
            content="Professional video editing techniques.",
            tags=["video"]
        )
        
        results = self.codex.search("python programming")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].document.title, "Python Guide")
    
    def test_edit_document(self):
        """Test document editing"""
        doc = self.codex.add_document(
            title="Edit Test",
            content="Original content here."
        )
        
        result = self.codex.edit_document(
            doc_id=doc.id,
            edit_type="replace",
            old_content="Original",
            new_content="Modified"
        )
        
        self.assertTrue(result)
        
        view = self.codex.view(doc.id)
        self.assertIn("Modified", view["document"]["content"])
    
    def test_section_parsing(self):
        """Test markdown section parsing"""
        doc = self.codex.add_document(
            title="Markdown Test",
            content="""# Section 1
Content for section 1.

## Subsection 1.1
More content here.

# Section 2
Final content.""",
            doc_type="markdown"
        )
        
        self.assertGreater(len(doc.sections), 0)
    
    def test_browse_documents(self):
        """Test document browsing"""
        self.codex.add_document(
            title="Doc 1",
            content="Content 1",
            path="docs/guide.md"
        )
        
        structure = self.codex.browse()
        self.assertIn("documents", structure)
        self.assertIn("subdirs", structure)
    
    def test_reasoning_integration(self):
        """Test integration with reasoning workflows"""
        self.codex.add_document(
            title="Reference Doc",
            content="Important reference information for reasoning."
        )
        
        result = self.codex.integrate_with_reasoning(
            query="reference information",
            context={"task": "test"}
        )
        
        self.assertIn("codex_results", result)
        self.assertGreater(result["total_relevant"], 0)


class TestCollaborationSystem(unittest.TestCase):
    """Test cases for the Collaboration System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.collab = CollaborationSystem(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        self.collab.shutdown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_module(self):
        """Test module registration"""
        module = self.collab.register_module(
            "test_module",
            capabilities=["test", "demo"]
        )
        
        self.assertEqual(module.name, "test_module")
        self.assertIn("test_module", self.collab.module_registry.modules)
    
    def test_shared_state(self):
        """Test shared state management"""
        self.collab.set_state("namespace", "key", "value", "test")
        
        result = self.collab.get_state("namespace", "key")
        self.assertEqual(result, "value")
    
    def test_task_coordination(self):
        """Test task creation and coordination"""
        task = self.collab.create_task(
            name="Test Task",
            owner="test_module",
            input_data={"param": "value"}
        )
        
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.status, "pending")
        
        self.collab.task_coordinator.start_task(task.id)
        self.assertEqual(task.status, "running")
        
        self.collab.task_coordinator.complete_task(task.id, {"result": "done"})
        self.assertEqual(task.status, "completed")
    
    def test_event_handling(self):
        """Test event publishing and handling"""
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        self.collab.subscribe(EventType.MESSAGE.value, handler)
        self.collab.send_message("source", "target", {"test": "data"})
        
        # Give time for async processing
        import time
        time.sleep(0.2)
        
        self.assertGreater(len(received_events), 0)
    
    def test_module_capability_discovery(self):
        """Test finding modules by capability"""
        self.collab.register_module(
            "module1",
            capabilities=["capability_a", "capability_b"]
        )
        
        self.collab.register_module(
            "module2",
            capabilities=["capability_a"]
        )
        
        found = self.collab.module_registry.find_by_capability("capability_a")
        self.assertEqual(len(found), 2)


class TestPluginSystem(unittest.TestCase):
    """Test cases for the Plugin System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.plugins = PluginSystem(plugins_dir=os.path.join(self.temp_dir, "plugins"))
    
    def tearDown(self):
        """Clean up after tests"""
        self.plugins.shutdown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_core_hooks_registered(self):
        """Test that core hooks are registered"""
        hooks = self.plugins.hooks.get_hook_info()
        hook_names = [h["name"] for h in hooks]
        
        self.assertIn("before_process", hook_names)
        self.assertIn("after_process", hook_names)
        self.assertIn("on_session_start", hook_names)
    
    def test_hook_execution(self):
        """Test hook execution"""
        # Add a test handler
        def test_handler(data):
            data["processed"] = True
            return data
        
        self.plugins.hooks.add_handler("before_process", "test_plugin", test_handler)
        
        result = self.plugins.execute_hook("before_process", {"original": True})
        
        self.assertTrue(result.get("processed"))
        self.assertTrue(result.get("original"))
    
    def test_context_setting(self):
        """Test context management"""
        self.plugins.set_context("test_key", "test_value")
        
        self.assertEqual(self.plugins.context["test_key"], "test_value")
    
    def test_plugin_discovery(self):
        """Test plugin discovery with empty directory"""
        plugins = self.plugins.discover()
        
        # Should return empty list for empty plugins directory
        self.assertIsInstance(plugins, list)


class TestIntegration(unittest.TestCase):
    """Integration tests for the unified system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_codex_integration(self):
        """Test integration between memory and Codex"""
        memory = HierarchicalMemory(storage_path=os.path.join(self.temp_dir, "memory"))
        codex = CodexSystem(storage_path=os.path.join(self.temp_dir, "codex"))
        
        # Create session and link to codex
        session_id = memory.create_session()
        codex_session = f"codex_{session_id[:8]}"
        memory.link_codex_session(session_id, codex_session)
        
        # Add document
        doc = codex.add_document(
            title="Integration Test",
            content="Testing memory and codex integration."
        )
        
        # Add memory referencing document
        memory.add_memory(
            content=f"Discussed document: {doc.title}",
            session_id=session_id,
            tags=["integration", "codex"]
        )
        
        # Verify integration
        context = memory.get_shared_context(session_id)
        self.assertEqual(context["codex_session_id"], codex_session)
    
    def test_collaboration_memory_integration(self):
        """Test integration between collaboration and memory"""
        memory = HierarchicalMemory(storage_path=os.path.join(self.temp_dir, "memory"))
        collab = CollaborationSystem(storage_path=os.path.join(self.temp_dir, "collab"))
        
        try:
            # Register memory module
            collab.register_module("memory", capabilities=["store", "retrieve"])
            
            # Create shared state
            session_id = memory.create_session()
            collab.set_state("memory", "active_session", session_id, "memory")
            
            # Verify
            stored_session = collab.get_state("memory", "active_session")
            self.assertEqual(stored_session, session_id)
        finally:
            collab.shutdown()
    
    def test_full_workflow(self):
        """Test a complete workflow through all systems"""
        # Initialize systems
        memory = HierarchicalMemory(storage_path=os.path.join(self.temp_dir, "memory"))
        codex = CodexSystem(storage_path=os.path.join(self.temp_dir, "codex"))
        collab = CollaborationSystem(storage_path=os.path.join(self.temp_dir, "collab"))
        plugins = PluginSystem(plugins_dir=os.path.join(self.temp_dir, "plugins"))
        
        try:
            # 1. Create session
            session_id = memory.create_session()
            
            # 2. Register modules
            collab.register_module("chat", capabilities=["send", "receive"])
            collab.register_module("codex", capabilities=["search", "browse"])
            
            # 3. Add documentation
            doc = codex.add_document(
                title="Workflow Test",
                content="Testing the complete workflow."
            )
            
            # 4. Store interaction in memory
            memory.add_memory(
                content="User asked about workflow",
                session_id=session_id
            )
            
            # 5. Search codex
            results = codex.search("workflow")
            
            # 6. Create task
            task = collab.create_task(
                name="Process workflow query",
                owner="chat"
            )
            
            # 7. Execute hook
            hook_result = plugins.execute_hook("before_process", {
                "session": session_id,
                "query": "workflow"
            })
            
            # Verify all components worked
            self.assertGreater(len(results), 0)
            self.assertIsNotNone(task.id)
            self.assertIsNotNone(hook_result)
            
        finally:
            collab.shutdown()
            plugins.shutdown()


class TestScalability(unittest.TestCase):
    """Test cases for system scalability"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_many_memories(self):
        """Test handling many memories"""
        memory = HierarchicalMemory(storage_path=self.temp_dir)
        session_id = memory.create_session()
        
        # Add 1000 memories
        for i in range(1000):
            memory.add_memory(
                content=f"Memory number {i} with some content",
                session_id=session_id
            )
        
        # Verify retrieval still works
        results = memory.retrieve("memory", session_id, max_results=10)
        self.assertEqual(len(results), 10)
    
    def test_many_documents(self):
        """Test handling many documents"""
        codex = CodexSystem(storage_path=self.temp_dir)
        
        # Add 100 documents
        for i in range(100):
            codex.add_document(
                title=f"Document {i}",
                content=f"Content for document {i} with various keywords."
            )
        
        # Verify search still works
        results = codex.search("document content")
        self.assertGreater(len(results), 0)
    
    def test_concurrent_sessions(self):
        """Test handling concurrent sessions"""
        memory = HierarchicalMemory(storage_path=self.temp_dir)
        
        sessions = []
        for i in range(50):
            session_id = memory.create_session()
            sessions.append(session_id)
            
            memory.add_memory(
                content=f"Content for session {i}",
                session_id=session_id
            )
        
        # Verify all sessions work
        for session_id in sessions:
            context = memory.get_shared_context(session_id)
            self.assertIsNotNone(context)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 THE FORGE - Test Suite for ChatGPT 2.0 Integration")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestHierarchicalMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestCodexSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCollaborationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestPluginSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestScalability))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
