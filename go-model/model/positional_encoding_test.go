package model

import (
	"math"
	"testing"
)

func TestPositionalEncoding(t *testing.T) {
	maxSeqLen := 10
	hiddenSize := 8
	pe := NewPositionalEncoding(maxSeqLen, hiddenSize)

	// Check that encoding tensor has correct shape
	if len(pe.Encoding.Shape) != 2 || pe.Encoding.Shape[0] != maxSeqLen || pe.Encoding.Shape[1] != hiddenSize {
		t.Errorf("expected encoding shape [%d, %d], got %v", maxSeqLen, hiddenSize, pe.Encoding.Shape)
	}

	// Check that positional encodings are different for different positions
	pos0 := pe.Encoding.Data[0*hiddenSize : 1*hiddenSize]
	pos1 := pe.Encoding.Data[1*hiddenSize : 2*hiddenSize]

	allSame := true
	for i := 0; i < hiddenSize; i++ {
		if math.Abs(pos0[i]-pos1[i]) > 1e-6 {
			allSame = false
			break
		}
	}

	if allSame {
		t.Errorf("positional encodings should be different for different positions")
	}

	// Check that encodings use sin for even indices and cos for odd indices
	// At position 0, even indices should be sin(0) = 0, odd should be cos(0) = 1
	for i := 0; i < hiddenSize; i++ {
		if i%2 == 0 {
			// Even index: sin(0) = 0
			if math.Abs(pe.Encoding.Data[i]) > 1e-6 {
				t.Errorf("even index %d at position 0 should be ~0, got %f", i, pe.Encoding.Data[i])
			}
		} else {
			// Odd index: cos(0) = 1
			if math.Abs(pe.Encoding.Data[i]-1.0) > 1e-6 {
				t.Errorf("odd index %d at position 0 should be ~1, got %f", i, pe.Encoding.Data[i])
			}
		}
	}
}

func TestPositionalEncodingForward(t *testing.T) {
	maxSeqLen := 10
	hiddenSize := 8
	pe := NewPositionalEncoding(maxSeqLen, hiddenSize)

	// Test 2D input
	input := NewTensor(3, hiddenSize)
	for i := range input.Data {
		input.Data[i] = 1.0
	}

	output := pe.Forward(input)

	// Check that output shape matches input shape
	if len(output.Shape) != len(input.Shape) {
		t.Errorf("output shape dimension mismatch")
	}
	for i := range output.Shape {
		if output.Shape[i] != input.Shape[i] {
			t.Errorf("output shape mismatch at dimension %d", i)
		}
	}

	// Check that positional encoding was added (values should differ from input)
	allSame := true
	for i := range output.Data {
		if math.Abs(output.Data[i]-input.Data[i]) > 1e-6 {
			allSame = false
			break
		}
	}

	if allSame {
		t.Errorf("positional encoding should modify the input")
	}
}

func TestPositionalEncoding3D(t *testing.T) {
	maxSeqLen := 10
	hiddenSize := 8
	batchSize := 2
	seqLen := 3

	pe := NewPositionalEncoding(maxSeqLen, hiddenSize)

	// Test 3D input [batch_size, seq_len, hidden_size]
	input := NewTensor(batchSize, seqLen, hiddenSize)
	for i := range input.Data {
		input.Data[i] = 1.0
	}

	output := pe.Forward(input)

	// Check output shape
	if len(output.Shape) != 3 {
		t.Errorf("expected 3D output")
	}
	if output.Shape[0] != batchSize || output.Shape[1] != seqLen || output.Shape[2] != hiddenSize {
		t.Errorf("output shape mismatch")
	}

	// The positional encoding should be the same for the same position across different batches
	for s := 0; s < seqLen; s++ {
		for h := 0; h < hiddenSize; h++ {
			val0 := output.Data[0*seqLen*hiddenSize+s*hiddenSize+h] - input.Data[0*seqLen*hiddenSize+s*hiddenSize+h]
			val1 := output.Data[1*seqLen*hiddenSize+s*hiddenSize+h] - input.Data[1*seqLen*hiddenSize+s*hiddenSize+h]

			if math.Abs(val0-val1) > 1e-6 {
				t.Errorf("positional encoding should be the same across batches")
			}
		}
	}
}
