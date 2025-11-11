"""
Example: Interaction Features
Demonstrates conversation management, personalization, and memory
"""

import os
from kimi_k2 import KimiClient
from kimi_k2.interaction import (
    ConversationManager,
    PersonalizationEngine,
    MemoryModule
)


def example_conversation_manager():
    """Example of multi-user conversation management."""
    print("=" * 50)
    print("Example 1: Conversation Manager")
    print("=" * 50)
    
    manager = ConversationManager()
    
    # Create a session
    session_result = manager.create_session("session_001", metadata={"topic": "AI Discussion"})
    print(f"Created session: {session_result}\n")
    
    # Add users
    manager.add_user_to_session("session_001", "user_alice")
    manager.add_user_to_session("session_001", "user_bob")
    
    # Add messages
    manager.add_message("session_001", "user_alice", "What are the benefits of MoE models?", "user")
    manager.add_message("session_001", "user_bob", "They allow for better scaling and efficiency", "user")
    
    # Get history
    history = manager.get_session_history("session_001")
    print(f"Session history: {history['filtered_count']} messages")
    for msg in history['messages']:
        print(f"  [{msg['user_id']}]: {msg['content']}")
    
    # Get stats
    stats = manager.get_stats()
    print(f"\nManager stats: {stats}\n")


def example_personalization():
    """Example of personalization engine."""
    print("=" * 50)
    print("Example 2: Personalization")
    print("=" * 50)
    
    engine = PersonalizationEngine()
    
    # Create profile
    engine.create_profile("user_001", preferences={
        "response_style": "concise",
        "language": "English",
        "expertise_level": "intermediate"
    })
    
    # Record interactions
    engine.record_interaction("user_001", "query", {
        "topics": ["machine learning", "python"],
        "complexity": "medium"
    })
    
    engine.record_interaction("user_001", "query", {
        "topics": ["deep learning", "pytorch"],
        "complexity": "advanced"
    })
    
    # Get adaptive settings
    settings = engine.get_adaptive_settings("user_001")
    print(f"User settings: {settings}\n")
    
    # Set custom setting
    engine.set_custom_setting("user_001", "preferred_temperature", 0.7)
    
    # Get preferences
    prefs = engine.get_preferences("user_001")
    print(f"User preferences: {prefs}\n")


def example_memory_module():
    """Example of memory module for session recall."""
    print("=" * 50)
    print("Example 3: Memory Module")
    print("=" * 50)
    
    memory = MemoryModule()
    
    # Store memories
    memory.store_memory(
        "user_001",
        "User is working on a machine learning project using PyTorch",
        category="project",
        tags=["pytorch", "ml", "work"]
    )
    
    memory.store_memory(
        "user_001",
        "User prefers detailed explanations with code examples",
        category="preference",
        tags=["learning_style", "code"]
    )
    
    memory.store_memory(
        "user_001",
        "User is interested in transformer architectures",
        category="interest",
        tags=["transformers", "nlp", "ml"]
    )
    
    # Recall by category
    project_memories = memory.recall_memories("user_001", category="project")
    print(f"Project memories: {project_memories['count']}")
    for mem in project_memories['memories']:
        print(f"  - {mem['content']}")
    
    # Search memories
    search_results = memory.search_memories("user_001", "pytorch")
    print(f"\nSearch results for 'pytorch': {search_results['count']}")
    for mem in search_results['memories']:
        print(f"  - {mem['content']}")
    
    # Get stats
    stats = memory.get_memory_stats("user_001")
    print(f"\nMemory stats: {stats}\n")


def example_integrated_workflow():
    """Example of integrated workflow using all interaction features."""
    print("=" * 50)
    print("Example 4: Integrated Workflow")
    print("=" * 50)
    
    # Initialize components
    manager = ConversationManager()
    personalization = PersonalizationEngine()
    memory = MemoryModule()
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    
    user_id = "user_integrated"
    session_id = "session_integrated"
    
    # Setup user profile
    personalization.create_profile(user_id, preferences={
        "response_style": "detailed",
        "domain": "software_engineering"
    })
    
    # Create conversation session
    manager.create_session(session_id)
    manager.add_user_to_session(session_id, user_id)
    
    # Store initial context in memory
    memory.store_memory(
        user_id,
        "User is learning about Kimi K2 integration features",
        category="learning",
        tags=["kimi_k2", "integration", "learning"]
    )
    
    # Simulate conversation
    user_message = "How can I use the memory module effectively?"
    manager.add_message(session_id, user_id, user_message, "user")
    
    # Get relevant memories
    relevant_memories = memory.recall_memories(user_id, tags=["kimi_k2"])
    
    # Get user preferences
    prefs = personalization.get_preferences(user_id)
    
    print(f"User question: {user_message}")
    print(f"Relevant memories: {relevant_memories['count']}")
    print(f"User preferences: {prefs['preferences']}")
    
    # In a real scenario, you'd use this context to inform the AI response
    print("\nWorkflow demonstrates integration of conversation, personalization, and memory!\n")


if __name__ == "__main__":
    print("Kimi K2 Interaction Features Examples\n")
    
    example_conversation_manager()
    example_personalization()
    example_memory_module()
    example_integrated_workflow()
    
    print("Interaction examples completed!")
