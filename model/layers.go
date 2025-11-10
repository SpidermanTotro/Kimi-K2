package model

import (
	"math"
)

// Matrix represents a 2D matrix
type Matrix [][]float64

// NewMatrix creates a new matrix with the given dimensions
func NewMatrix(rows, cols int) Matrix {
	m := make(Matrix, rows)
	for i := range m {
		m[i] = make([]float64, cols)
	}
	return m
}

// Tensor3D represents a 3D tensor (batch, seq, features)
type Tensor3D [][][]float64

// NewTensor3D creates a new 3D tensor
func NewTensor3D(dim1, dim2, dim3 int) Tensor3D {
	t := make(Tensor3D, dim1)
	for i := range t {
		t[i] = make([][]float64, dim2)
		for j := range t[i] {
			t[i][j] = make([]float64, dim3)
		}
	}
	return t
}

// LayerNorm applies layer normalization
type LayerNorm struct {
	Gamma []float64 // Scale parameter
	Beta  []float64 // Shift parameter
	Eps   float64   // Epsilon for numerical stability
}

// NewLayerNorm creates a new layer normalization layer
func NewLayerNorm(size int, eps float64) *LayerNorm {
	ln := &LayerNorm{
		Gamma: make([]float64, size),
		Beta:  make([]float64, size),
		Eps:   eps,
	}
	// Initialize gamma to 1
	for i := range ln.Gamma {
		ln.Gamma[i] = 1.0
	}
	return ln
}

// Forward applies layer normalization
func (ln *LayerNorm) Forward(x []float64) []float64 {
	// Calculate mean
	mean := 0.0
	for _, v := range x {
		mean += v
	}
	mean /= float64(len(x))

	// Calculate variance
	variance := 0.0
	for _, v := range x {
		diff := v - mean
		variance += diff * diff
	}
	variance /= float64(len(x))

	// Normalize
	output := make([]float64, len(x))
	stddev := math.Sqrt(variance + ln.Eps)
	for i, v := range x {
		normalized := (v - mean) / stddev
		output[i] = ln.Gamma[i]*normalized + ln.Beta[i]
	}
	return output
}

// GELU applies the Gaussian Error Linear Unit activation function
func GELU(x float64) float64 {
	return 0.5 * x * (1.0 + math.Tanh(math.Sqrt(2.0/math.Pi)*(x+0.044715*math.Pow(x, 3))))
}

// Softmax applies the softmax function to a slice
func Softmax(x []float64) []float64 {
	// Find max for numerical stability
	max := x[0]
	for _, v := range x {
		if v > max {
			max = v
		}
	}

	// Compute exp(x - max)
	expSum := 0.0
	output := make([]float64, len(x))
	for i, v := range x {
		output[i] = math.Exp(v - max)
		expSum += output[i]
	}

	// Normalize
	for i := range output {
		output[i] /= expSum
	}
	return output
}

// MatMul performs matrix multiplication: C = A * B
func MatMul(a Matrix, b Matrix) Matrix {
	if len(a) == 0 || len(b) == 0 || len(a[0]) != len(b) {
		return nil
	}

	rows := len(a)
	cols := len(b[0])
	inner := len(a[0])

	c := NewMatrix(rows, cols)
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			sum := 0.0
			for k := 0; k < inner; k++ {
				sum += a[i][k] * b[k][j]
			}
			c[i][j] = sum
		}
	}
	return c
}

// VectorMatMul performs vector-matrix multiplication
func VectorMatMul(vec []float64, mat Matrix) []float64 {
	if len(mat) == 0 || len(vec) != len(mat) {
		return nil
	}

	result := make([]float64, len(mat[0]))
	for j := 0; j < len(mat[0]); j++ {
		sum := 0.0
		for i := 0; i < len(vec); i++ {
			sum += vec[i] * mat[i][j]
		}
		result[j] = sum
	}
	return result
}

// AddVectors adds two vectors element-wise
func AddVectors(a, b []float64) []float64 {
	if len(a) != len(b) {
		return nil
	}
	result := make([]float64, len(a))
	for i := range a {
		result[i] = a[i] + b[i]
	}
	return result
}
