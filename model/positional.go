package model

import (
	"math"
)

// PositionalEncoding generates sinusoidal positional encodings
type PositionalEncoding struct {
	MaxSeqLength int
	HiddenSize   int
	Encodings    [][]float64
}

// NewPositionalEncoding creates a new positional encoding layer
func NewPositionalEncoding(maxSeqLength, hiddenSize int) *PositionalEncoding {
	pe := &PositionalEncoding{
		MaxSeqLength: maxSeqLength,
		HiddenSize:   hiddenSize,
		Encodings:    make([][]float64, maxSeqLength),
	}

	// Pre-compute positional encodings
	for pos := 0; pos < maxSeqLength; pos++ {
		pe.Encodings[pos] = make([]float64, hiddenSize)
		for i := 0; i < hiddenSize; i++ {
			if i%2 == 0 {
				// Even dimensions: sin
				pe.Encodings[pos][i] = math.Sin(float64(pos) / math.Pow(10000.0, float64(i)/float64(hiddenSize)))
			} else {
				// Odd dimensions: cos
				pe.Encodings[pos][i] = math.Cos(float64(pos) / math.Pow(10000.0, float64(i-1)/float64(hiddenSize)))
			}
		}
	}

	return pe
}

// Forward adds positional encodings to the input
func (pe *PositionalEncoding) Forward(input [][]float64) [][]float64 {
	seqLen := len(input)
	if seqLen > pe.MaxSeqLength {
		seqLen = pe.MaxSeqLength
	}

	output := make([][]float64, len(input))
	for i := 0; i < seqLen; i++ {
		output[i] = AddVectors(input[i], pe.Encodings[i])
	}
	return output
}
