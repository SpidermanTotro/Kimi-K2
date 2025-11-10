package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/moonshotai/Kimi-K2/animation/animation"
	"github.com/moonshotai/Kimi-K2/animation/claymation"
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "kimi-animation",
	Short: "Kimi-K2 Animation AI Assistant",
	Long: `Kimi-K2 Animation AI Assistant provides tools for creating claymation 
and animation sequences using AI-powered generation and optimization.`,
}

var claymationCmd = &cobra.Command{
	Use:   "claymation",
	Short: "Claymation tools and commands",
	Long:  "Tools for analyzing, generating, and smoothing claymation sequences",
}

var animationCmd = &cobra.Command{
	Use:   "animation",
	Short: "Animation tools and commands",
	Long:  "Tools for generating 2D/3D animations, rigging, and IK",
}

var analyzeCmd = &cobra.Command{
	Use:   "analyze [sequence-file]",
	Short: "Analyze a claymation sequence",
	Args:  cobra.ExactArgs(1),
	RunE:  runAnalyze,
}

var smoothCmd = &cobra.Command{
	Use:   "smooth [sequence-file] [output-file]",
	Short: "Smooth transitions in a claymation sequence",
	Args:  cobra.ExactArgs(2),
	RunE:  runSmooth,
}

var generateLoopCmd = &cobra.Command{
	Use:   "generate-loop [type] [output-file]",
	Short: "Generate an animation loop (walk, idle, run, jump)",
	Args:  cobra.ExactArgs(2),
	RunE:  runGenerateLoop,
}

var createRigCmd = &cobra.Command{
	Use:   "create-rig [type] [output-file]",
	Short: "Create a skeletal rig (humanoid, quadruped)",
	Args:  cobra.ExactArgs(2),
	RunE:  runCreateRig,
}

var applyStyleCmd = &cobra.Command{
	Use:   "apply-style [sequence-file] [style] [output-file]",
	Short: "Apply a style preset to a sequence",
	Args:  cobra.ExactArgs(3),
	RunE:  runApplyStyle,
}

var listStylesCmd = &cobra.Command{
	Use:   "list-styles",
	Short: "List available style presets",
	RunE:  runListStyles,
}

var (
	intermediateFrames int
	animationType      string
	fps                float64
	interpolation      string
)

func init() {
	// Claymation commands
	claymationCmd.AddCommand(analyzeCmd)
	claymationCmd.AddCommand(smoothCmd)
	claymationCmd.AddCommand(applyStyleCmd)
	claymationCmd.AddCommand(listStylesCmd)

	// Animation commands
	animationCmd.AddCommand(generateLoopCmd)
	animationCmd.AddCommand(createRigCmd)

	// Root commands
	rootCmd.AddCommand(claymationCmd)
	rootCmd.AddCommand(animationCmd)

	// Flags
	smoothCmd.Flags().IntVarP(&intermediateFrames, "intermediate-frames", "i", 3, "Number of intermediate frames per transition")
	smoothCmd.Flags().StringVarP(&interpolation, "interpolation", "t", "ease-in-out", "Interpolation type (linear, ease-in, ease-out, ease-in-out)")
	
	generateLoopCmd.Flags().StringVarP(&animationType, "type", "t", "3D", "Animation type (2D, 3D)")
	generateLoopCmd.Flags().Float64VarP(&fps, "fps", "f", 30.0, "Frames per second")
}

func runAnalyze(cmd *cobra.Command, args []string) error {
	sequenceFile := args[0]

	// Load sequence
	data, err := os.ReadFile(sequenceFile)
	if err != nil {
		return fmt.Errorf("failed to read sequence file: %v", err)
	}

	var seq claymation.Sequence
	if err := json.Unmarshal(data, &seq); err != nil {
		return fmt.Errorf("failed to parse sequence: %v", err)
	}

	// Analyze
	assistant := claymation.NewAssistant(nil)
	analysis, err := assistant.AnalyzeSequence(&seq)
	if err != nil {
		return fmt.Errorf("failed to analyze sequence: %v", err)
	}

	// Print results
	fmt.Printf("=== Sequence Analysis ===\n")
	fmt.Printf("Name: %s\n", seq.Name)
	fmt.Printf("Frame Count: %d\n", analysis.FrameCount)
	fmt.Printf("Duration: %.2f seconds\n", analysis.Duration)
	fmt.Printf("FPS: %.2f\n", analysis.AverageFPS)
	fmt.Printf("Quality Score: %.2f/100\n", analysis.QualityScore)
	fmt.Printf("\n=== Transition Metrics ===\n")
	for _, metric := range analysis.TransitionMetrics {
		fmt.Printf("Frame %d -> %d: Distance=%.2f, Smoothness=%.2f\n",
			metric.FromFrame, metric.ToFrame, metric.Distance, metric.Smoothness)
		for _, rec := range metric.Recommendations {
			fmt.Printf("  - %s\n", rec)
		}
	}
	fmt.Printf("\n=== Suggestions ===\n")
	for i, suggestion := range analysis.Suggestions {
		fmt.Printf("%d. %s\n", i+1, suggestion)
	}

	return nil
}

func runSmooth(cmd *cobra.Command, args []string) error {
	sequenceFile := args[0]
	outputFile := args[1]

	// Load sequence
	data, err := os.ReadFile(sequenceFile)
	if err != nil {
		return fmt.Errorf("failed to read sequence file: %v", err)
	}

	var seq claymation.Sequence
	if err := json.Unmarshal(data, &seq); err != nil {
		return fmt.Errorf("failed to parse sequence: %v", err)
	}

	// Create assistant with custom config
	config := claymation.DefaultConfig()
	config.InterpolationType = interpolation
	assistant := claymation.NewAssistant(config)

	// Smooth transitions
	smoothed, err := assistant.SmoothTransitions(&seq, intermediateFrames)
	if err != nil {
		return fmt.Errorf("failed to smooth sequence: %v", err)
	}

	// Save result
	result, err := json.MarshalIndent(smoothed, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal result: %v", err)
	}

	if err := os.WriteFile(outputFile, result, 0644); err != nil {
		return fmt.Errorf("failed to write output: %v", err)
	}

	fmt.Printf("Smoothed sequence saved to %s\n", outputFile)
	fmt.Printf("Added %d intermediate frames between each keyframe\n", intermediateFrames)
	fmt.Printf("Original keyframes: %d, New total frames: %d\n", len(seq.Keyframes), len(smoothed.Keyframes))

	return nil
}

func runGenerateLoop(cmd *cobra.Command, args []string) error {
	loopType := args[0]
	outputFile := args[1]

	var animType animation.AnimationType
	if animationType == "2D" {
		animType = animation.Animation2D
	} else {
		animType = animation.Animation3D
	}

	assistant := animation.NewAssistant(nil)
	loop, err := assistant.GenerateAnimationLoop(loopType, animType)
	if err != nil {
		return fmt.Errorf("failed to generate loop: %v", err)
	}

	// Save result
	result, err := json.MarshalIndent(loop, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal result: %v", err)
	}

	if err := os.WriteFile(outputFile, result, 0644); err != nil {
		return fmt.Errorf("failed to write output: %v", err)
	}

	fmt.Printf("Generated %s animation loop\n", loopType)
	fmt.Printf("Type: %s\n", loop.Type)
	fmt.Printf("Duration: %.2f seconds\n", loop.Duration)
	fmt.Printf("Keyframes: %d\n", len(loop.Keyframes))
	fmt.Printf("Output saved to %s\n", outputFile)

	return nil
}

func runCreateRig(cmd *cobra.Command, args []string) error {
	rigType := args[0]
	outputFile := args[1]

	assistant := animation.NewAssistant(nil)
	rig, err := assistant.CreateBasicRig(rigType)
	if err != nil {
		return fmt.Errorf("failed to create rig: %v", err)
	}

	// Save result
	result, err := json.MarshalIndent(rig, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal result: %v", err)
	}

	if err := os.WriteFile(outputFile, result, 0644); err != nil {
		return fmt.Errorf("failed to write output: %v", err)
	}

	fmt.Printf("Created %s rig\n", rigType)
	fmt.Printf("Name: %s\n", rig.Name)
	fmt.Printf("Bones: %d\n", len(rig.Bones))
	fmt.Printf("Joints: %d\n", len(rig.Joints))
	fmt.Printf("Output saved to %s\n", outputFile)

	return nil
}

func runApplyStyle(cmd *cobra.Command, args []string) error {
	sequenceFile := args[0]
	style := args[1]
	outputFile := args[2]

	// Load sequence
	data, err := os.ReadFile(sequenceFile)
	if err != nil {
		return fmt.Errorf("failed to read sequence file: %v", err)
	}

	var seq claymation.Sequence
	if err := json.Unmarshal(data, &seq); err != nil {
		return fmt.Errorf("failed to parse sequence: %v", err)
	}

	// Apply style
	assistant := claymation.NewAssistant(nil)
	if err := assistant.ApplyStylePreset(&seq, style); err != nil {
		return fmt.Errorf("failed to apply style: %v", err)
	}

	// Save result
	result, err := json.MarshalIndent(seq, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal result: %v", err)
	}

	if err := os.WriteFile(outputFile, result, 0644); err != nil {
		return fmt.Errorf("failed to write output: %v", err)
	}

	fmt.Printf("Applied style preset '%s' to sequence\n", style)
	fmt.Printf("Output saved to %s\n", outputFile)

	return nil
}

func runListStyles(cmd *cobra.Command, args []string) error {
	config := claymation.DefaultConfig()

	fmt.Printf("=== Available Style Presets ===\n\n")
	for name, preset := range config.StylePresets {
		fmt.Printf("Name: %s\n", name)
		fmt.Printf("  Display Name: %s\n", preset.Name)
		fmt.Printf("  Motion Blur: %.2f\n", preset.MotionBlur)
		fmt.Printf("  Frame Spacing: %.2f\n", preset.FrameSpacing)
		fmt.Printf("  Smoothing Intensity: %.2f\n", preset.SmoothingIntensity)
		fmt.Println()
	}

	return nil
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
