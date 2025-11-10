package model

import "math"

// LayerNorm implements layer normalization
type LayerNorm struct {
	Gamma   *Tensor // Scale parameter
	Beta    *Tensor // Shift parameter
	Epsilon float64 // Small constant for numerical stability
}

// NewLayerNorm creates a new layer normalization layer
func NewLayerNorm(size int, epsilon float64) *LayerNorm {
	gamma := NewTensor(size)
	beta := NewTensor(size)

	// Initialize gamma to 1 and beta to 0
	for i := 0; i < size; i++ {
		gamma.Data[i] = 1.0
		beta.Data[i] = 0.0
	}

	return &LayerNorm{
		Gamma:   gamma,
		Beta:    beta,
		Epsilon: epsilon,
	}
}

// Forward applies layer normalization to the input
// Input shape: [batch_size, seq_len, hidden_size] or [seq_len, hidden_size]
func (ln *LayerNorm) Forward(input *Tensor) *Tensor {
	shape := input.Shape
	if len(shape) < 2 {
		panic("LayerNorm requires at least 2D input")
	}

	normalizedSize := shape[len(shape)-1]
	output := NewTensor(shape...)

	// Calculate the number of normalization groups
	numGroups := input.Size() / normalizedSize

	for g := 0; g < numGroups; g++ {
		startIdx := g * normalizedSize

		// Calculate mean
		mean := 0.0
		for i := 0; i < normalizedSize; i++ {
			mean += input.Data[startIdx+i]
		}
		mean /= float64(normalizedSize)

		// Calculate variance
		variance := 0.0
		for i := 0; i < normalizedSize; i++ {
			diff := input.Data[startIdx+i] - mean
			variance += diff * diff
		}
		variance /= float64(normalizedSize)

		// Normalize and apply scale and shift
		std := math.Sqrt(variance + ln.Epsilon)
		for i := 0; i < normalizedSize; i++ {
			normalized := (input.Data[startIdx+i] - mean) / std
			output.Data[startIdx+i] = normalized*ln.Gamma.Data[i] + ln.Beta.Data[i]
		}
	}

	return output
}
