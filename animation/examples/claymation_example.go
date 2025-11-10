package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/moonshotai/Kimi-K2/animation/claymation"
)

func main() {
	fmt.Println("=== Kimi-K2 Claymation Example ===\n")

	// Create a simple sequence
	sequence := &claymation.Sequence{
		Name:  "Test Animation",
		FPS:   24.0,
		Style: "",
		Keyframes: []claymation.Frame{
			{
				ID:        0,
				Timestamp: 0.0,
				Objects: []claymation.Object{
					{
						Name:     "ball",
						Position: claymation.Position3D{X: 0, Y: 0, Z: 0},
						Rotation: claymation.Rotation3D{Pitch: 0, Yaw: 0, Roll: 0},
						Properties: map[string]float64{
							"radius": 10.0,
						},
					},
				},
			},
			{
				ID:        1,
				Timestamp: 1.0,
				Objects: []claymation.Object{
					{
						Name:     "ball",
						Position: claymation.Position3D{X: 100, Y: 50, Z: 0},
						Rotation: claymation.Rotation3D{Pitch: 0, Yaw: 180, Roll: 0},
						Properties: map[string]float64{
							"radius": 10.0,
						},
					},
				},
			},
			{
				ID:        2,
				Timestamp: 2.0,
				Objects: []claymation.Object{
					{
						Name:     "ball",
						Position: claymation.Position3D{X: 200, Y: 0, Z: 0},
						Rotation: claymation.Rotation3D{Pitch: 0, Yaw: 360, Roll: 0},
						Properties: map[string]float64{
							"radius": 10.0,
						},
					},
				},
			},
		},
	}

	// Create assistant
	assistant := claymation.NewAssistant(nil)

	// Analyze sequence
	fmt.Println("1. Analyzing sequence...")
	analysis, err := assistant.AnalyzeSequence(sequence)
	if err != nil {
		fmt.Printf("Error analyzing sequence: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Frame Count: %d\n", analysis.FrameCount)
	fmt.Printf("   Duration: %.2f seconds\n", analysis.Duration)
	fmt.Printf("   Quality Score: %.2f/100\n", analysis.QualityScore)
	fmt.Printf("   Suggestions: %d\n", len(analysis.Suggestions))
	for _, suggestion := range analysis.Suggestions {
		fmt.Printf("   - %s\n", suggestion)
	}

	// Smooth transitions
	fmt.Println("\n2. Smoothing transitions...")
	smoothed, err := assistant.SmoothTransitions(sequence, 3)
	if err != nil {
		fmt.Printf("Error smoothing transitions: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Original frames: %d\n", len(sequence.Keyframes))
	fmt.Printf("   Smoothed frames: %d\n", len(smoothed.Keyframes))

	// Apply style preset
	fmt.Println("\n3. Applying Wallace and Gromit style preset...")
	err = assistant.ApplyStylePreset(smoothed, "wallace-gromit")
	if err != nil {
		fmt.Printf("Error applying style: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Style applied: %s\n", smoothed.Style)

	// Save result
	fmt.Println("\n4. Saving result...")
	data, err := json.MarshalIndent(smoothed, "", "  ")
	if err != nil {
		fmt.Printf("Error marshaling result: %v\n", err)
		os.Exit(1)
	}

	err = os.WriteFile("output_claymation.json", data, 0644)
	if err != nil {
		fmt.Printf("Error writing file: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("   Saved to: output_claymation.json")
	fmt.Println("\n=== Example Complete ===")
}
