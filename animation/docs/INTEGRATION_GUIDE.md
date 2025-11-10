# Kimi-K2 Animation AI Integration Guide

## Overview

This guide explains how to integrate the Animation AI module with Kimi-K2's transformer capabilities to create powerful AI-assisted animation workflows.

## Architecture

The Animation AI module integrates with Kimi-K2 through:

1. **Tool Calling Interface**: Expose animation functions as tools for Kimi-K2
2. **API Integration**: Connect to Kimi-K2's inference API for generative tasks
3. **Workflow Automation**: Use Kimi-K2 to orchestrate complex animation pipelines

## Integration Methods

### Method 1: Tool Calling with Kimi-K2

Define animation functions as tools that Kimi-K2 can call:

```python
from openai import OpenAI

# Connect to Kimi-K2 API
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-api-key"
)

# Define animation tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_animation_loop",
            "description": "Generate an animation loop (walk, idle, run, jump) for a character",
            "parameters": {
                "type": "object",
                "required": ["loop_type"],
                "properties": {
                    "loop_type": {
                        "type": "string",
                        "enum": ["walk", "idle", "run", "jump"],
                        "description": "Type of animation loop to generate"
                    },
                    "animation_type": {
                        "type": "string",
                        "enum": ["2D", "3D"],
                        "description": "Whether to generate 2D or 3D animation"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "smooth_claymation_sequence",
            "description": "Smooth a claymation sequence by adding intermediate frames",
            "parameters": {
                "type": "object",
                "required": ["sequence_file", "intermediate_frames"],
                "properties": {
                    "sequence_file": {
                        "type": "string",
                        "description": "Path to the sequence JSON file"
                    },
                    "intermediate_frames": {
                        "type": "integer",
                        "description": "Number of intermediate frames to add"
                    },
                    "interpolation": {
                        "type": "string",
                        "enum": ["linear", "ease-in", "ease-out", "ease-in-out"],
                        "description": "Interpolation method"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sequence_quality",
            "description": "Analyze a claymation sequence for quality and smoothness",
            "parameters": {
                "type": "object",
                "required": ["sequence_file"],
                "properties": {
                    "sequence_file": {
                        "type": "string",
                        "description": "Path to the sequence JSON file"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_skeletal_rig",
            "description": "Create a skeletal rig for animation",
            "parameters": {
                "type": "object",
                "required": ["rig_type"],
                "properties": {
                    "rig_type": {
                        "type": "string",
                        "enum": ["humanoid", "quadruped"],
                        "description": "Type of rig to create"
                    }
                }
            }
        }
    }
]

# Example conversation
messages = [
    {"role": "system", "content": "You are Kimi, an AI assistant with animation creation capabilities."},
    {"role": "user", "content": "I need to create a walk cycle for my 3D character."}
]

response = client.chat.completions.create(
    model="kimi-k2",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0.6
)

# Process tool calls
if response.choices[0].finish_reason == "tool_calls":
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == "generate_animation_loop":
            import json
            import subprocess
            
            args = json.loads(tool_call.function.arguments)
            # Call the animation CLI
            result = subprocess.run([
                "./kimi-animation", "animation", "generate-loop",
                args["loop_type"], "output.json",
                "--type", args.get("animation_type", "3D")
            ], capture_output=True, text=True)
            
            # Return result to Kimi
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result.stdout
            })
```

### Method 2: Python Wrapper for Animation Module

Create a Python wrapper to call Go functions:

```python
import subprocess
import json
from typing import Dict, Any, List

class KimiAnimationAI:
    def __init__(self, cli_path: str = "./kimi-animation"):
        self.cli_path = cli_path
    
    def generate_loop(self, loop_type: str, output_file: str, 
                     animation_type: str = "3D") -> Dict[str, Any]:
        """Generate an animation loop."""
        result = subprocess.run([
            self.cli_path, "animation", "generate-loop",
            loop_type, output_file,
            "--type", animation_type
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(output_file, 'r') as f:
                return json.load(f)
        else:
            raise Exception(f"Failed to generate loop: {result.stderr}")
    
    def analyze_sequence(self, sequence_file: str) -> Dict[str, Any]:
        """Analyze a claymation sequence."""
        result = subprocess.run([
            self.cli_path, "claymation", "analyze", sequence_file
        ], capture_output=True, text=True)
        
        return self._parse_analysis_output(result.stdout)
    
    def smooth_sequence(self, input_file: str, output_file: str,
                       intermediate_frames: int = 3,
                       interpolation: str = "ease-in-out") -> str:
        """Smooth a claymation sequence."""
        result = subprocess.run([
            self.cli_path, "claymation", "smooth",
            input_file, output_file,
            "--intermediate-frames", str(intermediate_frames),
            "--interpolation", interpolation
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_file
        else:
            raise Exception(f"Failed to smooth: {result.stderr}")
    
    def create_rig(self, rig_type: str, output_file: str) -> Dict[str, Any]:
        """Create a skeletal rig."""
        result = subprocess.run([
            self.cli_path, "animation", "create-rig",
            rig_type, output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open(output_file, 'r') as f:
                return json.load(f)
        else:
            raise Exception(f"Failed to create rig: {result.stderr}")
    
    @staticmethod
    def _parse_analysis_output(output: str) -> Dict[str, Any]:
        """Parse analysis output into structured data."""
        # Simple parsing - in production, use structured output
        lines = output.split('\n')
        result = {}
        for line in lines:
            if 'Quality Score:' in line:
                score = line.split(':')[1].strip().split('/')[0]
                result['quality_score'] = float(score)
        return result

# Usage
anim_ai = KimiAnimationAI()

# Generate a walk cycle
walk_data = anim_ai.generate_loop("walk", "walk.json", "3D")

# Analyze a sequence
analysis = anim_ai.analyze_sequence("my_sequence.json")

# Smooth a sequence
smoothed_file = anim_ai.smooth_sequence(
    "my_sequence.json", 
    "smoothed.json",
    intermediate_frames=5
)
```

### Method 3: Direct Integration in Go

For Go applications, directly import the modules:

```go
package main

import (
    "fmt"
    "github.com/moonshotai/Kimi-K2/animation/animation"
    "github.com/moonshotai/Kimi-K2/animation/claymation"
)

func main() {
    // Create assistants
    clayAssist := claymation.NewAssistant(nil)
    animAssist := animation.NewAssistant(nil)
    
    // Generate animation
    loop, err := animAssist.GenerateAnimationLoop("walk", animation.Animation3D)
    if err != nil {
        panic(err)
    }
    
    // Create rig
    rig, err := animAssist.CreateBasicRig("humanoid")
    if err != nil {
        panic(err)
    }
    
    // Solve IK
    target := animation.Position3D{X: 50, Y: 100, Z: 20}
    rotations, err := animAssist.SolveIK(rig, "left_arm", target)
    
    fmt.Printf("Generated %s loop with %d keyframes\n", 
        loop.Name, len(loop.Keyframes))
}
```

## End-to-End Workflow Example

### Scenario: Creating a Character Animation with AI Assistance

```python
from openai import OpenAI
from kimi_animation_wrapper import KimiAnimationAI

# Initialize
client = OpenAI(base_url="http://localhost:8000/v1")
anim_ai = KimiAnimationAI()

# Step 1: Get AI recommendations
messages = [
    {"role": "system", "content": "You are Kimi, an expert animator."},
    {"role": "user", "content": """
    I'm creating a claymation character that needs to walk across the screen,
    wave hello, and then stand idle. What animations should I create?
    """}
]

response = client.chat.completions.create(
    model="kimi-k2",
    messages=messages,
    temperature=0.6
)

print("AI Recommendation:", response.choices[0].message.content)

# Step 2: Generate animations based on AI advice
print("\nGenerating animations...")

# Walk cycle
walk = anim_ai.generate_loop("walk", "character_walk.json", "3D")
print(f"✓ Created walk cycle with {len(walk['keyframes'])} keyframes")

# Idle animation
idle = anim_ai.generate_loop("idle", "character_idle.json", "3D")
print(f"✓ Created idle animation with {len(idle['keyframes'])} keyframes")

# Step 3: Create rig for the character
print("\nCreating character rig...")
rig = anim_ai.create_rig("humanoid", "character_rig.json")
print(f"✓ Created rig with {len(rig['bones'])} bones")

# Step 4: Get AI help with quality improvement
print("\nAnalyzing animation quality...")
# Assuming we have a combined sequence
analysis = anim_ai.analyze_sequence("full_sequence.json")

# Ask AI for improvement suggestions
messages.append({
    "role": "user",
    "content": f"The animation quality score is {analysis.get('quality_score', 0)}. How can I improve it?"
})

response = client.chat.completions.create(
    model="kimi-k2",
    messages=messages,
    temperature=0.6
)

print("AI Suggestions:", response.choices[0].message.content)

print("\n✓ Animation pipeline complete!")
```

## Configuration for Kimi-K2 Integration

Update `animation/config/animation_config.yaml`:

```yaml
# Kimi-K2 Integration Settings
model:
  transformer_integration: true
  kimi_k2_api_endpoint: "http://localhost:8000"
  enable_tool_calling: true
  temperature: 0.6
  max_tokens: 4096
  
  # Tool configurations
  tools:
    generate_loop:
      enabled: true
      max_duration: 10.0
    
    smooth_sequence:
      enabled: true
      max_intermediate_frames: 10
    
    create_rig:
      enabled: true
      allowed_types: ["humanoid", "quadruped"]
```

## Advanced: Custom AI Training

To fine-tune Kimi-K2 for animation tasks:

### 1. Prepare Training Data

```python
# Generate training examples
training_data = [
    {
        "messages": [
            {"role": "user", "content": "Create a walk cycle for a character"},
            {"role": "assistant", "content": "I'll generate a walk cycle animation.",
             "tool_calls": [{
                 "function": {"name": "generate_animation_loop", 
                            "arguments": {"loop_type": "walk", "animation_type": "3D"}}
             }]}
        ]
    },
    {
        "messages": [
            {"role": "user", "content": "My claymation looks jerky, can you help?"},
            {"role": "assistant", "content": "Let me analyze the sequence first.",
             "tool_calls": [{
                 "function": {"name": "analyze_sequence_quality",
                            "arguments": {"sequence_file": "input.json"}}
             }]}
        ]
    }
    # Add more examples...
]
```

### 2. Dataset Structure

See `animation/config/animation_config.yaml` for dataset paths:

```yaml
training:
  datasets:
    claymation:
      - name: "Aardman Classics"
        path: "datasets/claymation/aardman"
        styles: ["wallace-gromit", "chicken-run", "shaun-sheep"]
```

## Best Practices

1. **Use Tool Calling for Interactive Workflows**
   - Let Kimi-K2 decide when to use animation tools
   - Provide clear tool descriptions

2. **Combine AI Reasoning with Animation Logic**
   - Use Kimi-K2 for creative decisions
   - Use animation module for technical execution

3. **Iterative Improvement**
   - Analyze → Get AI suggestions → Apply → Repeat

4. **Cache Results**
   - Save generated animations for reuse
   - Version control your sequences

## Troubleshooting

### Issue: Tool calls not working
**Solution**: Ensure `--enable-auto-tool-choice` and `--tool-call-parser kimi_k2` are set when starting vLLM/SGLang.

### Issue: Animation quality is poor
**Solution**: Increase intermediate frames, use ease-in-out interpolation, and apply style presets.

### Issue: Integration is slow
**Solution**: Use async tool execution and cache generated animations.

## Next Steps

- Explore more complex animation pipelines
- Integrate with 3D modeling software (Blender, Maya)
- Train custom models on your animation data
- Create domain-specific style presets

## Support

For integration help:
- Check the main README.md
- Review example code in `examples/`
- Contact: support@moonshot.cn
