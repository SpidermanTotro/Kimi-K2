package main

import (
	"fmt"
	"log"

	"github.com/SpidermanTotro/Kimi-K2/model"
)

func main() {
	// Create a default configuration for a 16-layer model
	config := model.NewDefaultConfig()
	
	fmt.Println("=== Kimi-K2 16-Layer Transformer Model ===")
	fmt.Printf("Configuration:\n")
	fmt.Printf("  - Vocabulary Size: %d\n", config.VocabSize)
	fmt.Printf("  - Hidden Size: %d\n", config.HiddenSize)
	fmt.Printf("  - Number of Layers: %d\n", config.NumLayers)
	fmt.Printf("  - Number of Attention Heads: %d\n", config.NumHeads)
	fmt.Printf("  - Intermediate FFN Size: %d\n", config.IntermediateSize)
	fmt.Printf("  - Max Sequence Length: %d\n", config.MaxSeqLength)
	fmt.Printf("  - Activation: %s\n\n", config.ActivationType)

	// Create the model
	transformer, err := model.NewTransformer16(config)
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	// Calculate and display number of parameters
	numParams := transformer.NumParameters()
	fmt.Printf("Total Parameters: %d (%.2fM)\n\n", numParams, float64(numParams)/1_000_000)

	// Example: Forward pass with a sequence of tokens
	fmt.Println("Running forward pass...")
	tokens := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	
	logits, err := transformer.Forward(tokens)
	if err != nil {
		log.Fatalf("Forward pass failed: %v", err)
	}

	fmt.Printf("Input tokens: %v\n", tokens)
	fmt.Printf("Output shape: [%d, %d] (sequence_length, vocab_size)\n", len(logits), len(logits[0]))
	
	// Display logits for the last token (simplified view)
	lastLogits := logits[len(logits)-1]
	fmt.Printf("\nLogits for the last position (first 10 values):\n")
	for i := 0; i < 10 && i < len(lastLogits); i++ {
		fmt.Printf("  Token %d: %.4f\n", i, lastLogits[i])
	}

	// Example: Generate next token
	fmt.Println("\nGenerating next token...")
	nextToken, err := transformer.Generate(tokens, 1.0)
	if err != nil {
		log.Fatalf("Generation failed: %v", err)
	}
	fmt.Printf("Next token prediction: %d\n", nextToken)

	fmt.Println("\n=== Model successfully created and tested! ===")
}
