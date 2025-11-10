package model

import (
	"testing"
)

func TestMultiHeadAttention(t *testing.T) {
	hiddenSize := 64
	numHeads := 8
	seqLen := 4

	mha := NewMultiHeadAttention(hiddenSize, numHeads, 0.1)

	// Check head dimension
	expectedHeadDim := hiddenSize / numHeads
	if mha.HeadDim != expectedHeadDim {
		t.Errorf("expected head dim %d, got %d", expectedHeadDim, mha.HeadDim)
	}

	// Test forward pass
	input := NewTensor(seqLen, hiddenSize)
	for i := range input.Data {
		input.Data[i] = float64(i%10) / 10.0
	}

	output := mha.Forward(input)

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
		t.Errorf("attention output should not be all zeros")
	}
}

func TestMultiHeadAttentionInvalidConfig(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Errorf("expected panic for invalid configuration")
		}
	}()

	// This should panic because hidden size is not divisible by num heads
	NewMultiHeadAttention(65, 8, 0.1)
}

func TestAttentionExtractHead(t *testing.T) {
	hiddenSize := 64
	numHeads := 8
	seqLen := 3

	mha := NewMultiHeadAttention(hiddenSize, numHeads, 0.1)

	// Create test tensor
	tensor := NewTensor(seqLen, hiddenSize)
	for i := range tensor.Data {
		tensor.Data[i] = float64(i)
	}

	// Extract first head
	head := mha.extractHead(tensor, 0, seqLen)

	// Check shape
	if len(head.Shape) != 2 || head.Shape[0] != seqLen || head.Shape[1] != mha.HeadDim {
		t.Errorf("expected head shape [%d, %d], got %v", seqLen, mha.HeadDim, head.Shape)
	}
}

func TestAttentionConcatenateHeads(t *testing.T) {
	hiddenSize := 64
	numHeads := 8
	seqLen := 3

	mha := NewMultiHeadAttention(hiddenSize, numHeads, 0.1)

	// Create test heads
	heads := make([]*Tensor, numHeads)
	for h := 0; h < numHeads; h++ {
		heads[h] = NewTensor(seqLen, mha.HeadDim)
		for i := range heads[h].Data {
			heads[h].Data[i] = float64(h*100 + i)
		}
	}

	// Concatenate
	concat := mha.concatenateHeads(heads, seqLen)

	// Check shape
	if len(concat.Shape) != 2 || concat.Shape[0] != seqLen || concat.Shape[1] != hiddenSize {
		t.Errorf("expected concatenated shape [%d, %d], got %v", seqLen, hiddenSize, concat.Shape)
	}
}
