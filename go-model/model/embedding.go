package model

import "math"

// Embedding implements the token embedding layer
type Embedding struct {
	VocabSize  int
	HiddenSize int
	Weights    *Tensor // [vocab_size, hidden_size]
}

// NewEmbedding creates a new embedding layer
func NewEmbedding(vocabSize, hiddenSize int) *Embedding {
	weights := NewTensor(vocabSize, hiddenSize)

	// Initialize with small random values
	scale := math.Sqrt(1.0 / float64(hiddenSize))
	for i := range weights.Data {
		weights.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
	}

	return &Embedding{
		VocabSize:  vocabSize,
		HiddenSize: hiddenSize,
		Weights:    weights,
	}
}

// Forward performs the embedding lookup
// Input: token IDs [seq_len] as slice
// Output shape: [seq_len, hidden_size]
func (emb *Embedding) Forward(tokenIDs []int) *Tensor {
	seqLen := len(tokenIDs)
	output := NewTensor(seqLen, emb.HiddenSize)

	for s := 0; s < seqLen; s++ {
		tokenID := tokenIDs[s]
		if tokenID < 0 || tokenID >= emb.VocabSize {
			panic("token ID out of vocabulary range")
		}

		// Copy the embedding for this token
		for h := 0; h < emb.HiddenSize; h++ {
			output.Data[s*emb.HiddenSize+h] = emb.Weights.Data[tokenID*emb.HiddenSize+h]
		}
	}

	return output
}
