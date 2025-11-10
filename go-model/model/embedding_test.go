package model

import (
	"testing"
)

func TestEmbedding(t *testing.T) {
	vocabSize := 1000
	hiddenSize := 64

	emb := NewEmbedding(vocabSize, hiddenSize)

	// Check embedding weights shape
	if len(emb.Weights.Shape) != 2 || emb.Weights.Shape[0] != vocabSize || emb.Weights.Shape[1] != hiddenSize {
		t.Errorf("expected weights shape [%d, %d], got %v", vocabSize, hiddenSize, emb.Weights.Shape)
	}

	// Test forward pass
	tokenIDs := []int{0, 1, 2, 3, 4}
	output := emb.Forward(tokenIDs)

	// Check output shape
	expectedShape := []int{len(tokenIDs), hiddenSize}
	if len(output.Shape) != 2 || output.Shape[0] != expectedShape[0] || output.Shape[1] != expectedShape[1] {
		t.Errorf("expected output shape %v, got %v", expectedShape, output.Shape)
	}

	// Check that embeddings are different for different tokens
	emb0 := output.Data[0*hiddenSize : 1*hiddenSize]
	emb1 := output.Data[1*hiddenSize : 2*hiddenSize]

	allSame := true
	for i := 0; i < hiddenSize; i++ {
		if emb0[i] != emb1[i] {
			allSame = false
			break
		}
	}

	if allSame {
		t.Errorf("embeddings for different tokens should be different")
	}
}

func TestEmbeddingOutOfRange(t *testing.T) {
	vocabSize := 100
	hiddenSize := 64

	emb := NewEmbedding(vocabSize, hiddenSize)

	defer func() {
		if r := recover(); r == nil {
			t.Errorf("expected panic for out of range token ID")
		}
	}()

	// This should panic
	emb.Forward([]int{0, 1, 100}) // 100 is out of range
}

func TestEmbeddingConsistency(t *testing.T) {
	vocabSize := 100
	hiddenSize := 64

	emb := NewEmbedding(vocabSize, hiddenSize)

	// Get embedding for token 5
	output1 := emb.Forward([]int{5})
	output2 := emb.Forward([]int{5})

	// Should be identical
	for i := 0; i < hiddenSize; i++ {
		if output1.Data[i] != output2.Data[i] {
			t.Errorf("embedding should be consistent across calls")
			break
		}
	}
}
