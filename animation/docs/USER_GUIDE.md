# Kimi-K2 Animation AI - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Claymation Features](#claymation-features)
4. [Animation Features](#animation-features)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)

## Introduction

Welcome to the Kimi-K2 Animation AI module! This guide will help you get started with creating amazing claymation and animation sequences using AI-powered tools.

## Getting Started

### Installation

1. Clone the Kimi-K2 repository:
```bash
git clone https://github.com/moonshotai/Kimi-K2.git
cd Kimi-K2/animation
```

2. Build the CLI tool:
```bash
go mod download
go build -o kimi-animation ./cli
```

3. Verify installation:
```bash
./kimi-animation --help
```

### Your First Animation

Let's create a simple walk cycle:

```bash
# Generate a walk cycle
./kimi-animation animation generate-loop walk my_walk_cycle.json

# View the result
cat my_walk_cycle.json
```

## Claymation Features

### Understanding Claymation Sequences

A claymation sequence consists of:
- **Keyframes**: Major poses or positions in your animation
- **Objects**: Elements being animated (characters, props)
- **Metadata**: Additional information about the sequence

### Creating a Sequence

Create a JSON file with your keyframes:

```json
{
  "name": "My First Claymation",
  "fps": 24,
  "keyframes": [
    {
      "id": 0,
      "timestamp": 0.0,
      "objects": [
        {
          "name": "character",
          "position": {"x": 0, "y": 0, "z": 0},
          "rotation": {"pitch": 0, "yaw": 0, "roll": 0}
        }
      ]
    }
  ]
}
```

### Analyzing Your Sequence

```bash
./kimi-animation claymation analyze my_sequence.json
```

### Smoothing Transitions

```bash
./kimi-animation claymation smooth \
  my_sequence.json \
  my_sequence_smooth.json \
  --intermediate-frames 3 \
  --interpolation ease-in-out
```

## Animation Features

### Generating Animation Loops

```bash
# Walk cycle
./kimi-animation animation generate-loop walk walk.json --type 3D

# Idle animation
./kimi-animation animation generate-loop idle idle.json --type 3D

# Run cycle
./kimi-animation animation generate-loop run run.json --type 3D

# Jump
./kimi-animation animation generate-loop jump jump.json --type 3D
```

### Creating Rigs

```bash
# Humanoid rig
./kimi-animation animation create-rig humanoid humanoid.json

# Quadruped rig
./kimi-animation animation create-rig quadruped quadruped.json
```

## Best Practices

1. **Start Simple**: Begin with 2-3 keyframes
2. **Check Quality**: Run analysis after major changes
3. **Iterate**: Gradually increase smoothing
4. **Use References**: Study real motion

For more details, see the complete documentation in README.md
