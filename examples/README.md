# Kimi-K2 Examples

This directory contains working examples demonstrating all the enhanced capabilities of Kimi-K2.

## Running Examples

Each example can be run directly with Python:

```bash
python examples/example_claymation.py
python examples/example_animation.py
python examples/example_command_system.py
python examples/example_forge_ai.py
python examples/example_optimized_gpt.py
python examples/example_transformer.py
```

## Available Examples

### Animation Examples

#### `example_claymation.py`
Demonstrates the Claymation Assistant for stop-motion animation:
- Creating and analyzing stop-motion frame sequences
- Generating intermediate frames with different interpolation styles
- Adding custom styles
- Processing complete sequences

#### `example_animation.py`
Shows the Animation Assistant capabilities:
- Creating animation loops with keyframes
- Building skeletal rigs with bone hierarchies
- Applying animations to skeletons
- Keyframe interpolation
- Exporting to JSON, FBX, and glTF formats

### Command System Examples

#### `example_command_system.py`
Demonstrates the Linux-style command system:
- Basic filesystem operations (ls, cd, mkdir, rm, etc.)
- Creating and managing files
- Using variables
- Executing multi-line scripts
- Registering custom commands
- Command history

#### `example_forge_ai.py`
Shows the Forge AI extension for generative content:
- Generating creative writing in different styles
- Creating NPC dialogues with various personalities
- Generating quests with objectives and rewards
- Creating narrative scenes with atmosphere
- Using templates and context variables

### Model Examples

#### `example_optimized_gpt.py`
Demonstrates the Optimized GPT model:
- Creating models with Grouped Query Attention
- Forward passes with and without KV caching
- Text generation with various parameters
- Comparing memory efficiency
- Using FlashAttention

#### `example_transformer.py`
Shows the 16-layer transformer model:
- Creating and configuring the model
- Parameter counting and memory estimation
- Forward passes with hidden states
- Causal attention masking
- Multiple generation strategies (greedy, sampling, top-k, top-p)
- Gradient checkpointing for memory efficiency

## Example Output

All examples include informative output showing the operations being performed and their results. They are designed to be educational and demonstrate best practices for using each component.

## Prerequisites

Make sure you have installed Kimi-K2:

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Further Reading

For detailed API documentation, see [docs/enhancements_documentation.md](../docs/enhancements_documentation.md).
