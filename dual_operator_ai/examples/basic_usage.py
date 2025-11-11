"""
Example: Basic dual-operator AI usage

This example demonstrates basic usage of the dual-operator AI system
with two users collaborating through a single AI entity.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_operator_ai.core import (
    UserProfile,
    DualOperatorEngine,
    FusionStrategy
)


def main():
    """Run the basic example."""
    
    # Create user profiles
    user1 = UserProfile(
        user_id="user_alice",
        name="Alice",
        preferences={
            "communication_style": "detailed",
            "response_length": "comprehensive",
            "technical_level": "expert"
        },
        strengths=["technical_writing", "software_architecture", "debugging"],
        decision_weight=0.6
    )
    
    user2 = UserProfile(
        user_id="user_bob",
        name="Bob",
        preferences={
            "communication_style": "concise",
            "response_length": "brief",
            "technical_level": "intermediate"
        },
        strengths=["project_management", "user_experience", "communication"],
        decision_weight=0.4
    )
    
    # Create the dual-operator engine
    engine = DualOperatorEngine(
        user1_profile=user1,
        user2_profile=user2,
        fusion_strategy=FusionStrategy.ADAPTIVE
    )
    
    print("=" * 60)
    print("Dual Operator AI System - Basic Example")
    print("=" * 60)
    print(f"Users: {user1.name} and {user2.name}")
    print(f"Fusion Strategy: {FusionStrategy.ADAPTIVE.value}")
    print()
    
    # Process input from user 1
    print(f"[{user1.name}]: How should we structure our project?")
    engine.process_input(
        user_id=user1.user_id,
        content="How should we structure our project?",
        modality="text"
    )
    
    # Process input from user 2
    print(f"[{user2.name}]: I think we need a clear roadmap first.")
    engine.process_input(
        user_id=user2.user_id,
        content="I think we need a clear roadmap first.",
        modality="text"
    )
    
    # Generate a response considering both perspectives
    print("\n[AI Response Generation]")
    response = engine.generate_response(include_both_perspectives=True)
    
    print(f"\nResponse generated with {response['context_entries']} context entries")
    print(f"Fused preferences:")
    for key, value in response['fused_preferences'].items():
        print(f"  - {key}: {value}")
    
    # Make a collaborative decision
    print("\n" + "=" * 60)
    print("Collaborative Decision Making")
    print("=" * 60)
    
    decision_context = {
        "domain": "software_architecture",
        "question": "Choose project structure approach"
    }
    
    user1_decision = {
        "approach": "microservices",
        "rationale": "Better scalability and maintainability",
        "priority": 2
    }
    
    user2_decision = {
        "approach": "modular_monolith",
        "rationale": "Simpler to start, easier team coordination",
        "priority": 1
    }
    
    fused_decision = engine.make_collaborative_decision(
        decision_context=decision_context,
        user1_input=user1_decision,
        user2_input=user2_decision
    )
    
    print(f"\nDecision Context: {decision_context['question']}")
    print(f"{user1.name}'s preference: {user1_decision['approach']}")
    print(f"{user2.name}'s preference: {user2_decision['approach']}")
    print(f"\nFused Decision: {fused_decision.get('content', {})}")
    
    # Get audit trail
    print("\n" + "=" * 60)
    print("Audit Trail")
    print("=" * 60)
    
    audit = engine.get_audit_trail()
    print(f"Session ID: {audit['session_id']}")
    print(f"Total context entries: {audit['context_summary']['total_entries']}")
    print(f"Decisions made: {len(audit['decision_history'])}")
    print(f"Fusion strategy: {audit['fusion_strategy']}")
    
    # Export session
    session_file = "/tmp/dual_operator_session.json"
    engine.export_session(session_file)
    print(f"\nSession exported to: {session_file}")
    
    # Get context formatted for LLM
    print("\n" + "=" * 60)
    print("LLM Context Format")
    print("=" * 60)
    
    llm_context = engine.get_context_for_llm()
    print(f"Total messages for LLM: {len(llm_context)}")
    print("\nFirst few messages:")
    for i, msg in enumerate(llm_context[:3]):
        print(f"{i+1}. Role: {msg['role']}")
        if isinstance(msg['content'], str):
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"   Content: {content_preview}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
