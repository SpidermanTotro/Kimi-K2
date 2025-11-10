package model

import (
	"testing"
)

func TestFeedForward(t *testing.T) {
	hiddenSize := 64
	ffnHiddenSize := 256
	seqLen := 3

	ff := NewFeedForward(hiddenSize, ffnHiddenSize, 0.1)

	// Test forward pass
	input := NewTensor(seqLen, hiddenSize)
	for i := range input.Data {
		input.Data[i] = float64(i%10) / 10.0
	}

	output := ff.Forward(input)

	// Check output shape
	if len(output.Shape) != 2 || output.Shape[0] != seqLen || output.Shape[1] != hiddenSize {
		t.Errorf("expected output shape [%d, %d], got %v", seqLen, hiddenSize, output.Shape)
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
		t.Errorf("feed-forward output should not be all zeros")
	}
}

func TestFeedForwardBiasShape(t *testing.T) {
	hiddenSize := 64
	ffnHiddenSize := 256

	ff := NewFeedForward(hiddenSize, ffnHiddenSize, 0.1)

	// Check bias shapes
	if ff.Bias1.Size() != ffnHiddenSize {
		t.Errorf("expected bias1 size %d, got %d", ffnHiddenSize, ff.Bias1.Size())
	}

	if ff.Bias2.Size() != hiddenSize {
		t.Errorf("expected bias2 size %d, got %d", hiddenSize, ff.Bias2.Size())
	}
}
