package model

import (
	"math"
	"testing"
)

func TestLayerNorm(t *testing.T) {
	hiddenSize := 4
	ln := NewLayerNorm(hiddenSize, 1e-5)

	// Test input: [2, 4] (2 sequences, 4 features each)
	input := NewTensor(2, 4)
	input.Data = []float64{
		1.0, 2.0, 3.0, 4.0, // First sequence
		2.0, 4.0, 6.0, 8.0, // Second sequence
	}

	output := ln.Forward(input)

	// Check output shape
	if len(output.Shape) != 2 || output.Shape[0] != 2 || output.Shape[1] != 4 {
		t.Errorf("expected shape [2, 4], got %v", output.Shape)
	}

	// Check that each sequence is normalized (mean ≈ 0, variance ≈ 1)
	for seq := 0; seq < 2; seq++ {
		start := seq * hiddenSize
		mean := 0.0
		for i := 0; i < hiddenSize; i++ {
			mean += output.Data[start+i]
		}
		mean /= float64(hiddenSize)

		if math.Abs(mean) > 1e-5 {
			t.Errorf("sequence %d: expected mean ~0, got %f", seq, mean)
		}

		variance := 0.0
		for i := 0; i < hiddenSize; i++ {
			diff := output.Data[start+i] - mean
			variance += diff * diff
		}
		variance /= float64(hiddenSize)

		if math.Abs(variance-1.0) > 0.3 {
			t.Errorf("sequence %d: expected variance ~1, got %f", seq, variance)
		}
	}
}

func TestLayerNormGammaAndBeta(t *testing.T) {
	hiddenSize := 4
	ln := NewLayerNorm(hiddenSize, 1e-5)

	// Verify gamma is initialized to 1
	for i := 0; i < hiddenSize; i++ {
		if ln.Gamma.Data[i] != 1.0 {
			t.Errorf("gamma[%d] should be 1.0, got %f", i, ln.Gamma.Data[i])
		}
	}

	// Verify beta is initialized to 0
	for i := 0; i < hiddenSize; i++ {
		if ln.Beta.Data[i] != 0.0 {
			t.Errorf("beta[%d] should be 0.0, got %f", i, ln.Beta.Data[i])
		}
	}
}
