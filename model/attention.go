package model

import (
	"math"
)

// MultiHeadAttention implements multi-head self-attention mechanism
type MultiHeadAttention struct {
	NumHeads   int
	HeadDim    int
	HiddenSize int

	// Weight matrices for Q, K, V projections
	WQ Matrix
	WK Matrix
	WV Matrix
	WO Matrix // Output projection

	// Bias vectors
	BQ []float64
	BK []float64
	BV []float64
	BO []float64
}

// NewMultiHeadAttention creates a new multi-head attention layer
func NewMultiHeadAttention(hiddenSize, numHeads int) *MultiHeadAttention {
	headDim := hiddenSize / numHeads
	return &MultiHeadAttention{
		NumHeads:   numHeads,
		HeadDim:    headDim,
		HiddenSize: hiddenSize,
		WQ:         NewMatrix(hiddenSize, hiddenSize),
		WK:         NewMatrix(hiddenSize, hiddenSize),
		WV:         NewMatrix(hiddenSize, hiddenSize),
		WO:         NewMatrix(hiddenSize, hiddenSize),
		BQ:         make([]float64, hiddenSize),
		BK:         make([]float64, hiddenSize),
		BV:         make([]float64, hiddenSize),
		BO:         make([]float64, hiddenSize),
	}
}

// Forward performs the forward pass of multi-head attention
// input: [seqLen][hiddenSize]
func (mha *MultiHeadAttention) Forward(input [][]float64, mask [][]float64) [][]float64 {
	seqLen := len(input)
	if seqLen == 0 {
		return nil
	}

	// Project to Q, K, V
	Q := make([][]float64, seqLen)
	K := make([][]float64, seqLen)
	V := make([][]float64, seqLen)

	for i := 0; i < seqLen; i++ {
		Q[i] = AddVectors(VectorMatMul(input[i], mha.WQ), mha.BQ)
		K[i] = AddVectors(VectorMatMul(input[i], mha.WK), mha.BK)
		V[i] = AddVectors(VectorMatMul(input[i], mha.WV), mha.BV)
	}

	// Split into heads and compute attention
	output := make([][]float64, seqLen)
	for i := range output {
		output[i] = make([]float64, mha.HiddenSize)
	}

	// Process each head
	for h := 0; h < mha.NumHeads; h++ {
		startIdx := h * mha.HeadDim
		endIdx := (h + 1) * mha.HeadDim

		// Extract head-specific Q, K, V
		headQ := make([][]float64, seqLen)
		headK := make([][]float64, seqLen)
		headV := make([][]float64, seqLen)

		for i := 0; i < seqLen; i++ {
			headQ[i] = Q[i][startIdx:endIdx]
			headK[i] = K[i][startIdx:endIdx]
			headV[i] = V[i][startIdx:endIdx]
		}

		// Compute attention scores
		scores := NewMatrix(seqLen, seqLen)
		scaleFactor := 1.0 / math.Sqrt(float64(mha.HeadDim))

		for i := 0; i < seqLen; i++ {
			for j := 0; j < seqLen; j++ {
				// Dot product between Q[i] and K[j]
				dot := 0.0
				for k := 0; k < mha.HeadDim; k++ {
					dot += headQ[i][k] * headK[j][k]
				}
				scores[i][j] = dot * scaleFactor

				// Apply mask if provided
				if mask != nil && mask[i][j] == 0 {
					scores[i][j] = -1e9
				}
			}
		}

		// Apply softmax to get attention weights
		attnWeights := make([][]float64, seqLen)
		for i := 0; i < seqLen; i++ {
			attnWeights[i] = Softmax(scores[i])
		}

		// Weighted sum of values
		for i := 0; i < seqLen; i++ {
			headOutput := make([]float64, mha.HeadDim)
			for j := 0; j < seqLen; j++ {
				for k := 0; k < mha.HeadDim; k++ {
					headOutput[k] += attnWeights[i][j] * headV[j][k]
				}
			}
			// Copy to output
			copy(output[i][startIdx:endIdx], headOutput)
		}
	}

	// Final output projection
	result := make([][]float64, seqLen)
	for i := 0; i < seqLen; i++ {
		result[i] = AddVectors(VectorMatMul(output[i], mha.WO), mha.BO)
	}

	return result
}
