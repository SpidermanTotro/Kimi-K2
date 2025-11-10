package model

import "math"

// FeedForward implements the position-wise feed-forward network
type FeedForward struct {
	HiddenSize    int
	FFNHiddenSize int

	// Linear layers
	Weight1 *Tensor // [hidden_size, ffn_hidden_size]
	Bias1   *Tensor // [ffn_hidden_size]
	Weight2 *Tensor // [ffn_hidden_size, hidden_size]
	Bias2   *Tensor // [hidden_size]

	DropoutProb float64
}

// NewFeedForward creates a new feed-forward network layer
func NewFeedForward(hiddenSize, ffnHiddenSize int, dropoutProb float64) *FeedForward {
	// Initialize weights and biases
	weight1 := NewTensor(hiddenSize, ffnHiddenSize)
	bias1 := NewTensor(ffnHiddenSize)
	weight2 := NewTensor(ffnHiddenSize, hiddenSize)
	bias2 := NewTensor(hiddenSize)

	// Simple initialization
	scale1 := math.Sqrt(1.0 / float64(hiddenSize))
	scale2 := math.Sqrt(1.0 / float64(ffnHiddenSize))

	for i := range weight1.Data {
		weight1.Data[i] = (float64(i%100)/100.0 - 0.5) * scale1
	}
	for i := range weight2.Data {
		weight2.Data[i] = (float64(i%100)/100.0 - 0.5) * scale2
	}

	// Biases initialized to zero
	for i := range bias1.Data {
		bias1.Data[i] = 0.0
	}
	for i := range bias2.Data {
		bias2.Data[i] = 0.0
	}

	return &FeedForward{
		HiddenSize:    hiddenSize,
		FFNHiddenSize: ffnHiddenSize,
		Weight1:       weight1,
		Bias1:         bias1,
		Weight2:       weight2,
		Bias2:         bias2,
		DropoutProb:   dropoutProb,
	}
}

// Forward applies the feed-forward network
// Input shape: [seq_len, hidden_size]
// Output shape: [seq_len, hidden_size]
func (ff *FeedForward) Forward(input *Tensor) *Tensor {
	if len(input.Shape) != 2 {
		panic("FeedForward expects 2D input [seq_len, hidden_size]")
	}

	seqLen := input.Shape[0]

	// First linear transformation: input * W1 + b1
	hidden := input.MatMul(ff.Weight1)
	hidden = ff.addBias(hidden, ff.Bias1, seqLen)

	// Apply GELU activation
	hidden = hidden.GELU()

	// Second linear transformation: hidden * W2 + b2
	output := hidden.MatMul(ff.Weight2)
	output = ff.addBias(output, ff.Bias2, seqLen)

	return output
}

// addBias adds bias to each position in the sequence
func (ff *FeedForward) addBias(input *Tensor, bias *Tensor, seqLen int) *Tensor {
	output := input.Clone()
	biasSize := len(bias.Data)

	for s := 0; s < seqLen; s++ {
		for i := 0; i < biasSize; i++ {
			output.Data[s*biasSize+i] += bias.Data[i]
		}
	}

	return output
}
