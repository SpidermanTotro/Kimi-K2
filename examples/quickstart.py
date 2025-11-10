#!/usr/bin/env python3
"""
Kimi-K2 Skills Framework - Quick Start Example

This example demonstrates basic usage of the media generation and AI creativity modules.
"""

from skills.media_generation import (
    VideoGenerator,
    VoiceSynthesizer,
    MusicGenerator,
    ImageGenerator,
    AnimationEngine
)
from skills.ai_creativity import (
    StoryWriter,
    DialogueGenerator,
    ProceduralGenerator
)
from skills.core import CacheManager, PerformanceOptimizer, WorkflowManager


def example_voice_synthesis():
    """Example: Generate voice narration in multiple languages"""
    print("\n=== Voice Synthesis Example ===")
    
    from skills.media_generation.voice_synthesizer import (
        VoiceProfile, VoiceGender, Emotion
    )
    
    synthesizer = VoiceSynthesizer(device="cuda")
    
    # Create voice profile
    narrator = VoiceProfile(
        name="Narrator",
        gender=VoiceGender.FEMALE,
        language="en-US",
        pitch=1.0,
        speed=1.0
    )
    
    # Synthesize speech
    audio = synthesizer.synthesize(
        "Welcome to Kimi-K2's advanced AI media generation suite!",
        narrator,
        emotion=Emotion.HAPPY
    )
    
    print(f"Generated audio: {audio['duration']:.2f} seconds")
    print(f"Language: {audio['language']}")
    print(f"Phonemes for lip-sync: {len(audio['phonemes'])}")


def example_image_generation():
    """Example: Generate high-resolution images"""
    print("\n=== Image Generation Example ===")
    
    from skills.media_generation.image_generator import ImageConfig, ImageStyle
    
    generator = ImageGenerator(device="cuda")
    
    config = ImageConfig(
        width=2048,
        height=2048,
        style=ImageStyle.PHOTOREALISTIC,
        quality="high",
        steps=50
    )
    
    image = generator.generate(
        "A majestic mountain landscape at sunset with dramatic clouds",
        config,
        seed=42
    )
    
    print(f"Generated image: {image['width']}x{image['height']}")
    print(f"Style: {image['style']}")


def example_story_writing():
    """Example: Generate a story with characters"""
    print("\n=== Story Writing Example ===")
    
    from skills.ai_creativity.story_writer import (
        StoryConfig, Genre, Character
    )
    
    writer = StoryWriter()
    
    config = StoryConfig(
        title="The Crystal Quest",
        genre=Genre.FANTASY,
        num_chapters=10,
        target_word_count=50000
    )
    
    story = writer.create_story(
        config,
        premise="A young hero discovers a magical crystal"
    )
    
    # Add main character
    hero = Character(
        name="Elena",
        role="protagonist",
        description="A brave young adventurer",
        personality=["courageous", "kind", "determined"]
    )
    
    writer.add_character(story, hero)
    writer.generate_outline(story)
    
    print(f"Story created: {config.title}")
    print(f"Genre: {config.genre.value}")
    print(f"Characters: {len(story['characters'])}")
    print(f"Chapters planned: {len(story['chapters'])}")


def example_music_generation():
    """Example: Generate background music"""
    print("\n=== Music Generation Example ===")
    
    from skills.media_generation.music_generator import (
        MusicConfig, MusicGenre, Mood
    )
    
    generator = MusicGenerator(device="cuda")
    
    config = MusicConfig(
        duration=30.0,
        tempo=120,
        genre=MusicGenre.ELECTRONIC,
        mood=Mood.ENERGETIC
    )
    
    music = generator.generate(
        config,
        prompt="Upbeat electronic music for a game trailer"
    )
    
    print(f"Generated music: {music['duration']}s")
    print(f"Tempo: {music['tempo']} BPM")
    print(f"Genre: {music['genre']}")


def example_procedural_content():
    """Example: Generate procedural game content"""
    print("\n=== Procedural Generation Example ===")
    
    generator = ProceduralGenerator(seed=42)
    
    # Generate quest
    quest = generator.generate_quest(
        quest_type="fetch",
        difficulty="medium"
    )
    
    print(f"Quest: {quest['title']}")
    print(f"Type: {quest['type']}")
    print(f"Objectives: {len(quest['objectives'])}")
    
    # Generate character
    character = generator.generate_character(role="npc")
    
    print(f"\nGenerated NPC: {character['name']}")
    print(f"Archetype: {character['archetype']}")
    print(f"Personality: {', '.join(character['personality'])}")


def example_workflow():
    """Example: Create and execute a workflow"""
    print("\n=== Workflow Example ===")
    
    from skills.core.workflow_manager import WorkflowStep, WorkflowStage
    
    manager = WorkflowManager()
    
    # Create workflow
    workflow = manager.create_workflow(
        "demo_workflow",
        "Demonstration of workflow system"
    )
    
    # Add steps
    manager.add_step(workflow, WorkflowStep(
        name="step_1",
        stage=WorkflowStage.PLANNING,
        function=lambda: {"result": "Step 1 complete"},
        outputs=["result"]
    ))
    
    manager.add_step(workflow, WorkflowStep(
        name="step_2",
        stage=WorkflowStage.CONTENT_GENERATION,
        function=lambda result: {"final": f"Step 2 using {result}"},
        inputs=["result"],
        outputs=["final"],
        dependencies=["step_1"]
    ))
    
    # Execute
    result = manager.execute_workflow(workflow)
    
    print(f"Workflow: {result.workflow_id}")
    print(f"Success: {result.success}")
    print(f"Outputs: {result.outputs}")


def example_performance_optimization():
    """Example: Profile and optimize performance"""
    print("\n=== Performance Optimization Example ===")
    
    optimizer = PerformanceOptimizer(enable_gpu=True)
    
    # Profile an operation
    with optimizer.profile("example_operation"):
        import time
        time.sleep(0.1)  # Simulate work
    
    # Get metrics
    metrics = optimizer.get_metrics("example_operation")
    
    print(f"Operation: {metrics['operation']}")
    print(f"Executions: {metrics['num_executions']}")
    print(f"Avg duration: {metrics['avg_duration_ms']:.2f}ms")


def example_caching():
    """Example: Use caching system"""
    print("\n=== Caching Example ===")
    
    cache = CacheManager(max_memory_mb=1024)
    
    # Store data
    cache.set("video_frame_001", {"data": "frame_data"}, ttl=3600, tags=["video"])
    cache.set("audio_clip_001", {"data": "audio_data"}, tags=["audio"])
    
    # Retrieve data
    frame = cache.get("video_frame_001")
    print(f"Retrieved from cache: {frame is not None}")
    
    # Get statistics
    stats = cache.get_stats()
    print(f"Cache entries: {stats['num_entries']}")
    print(f"Hit rate: {stats['hit_rate'] * 100:.1f}%")
    print(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Kimi-K2 Skills Framework - Examples")
    print("=" * 60)
    
    try:
        example_voice_synthesis()
        example_image_generation()
        example_music_generation()
        example_story_writing()
        example_procedural_content()
        example_workflow()
        example_performance_optimization()
        example_caching()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nNote: These are demonstration examples showing API usage.")
        print("Actual media generation requires model weights and GPU resources.")


if __name__ == "__main__":
    main()
