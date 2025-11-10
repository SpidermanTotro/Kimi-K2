# Kimi-K2 Skills Framework - API Reference

## Table of Contents

- [Media Generation](#media-generation)
  - [VideoGenerator](#videogenerator)
  - [AnimationEngine](#animationengine)
  - [VoiceSynthesizer](#voicesynthesizer)
  - [MusicGenerator](#musicgenerator)
  - [ImageGenerator](#imagegenerator)
- [AI Creativity](#ai-creativity)
  - [StoryWriter](#storywriter)
  - [DialogueGenerator](#dialoguegenerator)
  - [ProceduralGenerator](#proceduralgenerator)
- [Core Utilities](#core-utilities)
  - [CacheManager](#cachemanager)
  - [PerformanceOptimizer](#performanceoptimizer)
  - [WorkflowManager](#workflowmanager)

---

## Media Generation

### VideoGenerator

Full-length video generation with scene composition and effects.

#### Class: `VideoGenerator(model_path=None, device="cuda")`

**Methods:**

##### `generate(scenes, config, prompt=None, negative_prompt=None, seed=None)`
Generate video from scene descriptions.

**Parameters:**
- `scenes` (List[Scene]): List of Scene objects
- `config` (VideoConfig): Video configuration
- `prompt` (str, optional): Text guidance
- `negative_prompt` (str, optional): Quality control
- `seed` (int, optional): Random seed

**Returns:** `Dict[str, any]` - Video data dictionary

**Example:**
```python
scenes = [Scene("Opening shot", duration=10.0, camera_angles=["wide"])]
config = VideoConfig(width=1920, height=1080, fps=30)
video = generator.generate(scenes, config, seed=42)
```

##### `generate_from_text(text_description, config, auto_scene_split=True)`
Generate video directly from text.

**Parameters:**
- `text_description` (str): Natural language video description
- `config` (VideoConfig): Video configuration  
- `auto_scene_split` (bool): Automatically split into scenes

**Returns:** `Dict[str, any]` - Video data

##### `add_audio_track(video_data, audio_path, volume=1.0, fade_in=0.0, fade_out=0.0)`
Add audio to video.

**Parameters:**
- `video_data` (Dict): Video data dictionary
- `audio_path` (str): Path to audio file
- `volume` (float): Volume level (0.0 to 1.0)
- `fade_in` (float): Fade in duration (seconds)
- `fade_out` (float): Fade out duration (seconds)

**Returns:** `Dict[str, any]` - Updated video data

##### `export(video_data, output_path, optimize_for_web=False)`
Export video to file.

**Parameters:**
- `video_data` (Dict): Video to export
- `output_path` (str): Output file path
- `optimize_for_web` (bool): Apply web optimization

**Returns:** `str` - Path to exported file

#### Data Classes:

##### `VideoConfig`
```python
@dataclass
class VideoConfig:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    duration: float = 60.0
    quality: VideoQuality = VideoQuality.FULL_HD
    format: VideoFormat = VideoFormat.MP4
    codec: str = "h264"
    bitrate: str = "8M"
    enable_hdr: bool = False
    enable_audio: bool = True
```

##### `Scene`
```python
@dataclass
class Scene:
    description: str
    duration: float
    camera_angles: List[str]
    lighting: Dict[str, any]
    objects: List[Dict[str, any]]
    transitions: Optional[Dict[str, any]] = None
```

---

### AnimationEngine

Cinematic-quality animation with advanced features.

#### Class: `AnimationEngine(model_path=None, device="cuda")`

**Methods:**

##### `create_animation(characters, config, scene_description=None)`
Create new animation.

**Parameters:**
- `characters` (List[Character]): Characters to animate
- `config` (AnimationConfig): Animation configuration
- `scene_description` (str, optional): Scene description

**Returns:** `Dict[str, any]` - Animation data

##### `add_motion_sequence(animation, motion_type, character_name=None, start_time=0.0, duration=5.0, parameters=None)`
Add choreographed motion.

**Parameters:**
- `animation` (Dict): Animation data
- `motion_type` (str): Motion type ("walk", "run", "jump", etc.)
- `character_name` (str, optional): Target character
- `start_time` (float): Start time in seconds
- `duration` (float): Motion duration
- `parameters` (Dict, optional): Motion parameters

**Returns:** `Dict[str, any]` - Updated animation

##### `setup_lighting(animation, lights, mode=None)`
Configure lighting.

**Parameters:**
- `animation` (Dict): Animation data
- `lights` (List[LightSource]): Light sources
- `mode` (LightingMode, optional): Lighting preset

**Returns:** `Dict[str, any]` - Updated animation

##### `add_lip_sync(animation, character_name, audio_path, phoneme_map=None)`
Add lip-sync animation.

**Parameters:**
- `animation` (Dict): Animation data
- `character_name` (str): Character name
- `audio_path` (str): Audio file path
- `phoneme_map` (Dict, optional): Phoneme to viseme mapping

**Returns:** `Dict[str, any]` - Updated animation

##### `render(animation, output_path, quality="high", denoising=True, samples=128)`
Render animation to file.

**Parameters:**
- `animation` (Dict): Animation to render
- `output_path` (str): Output path
- `quality` (str): Render quality
- `denoising` (bool): Enable AI denoising
- `samples` (int): Samples per pixel

**Returns:** `str` - Path to rendered file

#### Data Classes:

##### `AnimationConfig`
```python
@dataclass
class AnimationConfig:
    style: AnimationStyle = AnimationStyle.REALISTIC
    fps: int = 30
    duration: float = 60.0
    resolution: Tuple[int, int] = (1920, 1080)
    lighting_mode: LightingMode = LightingMode.CINEMATIC
    physics: PhysicsConfig = PhysicsConfig()
    camera: CameraConfig = CameraConfig()
    render_quality: str = "high"
```

##### `Character`
```python
@dataclass
class Character:
    name: str
    model_path: Optional[str] = None
    rigging_type: str = "auto"
    skeleton: Optional[Dict] = None
    animations: List[str] = []
```

---

### VoiceSynthesizer

Multi-language voice synthesis with emotional expression.

#### Class: `VoiceSynthesizer(model_path=None, device="cuda")`

**Supported Languages:** 100+ (see `SUPPORTED_LANGUAGES` attribute)

**Methods:**

##### `create_voice_profile(name, gender=VoiceGender.NEUTRAL, age=VoiceAge.ADULT, language="en-US", reference_audio=None, **kwargs)`
Create custom voice profile.

**Parameters:**
- `name` (str): Profile name
- `gender` (VoiceGender): Voice gender
- `age` (VoiceAge): Age category
- `language` (str): Language code
- `reference_audio` (str, optional): Audio for voice cloning
- `**kwargs`: Additional parameters (pitch, speed, energy)

**Returns:** `VoiceProfile` - Voice profile object

##### `synthesize(text, voice_profile, emotion=Emotion.NEUTRAL, emotion_intensity=1.0, config=None)`
Synthesize speech from text.

**Parameters:**
- `text` (str): Text to synthesize
- `voice_profile` (VoiceProfile): Voice to use
- `emotion` (Emotion): Emotional expression
- `emotion_intensity` (float): Emotion intensity (0.0 to 2.0)
- `config` (SynthesisConfig, optional): Synthesis configuration

**Returns:** `Dict[str, any]` - Audio data with phonemes

##### `synthesize_dialogue(dialogue, pause_between=0.5, config=None)`
Synthesize multi-character dialogue.

**Parameters:**
- `dialogue` (List[Tuple]): List of (text, emotion, voice_profile)
- `pause_between` (float): Pause between lines (seconds)
- `config` (SynthesisConfig, optional): Configuration

**Returns:** `List[Dict]` - Audio data for each line

##### `synthesize_multilingual(text_translations, base_voice, auto_adapt=True)`
Synthesize in multiple languages.

**Parameters:**
- `text_translations` (Dict[str, str]): language_code: text mapping
- `base_voice` (VoiceProfile): Base voice profile
- `auto_adapt` (bool): Adapt voice per language

**Returns:** `Dict[str, Dict]` - language_code: audio_data mapping

##### `extract_phonemes_for_lipsync(audio_data, time_aligned=True)`
Extract phoneme timings for lip-sync.

**Parameters:**
- `audio_data` (Dict): Audio data from synthesis
- `time_aligned` (bool): Include time alignment

**Returns:** `List[Dict]` - Phoneme data with timings

##### `export(audio_data, output_path, format=None)`
Export audio to file.

**Parameters:**
- `audio_data` (Dict): Audio to export
- `output_path` (str): Output path
- `format` (str, optional): Audio format override

**Returns:** `str` - Path to exported file

#### Data Classes:

##### `VoiceProfile`
```python
@dataclass
class VoiceProfile:
    name: str
    gender: VoiceGender = VoiceGender.NEUTRAL
    age: VoiceAge = VoiceAge.ADULT
    language: str = "en-US"
    pitch: float = 1.0  # 0.5 - 2.0
    speed: float = 1.0  # 0.5 - 2.0
    energy: float = 1.0
    accent: Optional[str] = None
```

---

### MusicGenerator

AI music generation with scene synchronization.

#### Class: `MusicGenerator(model_path=None, device="cuda")`

**Methods:**

##### `generate(config, prompt=None, reference_audio=None, seed=None)`
Generate music from configuration.

**Parameters:**
- `config` (MusicConfig): Music configuration
- `prompt` (str, optional): Text description
- `reference_audio` (str, optional): Reference for style
- `seed` (int, optional): Random seed

**Returns:** `Dict[str, any]` - Music data

##### `generate_for_scene(scene_data, sync_points=None, adaptive=True)`
Generate scene-synchronized music.

**Parameters:**
- `scene_data` (Dict): Animation scene data
- `sync_points` (List[Tuple], optional): (time, event) sync points
- `adaptive` (bool): Adapt to scene dynamics

**Returns:** `Dict[str, any]` - Scene-synced music

##### `add_track(music_data, instruments, role="melody")`
Add instrumental track.

**Parameters:**
- `music_data` (Dict): Music data
- `instruments` (List[Instrument]): Track instruments
- `role` (str): Musical role ("melody", "harmony", "rhythm", "bass")

**Returns:** `Dict[str, any]` - Updated music

##### `generate_ambient_loop(duration=60.0, mood=Mood.PEACEFUL, seamless=True)`
Generate seamless ambient loop.

**Parameters:**
- `duration` (float): Loop duration (seconds)
- `mood` (Mood): Desired mood
- `seamless` (bool): Ensure seamless looping

**Returns:** `Dict[str, any]` - Loopable music

##### `export(music_data, output_path, format="wav", export_stems=False)`
Export music to file.

**Parameters:**
- `music_data` (Dict): Music to export
- `output_path` (str): Output path
- `format` (str): Audio format
- `export_stems` (bool): Export individual tracks

**Returns:** `str` - Path to exported file

#### Data Classes:

##### `MusicConfig`
```python
@dataclass
class MusicConfig:
    duration: float = 60.0
    tempo: int = 120  # BPM
    key: str = "C"
    time_signature: str = "4/4"
    genre: MusicGenre = MusicGenre.CINEMATIC
    mood: Mood = Mood.EPIC
    complexity: float = 0.7  # 0.0 to 1.0
    sample_rate: int = 48000
```

---

### ImageGenerator

High-resolution image generation with artistic control.

#### Class: `ImageGenerator(model_path=None, device="cuda")`

**Methods:**

##### `generate(prompt, config, negative_prompt=None, reference_image=None, strength=0.8)`
Generate image from prompt.

**Parameters:**
- `prompt` (str): Image description
- `config` (ImageConfig): Generation configuration
- `negative_prompt` (str, optional): Things to avoid
- `reference_image` (str, optional): Reference for img2img
- `strength` (float): Reference image strength (0.0 to 1.0)

**Returns:** `Dict[str, any]` - Image data

##### `generate_variations(base_image, num_variations=4, variation_strength=0.3)`
Generate image variations.

**Parameters:**
- `base_image` (Dict): Base image data
- `num_variations` (int): Number of variations
- `variation_strength` (float): Variation strength (0.0 to 1.0)

**Returns:** `List[Dict]` - Image variations

##### `upscale(image_data, scale_factor=4, method="ai")`
Upscale image to higher resolution.

**Parameters:**
- `image_data` (Dict): Image to upscale
- `scale_factor` (int): Scaling factor (2, 4, 8)
- `method` (str): Method ("ai", "lanczos", "bicubic")

**Returns:** `Dict[str, any]` - Upscaled image

##### `inpaint(image_data, mask, prompt, config=None)`
Inpaint masked region.

**Parameters:**
- `image_data` (Dict): Original image
- `mask` (Dict): Mask indicating region
- `prompt` (str): Description of inpainted content
- `config` (ImageConfig, optional): Configuration

**Returns:** `Dict[str, any]` - Inpainted image

##### `export(image_data, output_path, format="png", quality=95)`
Export image to file.

**Parameters:**
- `image_data` (Dict): Image to export
- `output_path` (str): Output path
- `format` (str): Image format
- `quality` (int): Quality for lossy formats (0-100)

**Returns:** `str` - Path to exported file

#### Data Classes:

##### `ImageConfig`
```python
@dataclass
class ImageConfig:
    width: int = 1024
    height: int = 1024
    style: ImageStyle = ImageStyle.PHOTOREALISTIC
    quality: str = "high"
    steps: int = 50
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    upscale_factor: int = 1
```

---

## AI Creativity

### StoryWriter

Long-form narrative and book writing.

#### Class: `StoryWriter(kimi_client=None)`

**Methods:**

##### `create_story(config, premise=None)`
Create new story project.

**Parameters:**
- `config` (StoryConfig): Story configuration
- `premise` (str, optional): Story premise

**Returns:** `Dict[str, any]` - Story data structure

##### `add_character(story, character)`
Add character to story.

**Parameters:**
- `story` (Dict): Story data
- `character` (Character): Character to add

**Returns:** `Dict[str, any]` - Updated story

##### `generate_outline(story, use_structure="three_act")`
Generate story outline.

**Parameters:**
- `story` (Dict): Story data
- `use_structure` (str): Structure type

**Returns:** `Dict[str, any]` - Story with outline

##### `write_chapter(story, chapter_number, style_guidance=None)`
Write specific chapter.

**Parameters:**
- `story` (Dict): Story data
- `chapter_number` (int): Chapter to write (1-indexed)
- `style_guidance` (str, optional): Style guidance

**Returns:** `str` - Generated chapter text

##### `export_manuscript(story, format="markdown")`
Export completed story.

**Parameters:**
- `story` (Dict): Story data
- `format` (str): Export format

**Returns:** `str` - Path to exported manuscript

#### Data Classes:

##### `StoryConfig`
```python
@dataclass
class StoryConfig:
    title: str = "Untitled"
    genre: Genre = Genre.FANTASY
    target_word_count: int = 80000
    num_chapters: int = 20
    pov: NarrativePOV = NarrativePOV.THIRD_PERSON_LIMITED
    writing_style: str = "descriptive"
    tone: str = "serious"
```

---

### DialogueGenerator

Natural dialogue and conversation generation.

#### Class: `DialogueGenerator(kimi_client=None)`

**Methods:**

##### `define_character_voice(character_name, traits, speech_patterns, vocabulary="standard")`
Define character's unique voice.

**Parameters:**
- `character_name` (str): Character name
- `traits` (List[str]): Personality traits
- `speech_patterns` (List[str]): Speech patterns
- `vocabulary` (str): Vocabulary level

##### `generate_conversation(context, num_exchanges=10, style=DialogueStyle.PROSE, include_actions=True)`
Generate multi-character conversation.

**Parameters:**
- `context` (DialogueContext): Dialogue context
- `num_exchanges` (int): Number of exchanges
- `style` (DialogueStyle): Formatting style
- `include_actions` (bool): Include character actions

**Returns:** `List[DialogueLine]` - Dialogue lines

##### `generate_npc_dialogue(npc_name, player_action, context, branching=True)`
Generate NPC dialogue for games.

**Parameters:**
- `npc_name` (str): NPC name
- `player_action` (str): Player action
- `context` (str): Game context
- `branching` (bool): Generate dialogue tree

**Returns:** `Dict[str, any]` - Dialogue with branches

---

### ProceduralGenerator

Procedural content and branching narrative generation.

#### Class: `ProceduralGenerator(kimi_client=None, seed=None)`

**Methods:**

##### `create_branching_narrative(title, num_branches=3, depth=3, theme=None)`
Create branching narrative structure.

**Parameters:**
- `title` (str): Narrative title
- `num_branches` (int): Branches per node
- `depth` (int): Maximum depth
- `theme` (str, optional): Theme/genre

**Returns:** `BranchingNarrative` - Narrative structure

##### `generate_quest(quest_type="fetch", difficulty="medium", context=None)`
Generate game quest.

**Parameters:**
- `quest_type` (str): Quest type
- `difficulty` (str): Difficulty level
- `context` (Dict, optional): World context

**Returns:** `Dict[str, any]` - Quest data

##### `generate_character(role="npc", archetype=None, include_backstory=True)`
Procedurally generate character.

**Parameters:**
- `role` (str): Character role
- `archetype` (str, optional): Character archetype
- `include_backstory` (bool): Generate backstory

**Returns:** `Dict[str, any]` - Character data

---

## Core Utilities

### CacheManager

Intelligent caching for assets and generated content.

#### Class: `CacheManager(max_memory_mb=2048, cache_dir=None, eviction_policy="lru", enable_disk_cache=True, enable_persistence=True)`

**Methods:**

##### `get(key, default=None)`
Get value from cache.

**Parameters:**
- `key` (str): Cache key
- `default` (any): Default if not found

**Returns:** Cached value or default

##### `set(key, value, ttl=None, tags=None)`
Set value in cache.

**Parameters:**
- `key` (str): Cache key
- `value` (any): Value to cache
- `ttl` (int, optional): Time to live (seconds)
- `tags` (List[str], optional): Tags for invalidation

##### `invalidate_by_tag(tag)`
Invalidate all entries with tag.

**Parameters:**
- `tag` (str): Tag to invalidate

##### `get_stats()`
Get cache statistics.

**Returns:** `Dict[str, any]` - Statistics

---

### PerformanceOptimizer

Performance optimization and profiling.

#### Class: `PerformanceOptimizer(enable_gpu=True, enable_mixed_precision=True, memory_limit_mb=None)`

**Methods:**

##### `profile(operation_name)`
Context manager for profiling.

**Parameters:**
- `operation_name` (str): Operation name

**Usage:**
```python
with optimizer.profile("generation"):
    result = generate()
```

##### `get_metrics(operation_name, aggregate=True)`
Get performance metrics.

**Parameters:**
- `operation_name` (str): Operation name
- `aggregate` (bool): Return aggregated stats

**Returns:** `Dict[str, any]` - Metrics

##### `find_optimal_batch_size(operation, test_data, max_memory_mb=8000)`
Find optimal batch size.

**Parameters:**
- `operation` (Callable): Operation to test
- `test_data` (List): Sample data
- `max_memory_mb` (int): Memory constraint

**Returns:** `int` - Optimal batch size

---

### WorkflowManager

End-to-end workflow orchestration.

#### Class: `WorkflowManager()`

**Methods:**

##### `create_workflow(workflow_id, description=None)`
Create new workflow.

**Parameters:**
- `workflow_id` (str): Workflow identifier
- `description` (str, optional): Description

**Returns:** `Dict[str, any]` - Workflow structure

##### `add_step(workflow, step)`
Add step to workflow.

**Parameters:**
- `workflow` (Dict): Workflow data
- `step` (WorkflowStep): Step to add

##### `execute_workflow(workflow, parallel=True)`
Execute complete workflow.

**Parameters:**
- `workflow` (Dict): Workflow to execute
- `parallel` (bool): Enable parallel execution

**Returns:** `WorkflowResult` - Execution result

##### `create_animated_film_workflow(project_name, script, duration=60.0)`
Create pre-configured film workflow.

**Parameters:**
- `project_name` (str): Project name
- `script` (str): Film script
- `duration` (float): Film duration

**Returns:** `Dict[str, any]` - Configured workflow

---

## Enumerations

### VideoQuality
- `SD` - Standard Definition (480p)
- `HD` - High Definition (720p)
- `FULL_HD` - Full HD (1080p)
- `UHD_4K` - Ultra HD 4K (2160p)
- `UHD_8K` - Ultra HD 8K (4320p)

### AnimationStyle
- `REALISTIC` - Photorealistic
- `CARTOON` - Cartoon style
- `ANIME` - Anime style
- `STYLIZED` - Stylized art

### Emotion
- `NEUTRAL`, `HAPPY`, `SAD`, `ANGRY`, `EXCITED`, `CALM`, `FEARFUL`, `SURPRISED`

### MusicGenre
- `ORCHESTRAL`, `ELECTRONIC`, `AMBIENT`, `CINEMATIC`, `JAZZ`, `ROCK`, `POP`, `CLASSICAL`

### Mood
- `EPIC`, `PEACEFUL`, `TENSE`, `JOYFUL`, `MELANCHOLIC`, `MYSTERIOUS`, `ENERGETIC`

### ImageStyle
- `PHOTOREALISTIC`, `ILLUSTRATION`, `ANIME`, `PAINTING`, `SKETCH`, `WATERCOLOR`

### Genre (Story)
- `FANTASY`, `SCIENCE_FICTION`, `MYSTERY`, `THRILLER`, `ROMANCE`, `HORROR`

---

For complete examples and tutorials, see [skills_documentation.md](skills_documentation.md)
