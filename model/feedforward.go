package model

// FeedForward implements the position-wise feed-forward network
type FeedForward struct {
	HiddenSize       int
	IntermediateSize int
	ActivationType   string

	// First linear transformation
	W1 Matrix
	B1 []float64

	// Second linear transformation
	W2 Matrix
	B2 []float64
}

// NewFeedForward creates a new feed-forward network
func NewFeedForward(hiddenSize, intermediateSize int, activationType string) *FeedForward {
	return &FeedForward{
		HiddenSize:       hiddenSize,
		IntermediateSize: intermediateSize,
		ActivationType:   activationType,
		W1:               NewMatrix(hiddenSize, intermediateSize),
		B1:               make([]float64, intermediateSize),
		W2:               NewMatrix(intermediateSize, hiddenSize),
		B2:               make([]float64, hiddenSize),
	}
}

// Forward performs the forward pass of the feed-forward network
func (ff *FeedForward) Forward(input []float64) []float64 {
	// First linear transformation
	hidden := AddVectors(VectorMatMul(input, ff.W1), ff.B1)

	// Apply activation function
	for i := range hidden {
		switch ff.ActivationType {
		case "gelu":
			hidden[i] = GELU(hidden[i])
		default:
			hidden[i] = GELU(hidden[i])
		}
	}

	// Second linear transformation
	output := AddVectors(VectorMatMul(hidden, ff.W2), ff.B2)
	return output
}
