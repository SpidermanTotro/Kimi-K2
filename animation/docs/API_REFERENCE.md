# API Reference

## Claymation Package

### Types

#### `Frame`
Represents a single frame in a claymation sequence.

```go
type Frame struct {
    ID         int                    `json:"id"`
    Timestamp  float64                `json:"timestamp"`
    Objects    []Object               `json:"objects"`
    Metadata   map[string]interface{} `json:"metadata"`
}
```

#### `Object`
Represents a claymation object in a frame.

```go
type Object struct {
    Name       string             `json:"name"`
    Position   Position3D         `json:"position"`
    Rotation   Rotation3D         `json:"rotation"`
    Properties map[string]float64 `json:"properties"`
}
```

#### `Sequence`
Represents a complete claymation sequence.

```go
type Sequence struct {
    Name      string                 `json:"name"`
    FPS       float64                `json:"fps"`
    Keyframes []Frame                `json:"keyframes"`
    Style     string                 `json:"style"`
    Metadata  map[string]interface{} `json:"metadata"`
}
```

### Functions

#### `NewAssistant(config *Config) *Assistant`
Creates a new claymation assistant.

**Parameters:**
- `config`: Optional configuration. Pass `nil` for defaults.

**Returns:**
- `*Assistant`: New assistant instance

**Example:**
```go
assistant := claymation.NewAssistant(nil)
```

#### `AnalyzeSequence(seq *Sequence) (*SequenceAnalysis, error)`
Analyzes a claymation sequence for quality and smoothness.

**Parameters:**
- `seq`: The sequence to analyze

**Returns:**
- `*SequenceAnalysis`: Analysis results
- `error`: Error if analysis fails

**Example:**
```go
analysis, err := assistant.AnalyzeSequence(sequence)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Quality: %.2f\n", analysis.QualityScore)
```

#### `GenerateIntermediateFrames(from, to Frame, count int) ([]Frame, error)`
Generates intermediate frames between two keyframes.

**Parameters:**
- `from`: Starting frame
- `to`: Ending frame
- `count`: Number of intermediate frames to generate

**Returns:**
- `[]Frame`: Generated intermediate frames
- `error`: Error if generation fails

#### `SmoothTransitions(seq *Sequence, intermediateFramesPerTransition int) (*Sequence, error)`
Smooths all transitions in a sequence.

**Parameters:**
- `seq`: Input sequence
- `intermediateFramesPerTransition`: Number of frames to add between each keyframe

**Returns:**
- `*Sequence`: New smoothed sequence
- `error`: Error if smoothing fails

#### `ApplyStylePreset(seq *Sequence, presetName string) error`
Applies a style preset to a sequence.

**Parameters:**
- `seq`: Sequence to modify
- `presetName`: Name of style preset (e.g., "wallace-gromit")

**Returns:**
- `error`: Error if preset not found

## Animation Package

### Types

#### `AnimationLoop`
Represents a looping animation.

```go
type AnimationLoop struct {
    Name       string         `json:"name"`
    Type       AnimationType  `json:"type"`
    LoopType   string         `json:"loop_type"`
    Duration   float64        `json:"duration"`
    Keyframes  []AnimKeyframe `json:"keyframes"`
    Rig        *Rig           `json:"rig,omitempty"`
}
```

#### `Rig`
Represents a skeletal rig.

```go
type Rig struct {
    Name   string  `json:"name"`
    Bones  []Bone  `json:"bones"`
    Joints []Joint `json:"joints"`
}
```

### Functions

#### `NewAssistant(config *Config) *Assistant`
Creates a new animation assistant.

**Parameters:**
- `config`: Optional configuration. Pass `nil` for defaults.

**Returns:**
- `*Assistant`: New assistant instance

#### `GenerateAnimationLoop(loopType string, animType AnimationType) (*AnimationLoop, error)`
Generates an animation loop.

**Parameters:**
- `loopType`: Type of loop ("walk", "idle", "run", "jump")
- `animType`: Animation2D or Animation3D

**Returns:**
- `*AnimationLoop`: Generated animation loop
- `error`: Error if generation fails

**Example:**
```go
loop, err := assistant.GenerateAnimationLoop("walk", animation.Animation3D)
```

#### `CreateBasicRig(rigType string) (*Rig, error)`
Creates a basic skeletal rig.

**Parameters:**
- `rigType`: Type of rig ("humanoid", "quadruped")

**Returns:**
- `*Rig`: Created rig
- `error`: Error if creation fails

#### `SolveIK(rig *Rig, endEffectorID string, target Position3D) (map[string]Rotation3D, error)`
Performs inverse kinematics.

**Parameters:**
- `rig`: The skeletal rig
- `endEffectorID`: ID of the bone to position
- `target`: Target position

**Returns:**
- `map[string]Rotation3D`: Bone rotations
- `error`: Error if solving fails

#### `ExportAnimation(loop *AnimationLoop, format string) ([]byte, error)`
Exports animation to specified format.

**Parameters:**
- `loop`: Animation to export
- `format`: Export format ("json", "fbx", "gltf")

**Returns:**
- `[]byte`: Exported data
- `error`: Error if export fails
