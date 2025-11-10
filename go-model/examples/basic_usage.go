package main

import (
	"fmt"
	"github.com/SpidermanTotro/Kimi-K2/go-model/model"
)

func main() {
	fmt.Println("Kimi-K2 Go Language Model Example")
	fmt.Println("===================================")
	fmt.Println()

	// Create a default configuration with 16 transformer layers
	config := model.NewDefaultConfig()
	fmt.Printf("Model Configuration:\n")
	fmt.Printf("- Number of Layers: %d\n", config.NumLayers)
	fmt.Printf("- Hidden Size: %d\n", config.HiddenSize)
	fmt.Printf("- Number of Heads: %d\n", config.NumHeads)
	fmt.Printf("- Vocabulary Size: %d\n", config.VocabSize)
	fmt.Printf("- Max Sequence Length: %d\n", config.MaxSeqLen)
	fmt.Printf("- FFN Hidden Size: %d\n", config.FFNHiddenSize)
	fmt.Println()

	// Create the transformer model
	fmt.Println("Creating 16-layer transformer model...")
	transformer, err := model.NewTransformer(config)
	if err != nil {
		fmt.Printf("Error creating transformer: %v\n", err)
		return
	}

	// Display model statistics
	numParams := transformer.NumParameters()
	fmt.Printf("Model created successfully!\n")
	fmt.Printf("Total parameters: %d (%.2fM)\n", numParams, float64(numParams)/1e6)
	fmt.Println()

	// Example 1: Forward pass with a sequence of token IDs
	fmt.Println("Example 1: Forward Pass")
	fmt.Println("------------------------")
	tokenIDs := []int{10, 25, 100, 250, 500}
	fmt.Printf("Input token IDs: %v\n", tokenIDs)

	logits := transformer.Forward(tokenIDs)
	fmt.Printf("Output logits shape: %v\n", logits.Shape)
	fmt.Printf("Output size: %d elements\n", logits.Size())
	fmt.Println()

	// Example 2: Predict next token probabilities
	fmt.Println("Example 2: Next Token Prediction")
	fmt.Println("---------------------------------")
	probs := transformer.Predict(tokenIDs)
	fmt.Printf("Probability distribution shape: %v\n", probs.Shape)

	// Get top-5 most likely next tokens
	topK := transformer.GetTopK(probs, 5)
	fmt.Println("\nTop 5 most likely next tokens:")
	for i, tokenID := range topK {
		prob := probs.Data[tokenID]
		fmt.Printf("%d. Token ID: %d (probability: %.6f)\n", i+1, tokenID, prob)
	}
	fmt.Println()

	// Example 3: Custom configuration
	fmt.Println("Example 3: Custom Model Configuration")
	fmt.Println("--------------------------------------")
	customConfig := &model.Config{
		VocabSize:      30000,
		HiddenSize:     512,
		NumLayers:      16,
		NumHeads:       8,
		FFNHiddenSize:  2048,
		MaxSeqLen:      256,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	// Validate custom configuration
	if err := customConfig.Validate(); err != nil {
		fmt.Printf("Invalid configuration: %v\n", err)
	} else {
		fmt.Println("Custom configuration is valid!")
		customModel, err := model.NewTransformer(customConfig)
		if err != nil {
			fmt.Printf("Error creating custom model: %v\n", err)
		} else {
			customParams := customModel.NumParameters()
			fmt.Printf("Custom model created with %d parameters (%.2fM)\n",
				customParams, float64(customParams)/1e6)
		}
	}

	fmt.Println("\n✓ All examples completed successfully!")
}
