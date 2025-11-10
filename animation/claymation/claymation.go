package claymation

import (
	"fmt"
	"math"
)

// Frame represents a single frame in a claymation sequence
type Frame struct {
	ID         int                    `json:"id"`
	Timestamp  float64                `json:"timestamp"`
	Objects    []Object               `json:"objects"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// Object represents a claymation object in a frame
type Object struct {
	Name       string             `json:"name"`
	Position   Position3D         `json:"position"`
	Rotation   Rotation3D         `json:"rotation"`
	Properties map[string]float64 `json:"properties"`
}

// Position3D represents 3D coordinates
type Position3D struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

// Rotation3D represents 3D rotation
type Rotation3D struct {
	Pitch float64 `json:"pitch"`
	Yaw   float64 `json:"yaw"`
	Roll  float64 `json:"roll"`
}

// Sequence represents a claymation sequence
type Sequence struct {
	Name      string               `json:"name"`
	FPS       float64              `json:"fps"`
	Keyframes []Frame              `json:"keyframes"`
	Style     string               `json:"style"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// Assistant provides AI-powered claymation assistance
type Assistant struct {
	config *Config
}

// Config holds configuration for the claymation assistant
type Config struct {
	DefaultFPS        float64
	InterpolationType string // "linear", "ease-in", "ease-out", "ease-in-out"
	StylePresets      map[string]StylePreset
}

// StylePreset defines a claymation style preset
type StylePreset struct {
	Name               string
	MotionBlur         float64
	FrameSpacing       float64
	SmoothingIntensity float64
}

// NewAssistant creates a new claymation assistant
func NewAssistant(config *Config) *Assistant {
	if config == nil {
		config = DefaultConfig()
	}
	return &Assistant{config: config}
}

// DefaultConfig returns the default configuration
func DefaultConfig() *Config {
	return &Config{
		DefaultFPS:        24.0,
		InterpolationType: "ease-in-out",
		StylePresets: map[string]StylePreset{
			"wallace-gromit": {
				Name:               "Wallace and Gromit",
				MotionBlur:         0.2,
				FrameSpacing:       1.0,
				SmoothingIntensity: 0.8,
			},
			"robot-chicken": {
				Name:               "Robot Chicken",
				MotionBlur:         0.1,
				FrameSpacing:       0.8,
				SmoothingIntensity: 0.5,
			},
			"classic": {
				Name:               "Classic Stop-Motion",
				MotionBlur:         0.0,
				FrameSpacing:       1.0,
				SmoothingIntensity: 0.3,
			},
		},
	}
}

// AnalyzeSequence analyzes a sequence and provides suggestions
func (a *Assistant) AnalyzeSequence(seq *Sequence) (*SequenceAnalysis, error) {
	if len(seq.Keyframes) < 2 {
		return nil, fmt.Errorf("sequence must have at least 2 keyframes")
	}

	analysis := &SequenceAnalysis{
		FrameCount:        len(seq.Keyframes),
		Duration:          seq.Keyframes[len(seq.Keyframes)-1].Timestamp - seq.Keyframes[0].Timestamp,
		AverageFPS:        seq.FPS,
		Suggestions:       []string{},
		QualityScore:      0.0,
		TransitionMetrics: []TransitionMetric{},
	}

	// Analyze transitions between keyframes
	for i := 0; i < len(seq.Keyframes)-1; i++ {
		metric := a.analyzeTransition(seq.Keyframes[i], seq.Keyframes[i+1])
		analysis.TransitionMetrics = append(analysis.TransitionMetrics, metric)
	}

	// Calculate quality score
	analysis.QualityScore = a.calculateQualityScore(analysis)

	// Generate suggestions
	analysis.Suggestions = a.generateSuggestions(analysis, seq)

	return analysis, nil
}

// SequenceAnalysis contains the analysis results
type SequenceAnalysis struct {
	FrameCount        int
	Duration          float64
	AverageFPS        float64
	Suggestions       []string
	QualityScore      float64
	TransitionMetrics []TransitionMetric
}

// TransitionMetric represents metrics for a transition between frames
type TransitionMetric struct {
	FromFrame      int
	ToFrame        int
	Distance       float64
	Smoothness     float64
	Recommendations []string
}

// analyzeTransition analyzes the transition between two frames
func (a *Assistant) analyzeTransition(from, to Frame) TransitionMetric {
	metric := TransitionMetric{
		FromFrame:       from.ID,
		ToFrame:         to.ID,
		Distance:        0.0,
		Smoothness:      1.0,
		Recommendations: []string{},
	}

	// Calculate average distance moved by objects
	if len(from.Objects) > 0 && len(to.Objects) > 0 {
		totalDistance := 0.0
		for i := 0; i < len(from.Objects) && i < len(to.Objects); i++ {
			dist := calculateDistance(from.Objects[i].Position, to.Objects[i].Position)
			totalDistance += dist
		}
		metric.Distance = totalDistance / float64(len(from.Objects))
	}

	// Determine if transition is too abrupt
	if metric.Distance > 50.0 {
		metric.Smoothness = 0.5
		metric.Recommendations = append(metric.Recommendations,
			"Consider adding intermediate frames for smoother transition")
	}

	return metric
}

// calculateDistance calculates Euclidean distance between two positions
func calculateDistance(p1, p2 Position3D) float64 {
	dx := p2.X - p1.X
	dy := p2.Y - p1.Y
	dz := p2.Z - p1.Z
	return math.Sqrt(dx*dx + dy*dy + dz*dz)
}

// calculateQualityScore calculates an overall quality score for the sequence
func (a *Assistant) calculateQualityScore(analysis *SequenceAnalysis) float64 {
	if len(analysis.TransitionMetrics) == 0 {
		return 0.0
	}

	totalSmoothness := 0.0
	for _, metric := range analysis.TransitionMetrics {
		totalSmoothness += metric.Smoothness
	}

	return (totalSmoothness / float64(len(analysis.TransitionMetrics))) * 100.0
}

// generateSuggestions generates improvement suggestions
func (a *Assistant) generateSuggestions(analysis *SequenceAnalysis, seq *Sequence) []string {
	suggestions := []string{}

	// Check FPS
	if seq.FPS < 12 {
		suggestions = append(suggestions, "FPS is quite low. Consider increasing to at least 12-15 FPS for smoother playback")
	}

	// Check quality score
	if analysis.QualityScore < 70.0 {
		suggestions = append(suggestions, "Overall sequence smoothness could be improved. Consider adding more intermediate frames")
	}

	// Check for style preset recommendations
	if seq.Style == "" {
		suggestions = append(suggestions, "No style preset selected. Consider using 'wallace-gromit' or 'robot-chicken' for inspiration")
	}

	return suggestions
}

// GenerateIntermediateFrames generates intermediate frames between keyframes
func (a *Assistant) GenerateIntermediateFrames(from, to Frame, count int) ([]Frame, error) {
	if count < 1 {
		return nil, fmt.Errorf("count must be at least 1")
	}

	intermediateFrames := make([]Frame, count)
	
	for i := 0; i < count; i++ {
		t := float64(i+1) / float64(count+1)
		
		// Apply interpolation type
		t = a.applyInterpolation(t)
		
		intermediateFrames[i] = Frame{
			ID:        from.ID + i + 1,
			Timestamp: from.Timestamp + (to.Timestamp-from.Timestamp)*t,
			Objects:   a.interpolateObjects(from.Objects, to.Objects, t),
			Metadata:  map[string]interface{}{"generated": true, "interpolation": a.config.InterpolationType},
		}
	}

	return intermediateFrames, nil
}

// applyInterpolation applies the configured interpolation type
func (a *Assistant) applyInterpolation(t float64) float64 {
	switch a.config.InterpolationType {
	case "linear":
		return t
	case "ease-in":
		return t * t
	case "ease-out":
		return t * (2.0 - t)
	case "ease-in-out":
		if t < 0.5 {
			return 2.0 * t * t
		}
		return -1.0 + (4.0-2.0*t)*t
	default:
		return t
	}
}

// interpolateObjects interpolates between two object lists
func (a *Assistant) interpolateObjects(from, to []Object, t float64) []Object {
	result := make([]Object, 0, len(from))
	
	for i := 0; i < len(from) && i < len(to); i++ {
		obj := Object{
			Name: from[i].Name,
			Position: Position3D{
				X: from[i].Position.X + (to[i].Position.X-from[i].Position.X)*t,
				Y: from[i].Position.Y + (to[i].Position.Y-from[i].Position.Y)*t,
				Z: from[i].Position.Z + (to[i].Position.Z-from[i].Position.Z)*t,
			},
			Rotation: Rotation3D{
				Pitch: from[i].Rotation.Pitch + (to[i].Rotation.Pitch-from[i].Rotation.Pitch)*t,
				Yaw:   from[i].Rotation.Yaw + (to[i].Rotation.Yaw-from[i].Rotation.Yaw)*t,
				Roll:  from[i].Rotation.Roll + (to[i].Rotation.Roll-from[i].Rotation.Roll)*t,
			},
			Properties: make(map[string]float64),
		}
		
		// Interpolate custom properties
		for key, fromVal := range from[i].Properties {
			if toVal, exists := to[i].Properties[key]; exists {
				obj.Properties[key] = fromVal + (toVal-fromVal)*t
			}
		}
		
		result = append(result, obj)
	}
	
	return result
}

// SmoothTransitions applies smoothing to all transitions in a sequence
func (a *Assistant) SmoothTransitions(seq *Sequence, intermediateFramesPerTransition int) (*Sequence, error) {
	if intermediateFramesPerTransition < 1 {
		return nil, fmt.Errorf("intermediateFramesPerTransition must be at least 1")
	}

	smoothedSeq := &Sequence{
		Name:      seq.Name + "_smoothed",
		FPS:       seq.FPS,
		Style:     seq.Style,
		Metadata:  seq.Metadata,
		Keyframes: []Frame{},
	}

	for i := 0; i < len(seq.Keyframes)-1; i++ {
		// Add original keyframe
		smoothedSeq.Keyframes = append(smoothedSeq.Keyframes, seq.Keyframes[i])
		
		// Generate and add intermediate frames
		intermediates, err := a.GenerateIntermediateFrames(
			seq.Keyframes[i],
			seq.Keyframes[i+1],
			intermediateFramesPerTransition,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to generate intermediate frames: %v", err)
		}
		
		smoothedSeq.Keyframes = append(smoothedSeq.Keyframes, intermediates...)
	}

	// Add final keyframe
	smoothedSeq.Keyframes = append(smoothedSeq.Keyframes, seq.Keyframes[len(seq.Keyframes)-1])

	return smoothedSeq, nil
}

// ApplyStylePreset applies a style preset to a sequence
func (a *Assistant) ApplyStylePreset(seq *Sequence, presetName string) error {
	preset, exists := a.config.StylePresets[presetName]
	if !exists {
		return fmt.Errorf("style preset '%s' not found", presetName)
	}

	seq.Style = preset.Name
	if seq.Metadata == nil {
		seq.Metadata = make(map[string]interface{})
	}
	seq.Metadata["style_preset"] = presetName
	seq.Metadata["motion_blur"] = preset.MotionBlur
	seq.Metadata["frame_spacing"] = preset.FrameSpacing
	seq.Metadata["smoothing_intensity"] = preset.SmoothingIntensity

	return nil
}
