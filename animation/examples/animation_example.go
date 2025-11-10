package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/moonshotai/Kimi-K2/animation/animation"
)

func main() {
	fmt.Println("=== Kimi-K2 Animation Example ===\n")

	assistant := animation.NewAssistant(nil)

	// Example 1: Generate a walk cycle
	fmt.Println("1. Generating walk cycle animation...")
	walkLoop, err := assistant.GenerateAnimationLoop("walk", animation.Animation3D)
	if err != nil {
		fmt.Printf("Error generating walk cycle: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Name: %s\n", walkLoop.Name)
	fmt.Printf("   Type: %s\n", walkLoop.Type)
	fmt.Printf("   Duration: %.2f seconds\n", walkLoop.Duration)
	fmt.Printf("   Keyframes: %d\n", len(walkLoop.Keyframes))

	// Save walk cycle
	data, _ := json.MarshalIndent(walkLoop, "", "  ")
	os.WriteFile("output_walk_cycle.json", data, 0644)
	fmt.Println("   Saved to: output_walk_cycle.json")

	// Example 2: Generate an idle animation
	fmt.Println("\n2. Generating idle animation...")
	idleLoop, err := assistant.GenerateAnimationLoop("idle", animation.Animation3D)
	if err != nil {
		fmt.Printf("Error generating idle animation: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Name: %s\n", idleLoop.Name)
	fmt.Printf("   Duration: %.2f seconds\n", idleLoop.Duration)
	fmt.Printf("   Keyframes: %d\n", len(idleLoop.Keyframes))

	// Example 3: Create a humanoid rig
	fmt.Println("\n3. Creating humanoid rig...")
	rig, err := assistant.CreateBasicRig("humanoid")
	if err != nil {
		fmt.Printf("Error creating rig: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("   Rig Name: %s\n", rig.Name)
	fmt.Printf("   Bones: %d\n", len(rig.Bones))
	fmt.Printf("   Joints: %d\n", len(rig.Joints))

	// List bones
	fmt.Println("   Bone hierarchy:")
	for _, bone := range rig.Bones {
		indent := ""
		if bone.ParentID != "" {
			indent = "    "
		}
		fmt.Printf("   %s- %s (length: %.1f)\n", indent, bone.Name, bone.Length)
	}

	// Save rig
	rigData, _ := json.MarshalIndent(rig, "", "  ")
	os.WriteFile("output_humanoid_rig.json", rigData, 0644)
	fmt.Println("   Saved to: output_humanoid_rig.json")

	// Example 4: Test IK solver
	fmt.Println("\n4. Testing IK solver...")
	target := animation.Position3D{X: 50, Y: 100, Z: 20}
	rotations, err := assistant.SolveIK(rig, "left_arm", target)
	if err != nil {
		fmt.Printf("Error solving IK: %v\n", err)
	} else {
		fmt.Printf("   Target position: (%.1f, %.1f, %.1f)\n", target.X, target.Y, target.Z)
		fmt.Printf("   Calculated rotations for %d bones\n", len(rotations))
	}

	// Example 5: Export animation
	fmt.Println("\n5. Exporting animation...")
	formats := []string{"json", "fbx", "gltf"}
	for _, format := range formats {
		_, err := assistant.ExportAnimation(walkLoop, format)
		if err != nil {
			fmt.Printf("   Error exporting to %s: %v\n", format, err)
		} else {
			fmt.Printf("   ✓ Export to %s format successful\n", format)
		}
	}

	fmt.Println("\n=== Example Complete ===")
}
