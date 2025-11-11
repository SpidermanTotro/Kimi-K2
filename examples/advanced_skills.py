"""
Example: Advanced Skills
Demonstrates reasoning, image generation, and specialized pipelines
"""

import os
from kimi_k2 import KimiClient
from kimi_k2.skills import (
    AdvancedReasoning,
    TextToImageGenerator,
    ContextualChat,
    SpecializedPipeline
)


def example_advanced_reasoning():
    """Example of advanced reasoning."""
    print("=" * 50)
    print("Example 1: Advanced Reasoning")
    print("=" * 50)
    
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    reasoning = AdvancedReasoning(client)
    
    # Chain-of-thought reasoning
    result = reasoning.chain_of_thought(
        "If a train travels 120 km in 2 hours, then speeds up and travels 200 km in the next 2.5 hours, what is its average speed for the entire journey?",
        domain="math"
    )
    print(f"Problem: {result['problem']}")
    print(f"Reasoning:\n{result['reasoning']}\n")
    
    # Problem decomposition
    complex_problem = "Design and implement a scalable microservices architecture for an e-commerce platform"
    result = reasoning.decompose_problem(complex_problem)
    print(f"Complex Problem: {complex_problem}")
    print(f"Decomposition:\n{result['decomposition']}\n")


def example_text_to_image():
    """Example of text-to-image integration."""
    print("=" * 50)
    print("Example 2: Text-to-Image Generation")
    print("=" * 50)
    
    # Note: Requires appropriate API keys for image generation
    generator = TextToImageGenerator(backend="dalle", api_key=os.getenv("OPENAI_API_KEY"))
    
    # Enhance a simple prompt
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    simple_prompt = "a cat in a garden"
    enhanced = generator.enhance_prompt(simple_prompt, client)
    print(f"Original prompt: {simple_prompt}")
    print(f"Enhanced prompt: {enhanced}\n")
    
    # Generate image (placeholder - requires actual API key)
    result = generator.generate(
        prompt=enhanced,
        size="1024x1024",
        quality="standard"
    )
    print(f"Generation result: {result}\n")


def example_contextual_chat():
    """Example of contextual chat."""
    print("=" * 50)
    print("Example 3: Contextual Chat")
    print("=" * 50)
    
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    chat = ContextualChat(client)
    
    # User context
    context = {
        "user_info": "Software engineer with 5 years experience",
        "preferences": "Prefers concise, technical explanations",
        "location": "San Francisco"
    }
    
    # First message
    result1 = chat.chat_with_context(
        "What's the best way to learn Kubernetes?",
        context=context
    )
    print(f"Q1: What's the best way to learn Kubernetes?")
    print(f"A1: {result1['response']}\n")
    
    # Follow-up with history
    result2 = chat.chat_with_context(
        "How long will it take?",
        context=context,
        maintain_history=True
    )
    print(f"Q2: How long will it take?")
    print(f"A2: {result2['response']}\n")
    
    # Get conversation stats
    stats = chat.get_context_stats()
    print(f"Conversation stats: {stats}\n")


def example_specialized_pipeline():
    """Example of specialized pipelines."""
    print("=" * 50)
    print("Example 4: Specialized Pipelines")
    print("=" * 50)
    
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    
    # Education pipeline
    edu_pipeline = SpecializedPipeline("education", client)
    result = edu_pipeline.education_tutor(
        subject="mathematics",
        topic="quadratic equations",
        student_level="high",
        question="How do I solve x² - 5x + 6 = 0?"
    )
    print(f"Education (Math Tutoring):")
    print(f"{result['response']}\n")
    
    # Healthcare pipeline (educational)
    health_pipeline = SpecializedPipeline("healthcare", client)
    result = health_pipeline.healthcare_analysis(
        symptoms=["headache", "fatigue", "fever"],
        patient_info={"age": "30", "context": "educational example"}
    )
    print(f"Healthcare (Educational Analysis):")
    print(f"{result['response']}\n")


if __name__ == "__main__":
    print("Kimi K2 Advanced Skills Examples\n")
    
    if not os.getenv("MOONSHOT_API_KEY"):
        print("⚠️  MOONSHOT_API_KEY not set. Examples will not make actual API calls.")
        print("Set it with: export MOONSHOT_API_KEY='your-api-key'\n")
    
    example_advanced_reasoning()
    example_text_to_image()
    example_contextual_chat()
    example_specialized_pipeline()
    
    print("Advanced examples completed!")
