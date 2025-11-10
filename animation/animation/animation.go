package animation

import (
	"fmt"
	"math"
)

// AnimationType represents the type of animation
type AnimationType string

const (
	Animation2D AnimationType = "2D"
	Animation3D AnimationType = "3D"
)

// AnimationLoop represents a looping animation
type AnimationLoop struct {
	Name       string         `json:"name"`
	Type       AnimationType  `json:"type"`
	LoopType   string         `json:"loop_type"` // "walk", "idle", "run", "jump"
	Duration   float64        `json:"duration"`
	Keyframes  []AnimKeyframe `json:"keyframes"`
	Rig        *Rig           `json:"rig,omitempty"`
}

// AnimKeyframe represents a keyframe in an animation
type AnimKeyframe struct {
	Time      float64            `json:"time"`
	Transforms map[string]Transform `json:"transforms"`
}

// Transform represents a transformation
type Transform struct {
	Position Position3D `json:"position"`
	Rotation Rotation3D `json:"rotation"`
	Scale    Scale3D    `json:"scale"`
}

// Position3D represents a 3D position
type Position3D struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

// Rotation3D represents a 3D rotation
type Rotation3D struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

// Scale3D represents a 3D scale
type Scale3D struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

// Rig represents a skeletal rig for animation
type Rig struct {
	Name   string  `json:"name"`
	Bones  []Bone  `json:"bones"`
	Joints []Joint `json:"joints"`
}

// Bone represents a bone in a rig
type Bone struct {
	ID           string     `json:"id"`
	Name         string     `json:"name"`
	ParentID     string     `json:"parent_id,omitempty"`
	Length       float64    `json:"length"`
	RestPosition Position3D `json:"rest_position"`
	RestRotation Rotation3D `json:"rest_rotation"`
}

// Joint represents a joint in a rig
type Joint struct {
	ID         string     `json:"id"`
	BoneID     string     `json:"bone_id"`
	Position   Position3D `json:"position"`
	Constraints Constraints `json:"constraints"`
}

// Constraints represents joint constraints
type Constraints struct {
	MinRotation Rotation3D `json:"min_rotation"`
	MaxRotation Rotation3D `json:"max_rotation"`
}

// Assistant provides AI-powered animation assistance
type Assistant struct {
	config *Config
}

// Config holds configuration for animation assistant
type Config struct {
	DefaultFPS        float64
	LoopTemplates     map[string]LoopTemplate
	IKSolverPrecision float64
}

// LoopTemplate defines a template for animation loops
type LoopTemplate struct {
	Name           string
	Type           string
	DefaultDuration float64
	KeyframeCount  int
	Description    string
}

// NewAssistant creates a new animation assistant
func NewAssistant(config *Config) *Assistant {
	if config == nil {
		config = DefaultConfig()
	}
	return &Assistant{config: config}
}

// DefaultConfig returns default configuration
func DefaultConfig() *Config {
	return &Config{
		DefaultFPS:        30.0,
		IKSolverPrecision: 0.001,
		LoopTemplates: map[string]LoopTemplate{
			"walk": {
				Name:            "Walk Cycle",
				Type:            "walk",
				DefaultDuration: 1.0,
				KeyframeCount:   8,
				Description:     "Standard walk cycle with natural foot placement",
			},
			"idle": {
				Name:            "Idle Animation",
				Type:            "idle",
				DefaultDuration: 2.0,
				KeyframeCount:   4,
				Description:     "Subtle breathing and weight shifting",
			},
			"run": {
				Name:            "Run Cycle",
				Type:            "run",
				DefaultDuration: 0.6,
				KeyframeCount:   8,
				Description:     "Fast run cycle with extended stride",
			},
			"jump": {
				Name:            "Jump",
				Type:            "jump",
				DefaultDuration: 1.5,
				KeyframeCount:   6,
				Description:     "Jump animation with anticipation and landing",
			},
		},
	}
}

// GenerateAnimationLoop generates an animation loop based on minimal input
func (a *Assistant) GenerateAnimationLoop(loopType string, animType AnimationType) (*AnimationLoop, error) {
	template, exists := a.config.LoopTemplates[loopType]
	if !exists {
		return nil, fmt.Errorf("loop template '%s' not found", loopType)
	}

	loop := &AnimationLoop{
		Name:      template.Name,
		Type:      animType,
		LoopType:  loopType,
		Duration:  template.DefaultDuration,
		Keyframes: []AnimKeyframe{},
	}

	// Generate keyframes based on template
	switch loopType {
	case "walk":
		loop.Keyframes = a.generateWalkCycle(template.KeyframeCount, template.DefaultDuration)
	case "idle":
		loop.Keyframes = a.generateIdleAnimation(template.KeyframeCount, template.DefaultDuration)
	case "run":
		loop.Keyframes = a.generateRunCycle(template.KeyframeCount, template.DefaultDuration)
	case "jump":
		loop.Keyframes = a.generateJumpAnimation(template.KeyframeCount, template.DefaultDuration)
	default:
		return nil, fmt.Errorf("unsupported loop type: %s", loopType)
	}

	return loop, nil
}

// generateWalkCycle generates a walk cycle animation
func (a *Assistant) generateWalkCycle(keyframeCount int, duration float64) []AnimKeyframe {
	keyframes := make([]AnimKeyframe, keyframeCount)
	
	for i := 0; i < keyframeCount; i++ {
		t := float64(i) / float64(keyframeCount)
		time := duration * t
		
		// Simulate walk cycle motion
		legPhase := math.Sin(t * 2 * math.Pi)
		armPhase := math.Sin((t + 0.5) * 2 * math.Pi) // Arms opposite to legs
		
		keyframes[i] = AnimKeyframe{
			Time: time,
			Transforms: map[string]Transform{
				"root": {
					Position: Position3D{X: t * 100, Y: 0, Z: 0},
					Rotation: Rotation3D{X: 0, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"left_leg": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: legPhase * 30, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"right_leg": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: -legPhase * 30, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"left_arm": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: armPhase * 20, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"right_arm": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: -armPhase * 20, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
			},
		}
	}
	
	return keyframes
}

// generateIdleAnimation generates an idle animation
func (a *Assistant) generateIdleAnimation(keyframeCount int, duration float64) []AnimKeyframe {
	keyframes := make([]AnimKeyframe, keyframeCount)
	
	for i := 0; i < keyframeCount; i++ {
		t := float64(i) / float64(keyframeCount)
		time := duration * t
		
		// Subtle breathing motion
		breathPhase := math.Sin(t * 2 * math.Pi)
		
		keyframes[i] = AnimKeyframe{
			Time: time,
			Transforms: map[string]Transform{
				"root": {
					Position: Position3D{X: 0, Y: breathPhase * 0.5, Z: 0},
					Rotation: Rotation3D{X: 0, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1 + breathPhase*0.01, Z: 1},
				},
				"torso": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: breathPhase * 2, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
			},
		}
	}
	
	return keyframes
}

// generateRunCycle generates a run cycle animation
func (a *Assistant) generateRunCycle(keyframeCount int, duration float64) []AnimKeyframe {
	keyframes := make([]AnimKeyframe, keyframeCount)
	
	for i := 0; i < keyframeCount; i++ {
		t := float64(i) / float64(keyframeCount)
		time := duration * t
		
		// More exaggerated motion for running
		legPhase := math.Sin(t * 2 * math.Pi)
		
		keyframes[i] = AnimKeyframe{
			Time: time,
			Transforms: map[string]Transform{
				"root": {
					Position: Position3D{X: t * 200, Y: math.Abs(math.Sin(t*4*math.Pi)) * 5, Z: 0},
					Rotation: Rotation3D{X: -10, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"left_leg": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: legPhase * 50, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"right_leg": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: -legPhase * 50, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
			},
		}
	}
	
	return keyframes
}

// generateJumpAnimation generates a jump animation
func (a *Assistant) generateJumpAnimation(keyframeCount int, duration float64) []AnimKeyframe {
	keyframes := make([]AnimKeyframe, keyframeCount)
	
	for i := 0; i < keyframeCount; i++ {
		t := float64(i) / float64(keyframeCount)
		time := duration * t
		
		// Parabolic jump trajectory
		height := -4 * (t - 0.5) * (t - 0.5) + 1
		yPos := height * 100
		
		keyframes[i] = AnimKeyframe{
			Time: time,
			Transforms: map[string]Transform{
				"root": {
					Position: Position3D{X: 0, Y: yPos, Z: 0},
					Rotation: Rotation3D{X: 0, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
				"legs": {
					Position: Position3D{X: 0, Y: 0, Z: 0},
					Rotation: Rotation3D{X: (1 - height) * 45, Y: 0, Z: 0},
					Scale:    Scale3D{X: 1, Y: 1, Z: 1},
				},
			},
		}
	}
	
	return keyframes
}

// CreateBasicRig creates a basic skeletal rig
func (a *Assistant) CreateBasicRig(rigType string) (*Rig, error) {
	switch rigType {
	case "humanoid":
		return a.createHumanoidRig(), nil
	case "quadruped":
		return a.createQuadrupedRig(), nil
	default:
		return nil, fmt.Errorf("unsupported rig type: %s", rigType)
	}
}

// createHumanoidRig creates a basic humanoid rig
func (a *Assistant) createHumanoidRig() *Rig {
	return &Rig{
		Name: "Humanoid",
		Bones: []Bone{
			{ID: "root", Name: "Root", Length: 10, RestPosition: Position3D{0, 0, 0}},
			{ID: "spine", Name: "Spine", ParentID: "root", Length: 30, RestPosition: Position3D{0, 10, 0}},
			{ID: "head", Name: "Head", ParentID: "spine", Length: 15, RestPosition: Position3D{0, 40, 0}},
			{ID: "left_shoulder", Name: "Left Shoulder", ParentID: "spine", Length: 5, RestPosition: Position3D{-10, 35, 0}},
			{ID: "left_arm", Name: "Left Arm", ParentID: "left_shoulder", Length: 20, RestPosition: Position3D{-15, 35, 0}},
			{ID: "right_shoulder", Name: "Right Shoulder", ParentID: "spine", Length: 5, RestPosition: Position3D{10, 35, 0}},
			{ID: "right_arm", Name: "Right Arm", ParentID: "right_shoulder", Length: 20, RestPosition: Position3D{15, 35, 0}},
			{ID: "left_leg", Name: "Left Leg", ParentID: "root", Length: 40, RestPosition: Position3D{-5, 10, 0}},
			{ID: "right_leg", Name: "Right Leg", ParentID: "root", Length: 40, RestPosition: Position3D{5, 10, 0}},
		},
		Joints: []Joint{
			{ID: "spine_joint", BoneID: "spine", Position: Position3D{0, 10, 0}, Constraints: Constraints{MinRotation: Rotation3D{-45, -30, -20}, MaxRotation: Rotation3D{45, 30, 20}}},
			{ID: "neck_joint", BoneID: "head", Position: Position3D{0, 40, 0}, Constraints: Constraints{MinRotation: Rotation3D{-60, -80, -45}, MaxRotation: Rotation3D{60, 80, 45}}},
		},
	}
}

// createQuadrupedRig creates a basic quadruped rig
func (a *Assistant) createQuadrupedRig() *Rig {
	return &Rig{
		Name: "Quadruped",
		Bones: []Bone{
			{ID: "root", Name: "Root", Length: 15, RestPosition: Position3D{0, 0, 0}},
			{ID: "spine", Name: "Spine", ParentID: "root", Length: 40, RestPosition: Position3D{0, 20, 0}},
			{ID: "head", Name: "Head", ParentID: "spine", Length: 20, RestPosition: Position3D{0, 25, 40}},
			{ID: "front_left_leg", Name: "Front Left Leg", ParentID: "spine", Length: 30, RestPosition: Position3D{-10, 20, 30}},
			{ID: "front_right_leg", Name: "Front Right Leg", ParentID: "spine", Length: 30, RestPosition: Position3D{10, 20, 30}},
			{ID: "back_left_leg", Name: "Back Left Leg", ParentID: "root", Length: 30, RestPosition: Position3D{-10, 20, -20}},
			{ID: "back_right_leg", Name: "Back Right Leg", ParentID: "root", Length: 30, RestPosition: Position3D{10, 20, -20}},
		},
		Joints: []Joint{},
	}
}

// SolveIK performs inverse kinematics to position end effector at target
func (a *Assistant) SolveIK(rig *Rig, endEffectorID string, target Position3D) (map[string]Rotation3D, error) {
	// Simple CCD (Cyclic Coordinate Descent) IK solver
	rotations := make(map[string]Rotation3D)
	
	// Find the chain from root to end effector
	chain := a.findChain(rig, endEffectorID)
	if len(chain) == 0 {
		return nil, fmt.Errorf("could not find chain to end effector: %s", endEffectorID)
	}
	
	// Iterative solver
	maxIterations := 10
	for iter := 0; iter < maxIterations; iter++ {
		for i := len(chain) - 2; i >= 0; i-- {
			bone := chain[i]
			
			// Calculate the angle needed to move end effector closer to target
			// This is a simplified IK solver for demonstration
			angle := a.calculateIKAngle(bone, target)
			rotations[bone.ID] = Rotation3D{X: angle, Y: 0, Z: 0}
		}
	}
	
	return rotations, nil
}

// findChain finds the bone chain from root to specified bone
func (a *Assistant) findChain(rig *Rig, targetID string) []Bone {
	chain := []Bone{}
	
	for _, bone := range rig.Bones {
		if bone.ID == targetID {
			chain = append([]Bone{bone}, chain...)
			// Recursively add parents
			for bone.ParentID != "" {
				for _, parentBone := range rig.Bones {
					if parentBone.ID == bone.ParentID {
						chain = append([]Bone{parentBone}, chain...)
						bone = parentBone
						break
					}
				}
			}
			break
		}
	}
	
	return chain
}

// calculateIKAngle calculates the rotation angle needed for IK (simplified)
func (a *Assistant) calculateIKAngle(bone Bone, target Position3D) float64 {
	// Simplified angle calculation
	dx := target.X - bone.RestPosition.X
	dy := target.Y - bone.RestPosition.Y
	return math.Atan2(dy, dx) * 180 / math.Pi
}

// ExportAnimation exports animation to a common format
func (a *Assistant) ExportAnimation(loop *AnimationLoop, format string) ([]byte, error) {
	switch format {
	case "json":
		// In a real implementation, this would use json.Marshal
		return []byte(fmt.Sprintf("Animation: %s exported as JSON", loop.Name)), nil
	case "fbx":
		return []byte(fmt.Sprintf("Animation: %s exported as FBX", loop.Name)), nil
	case "gltf":
		return []byte(fmt.Sprintf("Animation: %s exported as glTF", loop.Name)), nil
	default:
		return nil, fmt.Errorf("unsupported export format: %s", format)
	}
}
