"""
Example: Integration with Kimi-K2 API

This example demonstrates how to integrate the dual-operator AI system
with the Kimi-K2 model API.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_operator_ai.core import (
    UserProfile,
    DualOperatorEngine,
    FusionStrategy
)
from dual_operator_ai.modules.kimi_adapter import KimiK2Adapter


def main():
    """Run the Kimi-K2 integration example."""
    
    # Note: This example shows the integration pattern
    # You would need to provide your actual API key to run it
    
    print("=" * 60)
    print("Dual Operator AI + Kimi-K2 Integration Example")
    print("=" * 60)
    print()
    
    # Create user profiles
    user1 = UserProfile(
        user_id="partner_a",
        name="Partner A",
        preferences={
            "detail_level": "high",
            "creativity": 0.7,
            "formality": "professional"
        },
        strengths=["analysis", "research", "technical_writing"],
        decision_weight=0.5
    )
    
    user2 = UserProfile(
        user_id="partner_b",
        name="Partner B",
        preferences={
            "detail_level": "medium",
            "creativity": 0.8,
            "formality": "casual"
        },
        strengths=["creativity", "communication", "design"],
        decision_weight=0.5
    )
    
    # Create dual-operator engine
    engine = DualOperatorEngine(
        user1_profile=user1,
        user2_profile=user2,
        fusion_strategy=FusionStrategy.ADAPTIVE
    )
    
    print(f"Created dual-operator system for {user1.name} and {user2.name}")
    print()
    
    # Initialize Kimi-K2 adapter (mock for demonstration)
    print("Initializing Kimi-K2 adapter...")
    print("Note: This is a demonstration. Actual API calls require a valid API key.")
    print()
    
    # Simulate conversation
    print("Simulating conversation flow:")
    print("-" * 60)
    
    # Partner A asks a question
    question_a = "What are the key considerations for building a scalable web application?"
    print(f"[{user1.name}]: {question_a}")
    engine.process_input(
        user_id=user1.user_id,
        content=question_a,
        modality="text"
    )
    
    # Partner B adds their perspective
    addition_b = "Also, we should consider user experience and accessibility from the start."
    print(f"[{user2.name}]: {addition_b}")
    engine.process_input(
        user_id=user2.user_id,
        content=addition_b,
        modality="text"
    )
    
    # Get combined context for Kimi-K2
    print("\n[System]: Preparing context for Kimi-K2...")
    messages = engine.get_context_for_llm()
    
    print(f"Context prepared with {len(messages)} messages")
    print("\nSystem Prompt includes both partners' information:")
    print(f"  - {user1.name}: strengths in {', '.join(user1.strengths)}")
    print(f"  - {user2.name}: strengths in {', '.join(user2.strengths)}")
    
    # Show how the request would be formatted
    print("\n" + "=" * 60)
    print("Example API Request Format")
    print("=" * 60)
    
    api_request_example = {
        "model": "moonshotai/Kimi-K2-Instruct",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 2048
    }
    
    print("Request structure:")
    print(f"  Model: {api_request_example['model']}")
    print(f"  Messages: {len(api_request_example['messages'])} entries")
    print(f"  Temperature: {api_request_example['temperature']}")
    print(f"  Max Tokens: {api_request_example['max_tokens']}")
    
    # Show fused preferences
    print("\n" + "=" * 60)
    print("Fused Preferences for Response Generation")
    print("=" * 60)
    
    response_config = engine.generate_response()
    print("\nFused preferences:")
    for key, value in response_config['fused_preferences'].items():
        print(f"  {key}: {value}")
    
    # Example with tools
    print("\n" + "=" * 60)
    print("Tool Calling Example")
    print("=" * 60)
    
    # Define a collaborative tool
    tools = [{
        "type": "function",
        "function": {
            "name": "collaborative_decision",
            "description": "Make a decision considering both partners' perspectives",
            "parameters": {
                "type": "object",
                "required": ["decision_topic", "options"],
                "properties": {
                    "decision_topic": {
                        "type": "string",
                        "description": "The topic requiring a decision"
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available options to choose from"
                    }
                }
            }
        }
    }]
    
    print("Registered collaborative tool:")
    print(f"  Name: {tools[0]['function']['name']}")
    print(f"  Description: {tools[0]['function']['description']}")
    
    # Show how to use with Kimi-K2 adapter
    print("\n" + "=" * 60)
    print("Integration Code Pattern")
    print("=" * 60)
    
    integration_code = '''
# Initialize Kimi-K2 adapter with your API key
adapter = KimiK2Adapter(
    api_key="your_api_key_here",
    base_url="https://api.moonshot.cn/v1",
    model_name="moonshotai/Kimi-K2-Instruct"
)

# Get context from dual-operator engine
messages = engine.get_context_for_llm()

# Generate response using Kimi-K2
response = adapter.generate_response(
    messages=messages,
    tools=tools,
    max_tokens=2048
)

# Add response to context
engine.context_manager.add_context(
    user_id=None,
    role="assistant",
    content=response['content'],
    modality="text",
    shared=True
)
'''
    
    print(integration_code)
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("To run with actual API calls, provide a valid API key.")
    print("=" * 60)


if __name__ == "__main__":
    main()
