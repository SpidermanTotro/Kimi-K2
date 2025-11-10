package model

import (
	"testing"
)

func TestTransformerCreation(t *testing.T) {
	config := NewDefaultConfig()

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	// Check that model has correct number of layers
	if len(model.Blocks) != config.NumLayers {
		t.Errorf("expected %d transformer blocks, got %d", config.NumLayers, len(model.Blocks))
	}

	// Check that model has 16 layers as specified
	if len(model.Blocks) != 16 {
		t.Errorf("expected 16 transformer blocks, got %d", len(model.Blocks))
	}
}

func TestTransformerForward(t *testing.T) {
	config := &Config{
		VocabSize:      1000,
		HiddenSize:     64,
		NumLayers:      4, // Smaller for faster testing
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      128,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	// Test forward pass
	tokenIDs := []int{1, 2, 3, 4, 5}
	output := model.Forward(tokenIDs)

	// Check output shape: [seq_len, vocab_size]
	expectedShape := []int{len(tokenIDs), config.VocabSize}
	if len(output.Shape) != 2 || output.Shape[0] != expectedShape[0] || output.Shape[1] != expectedShape[1] {
		t.Errorf("expected output shape %v, got %v", expectedShape, output.Shape)
	}
}

func TestTransformerPredict(t *testing.T) {
	config := &Config{
		VocabSize:      1000,
		HiddenSize:     64,
		NumLayers:      2,
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      128,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	// Test prediction
	tokenIDs := []int{1, 2, 3}
	probs := model.Predict(tokenIDs)

	// Check that we get a probability distribution
	if probs.Size() != config.VocabSize {
		t.Errorf("expected probability vector of size %d, got %d", config.VocabSize, probs.Size())
	}

	// Check that probabilities sum to approximately 1
	sum := 0.0
	for _, p := range probs.Data {
		sum += p
	}

	if sum < 0.99 || sum > 1.01 {
		t.Errorf("probabilities should sum to ~1, got %f", sum)
	}

	// Check that all probabilities are non-negative
	for i, p := range probs.Data {
		if p < 0 {
			t.Errorf("probability at index %d is negative: %f", i, p)
		}
	}
}

func TestTransformerGetTopK(t *testing.T) {
	config := &Config{
		VocabSize:      100,
		HiddenSize:     32,
		NumLayers:      2,
		NumHeads:       4,
		FFNHiddenSize:  128,
		MaxSeqLen:      64,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	// Create a simple probability distribution
	probs := NewTensor(config.VocabSize)
	for i := 0; i < config.VocabSize; i++ {
		probs.Data[i] = float64(i) / 100.0
	}

	// Get top 5
	topK := model.GetTopK(probs, 5)

	if len(topK) != 5 {
		t.Errorf("expected 5 top tokens, got %d", len(topK))
	}

	// Check that they are in descending order of probability
	for i := 1; i < len(topK); i++ {
		if probs.Data[topK[i]] > probs.Data[topK[i-1]] {
			t.Errorf("top-k tokens should be in descending order of probability")
		}
	}
}

func TestTransformerNumParameters(t *testing.T) {
	config := &Config{
		VocabSize:      1000,
		HiddenSize:     64,
		NumLayers:      2,
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      128,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	numParams := model.NumParameters()

	// Should have a positive number of parameters
	if numParams <= 0 {
		t.Errorf("model should have positive number of parameters, got %d", numParams)
	}

	// Rough sanity check: should have at least embedding parameters
	minExpected := config.VocabSize * config.HiddenSize
	if numParams < minExpected {
		t.Errorf("expected at least %d parameters (embeddings alone), got %d", minExpected, numParams)
	}
}

func TestTransformerInvalidConfig(t *testing.T) {
	config := &Config{
		VocabSize:      -1, // Invalid
		HiddenSize:     64,
		NumLayers:      16,
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      128,
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	_, err := NewTransformer(config)
	if err == nil {
		t.Errorf("expected error for invalid config, got none")
	}
}

func TestTransformerSequenceTooLong(t *testing.T) {
	config := &Config{
		VocabSize:      1000,
		HiddenSize:     64,
		NumLayers:      2,
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      10, // Small max sequence length
		DropoutProb:    0.1,
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	defer func() {
		if r := recover(); r == nil {
			t.Errorf("expected panic for sequence too long")
		}
	}()

	// This should panic because sequence is longer than max_seq_len
	tokenIDs := make([]int, 20)
	for i := range tokenIDs {
		tokenIDs[i] = i % 100
	}
	model.Forward(tokenIDs)
}

func TestTransformer16Layers(t *testing.T) {
	config := NewDefaultConfig()

	model, err := NewTransformer(config)
	if err != nil {
		t.Fatalf("failed to create transformer: %v", err)
	}

	// Verify it has exactly 16 layers
	if config.NumLayers != 16 {
		t.Errorf("default config should have 16 layers, got %d", config.NumLayers)
	}

	if len(model.Blocks) != 16 {
		t.Errorf("model should have 16 transformer blocks, got %d", len(model.Blocks))
	}

	// Test that all 16 layers work
	tokenIDs := []int{1, 2, 3, 4, 5}
	output := model.Forward(tokenIDs)

	if output == nil {
		t.Errorf("16-layer model should produce output")
	}
}
