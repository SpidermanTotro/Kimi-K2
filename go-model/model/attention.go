package model

import "math"

// MultiHeadAttention implements the multi-head attention mechanism
type MultiHeadAttention struct {
	NumHeads   int
	HiddenSize int
	HeadDim    int

	// Linear projections for Q, K, V and output
	QueryWeight *Tensor // [hidden_size, hidden_size]
	KeyWeight   *Tensor // [hidden_size, hidden_size]
	ValueWeight *Tensor // [hidden_size, hidden_size]
	OutWeight   *Tensor // [hidden_size, hidden_size]

	DropoutProb float64
}

// NewMultiHeadAttention creates a new multi-head attention layer
func NewMultiHeadAttention(hiddenSize, numHeads int, dropoutProb float64) *MultiHeadAttention {
	if hiddenSize%numHeads != 0 {
		panic("hidden size must be divisible by number of heads")
	}

	headDim := hiddenSize / numHeads

	// Initialize weight matrices with small random values
	// In production, proper initialization (e.g., Xavier/He) should be used
	queryWeight := NewTensor(hiddenSize, hiddenSize)
	keyWeight := NewTensor(hiddenSize, hiddenSize)
	valueWeight := NewTensor(hiddenSize, hiddenSize)
	outWeight := NewTensor(hiddenSize, hiddenSize)

	// Simple initialization (normally distributed around 0)
	scale := math.Sqrt(1.0 / float64(hiddenSize))
	for i := range queryWeight.Data {
		queryWeight.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
		keyWeight.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
		valueWeight.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
		outWeight.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
	}

	return &MultiHeadAttention{
		NumHeads:    numHeads,
		HiddenSize:  hiddenSize,
		HeadDim:     headDim,
		QueryWeight: queryWeight,
		KeyWeight:   keyWeight,
		ValueWeight: valueWeight,
		OutWeight:   outWeight,
		DropoutProb: dropoutProb,
	}
}

// Forward performs the multi-head attention computation
// Input shape: [seq_len, hidden_size]
// Output shape: [seq_len, hidden_size]
func (mha *MultiHeadAttention) Forward(input *Tensor) *Tensor {
	if len(input.Shape) != 2 {
		panic("MultiHeadAttention expects 2D input [seq_len, hidden_size]")
	}

	seqLen := input.Shape[0]

	// Linear projections: Q = input * W_q, K = input * W_k, V = input * W_v
	query := input.MatMul(mha.QueryWeight)
	key := input.MatMul(mha.KeyWeight)
	value := input.MatMul(mha.ValueWeight)

	// Reshape for multi-head: [seq_len, hidden_size] -> [num_heads, seq_len, head_dim]
	// For simplification, we'll process heads sequentially
	outputs := make([]*Tensor, mha.NumHeads)

	for h := 0; h < mha.NumHeads; h++ {
		// Extract head-specific Q, K, V
		headQuery := mha.extractHead(query, h, seqLen)
		headKey := mha.extractHead(key, h, seqLen)
		headValue := mha.extractHead(value, h, seqLen)

		// Compute attention scores: Q * K^T / sqrt(head_dim)
		// headQuery: [seq_len, head_dim], headKey^T: [head_dim, seq_len]
		keyTransposed := headKey.Transpose()
		scores := headQuery.MatMul(keyTransposed) // [seq_len, seq_len]

		// Scale scores
		scale := 1.0 / math.Sqrt(float64(mha.HeadDim))
		scores = scores.Scale(scale)

		// Apply softmax to get attention weights
		attentionWeights := scores.Softmax()

		// Apply attention to values: attention_weights * V
		// [seq_len, seq_len] * [seq_len, head_dim] -> [seq_len, head_dim]
		headOutput := attentionWeights.MatMul(headValue)

		outputs[h] = headOutput
	}

	// Concatenate heads: [num_heads, seq_len, head_dim] -> [seq_len, hidden_size]
	concatenated := mha.concatenateHeads(outputs, seqLen)

	// Final linear projection
	output := concatenated.MatMul(mha.OutWeight)

	return output
}

// extractHead extracts the portion of the tensor for a specific attention head
func (mha *MultiHeadAttention) extractHead(tensor *Tensor, headIdx, seqLen int) *Tensor {
	headTensor := NewTensor(seqLen, mha.HeadDim)

	for s := 0; s < seqLen; s++ {
		for d := 0; d < mha.HeadDim; d++ {
			srcIdx := s*mha.HiddenSize + headIdx*mha.HeadDim + d
			dstIdx := s*mha.HeadDim + d
			headTensor.Data[dstIdx] = tensor.Data[srcIdx]
		}
	}

	return headTensor
}

// concatenateHeads merges outputs from all attention heads
func (mha *MultiHeadAttention) concatenateHeads(heads []*Tensor, seqLen int) *Tensor {
	output := NewTensor(seqLen, mha.HiddenSize)

	for h := 0; h < mha.NumHeads; h++ {
		for s := 0; s < seqLen; s++ {
			for d := 0; d < mha.HeadDim; d++ {
				srcIdx := s*mha.HeadDim + d
				dstIdx := s*mha.HiddenSize + h*mha.HeadDim + d
				output.Data[dstIdx] = heads[h].Data[srcIdx]
			}
		}
	}

	return output
}
