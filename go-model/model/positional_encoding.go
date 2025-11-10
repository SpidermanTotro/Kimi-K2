package model

import "math"

// PositionalEncoding implements sinusoidal positional encoding
type PositionalEncoding struct {
	MaxSeqLen  int
	HiddenSize int
	Encoding   *Tensor // Precomputed positional encodings [max_seq_len, hidden_size]
}

// NewPositionalEncoding creates a new positional encoding layer
func NewPositionalEncoding(maxSeqLen, hiddenSize int) *PositionalEncoding {
	encoding := NewTensor(maxSeqLen, hiddenSize)

	// Compute positional encodings using sinusoidal functions
	// PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
	// PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
	for pos := 0; pos < maxSeqLen; pos++ {
		for i := 0; i < hiddenSize; i++ {
			angle := float64(pos) / math.Pow(10000.0, float64(2*i)/float64(hiddenSize))
			if i%2 == 0 {
				encoding.Data[pos*hiddenSize+i] = math.Sin(angle)
			} else {
				encoding.Data[pos*hiddenSize+i] = math.Cos(angle)
			}
		}
	}

	return &PositionalEncoding{
		MaxSeqLen:  maxSeqLen,
		HiddenSize: hiddenSize,
		Encoding:   encoding,
	}
}

// Forward adds positional encoding to the input embeddings
// Input shape: [batch_size, seq_len, hidden_size] or [seq_len, hidden_size]
func (pe *PositionalEncoding) Forward(input *Tensor) *Tensor {
	shape := input.Shape
	var seqLen int

	if len(shape) == 3 {
		// [batch_size, seq_len, hidden_size]
		seqLen = shape[1]
	} else if len(shape) == 2 {
		// [seq_len, hidden_size]
		seqLen = shape[0]
	} else {
		panic("PositionalEncoding requires 2D or 3D input")
	}

	if seqLen > pe.MaxSeqLen {
		panic("sequence length exceeds maximum sequence length")
	}

	output := input.Clone()

	if len(shape) == 3 {
		// 3D case: [batch_size, seq_len, hidden_size]
		batchSize, seqLen, hiddenSize := shape[0], shape[1], shape[2]
		for b := 0; b < batchSize; b++ {
			for s := 0; s < seqLen; s++ {
				for h := 0; h < hiddenSize; h++ {
					idx := b*seqLen*hiddenSize + s*hiddenSize + h
					output.Data[idx] += pe.Encoding.Data[s*hiddenSize+h]
				}
			}
		}
	} else {
		// 2D case: [seq_len, hidden_size]
		seqLen, hiddenSize := shape[0], shape[1]
		for s := 0; s < seqLen; s++ {
			for h := 0; h < hiddenSize; h++ {
				idx := s*hiddenSize + h
				output.Data[idx] += pe.Encoding.Data[idx]
			}
		}
	}

	return output
}
