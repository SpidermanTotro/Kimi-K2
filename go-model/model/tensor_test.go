package model

import (
	"math"
	"testing"
)

func TestTensorCreation(t *testing.T) {
	tensor := NewTensor(3, 4)

	if len(tensor.Shape) != 2 {
		t.Errorf("expected 2D tensor, got %dD", len(tensor.Shape))
	}

	if tensor.Shape[0] != 3 || tensor.Shape[1] != 4 {
		t.Errorf("expected shape [3, 4], got %v", tensor.Shape)
	}

	if tensor.Size() != 12 {
		t.Errorf("expected size 12, got %d", tensor.Size())
	}
}

func TestTensorAdd(t *testing.T) {
	t1 := NewTensor(2, 2)
	t2 := NewTensor(2, 2)

	t1.Data = []float64{1, 2, 3, 4}
	t2.Data = []float64{5, 6, 7, 8}

	result := t1.Add(t2)

	expected := []float64{6, 8, 10, 12}
	for i, v := range result.Data {
		if v != expected[i] {
			t.Errorf("at index %d: expected %f, got %f", i, expected[i], v)
		}
	}
}

func TestTensorMultiply(t *testing.T) {
	t1 := NewTensor(2, 2)
	t2 := NewTensor(2, 2)

	t1.Data = []float64{1, 2, 3, 4}
	t2.Data = []float64{2, 3, 4, 5}

	result := t1.Multiply(t2)

	expected := []float64{2, 6, 12, 20}
	for i, v := range result.Data {
		if v != expected[i] {
			t.Errorf("at index %d: expected %f, got %f", i, expected[i], v)
		}
	}
}

func TestTensorScale(t *testing.T) {
	tensor := NewTensor(2, 2)
	tensor.Data = []float64{1, 2, 3, 4}

	result := tensor.Scale(2.0)

	expected := []float64{2, 4, 6, 8}
	for i, v := range result.Data {
		if v != expected[i] {
			t.Errorf("at index %d: expected %f, got %f", i, expected[i], v)
		}
	}
}

func TestTensorMean(t *testing.T) {
	tensor := NewTensor(4)
	tensor.Data = []float64{1, 2, 3, 4}

	mean := tensor.Mean()

	expected := 2.5
	if mean != expected {
		t.Errorf("expected mean %f, got %f", expected, mean)
	}
}

func TestTensorMatMul(t *testing.T) {
	// Test matrix multiplication: [2, 3] x [3, 2] -> [2, 2]
	t1 := NewTensor(2, 3)
	t2 := NewTensor(3, 2)

	t1.Data = []float64{1, 2, 3, 4, 5, 6}
	t2.Data = []float64{7, 8, 9, 10, 11, 12}

	result := t1.MatMul(t2)

	if len(result.Shape) != 2 || result.Shape[0] != 2 || result.Shape[1] != 2 {
		t.Errorf("expected shape [2, 2], got %v", result.Shape)
	}

	// Manual calculation:
	// [1, 2, 3]   [7, 8]     [58, 64]
	// [4, 5, 6] x [9, 10] =  [139, 154]
	//             [11, 12]
	expected := []float64{58, 64, 139, 154}
	for i, v := range result.Data {
		if v != expected[i] {
			t.Errorf("at index %d: expected %f, got %f", i, expected[i], v)
		}
	}
}

func TestTensorSoftmax(t *testing.T) {
	tensor := NewTensor(3)
	tensor.Data = []float64{1.0, 2.0, 3.0}

	result := tensor.Softmax()

	// Check that probabilities sum to 1
	sum := 0.0
	for _, v := range result.Data {
		sum += v
	}

	if math.Abs(sum-1.0) > 1e-6 {
		t.Errorf("softmax probabilities should sum to 1, got %f", sum)
	}

	// Check that all probabilities are positive
	for i, v := range result.Data {
		if v <= 0 {
			t.Errorf("at index %d: softmax probability should be positive, got %f", i, v)
		}
	}

	// Check that probabilities are in increasing order for increasing inputs
	for i := 1; i < len(result.Data); i++ {
		if result.Data[i] <= result.Data[i-1] {
			t.Errorf("softmax probabilities should increase with inputs")
		}
	}
}

func TestTensorGELU(t *testing.T) {
	tensor := NewTensor(3)
	tensor.Data = []float64{-1.0, 0.0, 1.0}

	result := tensor.GELU()

	// GELU(0) should be approximately 0
	if math.Abs(result.Data[1]) > 1e-6 {
		t.Errorf("GELU(0) should be ~0, got %f", result.Data[1])
	}

	// For positive input, GELU should be positive
	if result.Data[2] <= 0 {
		t.Errorf("GELU(1) should be positive, got %f", result.Data[2])
	}

	// For negative input, GELU should be negative
	if result.Data[0] >= 0 {
		t.Errorf("GELU(-1) should be negative, got %f", result.Data[0])
	}
}

func TestTensorTranspose(t *testing.T) {
	tensor := NewTensor(2, 3)
	tensor.Data = []float64{1, 2, 3, 4, 5, 6}

	result := tensor.Transpose()

	if len(result.Shape) != 2 || result.Shape[0] != 3 || result.Shape[1] != 2 {
		t.Errorf("expected transposed shape [3, 2], got %v", result.Shape)
	}

	expected := []float64{1, 4, 2, 5, 3, 6}
	for i, v := range result.Data {
		if v != expected[i] {
			t.Errorf("at index %d: expected %f, got %f", i, expected[i], v)
		}
	}
}

func TestTensorClone(t *testing.T) {
	original := NewTensor(2, 2)
	original.Data = []float64{1, 2, 3, 4}

	clone := original.Clone()

	// Modify clone
	clone.Data[0] = 999

	// Original should be unchanged
	if original.Data[0] != 1 {
		t.Errorf("original tensor was modified by clone")
	}
}
