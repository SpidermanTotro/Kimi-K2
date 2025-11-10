package model

import (
	"testing"
)

func TestTransformerBlock(t *testing.T) {
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

	block := NewTransformerBlock(config)

	// Test forward pass
	seqLen := 3
	input := NewTensor(seqLen, config.HiddenSize)
	for i := range input.Data {
		input.Data[i] = float64(i%10) / 10.0
	}

	output := block.Forward(input)

	// Check output shape matches input shape
	if len(output.Shape) != len(input.Shape) {
		t.Errorf("output shape dimension mismatch")
	}
	for i := range output.Shape {
		if output.Shape[i] != input.Shape[i] {
			t.Errorf("output shape mismatch at dimension %d", i)
		}
	}

	// Output should not be all zeros
	allZeros := true
	for _, v := range output.Data {
		if v != 0 {
			allZeros = false
			break
		}
	}

	if allZeros {
		t.Errorf("transformer block output should not be all zeros")
	}
}

func TestTransformerBlockResidualConnections(t *testing.T) {
	config := &Config{
		VocabSize:      1000,
		HiddenSize:     64,
		NumLayers:      1,
		NumHeads:       8,
		FFNHiddenSize:  256,
		MaxSeqLen:      128,
		DropoutProb:    0.0, // No dropout for testing
		EpsilonLN:      1e-12,
		UsePositionEnc: true,
	}

	block := NewTransformerBlock(config)

	seqLen := 2
	input := NewTensor(seqLen, config.HiddenSize)
	for i := range input.Data {
		input.Data[i] = 1.0
	}

	output := block.Forward(input)

	// Due to residual connections, output should be significantly influenced by input
	// We can't test exact values due to random initialization, but output should not be zero
	hasNonZero := false
	for _, v := range output.Data {
		if v != 0 {
			hasNonZero = true
			break
		}
	}

	if !hasNonZero {
		t.Errorf("transformer block output should have non-zero values due to residual connections")
	}
}
