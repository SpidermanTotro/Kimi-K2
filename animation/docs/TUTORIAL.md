# Tutorial: Creating Your First Animation with Kimi-K2 Animation AI

This tutorial will walk you through creating a complete animation project using the Kimi-K2 Animation AI module.

## Tutorial 1: Creating a Walk Cycle

### Step 1: Build the CLI Tool

```bash
cd animation
go build -o kimi-animation ./cli
```

### Step 2: Generate a Basic Walk Cycle

```bash
./kimi-animation animation generate-loop walk my_walk.json --type 3D --fps 30
```

### Step 3: Inspect the Output

```bash
cat my_walk.json | jq '.keyframes | length'
# Output: 8 (8 keyframes in the walk cycle)
```

### Step 4: Modify and Customize

The generated walk cycle is a template. You can:
- Adjust keyframe timings
- Modify bone rotations
- Add custom properties

## Tutorial 2: Smoothing a Claymation Sequence

### Step 1: Create a Simple Sequence

Create `my_animation.json`:

```json
{
  "name": "Bouncing Ball",
  "fps": 24,
  "keyframes": [
    {
      "id": 0,
      "timestamp": 0.0,
      "objects": [{
        "name": "ball",
        "position": {"x": 0, "y": 100, "z": 0},
        "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
      }]
    },
    {
      "id": 1,
      "timestamp": 0.5,
      "objects": [{
        "name": "ball",
        "position": {"x": 50, "y": 0, "z": 0},
        "rotation": {"pitch": 0, "yaw": 180, "roll": 0}
      }]
    },
    {
      "id": 2,
      "timestamp": 1.0,
      "objects": [{
        "name": "ball",
        "position": {"x": 100, "y": 100, "z": 0},
        "rotation": {"pitch": 0, "yaw": 360, "roll": 0}
      }]
    }
  ]
}
```

### Step 2: Analyze the Sequence

```bash
./kimi-animation claymation analyze my_animation.json
```

Expected output:
```
=== Sequence Analysis ===
Name: Bouncing Ball
Frame Count: 3
Duration: 1.00 seconds
FPS: 24.00
Quality Score: XX.XX/100

=== Suggestions ===
1. Overall sequence smoothness could be improved...
```

### Step 3: Smooth the Animation

```bash
./kimi-animation claymation smooth \
  my_animation.json \
  smooth_animation.json \
  --intermediate-frames 4 \
  --interpolation ease-in-out
```

### Step 4: Compare Results

```bash
# Original
./kimi-animation claymation analyze my_animation.json

# Smoothed
./kimi-animation claymation analyze smooth_animation.json
```

The smoothed version should have a higher quality score!

## Tutorial 3: Creating a Character with Rig

### Step 1: Create a Humanoid Rig

```bash
./kimi-animation animation create-rig humanoid character_rig.json
```

### Step 2: Inspect the Rig

```bash
cat character_rig.json | jq '.bones'
```

You'll see bones like:
- Root
- Spine
- Head
- Arms (left/right)
- Legs (left/right)

### Step 3: Generate Multiple Animations

```bash
# Walk cycle
./kimi-animation animation generate-loop walk char_walk.json

# Idle animation
./kimi-animation animation generate-loop idle char_idle.json

# Run cycle
./kimi-animation animation generate-loop run char_run.json

# Jump
./kimi-animation animation generate-loop jump char_jump.json
```

### Step 4: Combine with Rig

Create a Go program to combine:

```go
package main

import (
    "encoding/json"
    "os"
    "github.com/moonshotai/Kimi-K2/animation/animation"
)

func main() {
    // Load rig
    rigData, _ := os.ReadFile("character_rig.json")
    var rig animation.Rig
    json.Unmarshal(rigData, &rig)
    
    // Load walk animation
    walkData, _ := os.ReadFile("char_walk.json")
    var walk animation.AnimationLoop
    json.Unmarshal(walkData, &walk)
    
    // Attach rig to animation
    walk.Rig = &rig
    
    // Save combined
    output, _ := json.MarshalIndent(walk, "", "  ")
    os.WriteFile("character_complete.json", output, 0644)
}
```

## Tutorial 4: Applying Style Presets

### Step 1: List Available Styles

```bash
./kimi-animation claymation list-styles
```

### Step 2: Apply Wallace and Gromit Style

```bash
./kimi-animation claymation apply-style \
  my_animation.json \
  wallace-gromit \
  wallace_style.json
```

### Step 3: Compare Styles

Try all three styles:

```bash
# Wallace and Gromit - smooth and charming
./kimi-animation claymation apply-style \
  my_animation.json wallace-gromit wg_style.json

# Robot Chicken - snappy and fast
./kimi-animation claymation apply-style \
  my_animation.json robot-chicken rc_style.json

# Classic - traditional stop-motion
./kimi-animation claymation apply-style \
  my_animation.json classic classic_style.json
```

Each style will add different metadata affecting rendering.

## Tutorial 5: Complete Animation Workflow

Let's create a complete animation from scratch!

### Scenario: Character Walking and Waving

#### Step 1: Create the Character Rig

```bash
./kimi-animation animation create-rig humanoid bob_rig.json
```

#### Step 2: Generate Base Animations

```bash
# Walk cycle (2 seconds)
./kimi-animation animation generate-loop walk bob_walk.json

# Idle (for standing)
./kimi-animation animation generate-loop idle bob_idle.json
```

#### Step 3: Create Custom Wave Sequence

Create `wave_keyframes.json`:

```json
{
  "name": "Wave Hello",
  "fps": 24,
  "keyframes": [
    {
      "id": 0,
      "timestamp": 0.0,
      "objects": [{
        "name": "right_arm",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
      }]
    },
    {
      "id": 1,
      "timestamp": 0.3,
      "objects": [{
        "name": "right_arm",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"pitch": 90, "yaw": 0, "roll": 0}
      }]
    },
    {
      "id": 2,
      "timestamp": 0.6,
      "objects": [{
        "name": "right_arm",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"pitch": 110, "yaw": 0, "roll": 15}
      }]
    },
    {
      "id": 3,
      "timestamp": 0.9,
      "objects": [{
        "name": "right_arm",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"pitch": 90, "yaw": 0, "roll": -15}
      }]
    },
    {
      "id": 4,
      "timestamp": 1.2,
      "objects": [{
        "name": "right_arm",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
      }]
    }
  ]
}
```

#### Step 4: Smooth the Wave

```bash
./kimi-animation claymation smooth \
  wave_keyframes.json \
  wave_smooth.json \
  --intermediate-frames 3 \
  --interpolation ease-in-out
```

#### Step 5: Combine Everything

Create a script `combine_animations.go`:

```go
package main

import (
    "encoding/json"
    "os"
)

type Timeline struct {
    Segments []Segment `json:"segments"`
}

type Segment struct {
    Animation string  `json:"animation"`
    Start     float64 `json:"start"`
    Duration  float64 `json:"duration"`
}

func main() {
    timeline := Timeline{
        Segments: []Segment{
            {Animation: "bob_walk.json", Start: 0.0, Duration: 2.0},
            {Animation: "wave_smooth.json", Start: 2.0, Duration: 1.5},
            {Animation: "bob_idle.json", Start: 3.5, Duration: 2.0},
        },
    }
    
    output, _ := json.MarshalIndent(timeline, "", "  ")
    os.WriteFile("complete_animation.json", output, 0644)
}
```

#### Step 6: Apply Final Style

```bash
./kimi-animation claymation apply-style \
  complete_animation.json \
  wallace-gromit \
  final_animation.json
```

## Tutorial 6: Using with Python

### Setup Python Wrapper

Create `animation_wrapper.py`:

```python
import subprocess
import json

class AnimationAI:
    def __init__(self):
        self.cli = "./kimi-animation"
    
    def generate_walk(self, output="walk.json"):
        subprocess.run([
            self.cli, "animation", "generate-loop",
            "walk", output
        ])
        with open(output) as f:
            return json.load(f)
    
    def analyze(self, file):
        result = subprocess.run([
            self.cli, "claymation", "analyze", file
        ], capture_output=True, text=True)
        return result.stdout

# Usage
ai = AnimationAI()
walk = ai.generate_walk("python_walk.json")
print(f"Generated walk with {len(walk['keyframes'])} keyframes")
```

### Run it:

```bash
python animation_wrapper.py
```

## Tips and Tricks

### Tip 1: Start with Low FPS

For testing, use 12 FPS instead of 24:
```bash
./kimi-animation animation generate-loop walk test.json --fps 12
```

### Tip 2: Use Intermediate Frames Wisely

- 2-3 frames: Fast animations
- 4-5 frames: Smooth animations
- 6+ frames: Very smooth, but larger files

### Tip 3: Analyze Before and After

Always analyze before smoothing to know your baseline:
```bash
./kimi-animation claymation analyze original.json > before.txt
./kimi-animation claymation smooth original.json smoothed.json -i 4
./kimi-animation claymation analyze smoothed.json > after.txt
diff before.txt after.txt
```

### Tip 4: Chain Commands

```bash
# Generate, analyze, and smooth in one go
./kimi-animation animation generate-loop walk temp.json && \
./kimi-animation claymation analyze temp.json && \
./kimi-animation claymation smooth temp.json final.json -i 5
```

## Common Problems and Solutions

### Problem: Animation looks stiff
**Solution**: Increase intermediate frames and use ease-in-out interpolation

### Problem: Quality score is low
**Solution**: 
1. Add more keyframes
2. Use smoother transitions
3. Apply style presets

### Problem: Rig bones don't match my character
**Solution**: Modify the generated rig JSON to add/remove bones

### Problem: Export format not supported
**Solution**: Use JSON as intermediate, then convert with external tools

## Next Steps

1. **Experiment with Different Styles**
   - Try all three style presets
   - Create your own style in the config

2. **Build Complex Scenes**
   - Multiple characters
   - Interactive sequences
   - Camera movements

3. **Integrate with Other Tools**
   - Export to Blender
   - Use with Unity or Unreal
   - Render with your preferred engine

4. **Learn the API**
   - Read the API reference
   - Create custom Go applications
   - Build automation scripts

## Resources

- Main README: `animation/README.md`
- API Reference: `animation/docs/API_REFERENCE.md`
- Integration Guide: `animation/docs/INTEGRATION_GUIDE.md`
- Examples: `animation/examples/`

Happy animating! 🎬
