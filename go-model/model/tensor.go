package model

import "math"

// Tensor represents a multi-dimensional array for neural network computations
// In a production system, this would be replaced with a proper tensor library
type Tensor struct {
	Data  []float64
	Shape []int
}

// NewTensor creates a new tensor with the given shape
func NewTensor(shape ...int) *Tensor {
	size := 1
	for _, dim := range shape {
		size *= dim
	}
	return &Tensor{
		Data:  make([]float64, size),
		Shape: shape,
	}
}

// Size returns the total number of elements in the tensor
func (t *Tensor) Size() int {
	if len(t.Shape) == 0 {
		return 0
	}
	size := 1
	for _, dim := range t.Shape {
		size *= dim
	}
	return size
}

// Reshape changes the shape of the tensor
func (t *Tensor) Reshape(newShape ...int) *Tensor {
	newSize := 1
	for _, dim := range newShape {
		newSize *= dim
	}
	if newSize != t.Size() {
		panic("new shape must have the same total size as original")
	}
	return &Tensor{
		Data:  t.Data,
		Shape: newShape,
	}
}

// Clone creates a deep copy of the tensor
func (t *Tensor) Clone() *Tensor {
	newData := make([]float64, len(t.Data))
	copy(newData, t.Data)
	newShape := make([]int, len(t.Shape))
	copy(newShape, t.Shape)
	return &Tensor{
		Data:  newData,
		Shape: newShape,
	}
}

// Add performs element-wise addition
func (t *Tensor) Add(other *Tensor) *Tensor {
	if t.Size() != other.Size() {
		panic("tensors must have the same size for addition")
	}
	result := NewTensor(t.Shape...)
	for i := range t.Data {
		result.Data[i] = t.Data[i] + other.Data[i]
	}
	return result
}

// Multiply performs element-wise multiplication
func (t *Tensor) Multiply(other *Tensor) *Tensor {
	if t.Size() != other.Size() {
		panic("tensors must have the same size for multiplication")
	}
	result := NewTensor(t.Shape...)
	for i := range t.Data {
		result.Data[i] = t.Data[i] * other.Data[i]
	}
	return result
}

// Scale multiplies all elements by a scalar
func (t *Tensor) Scale(scalar float64) *Tensor {
	result := NewTensor(t.Shape...)
	for i := range t.Data {
		result.Data[i] = t.Data[i] * scalar
	}
	return result
}

// Sqrt computes element-wise square root
func (t *Tensor) Sqrt() *Tensor {
	result := NewTensor(t.Shape...)
	for i := range t.Data {
		result.Data[i] = math.Sqrt(t.Data[i])
	}
	return result
}

// Mean computes the mean of all elements
func (t *Tensor) Mean() float64 {
	if len(t.Data) == 0 {
		return 0
	}
	sum := 0.0
	for _, v := range t.Data {
		sum += v
	}
	return sum / float64(len(t.Data))
}

// Variance computes the variance of all elements
func (t *Tensor) Variance(mean float64) float64 {
	if len(t.Data) == 0 {
		return 0
	}
	variance := 0.0
	for _, v := range t.Data {
		diff := v - mean
		variance += diff * diff
	}
	return variance / float64(len(t.Data))
}

// MatMul performs matrix multiplication (simplified for 2D matrices)
// Shape [M, K] x [K, N] -> [M, N]
func (t *Tensor) MatMul(other *Tensor) *Tensor {
	if len(t.Shape) != 2 || len(other.Shape) != 2 {
		panic("MatMul requires 2D tensors")
	}
	if t.Shape[1] != other.Shape[0] {
		panic("incompatible dimensions for matrix multiplication")
	}

	M, K, N := t.Shape[0], t.Shape[1], other.Shape[1]
	result := NewTensor(M, N)

	for i := 0; i < M; i++ {
		for j := 0; j < N; j++ {
			sum := 0.0
			for k := 0; k < K; k++ {
				sum += t.Data[i*K+k] * other.Data[k*N+j]
			}
			result.Data[i*N+j] = sum
		}
	}

	return result
}

// Softmax applies softmax activation along the last dimension
func (t *Tensor) Softmax() *Tensor {
	result := NewTensor(t.Shape...)

	if len(t.Shape) == 1 {
		// 1D case
		maxVal := t.Data[0]
		for _, v := range t.Data {
			if v > maxVal {
				maxVal = v
			}
		}

		sum := 0.0
		for i, v := range t.Data {
			result.Data[i] = math.Exp(v - maxVal)
			sum += result.Data[i]
		}

		for i := range result.Data {
			result.Data[i] /= sum
		}
	} else if len(t.Shape) == 2 {
		// 2D case - apply softmax to each row
		rows, cols := t.Shape[0], t.Shape[1]
		for i := 0; i < rows; i++ {
			// Find max in row
			maxVal := t.Data[i*cols]
			for j := 1; j < cols; j++ {
				if t.Data[i*cols+j] > maxVal {
					maxVal = t.Data[i*cols+j]
				}
			}

			// Compute exp and sum
			sum := 0.0
			for j := 0; j < cols; j++ {
				result.Data[i*cols+j] = math.Exp(t.Data[i*cols+j] - maxVal)
				sum += result.Data[i*cols+j]
			}

			// Normalize
			for j := 0; j < cols; j++ {
				result.Data[i*cols+j] /= sum
			}
		}
	}

	return result
}

// GELU applies the Gaussian Error Linear Unit activation function
func (t *Tensor) GELU() *Tensor {
	result := NewTensor(t.Shape...)
	for i, x := range t.Data {
		// GELU(x) = x * Φ(x) where Φ is the cumulative distribution function of the standard normal distribution
		// Approximation: 0.5 * x * (1 + tanh(sqrt(2/π) * (x + 0.044715 * x^3)))
		result.Data[i] = 0.5 * x * (1.0 + math.Tanh(math.Sqrt(2.0/math.Pi)*(x+0.044715*x*x*x)))
	}
	return result
}

// Transpose transposes a 2D tensor
func (t *Tensor) Transpose() *Tensor {
	if len(t.Shape) != 2 {
		panic("Transpose requires 2D tensor")
	}
	rows, cols := t.Shape[0], t.Shape[1]
	result := NewTensor(cols, rows)
	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			result.Data[j*rows+i] = t.Data[i*cols+j]
		}
	}
	return result
}
