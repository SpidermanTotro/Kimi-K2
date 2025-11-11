"""
Example: Visualization and Audit Dashboard

This example demonstrates the visualization and audit capabilities
of the dual-operator AI system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_operator_ai.core import (
    UserProfile,
    DualOperatorEngine,
    FusionStrategy
)
from dual_operator_ai.modules.visualization import DecisionVisualizer


def main():
    """Run the visualization example."""
    
    print("=" * 60)
    print("Dual Operator AI - Visualization & Audit Example")
    print("=" * 60)
    print()
    
    # Create user profiles
    user1 = UserProfile(
        user_id="engineer",
        name="Engineer",
        preferences={
            "approach": "methodical",
            "detail_level": "high"
        },
        strengths=["system_design", "optimization", "debugging"],
        decision_weight=0.6
    )
    
    user2 = UserProfile(
        user_id="designer",
        name="Designer",
        preferences={
            "approach": "creative",
            "detail_level": "medium"
        },
        strengths=["user_interface", "user_experience", "aesthetics"],
        decision_weight=0.4
    )
    
    # Create engine with consensus strategy for this example
    engine = DualOperatorEngine(
        user1_profile=user1,
        user2_profile=user2,
        fusion_strategy=FusionStrategy.CONSENSUS
    )
    
    print(f"Created dual-operator system:")
    print(f"  User 1: {user1.name} (weight: {user1.decision_weight})")
    print(f"  User 2: {user2.name} (weight: {user2.decision_weight})")
    print(f"  Strategy: {FusionStrategy.CONSENSUS.value}")
    print()
    
    # Simulate a conversation and decisions
    print("Simulating conversation...")
    print("-" * 60)
    
    # Round 1: Feature prioritization
    print("\n[Decision 1: Feature Prioritization]")
    decision1 = engine.make_collaborative_decision(
        decision_context={
            "domain": "product_development",
            "topic": "Feature prioritization for Q1"
        },
        user1_input={
            "priority_1": "performance_optimization",
            "priority_2": "security_audit",
            "priority_3": "new_ui"
        },
        user2_input={
            "priority_1": "new_ui",
            "priority_2": "user_onboarding",
            "priority_3": "performance_optimization"
        }
    )
    print(f"Engineer's preference: Performance → Security → UI")
    print(f"Designer's preference: UI → Onboarding → Performance")
    
    # Round 2: Tech stack decision
    print("\n[Decision 2: Technology Stack]")
    decision2 = engine.make_collaborative_decision(
        decision_context={
            "domain": "system_design",
            "topic": "Choose frontend framework"
        },
        user1_input={
            "framework": "React",
            "rationale": "Better performance, larger ecosystem",
            "confidence": 0.8
        },
        user2_input={
            "framework": "Vue",
            "rationale": "Easier to learn, better design tools",
            "confidence": 0.6
        }
    )
    print(f"Engineer's choice: React (confidence: 0.8)")
    print(f"Designer's choice: Vue (confidence: 0.6)")
    
    # Round 3: Release timeline
    print("\n[Decision 3: Release Timeline]")
    decision3 = engine.make_collaborative_decision(
        decision_context={
            "domain": "project_management",
            "topic": "Q1 release date"
        },
        user1_input={
            "date": "2025-03-15",
            "buffer_days": 14,
            "risk_level": "low"
        },
        user2_input={
            "date": "2025-03-01",
            "buffer_days": 7,
            "risk_level": "medium"
        }
    )
    print(f"Engineer's timeline: March 15 (14-day buffer)")
    print(f"Designer's timeline: March 1 (7-day buffer)")
    
    # Get audit trail
    print("\n" + "=" * 60)
    print("Generating Audit Trail...")
    print("=" * 60)
    
    audit = engine.get_audit_trail()
    
    print(f"\nSession Information:")
    print(f"  Session ID: {audit['session_id']}")
    print(f"  Total Decisions: {len(audit['decision_history'])}")
    print(f"  Fusion Strategy: {audit['fusion_strategy']}")
    
    print(f"\nUser Contributions:")
    for user_key, user_data in audit['users'].items():
        print(f"  {user_data['name']}:")
        print(f"    - Weight: {user_data['weight']}")
        print(f"    - Strengths: {', '.join(user_data['strengths'])}")
    
    print(f"\nContext Summary:")
    context_summary = audit['context_summary']
    print(f"  Total entries: {context_summary['total_entries']}")
    print(f"  Shared entries: {context_summary['shared_entries']}")
    
    # Create visualizer
    print("\n" + "=" * 60)
    print("Creating Visualization Dashboard...")
    print("=" * 60)
    
    visualizer = DecisionVisualizer()
    
    # Generate dashboard
    dashboard = visualizer.generate_audit_dashboard(audit)
    
    print(f"\nDashboard Generated:")
    print(f"  Overview:")
    print(f"    - Total Decisions: {dashboard['overview']['total_decisions']}")
    print(f"    - Context Entries: {dashboard['overview']['context_entries']}")
    
    print(f"\n  User Contributions:")
    for user_id, contrib in dashboard['user_contributions'].items():
        print(f"    {contrib['name']}: {contrib['decision_count']} decisions")
    
    print(f"\n  Fusion Statistics:")
    fusion_stats = dashboard['fusion_statistics']
    print(f"    - Total Fusions: {fusion_stats['total_fusions']}")
    print(f"    - Average Consensus: {fusion_stats['average_consensus']:.1%}")
    print(f"    - High Consensus Decisions: {fusion_stats['consensus_decisions']}")
    
    # Export dashboard
    print("\n" + "=" * 60)
    print("Exporting Dashboard...")
    print("=" * 60)
    
    # Export as JSON
    json_file = "/tmp/dual_operator_dashboard.json"
    visualizer.export_visualization(dashboard, json_file, format='json')
    print(f"✓ JSON dashboard exported to: {json_file}")
    
    # Export as HTML
    html_file = "/tmp/dual_operator_dashboard.html"
    visualizer.export_visualization(dashboard, html_file, format='html')
    print(f"✓ HTML dashboard exported to: {html_file}")
    print(f"\n  Open {html_file} in your browser to view the interactive dashboard!")
    
    # Generate decision summaries
    print("\n" + "=" * 60)
    print("Decision Summaries")
    print("=" * 60)
    
    for i, decision_record in enumerate(audit['decision_history'], 1):
        summary = visualizer.generate_decision_summary(decision_record, include_details=False)
        print(f"\nDecision {i}:")
        print(f"  Strategy: {summary['strategy']}")
        print(f"  Participants: {len(summary['participants'])}")
        print(f"  Consensus Level: {summary['consensus_level']:.1%}")
        
        for participant in summary['participants']:
            print(f"    - {participant['user_id']}: weight={participant['weight']}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. All decisions are tracked with full audit trail")
    print("  2. Consensus levels show agreement between users")
    print("  3. User contributions are transparently tracked")
    print("  4. Dashboards can be exported as JSON or HTML")
    print("  5. Visualization helps understand decision-making process")


if __name__ == "__main__":
    main()
