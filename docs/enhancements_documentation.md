# Kimi-K2 Enhancements Documentation

This document provides comprehensive documentation for the new features added to Kimi-K2, including Animation AI Capabilities, Linux-style Command System, and Optimized GPT Models.

## Table of Contents

1. [Animation AI Capabilities](#animation-ai-capabilities)
   - [Claymation Assistant](#claymation-assistant)
   - [Animation Assistant](#animation-assistant)
2. [Linux-style Command System](#linux-style-command-system)
   - [Command System](#command-system)
   - [Forge AI Extension](#forge-ai-extension)
3. [Optimized GPT Models](#optimized-gpt-models)
   - [Optimized GPT](#optimized-gpt)
   - [16-Layer Transformer Model](#16-layer-transformer-model)
4. [Examples](#examples)
5. [Testing](#testing)

---

## Animation AI Capabilities

### Claymation Assistant

The Claymation Assistant is designed for analyzing stop-motion sequences, generating intermediate frames, and applying style presets.

#### Features

- **Sequence Analysis**: Analyze stop-motion frames to detect motion and identify keyframes
- **Intermediate Frame Generation**: Create smooth transitions between keyframes
- **Style Presets**: Apply different interpolation styles (classic, smooth, artistic)
- **Custom Styles**: Define custom interpolation styles

#### Usage

```python
from kimi_k2.animation import ClayamationAssistant
import numpy as np

# Create assistant
assistant = ClayamationAssistant()

# Create sample frames
frames = [np.random.rand(100, 100, 3) for _ in range(5)]

# Analyze sequence
analysis = assistant.analyze_sequence(frames)

# Generate intermediate frames
start_frame = frames[0]
end_frame = frames[-1]
intermediate = assistant.generate_intermediate_frames(
    start_frame, end_frame, num_frames=10, style="smooth"
)

# Process complete sequence
result = assistant.process_sequence(frames, target_fps=24, style="smooth")
```

#### API Reference

##### `analyze_sequence(frames: List[np.ndarray]) -> Dict[str, Any]`
Analyze a stop-motion sequence to extract motion patterns and keyframes.

**Parameters:**
- `frames`: List of frame arrays representing the stop-motion sequence

**Returns:**
- Dictionary containing:
  - `frame_count`: Number of frames
  - `motion_detected`: Whether motion was detected
  - `keyframe_indices`: Indices of detected keyframes
  - `motion_vectors`: Estimated motion between frames

##### `generate_intermediate_frames(start_frame, end_frame, num_frames=5, style=None) -> List[np.ndarray]`
Generate intermediate frames between two keyframes.

**Parameters:**
- `start_frame`: Starting keyframe
- `end_frame`: Ending keyframe
- `num_frames`: Number of intermediate frames to generate
- `style`: Style preset to use (None uses current style)

**Returns:**
- List of generated intermediate frames

##### `apply_style_preset(style_name: str) -> bool`
Apply a style preset to the assistant.

**Parameters:**
- `style_name`: Name of the style preset

**Returns:**
- True if style was applied, False if style not found

---

### Animation Assistant

The Animation Assistant provides tools for creating animation loops, skeletal rigging, and exporting to various formats (JSON, FBX, glTF).

#### Features

- **Animation Loop Creation**: Define keyframe-based animations with loop types
- **Skeletal Rigging**: Create hierarchical bone structures
- **Keyframe Interpolation**: Smooth interpolation between animation keyframes
- **Multi-format Export**: Export to JSON, FBX, and glTF formats

#### Usage

```python
from kimi_k2.animation import AnimationAssistant

# Create assistant
assistant = AnimationAssistant()

# Create animation loop
keyframes = [
    {"time": 0.0, "transform": {"x": 0, "y": 0}},
    {"time": 1.0, "transform": {"x": 10, "y": 0}},
]
assistant.create_animation_loop("walk", keyframes, duration=2.0, loop_type="repeat")

# Create skeleton
bones = [
    {"name": "root", "position": [0, 0, 0]},
    {"name": "spine", "position": [0, 1, 0]},
]
hierarchy = {"spine": "root"}
assistant.create_skeleton("character", bones, hierarchy)

# Export to different formats
json_output = assistant.export_to_json("walk", "character")
fbx_output = assistant.export_to_fbx("walk", "character")
gltf_output = assistant.export_to_gltf("walk", "character")
```

#### API Reference

##### `create_animation_loop(name, keyframes, duration=1.0, loop_type="repeat") -> bool`
Create an animation loop from keyframes.

**Parameters:**
- `name`: Name for the animation
- `keyframes`: List of keyframe dictionaries with 'time' and 'transform' data
- `duration`: Total duration of the animation in seconds
- `loop_type`: Type of loop ('repeat', 'pingpong', 'once')

**Returns:**
- True if animation was created successfully

##### `create_skeleton(name, bones, hierarchy) -> bool`
Create a skeletal rig structure.

**Parameters:**
- `name`: Name for the skeleton
- `bones`: List of bone definitions with name, position, rotation
- `hierarchy`: Dictionary mapping child bone names to parent bone names

**Returns:**
- True if skeleton was created successfully

---

## Linux-style Command System

### Command System

A Linux-style command interface supporting commands like `ls`, `mkdir`, `cd`, etc., with scripting capabilities.

#### Features

- **Virtual Filesystem**: Simulated filesystem for safe command execution
- **Built-in Commands**: ls, cd, pwd, mkdir, rm, touch, cat, echo, set, get, help
- **Scripting**: Execute multi-line scripts with comment support
- **Variables**: Set and retrieve variables
- **Command History**: Track all executed commands
- **Extensibility**: Register custom commands

#### Usage

```python
from kimi_k2.commands import CommandSystem

# Create command system
cmd = CommandSystem(virtual_fs=True)

# Execute commands
cmd.execute("mkdir projects")
cmd.execute("cd projects")
result = cmd.execute("pwd")  # Returns "/projects"

# Execute script
script = """
mkdir src
mkdir tests
touch README.md
"""
results = cmd.execute_script(script)

# Variables
cmd.execute("set name MyProject")
result = cmd.execute("get name")

# Custom commands
def greet_handler(args):
    return f"Hello, {args[0] if args else 'World'}!"

cmd.register_command("greet", greet_handler)
cmd.execute("greet Alice")
```

#### API Reference

##### `execute(command: str) -> Dict[str, Any]`
Execute a command or script.

**Parameters:**
- `command`: Command string to execute

**Returns:**
- Dictionary with execution results containing 'status' and 'output' or 'error'

##### `execute_script(script: str) -> List[Dict[str, Any]]`
Execute a multi-line script.

**Parameters:**
- `script`: Multi-line script string

**Returns:**
- List of results for each command

---

### Forge AI Extension

A Forge-like AI extension for generative tasks such as writing, NPC dialogues, and quest scripting.

#### Features

- **Creative Writing**: Generate text in various styles
- **NPC Dialogue**: Create personality-based NPC dialogues
- **Quest Generation**: Generate quests with objectives and rewards
- **Narrative Scenes**: Create atmospheric scene descriptions
- **Template System**: Add custom templates for dialogue generation

#### Usage

```python
from kimi_k2.commands import ForgeAI

# Create Forge AI
forge = ForgeAI()

# Generate writing
text = forge.generate_writing("A mysterious forest", style="narrative")

# Generate NPC dialogue
dialogue = forge.generate_npc_dialogue(
    "Merchant",
    personality="friendly",
    context={"player_title": "adventurer"}
)

# Generate quest
quest = forge.generate_quest(
    quest_type="fetch",
    difficulty="medium",
    location="Dark Cave"
)

# Create narrative scene
scene = forge.create_narrative_scene(
    setting="Ancient Temple",
    characters=["Hero", "Guide"],
    mood="mysterious"
)
```

#### API Reference

##### `generate_writing(prompt, style="narrative", max_length=200) -> str`
Generate creative writing based on a prompt.

**Parameters:**
- `prompt`: Writing prompt or topic
- `style`: Writing style (narrative, descriptive, dialogue, technical)
- `max_length`: Maximum length of generated text

**Returns:**
- Generated text

##### `generate_npc_dialogue(npc_name, personality="friendly", context=None) -> Dict`
Generate NPC dialogue based on personality and context.

**Parameters:**
- `npc_name`: Name of the NPC
- `personality`: Personality type (friendly, hostile, mysterious, merchant)
- `context`: Additional context for dialogue generation

**Returns:**
- Dictionary containing dialogue options and metadata

---

## Optimized GPT Models

### Optimized GPT

A 16GB optimized GPT model with grouped query attention, KV caching, and FlashAttention integration.

#### Features

- **Grouped Query Attention (GQA)**: Reduced memory usage with fewer KV heads
- **KV Caching**: Efficient autoregressive generation
- **FlashAttention**: Memory-efficient attention computation
- **Autoregressive Generation**: Text generation with temperature and top-k sampling

#### Usage

```python
import torch
from kimi_k2.models import OptimizedGPT

# Create model
model = OptimizedGPT(
    vocab_size=50257,
    embed_dim=768,
    num_layers=12,
    num_heads=12,
    num_kv_heads=4,  # GQA with 4 KV heads
    use_flash_attention=True,
)

# Forward pass with KV caching
input_ids = torch.randint(0, 50257, (2, 20))
logits, cache = model(input_ids, use_cache=True)

# Generate text
generated = model.generate(
    input_ids,
    max_new_tokens=50,
    temperature=0.8,
    top_k=50,
)
```

#### API Reference

##### `forward(input_ids, attention_mask=None, kv_cache=None, use_cache=False)`
Forward pass through the model.

**Parameters:**
- `input_ids`: Input token IDs [batch, seq_len]
- `attention_mask`: Optional attention mask
- `kv_cache`: Optional cached KV tensors
- `use_cache`: Whether to return KV cache

**Returns:**
- Tuple of (logits, kv_cache)

##### `generate(input_ids, max_new_tokens=50, temperature=1.0, top_k=None)`
Generate tokens autoregressively.

**Parameters:**
- `input_ids`: Starting token IDs
- `max_new_tokens`: Maximum number of tokens to generate
- `temperature`: Sampling temperature
- `top_k`: Optional top-k sampling

**Returns:**
- Generated token IDs

---

### 16-Layer Transformer Model

A memory-efficient 16-layer transformer model with autoregressive generation capabilities.

#### Features

- **16 Transformer Layers**: Deep model for complex tasks
- **Memory Efficiency**: Optimized for reduced memory footprint
- **Gradient Checkpointing**: Optional memory savings during training
- **Autoregressive Generation**: Support for greedy, top-k, and top-p sampling
- **Memory Usage Estimation**: Tools to estimate model memory requirements

#### Usage

```python
import torch
from kimi_k2.models import TransformerModel

# Create model
model = TransformerModel(
    vocab_size=50257,
    embed_dim=512,
    num_layers=16,
    num_heads=8,
    ffn_dim=2048,
    gradient_checkpointing=True,
)

# Count parameters
param_count = model.count_parameters()

# Estimate memory
memory = model.estimate_memory_usage(batch_size=4, seq_len=512)

# Forward pass
input_ids = torch.randint(0, 50257, (2, 20))
logits, hidden_states = model(input_ids, return_hidden_states=True)

# Generate with different sampling methods
generated = model.generate(
    input_ids,
    max_new_tokens=50,
    do_sample=True,
    temperature=0.8,
    top_k=50,
    top_p=0.9,
)
```

#### API Reference

##### `forward(input_ids, attention_mask=None, return_hidden_states=False)`
Forward pass through the model.

**Parameters:**
- `input_ids`: Input token IDs [batch, seq_len]
- `attention_mask`: Optional attention mask
- `return_hidden_states`: Whether to return all hidden states

**Returns:**
- Tuple of (logits, optional hidden_states)

##### `generate(input_ids, max_new_tokens=50, temperature=1.0, top_k=None, top_p=None, do_sample=True)`
Autoregressive generation with various sampling methods.

**Parameters:**
- `input_ids`: Starting token IDs
- `max_new_tokens`: Maximum number of tokens to generate
- `temperature`: Sampling temperature
- `top_k`: Top-k sampling parameter
- `top_p`: Top-p (nucleus) sampling parameter
- `do_sample`: Whether to sample (vs. greedy)

**Returns:**
- Generated token IDs

##### `count_parameters() -> int`
Count the number of trainable parameters.

##### `estimate_memory_usage(batch_size=1, seq_len=512) -> dict`
Estimate memory usage for the model.

---

## Examples

Complete working examples are provided in the `examples/` directory:

- `example_claymation.py`: Claymation Assistant usage
- `example_animation.py`: Animation Assistant usage
- `example_command_system.py`: Command System usage
- `example_forge_ai.py`: Forge AI Extension usage
- `example_optimized_gpt.py`: Optimized GPT Model usage
- `example_transformer.py`: 16-Layer Transformer Model usage

Run any example:
```bash
python examples/example_claymation.py
```

---

## Testing

The project includes comprehensive test coverage (90%+) using pytest.

### Running Tests

```bash
# Install test dependencies
pip install -e .

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/kimi_k2 --cov-report=term-missing

# Run specific test file
pytest tests/test_claymation_assistant.py -v
```

### Test Structure

- `tests/test_claymation_assistant.py`: Tests for Claymation Assistant
- `tests/test_animation_assistant.py`: Tests for Animation Assistant
- `tests/test_command_system.py`: Tests for Command System
- `tests/test_forge_ai.py`: Tests for Forge AI Extension
- `tests/test_optimized_gpt.py`: Tests for Optimized GPT Model
- `tests/test_transformer_model.py`: Tests for Transformer Model

---

## Installation

```bash
# Install from source
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.8
- numpy >= 1.24.0
- torch >= 2.0.0
- transformers >= 4.35.0

---

## License

See the [LICENSE](../LICENSE) file for details.
