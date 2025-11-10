# Kimi-K2 Skills Framework - Comprehensive Tutorial

## Tutorial 1: Creating Your First Animated Short Film

This tutorial guides you through creating a complete animated film with dialogue, music, and visual effects.

### Project Overview

We'll create a 60-second animated short featuring:
- Opening narration with professional voice
- Background music synced to the narrative
- Animated character with lip-sync
- Cinematic lighting and camera work
- Final export in 4K quality

### Step 1: Script and Story Setup

```python
from skills.ai_creativity import StoryWriter
from skills.ai_creativity.story_writer import StoryConfig, Genre, NarrativePOV

# Initialize story writer
writer = StoryWriter()

# Create story project
config = StoryConfig(
    title="The Last Guardian",
    genre=Genre.FANTASY,
    target_word_count=500,  # Short script
    num_chapters=1,
    pov=NarrativePOV.THIRD_PERSON_LIMITED
)

story = writer.create_story(
    config,
    premise="A lone guardian protects an ancient tree in a mystical forest"
)

# Generate the script
script = writer.generate_scene(
    story,
    scene_description="Opening scene: Guardian watches over the glowing tree at dawn",
    characters=["Guardian"],
    location="Mystical Forest",
    word_count=100
)

print("Script generated:")
print(script)
```

### Step 2: Voice Synthesis with Emotion

```python
from skills.media_generation import VoiceSynthesizer
from skills.media_generation.voice_synthesizer import (
    VoiceProfile, VoiceGender, VoiceAge, Emotion, SynthesisConfig
)

# Initialize synthesizer
voice_synth = VoiceSynthesizer(device="cuda")

# Create narrator voice profile
narrator = voice_synth.create_voice_profile(
    name="MysticNarrator",
    gender=VoiceGender.MALE,
    age=VoiceAge.ELDERLY,
    language="en-US",
    pitch=0.85,  # Lower, deeper voice
    speed=0.9    # Slightly slower for gravitas
)

# Configure high-quality synthesis
synth_config = SynthesisConfig(
    sample_rate=48000,
    bit_depth=24,
    quality="ultra",
    enable_enhancement=True,
    noise_reduction=True
)

# Synthesize narration with emotion
narration_text = """
In an age long forgotten, when magic still flowed through the world,
a lone guardian stood watch. His duty: to protect the Tree of Eternity,
whose roots reached deep into the heart of the world itself.
"""

narration_audio = voice_synth.synthesize(
    narration_text,
    narrator,
    emotion=Emotion.CALM,
    emotion_intensity=0.8,
    config=synth_config
)

# Extract phonemes for lip-sync
phonemes = voice_synth.extract_phonemes_for_lipsync(
    narration_audio,
    time_aligned=True
)

# Export narration
voice_synth.export(narration_audio, "narration.wav")

print(f"Narration generated: {narration_audio['duration']:.2f} seconds")
print(f"Phonemes for lip-sync: {len(phonemes)}")
```

### Step 3: Music Composition

```python
from skills.media_generation import MusicGenerator
from skills.media_generation.music_generator import (
    MusicConfig, MusicGenre, Mood, Instrument
)

# Initialize music generator
music_gen = MusicGenerator(device="cuda")

# Configure music to match the mystical, calm mood
music_config = MusicConfig(
    duration=60.0,
    tempo=80,  # Slow, contemplative
    key="D minor",
    time_signature="4/4",
    genre=MusicGenre.ORCHESTRAL,
    mood=Mood.PEACEFUL,
    complexity=0.6,
    sample_rate=48000
)

# Generate main theme
music = music_gen.generate(
    music_config,
    prompt="Mystical forest theme with ethereal atmosphere, gentle strings and woodwinds",
    seed=42
)

# Add orchestral tracks
strings = [
    Instrument("Violins", "string", volume=0.7, pan=-0.3),
    Instrument("Violas", "string", volume=0.6, pan=0.0),
    Instrument("Cellos", "string", volume=0.8, pan=0.3)
]

woodwinds = [
    Instrument("Flute", "woodwind", volume=0.5, pan=-0.2),
    Instrument("Oboe", "woodwind", volume=0.4, pan=0.2)
]

ambient = [
    Instrument("Synth Pad", "synth", volume=0.3, pan=0.0)
]

music_gen.add_track(music, strings, role="melody")
music_gen.add_track(music, woodwinds, role="harmony")
music_gen.add_track(music, ambient, role="bass")

# Dynamic mixing - build intensity then calm
intensity_curve = [
    (0.0, 0.2),    # Quiet opening
    (15.0, 0.4),   # Building
    (30.0, 0.7),   # Peak (guardian moment)
    (45.0, 0.5),   # Release
    (60.0, 0.3)    # Fade to calm
]

music_gen.apply_dynamic_mixing(music, intensity_curve, auto_duck=True)

# Export music
music_gen.export(music, "mystical_forest_theme.wav", export_stems=True)

print("Music generated with dynamic intensity curve")
```

### Step 4: Character Animation

```python
from skills.media_generation import AnimationEngine
from skills.media_generation.animation_engine import (
    AnimationConfig, AnimationStyle, LightingMode,
    Character, LightSource, CameraConfig, PhysicsConfig
)

# Initialize animation engine
anim_engine = AnimationEngine(device="cuda")

# Create guardian character
guardian = Character(
    name="Guardian",
    rigging_type="humanoid",
    animations=["idle", "breathing", "looking_around"]
)

# Configure animation
anim_config = AnimationConfig(
    style=AnimationStyle.REALISTIC,
    fps=60,
    duration=60.0,
    resolution=(3840, 2160),  # 4K
    lighting_mode=LightingMode.CINEMATIC,
    render_quality="ultra"
)

# Enable physics for realistic cloth and hair
anim_config.physics = PhysicsConfig(
    enabled=True,
    cloth_simulation=True,
    soft_body=True
)

# Create animation
animation = anim_engine.create_animation(
    [guardian],
    anim_config,
    scene_description="Guardian standing watch over glowing tree at dawn"
)

# Add subtle idle motion
anim_engine.add_motion_sequence(
    animation,
    motion_type="breathing",
    character_name="Guardian",
    start_time=0.0,
    duration=60.0,
    parameters={"intensity": 0.3, "rate": 0.2}
)

# Add lip-sync for narration
anim_engine.add_lip_sync(
    animation,
    character_name="Guardian",
    audio_path="narration.wav",
    phoneme_map=None  # Use default mapping
)

# Setup cinematic lighting
sun_light = LightSource(
    type="directional",
    direction=(0.4, -0.8, 0.4),
    color=(1.0, 0.9, 0.7),  # Warm sunrise
    intensity=2.0,
    shadows=True,
    shadow_quality="ultra"
)

rim_light = LightSource(
    type="directional",
    direction=(-0.3, 0.2, -1.0),
    color=(0.6, 0.7, 1.0),  # Cool blue rim
    intensity=0.8
)

tree_glow = LightSource(
    type="point",
    position=(0, 3, -2),
    color=(0.3, 1.0, 0.5),  # Magical green glow
    intensity=1.5
)

anim_engine.setup_lighting(animation, [sun_light, rim_light, tree_glow])

# Camera movement
camera_keyframes = [
    (0.0, CameraConfig(
        position=(8, 2, 10),
        target=(0, 1.7, 0),
        fov=45.0
    )),
    (30.0, CameraConfig(
        position=(6, 2, 8),
        target=(0, 1.7, 0),
        fov=40.0
    )),
    (60.0, CameraConfig(
        position=(10, 3, 12),
        target=(0, 2, 0),
        fov=50.0
    ))
]

anim_engine.create_camera_path(animation, camera_keyframes, smooth=True)

# Render animation
anim_engine.render(
    animation,
    "guardian_animation.mp4",
    quality="ultra",
    denoising=True,
    samples=256
)

print("Animation rendered in 4K with cinematic lighting")
```

### Step 5: Background Environment

```python
from skills.media_generation import ImageGenerator
from skills.media_generation.image_generator import ImageConfig, ImageStyle

# Initialize image generator
img_gen = ImageGenerator(device="cuda")

# Generate background scene
bg_config = ImageConfig(
    width=3840,
    height=2160,
    style=ImageStyle.PHOTOREALISTIC,
    quality="ultra",
    steps=150,
    guidance_scale=8.5
)

background = img_gen.generate(
    prompt="""Mystical ancient forest at dawn, glowing ethereal tree in center,
    soft mist, magical atmosphere, rays of sunlight through trees,
    fantasy landscape, highly detailed, cinematic lighting""",
    config=bg_config,
    negative_prompt="people, characters, low quality, blurry",
    seed=42
)

# Enhance and upscale
background = img_gen.enhance(
    background,
    enhance_faces=False,
    denoise=True,
    sharpen=True,
    color_correction=True
)

# Export
img_gen.export(background, "forest_background.png", format="png", quality=100)

print("Background environment generated")
```

### Step 6: Final Assembly and Export

```python
from skills.media_generation import VideoGenerator
from skills.media_generation.video_generator import (
    VideoConfig, VideoQuality, VideoFormat, Scene
)

# Initialize video generator
video_gen = VideoGenerator(device="cuda")

# Configure final video
video_config = VideoConfig(
    width=3840,
    height=2160,
    fps=60,
    duration=60.0,
    quality=VideoQuality.UHD_4K,
    format=VideoFormat.MP4,
    codec="h265",  # HEVC for better compression
    bitrate="25M",
    enable_hdr=True,
    enable_audio=True
)

# Create complete scene
final_scene = Scene(
    description="Guardian standing before the Tree of Eternity at dawn",
    duration=60.0,
    camera_angles=["cinematic"],
    lighting={"type": "natural", "time": "sunrise"},
    objects=[]
)

# Generate final video (combines animation and background)
final_video = video_gen.generate(
    [final_scene],
    video_config,
    seed=42
)

# Add narration audio
final_video = video_gen.add_audio_track(
    final_video,
    "narration.wav",
    volume=0.9,
    fade_in=1.0,
    fade_out=2.0
)

# Add music track (ducked for narration)
final_video = video_gen.add_audio_track(
    final_video,
    "mystical_forest_theme.wav",
    volume=0.6  # Lower volume so narration is clear
)

# Apply final effects
effects = [
    {"type": "color_grade", "preset": "cinematic_warm"},
    {"type": "lens_flare", "intensity": 0.3, "position": "sun"},
    {"type": "depth_of_field", "strength": 0.4},
    {"type": "film_grain", "intensity": 0.1},
    {"type": "vignette", "strength": 0.2}
]

final_video = video_gen.apply_effects(final_video, effects)

# Export final production
video_gen.export(
    final_video,
    "The_Last_Guardian_Final.mp4",
    optimize_for_web=True
)

print("\\n=== PRODUCTION COMPLETE ===")
print("Film: The Last Guardian")
print("Duration: 60 seconds")
print("Resolution: 4K UHD (3840x2160)")
print("Format: MP4 (H.265)")
print("Output: The_Last_Guardian_Final.mp4")
print("\\nYour animated short film is ready!")
```

### Step 7: Using Workflow Manager (Alternative)

For automated production, use the Workflow Manager:

```python
from skills.core import WorkflowManager
from skills.core.workflow_manager import WorkflowStep, WorkflowStage

# Create complete production workflow
manager = WorkflowManager()

# Use pre-configured film workflow
workflow = manager.create_animated_film_workflow(
    project_name="The Last Guardian",
    script=narration_text,
    duration=60.0
)

# Execute entire production pipeline
result = manager.execute_workflow(workflow, parallel=True)

if result.success:
    print(f"\\nProduction completed successfully!")
    print(f"Final video: {result.outputs['exported_path']}")
else:
    print("\\nErrors during production:")
    for error in result.errors:
        print(f"  - {error}")

# Check workflow status
status = manager.get_workflow_status(workflow['id'])
print(f"\\nWorkflow Status: {status['status']}")
print(f"Progress: {status['progress'] * 100:.1f}%")
```

## Tutorial 2: Interactive Game Dialogue System

Create dynamic NPC dialogues with branching choices.

```python
from skills.ai_creativity import DialogueGenerator, ProceduralGenerator
from skills.media_generation import VoiceSynthesizer

# Initialize generators
dialogue_gen = DialogueGenerator()
proc_gen = ProceduralGenerator(seed=42)
voice_synth = VoiceSynthesizer(device="cuda")

# Define NPC character voice
dialogue_gen.define_character_voice(
    "Elder Wizard",
    traits=["wise", "mysterious", "patient"],
    speech_patterns=["speaks in riddles", "uses archaic language"],
    vocabulary="formal"
)

# Create NPC voice profile
wizard_voice = voice_synth.create_voice_profile(
    name="ElderWizard",
    gender=VoiceGender.MALE,
    age=VoiceAge.ELDERLY,
    language="en-US",
    pitch=0.8,
    speed=0.85
)

# Generate branching dialogue tree
dialogue_tree = proc_gen.generate_dialogue_tree(
    topic="ancient prophecy",
    depth=4,
    personality="wise_mentor"
)

# Generate voiced responses for each node
for node_id, node in dialogue_tree.items():
    if node.type == "response":
        audio = voice_synth.synthesize(
            node.content,
            wizard_voice,
            emotion=Emotion.CALM
        )
        voice_synth.export(audio, f"dialogue_{node_id}.wav")

print(f"Generated dialogue tree with {len(dialogue_tree)} nodes")
print("All dialogue voiced and exported")
```

## Tutorial 3: Procedural Quest Generation

Generate dynamic quests for an RPG game.

```python
from skills.ai_creativity import ProceduralGenerator, StoryWriter

proc_gen = ProceduralGenerator(seed=None)  # Random each time
story_writer = StoryWriter()

# Generate main quest
main_quest = proc_gen.generate_quest(
    quest_type="investigate",
    difficulty="hard",
    context={
        "location": "Ancient Ruins",
        "threat": "Dark Magic",
        "urgency": "high"
    }
)

print(f"Main Quest: {main_quest['title']}")
print(f"Objectives:")
for obj in main_quest['objectives']:
    print(f"  {obj['type']}: {obj.get('location', obj.get('item', 'unknown'))}")

# Generate side quests
for i in range(3):
    side_quest = proc_gen.generate_quest(
        quest_type=random.choice(["fetch", "escort", "puzzle"]),
        difficulty="medium"
    )
    print(f"\\nSide Quest {i+1}: {side_quest['title']}")

# Generate quest NPCs
quest_giver = proc_gen.generate_character(
    role="quest_giver",
    archetype="wise_elder",
    include_backstory=True
)

print(f"\\nQuest Giver: {quest_giver['name']}")
print(f"Background: {quest_giver['backstory']}")

# Generate quest locations
for i in range(3):
    location = proc_gen.generate_world_element(
        element_type="location",
        theme="dark_fantasy"
    )
    print(f"\\nLocation {i+1}: {location['name']}")
    print(f"  Terrain: {location.get('terrain', 'unknown')}")
```

## Performance Tips

### 1. Use Caching for Repeated Assets

```python
from skills.core import CacheManager

cache = CacheManager(max_memory_mb=4096)

# Cache generated models
cache.set("wizard_voice_model", wizard_voice, ttl=7200, tags=["voices"])
cache.set("forest_bg", background, tags=["backgrounds"])

# Reuse cached assets
cached_voice = cache.get("wizard_voice_model")
```

### 2. Batch Processing

```python
from skills.media_generation import ImageGenerator

img_gen = ImageGenerator(device="cuda")

prompts = [
    "Forest scene at dawn",
    "Mountain landscape at sunset",
    "Ocean waves at midnight"
]

# Generate all at once
images = img_gen.batch_generate(prompts, config, parallel=True)
```

### 3. Profile Performance

```python
from skills.core import PerformanceOptimizer

optimizer = PerformanceOptimizer()

with optimizer.profile("video_generation"):
    video = video_gen.generate(scenes, config)

metrics = optimizer.get_metrics("video_generation")
print(f"Generation took {metrics['avg_duration_ms']:.0f}ms")
```

## Next Steps

- Explore [API Reference](api_reference.md) for detailed documentation
- See [Skills Documentation](skills_documentation.md) for more examples
- Experiment with different styles, moods, and configurations
- Share your creations with the community!

---

For questions and support, visit the [Kimi-K2 repository](https://github.com/moonshotai/Kimi-K2).
