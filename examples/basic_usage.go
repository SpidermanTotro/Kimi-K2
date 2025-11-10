package main

import (
	"fmt"
	"log"

	"github.com/SpidermanTotro/Kimi-K2/pkg/benchmark"
	"github.com/SpidermanTotro/Kimi-K2/pkg/config"
	"github.com/SpidermanTotro/Kimi-K2/pkg/model"
	"github.com/SpidermanTotro/Kimi-K2/pkg/tokenizer"
)

func main() {
	fmt.Println("Kimi-K2 16GB GPT Model - Example Usage")
	fmt.Println("========================================")
	fmt.Println()
	
	// Use small config for demo (to run on limited resources)
	cfg := config.SmallConfig()
	
	fmt.Println("Model Configuration:")
	fmt.Printf("  Vocabulary Size: %d\n", cfg.VocabSize)
	fmt.Printf("  Hidden Dimension: %d\n", cfg.HiddenDim)
	fmt.Printf("  Number of Layers: %d\n", cfg.NumLayers)
	fmt.Printf("  Number of Heads: %d\n", cfg.NumHeads)
	fmt.Printf("  Max Sequence Length: %d\n", cfg.MaxSeqLen)
	fmt.Printf("  FP16 Enabled: %v\n", cfg.UseFP16)
	fmt.Printf("  FlashAttention Enabled: %v\n", cfg.UseFlashAttention)
	fmt.Printf("  KV Cache Enabled: %v\n", cfg.UseKVCache)
	
	estimatedMem := cfg.EstimateMemoryUsage()
	fmt.Printf("  Estimated Memory: %.2f GB\n\n", estimatedMem)
	
	// Create model
	fmt.Println("Creating model...")
	m, err := model.NewGPTModel(cfg)
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}
	fmt.Println("Model created successfully!")
	
	// Create tokenizer
	fmt.Println("\nCreating tokenizer...")
	tok := tokenizer.NewTokenizer(cfg.VocabSize)
	
	// Build vocabulary from sample texts
	sampleTexts := []string{
		"the quick brown fox jumps over the lazy dog",
		"hello world from the kimi k2 model",
		"machine learning and natural language processing",
		"artificial intelligence is transforming the world",
		"deep learning neural networks are powerful tools",
	}
	tok.BuildVocab(sampleTexts)
	fmt.Printf("Tokenizer created with vocabulary size: %d\n", tok.GetVocabSize())
	
	// Example: Encode and decode
	fmt.Println("\n--- Tokenization Example ---")
	testText := "hello world"
	fmt.Printf("Input text: %s\n", testText)
	
	encoded := tok.Encode(testText, true)
	fmt.Printf("Encoded (with special tokens): %v\n", encoded)
	
	decoded := tok.Decode(encoded, true)
	fmt.Printf("Decoded: %s\n", decoded)
	
	// Example: Forward pass
	fmt.Println("\n--- Forward Pass Example ---")
	inputText := "the quick brown"
	inputIDs := tok.Encode(inputText, false)
	fmt.Printf("Input: %s\n", inputText)
	fmt.Printf("Input IDs: %v\n", inputIDs)
	
	if len(inputIDs) > 0 && len(inputIDs) <= cfg.MaxSeqLen {
		logits, err := m.Forward(inputIDs, false)
		if err != nil {
			log.Printf("Forward pass failed: %v", err)
		} else {
			rows, cols := logits.Dims()
			fmt.Printf("Output logits shape: (%d, %d)\n", rows, cols)
			fmt.Println("Forward pass completed successfully!")
		}
	}
	
	// Example: Text generation
	fmt.Println("\n--- Text Generation Example ---")
	promptText := "hello"
	promptIDs := tok.Encode(promptText, false)
	fmt.Printf("Prompt: %s\n", promptText)
	
	if len(promptIDs) > 0 && len(promptIDs) < cfg.MaxSeqLen {
		fmt.Println("Generating 5 new tokens...")
		generated, err := m.Generate(promptIDs, 5, 1.0)
		if err != nil {
			log.Printf("Generation failed: %v", err)
		} else {
			generatedText := tok.Decode(generated, false)
			fmt.Printf("Generated: %s\n", generatedText)
		}
	}
	
	// Run benchmarks
	fmt.Println("\n--- Running Benchmarks ---")
	benchmark.PrintSystemInfo()
	
	bench, err := benchmark.NewModelBenchmark(cfg)
	if err != nil {
		log.Fatalf("Failed to create benchmark: %v", err)
	}
	
	results := bench.RunAll()
	benchmark.PrintResults(results)
	
	// Save configuration
	fmt.Println("\n--- Saving Configuration ---")
	configFile := "model_config.json"
	if err := cfg.SaveToFile(configFile); err != nil {
		log.Printf("Failed to save config: %v", err)
	} else {
		fmt.Printf("Configuration saved to %s\n", configFile)
	}
	
	// Save tokenizer vocabulary
	vocabFile := "tokenizer_vocab.json"
	if err := tok.SaveVocab(vocabFile); err != nil {
		log.Printf("Failed to save vocabulary: %v", err)
	} else {
		fmt.Printf("Vocabulary saved to %s\n", vocabFile)
	}
	
	fmt.Println("\n========================================")
	fmt.Println("Example completed successfully!")
}
