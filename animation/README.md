# Kimi-K2 Animation AI

## Overview

The Kimi-K2 Animation AI module extends the Kimi-K2 transformer project with advanced capabilities for creating and optimizing claymation and animation sequences. This module leverages AI to assist artists and animators in generating stop-motion claymation sequences and 2D/3D animations through intelligent frame generation, smoothing, and rigging.

## Features

### 🎨 Claymation Assistant

The Claymation Assistant provides AI-powered tools for stop-motion animation:

- **Frame-by-Frame Analysis**: Analyze claymation sequences for quality, smoothness, and pacing
- **Transition Smoothing**: Automatically generate intermediate frames to smooth out abrupt transitions
- **Style Presets**: Apply popular claymation styles (Wallace and Gromit, Robot Chicken, Classic)
- **Quality Scoring**: Get automated quality assessments and improvement suggestions

### 🎬 Animation Assistant

The Animation Assistant enables creation of 2D and 3D animations:

- **Animation Loop Generation**: Generate common animation loops (walk cycles, idle animations, run cycles, jumps)
- **Skeletal Rigging**: Create basic skeletal rigs for humanoid and quadruped characters
- **Inverse Kinematics (IK)**: Position character limbs naturally using IK solving
- **Multi-format Export**: Export animations to JSON, FBX, glTF, and other formats

## Architecture

```
animation/
├── claymation/          # Claymation AI module
│   └── claymation.go    # Core claymation logic
├── animation/           # Animation AI module
│   └── animation.go     # Core animation logic
├── cli/                 # Command-line interface
│   └── main.go          # CLI application
├── config/              # Configuration files
│   └── animation_config.yaml
├── examples/            # Example scripts and data
│   ├── claymation_example.go
│   ├── animation_example.go
│   └── example_sequence.json
└── docs/                # Documentation
```

## Installation

### Prerequisites

- Go 1.21 or later
- Kimi-K2 model (for full AI integration)

### Build from Source

```bash
cd animation
go mod download
go build -o kimi-animation ./cli
```

## Quick Start

### Using the CLI

#### 1. Analyze a Claymation Sequence

```bash
./kimi-animation claymation analyze examples/example_sequence.json
```

#### 2. Smooth Transitions

```bash
./kimi-animation claymation smooth \
  examples/example_sequence.json \
  output_smoothed.json \
  --intermediate-frames 3 \
  --interpolation ease-in-out
```

#### 3. Generate an Animation Loop

```bash
./kimi-animation animation generate-loop walk output_walk.json --type 3D
```

#### 4. Create a Skeletal Rig

```bash
./kimi-animation animation create-rig humanoid output_rig.json
```

#### 5. Apply a Style Preset

```bash
./kimi-animation claymation apply-style \
  examples/example_sequence.json \
  wallace-gromit \
  output_styled.json
```

#### 6. List Available Styles

```bash
./kimi-animation claymation list-styles
```

### Using the Go API

#### Claymation Example

```go
package main

import (
    "github.com/moonshotai/Kimi-K2/animation/claymation"
)

func main() {
    // Create assistant
    assistant := claymation.NewAssistant(nil)
    
    // Create a sequence
    sequence := &claymation.Sequence{
        Name: "My Animation",
        FPS:  24.0,
        Keyframes: []claymation.Frame{
            // ... your keyframes
        },
    }
    
    // Analyze the sequence
    analysis, err := assistant.AnalyzeSequence(sequence)
    if err != nil {
        panic(err)
    }
    
    // Smooth transitions
    smoothed, err := assistant.SmoothTransitions(sequence, 3)
    if err != nil {
        panic(err)
    }
    
    // Apply style preset
    err = assistant.ApplyStylePreset(smoothed, "wallace-gromit")
}
```

#### Animation Example

```go
package main

import (
    "github.com/moonshotai/Kimi-K2/animation/animation"
)

func main() {
    // Create assistant
    assistant := animation.NewAssistant(nil)
    
    // Generate a walk cycle
    walkLoop, err := assistant.GenerateAnimationLoop("walk", animation.Animation3D)
    if err != nil {
        panic(err)
    }
    
    // Create a rig
    rig, err := assistant.CreateBasicRig("humanoid")
    if err != nil {
        panic(err)
    }
    
    // Solve IK for positioning
    target := animation.Position3D{X: 50, Y: 100, Z: 20}
    rotations, err := assistant.SolveIK(rig, "left_arm", target)
    
    // Export animation
    data, err := assistant.ExportAnimation(walkLoop, "json")
}
```

## Configuration

The animation module can be configured via `config/animation_config.yaml`:

```yaml
claymation:
  default_fps: 24.0
  interpolation_type: "ease-in-out"
  style_presets:
    wallace-gromit:
      name: "Wallace and Gromit"
      motion_blur: 0.2
      smoothing_intensity: 0.8

animation:
  default_fps: 30.0
  ik_solver_precision: 0.001
  loop_templates:
    walk:
      default_duration: 1.0
      keyframe_count: 8
```

## Style Presets

### Wallace and Gromit Style
- High smoothing intensity (0.8)
- Moderate motion blur (0.2)
- Classic Aardman charm

### Robot Chicken Style
- Medium smoothing intensity (0.5)
- Low motion blur (0.1)
- Snappy, comedic timing

### Classic Stop-Motion
- Low smoothing intensity (0.3)
- No motion blur
- Traditional frame-by-frame aesthetic

## Animation Loop Types

### Walk Cycle
- Duration: 1.0 second
- 8 keyframes
- Natural foot placement and arm swing

### Idle Animation
- Duration: 2.0 seconds
- 4 keyframes
- Subtle breathing and weight shifting

### Run Cycle
- Duration: 0.6 seconds
- 8 keyframes
- Extended stride and vertical movement

### Jump
- Duration: 1.5 seconds
- 6 keyframes
- Anticipation, air time, and landing

## Skeletal Rig Types

### Humanoid
- Root, spine, head
- Left/right shoulders and arms
- Left/right legs
- Configurable joint constraints

### Quadruped
- Root, spine, head
- Four legs (front left/right, back left/right)
- Suitable for animals and creatures

## Integration with Kimi-K2

The animation module integrates with Kimi-K2's transformer capabilities:

1. **Tool Calling**: Animation functions can be exposed as tools for Kimi-K2 to call
2. **Generative AI**: Leverage Kimi-K2's generative capabilities for creative animation suggestions
3. **Style Transfer**: Use Kimi-K2's understanding to apply and blend animation styles

### Example Tool Configuration

```python
tools = [{
    "type": "function",
    "function": {
        "name": "generate_animation_loop",
        "description": "Generate an animation loop (walk, idle, run, jump)",
        "parameters": {
            "type": "object",
            "required": ["loop_type"],
            "properties": {
                "loop_type": {
                    "type": "string",
                    "enum": ["walk", "idle", "run", "jump"]
                },
                "animation_type": {
                    "type": "string",
                    "enum": ["2D", "3D"]
                }
            }
        }
    }
}]
```

## Training Data

The module can be trained on datasets of claymation and animation sequences:

### Claymation Datasets
- Aardman Classics (Wallace and Gromit, Chicken Run, Shaun the Sheep)
- Robot Chicken episodes
- General stop-motion collections

### Animation Datasets
- 2D animation sequences (sprite, vector, traditional)
- 3D animation data (rigged, mocap, procedural)

Training configuration is specified in `config/animation_config.yaml`.

## Export Formats

The module supports exporting animations to multiple formats:

- **JSON**: Human-readable, easy to parse
- **FBX**: Industry-standard 3D format (Autodesk)
- **glTF**: Modern 3D transmission format
- **Blender**: Direct Blender integration
- **Maya**: Autodesk Maya format

## API Reference

### Claymation Module

#### `NewAssistant(config *Config) *Assistant`
Creates a new claymation assistant with optional configuration.

#### `AnalyzeSequence(seq *Sequence) (*SequenceAnalysis, error)`
Analyzes a claymation sequence and provides quality metrics and suggestions.

#### `GenerateIntermediateFrames(from, to Frame, count int) ([]Frame, error)`
Generates intermediate frames between two keyframes.

#### `SmoothTransitions(seq *Sequence, intermediateFramesPerTransition int) (*Sequence, error)`
Smooths all transitions in a sequence by adding intermediate frames.

#### `ApplyStylePreset(seq *Sequence, presetName string) error`
Applies a style preset to a sequence.

### Animation Module

#### `NewAssistant(config *Config) *Assistant`
Creates a new animation assistant with optional configuration.

#### `GenerateAnimationLoop(loopType string, animType AnimationType) (*AnimationLoop, error)`
Generates an animation loop of the specified type.

#### `CreateBasicRig(rigType string) (*Rig, error)`
Creates a basic skeletal rig (humanoid or quadruped).

#### `SolveIK(rig *Rig, endEffectorID string, target Position3D) (map[string]Rotation3D, error)`
Performs inverse kinematics to position an end effector at a target location.

#### `ExportAnimation(loop *AnimationLoop, format string) ([]byte, error)`
Exports an animation to the specified format.

## Examples

See the `examples/` directory for complete working examples:

- `claymation_example.go`: Demonstrates claymation analysis, smoothing, and styling
- `animation_example.go`: Shows animation loop generation, rigging, and IK
- `example_sequence.json`: Sample claymation sequence data

## Performance Considerations

- **Frame Generation**: Generating intermediate frames is fast (< 1ms per frame)
- **IK Solving**: Current implementation uses CCD solver with ~10 iterations
- **Analysis**: Sequence analysis scales linearly with keyframe count
- **Memory**: Each frame stores transform data for all objects (~1KB per frame)

## Troubleshooting

### Common Issues

**Q: "sequence must have at least 2 keyframes"**  
A: Ensure your input sequence has at least two keyframes for analysis or smoothing.

**Q: "style preset 'X' not found"**  
A: Check available style presets with `./kimi-animation claymation list-styles`.

**Q: "unsupported loop type"**  
A: Valid loop types are: walk, idle, run, jump.

**Q: "unsupported rig type"**  
A: Valid rig types are: humanoid, quadruped.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional animation loop types
- More sophisticated IK solvers
- Additional style presets
- Support for more export formats
- Integration with 3D modeling software

## License

This module is released under the same Modified MIT License as Kimi-K2.

## Support

For questions, issues, or feature requests:
- Email: support@moonshot.cn
- GitHub Issues: [Kimi-K2 Repository](https://github.com/moonshotai/Kimi-K2)

## Acknowledgments

- Inspired by classic claymation studios: Aardman Animations, Laika
- Animation techniques based on traditional principles of animation
- Built on the Kimi-K2 transformer foundation
