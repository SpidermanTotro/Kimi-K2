package attention

import (
	"fmt"
	"math"
	"sync"

	"gonum.org/v1/gonum/mat"
)

// Attention implements multi-head attention with optimizations
type Attention struct {
	numHeads   int
	numKVHeads int
	headDim    int
	hiddenDim  int
	
	// Projection matrices
	qProj *mat.Dense
	kProj *mat.Dense
	vProj *mat.Dense
	oProj *mat.Dense
	
	// Configuration flags
	useFlash   bool
	numWorkers int
	
	// KV cache for inference optimization
	kvCache *KVCache
}

// KVCache stores key-value pairs for efficient inference
type KVCache struct {
	keys   []*mat.Dense
	values []*mat.Dense
	seqLen int
	mu     sync.RWMutex
}

// NewKVCache creates a new KV cache
func NewKVCache(numLayers int) *KVCache {
	return &KVCache{
		keys:   make([]*mat.Dense, numLayers),
		values: make([]*mat.Dense, numLayers),
		seqLen: 0,
	}
}

// Update updates the cache for a specific layer
func (kv *KVCache) Update(layer int, k, v *mat.Dense) {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	
	kv.keys[layer] = k
	kv.values[layer] = v
	
	// Update sequence length based on key dimensions
	if k != nil {
		_, seqLen := k.Dims()
		kv.seqLen = seqLen
	}
}

// Get retrieves cached keys and values for a layer
func (kv *KVCache) Get(layer int) (*mat.Dense, *mat.Dense) {
	kv.mu.RLock()
	defer kv.mu.RUnlock()
	
	return kv.keys[layer], kv.values[layer]
}

// Clear clears the cache
func (kv *KVCache) Clear() {
	kv.mu.Lock()
	defer kv.mu.Unlock()
	
	for i := range kv.keys {
		kv.keys[i] = nil
		kv.values[i] = nil
	}
	kv.seqLen = 0
}

// NewAttention creates a new attention layer
func NewAttention(hiddenDim, numHeads, numKVHeads int, useFlash bool, numWorkers int) *Attention {
	headDim := hiddenDim / numHeads
	
	return &Attention{
		numHeads:   numHeads,
		numKVHeads: numKVHeads,
		headDim:    headDim,
		hiddenDim:  hiddenDim,
		useFlash:   useFlash,
		numWorkers: numWorkers,
	}
}

// InitWeights initializes the projection weight matrices
func (a *Attention) InitWeights() {
	// Initialize Q, K, V, O projection matrices with small random values
	a.qProj = mat.NewDense(a.hiddenDim, a.hiddenDim, nil)
	a.kProj = mat.NewDense(a.hiddenDim, a.numKVHeads*a.headDim, nil)
	a.vProj = mat.NewDense(a.hiddenDim, a.numKVHeads*a.headDim, nil)
	a.oProj = mat.NewDense(a.hiddenDim, a.hiddenDim, nil)
	
	// Xavier/Glorot initialization
	initScale := math.Sqrt(2.0 / float64(a.hiddenDim))
	
	initMatrix(a.qProj, initScale)
	initMatrix(a.kProj, initScale)
	initMatrix(a.vProj, initScale)
	initMatrix(a.oProj, initScale)
}

// initMatrix initializes a matrix with random values
func initMatrix(m *mat.Dense, scale float64) {
	r, c := m.Dims()
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			// Simple random initialization (in practice, use better random source)
			val := (float64(i*c+j)/(float64(r*c)) - 0.5) * scale
			m.Set(i, j, val)
		}
	}
}

// Forward performs forward pass through the attention layer
// Input shape: (batchSize, seqLen, hiddenDim)
// Returns: (batchSize, seqLen, hiddenDim)
func (a *Attention) Forward(x *mat.Dense, mask *mat.Dense, layerIdx int, cache *KVCache) (*mat.Dense, error) {
	batchSize, seqLen := x.Dims()
	if seqLen != a.hiddenDim {
		return nil, fmt.Errorf("input second dimension must be hiddenDim, got %d, expected %d", seqLen, a.hiddenDim)
	}
	
	// For simplicity, we assume batchSize=1 (single sequence)
	// In production, proper batch handling would be needed
	
	// Project to Q, K, V
	q := mat.NewDense(batchSize, a.hiddenDim, nil)
	q.Mul(x, a.qProj)
	
	k := mat.NewDense(batchSize, a.numKVHeads*a.headDim, nil)
	k.Mul(x, a.kProj)
	
	v := mat.NewDense(batchSize, a.numKVHeads*a.headDim, nil)
	v.Mul(x, a.vProj)
	
	// Handle KV cache if provided
	if cache != nil {
		cachedK, cachedV := cache.Get(layerIdx)
		if cachedK != nil && cachedV != nil {
			// Concatenate with cached values
			k = concatenate(cachedK, k)
			v = concatenate(cachedV, v)
		}
		cache.Update(layerIdx, k, v)
	}
	
	// Perform attention computation
	var output *mat.Dense
	var err error
	
	if a.useFlash {
		output, err = a.flashAttention(q, k, v, mask)
	} else {
		output, err = a.standardAttention(q, k, v, mask)
	}
	
	if err != nil {
		return nil, err
	}
	
	// Output projection
	result := mat.NewDense(batchSize, a.hiddenDim, nil)
	result.Mul(output, a.oProj)
	
	return result, nil
}

// standardAttention implements standard scaled dot-product attention
func (a *Attention) standardAttention(q, k, v, mask *mat.Dense) (*mat.Dense, error) {
	qRows, _ := q.Dims()
	kRows, kCols := k.Dims()
	
	// Compute attention scores: Q @ K^T
	scores := mat.NewDense(qRows, kRows, nil)
	scores.Mul(q, k.T())
	
	// Scale by sqrt(headDim)
	scale := 1.0 / math.Sqrt(float64(a.headDim))
	scores.Scale(scale, scores)
	
	// Apply mask if provided
	if mask != nil {
		applyMask(scores, mask)
	}
	
	// Softmax
	softmax(scores)
	
	// Multiply by values: scores @ V
	output := mat.NewDense(qRows, kCols, nil)
	output.Mul(scores, v)
	
	return output, nil
}

// flashAttention implements memory-efficient FlashAttention
// This is a simplified version of FlashAttention for demonstration
func (a *Attention) flashAttention(q, k, v, mask *mat.Dense) (*mat.Dense, error) {
	qRows, _ := q.Dims()
	_, vCols := v.Dims()
	
	// FlashAttention computes attention in blocks to reduce memory usage
	// For this implementation, we use a simplified online softmax approach
	
	output := mat.NewDense(qRows, vCols, nil)
	
	// Process in chunks using goroutines for parallelization
	chunkSize := max(1, qRows/a.numWorkers)
	var wg sync.WaitGroup
	
	for start := 0; start < qRows; start += chunkSize {
		end := min(start+chunkSize, qRows)
		
		wg.Add(1)
		go func(startIdx, endIdx int) {
			defer wg.Done()
			
			for i := startIdx; i < endIdx; i++ {
				// Extract query vector
				qVec := mat.Row(nil, i, q)
				
				// Compute attention for this query
				attnOut := a.computeQueryAttention(qVec, k, v, mask)
				
				// Set output row
				output.SetRow(i, attnOut)
			}
		}(start, end)
	}
	
	wg.Wait()
	
	return output, nil
}

// computeQueryAttention computes attention for a single query vector
func (a *Attention) computeQueryAttention(q []float64, k, v *mat.Dense, mask *mat.Dense) []float64 {
	kRows, _ := k.Dims()
	_, vCols := v.Dims()
	
	// Compute scores for this query
	scores := make([]float64, kRows)
	scale := 1.0 / math.Sqrt(float64(a.headDim))
	
	for i := 0; i < kRows; i++ {
		kVec := mat.Row(nil, i, k)
		score := dotProduct(q, kVec) * scale
		scores[i] = score
	}
	
	// Apply softmax
	expScores := make([]float64, len(scores))
	maxScore := max64(scores)
	sumExp := 0.0
	
	for i := range scores {
		expScores[i] = math.Exp(scores[i] - maxScore)
		sumExp += expScores[i]
	}
	
	for i := range expScores {
		expScores[i] /= sumExp
	}
	
	// Compute weighted sum of values
	output := make([]float64, vCols)
	for i := 0; i < kRows; i++ {
		vVec := mat.Row(nil, i, v)
		weight := expScores[i]
		
		for j := range output {
			output[j] += weight * vVec[j]
		}
	}
	
	return output
}

// Helper functions

func concatenate(a, b *mat.Dense) *mat.Dense {
	aRows, aCols := a.Dims()
	bRows, bCols := b.Dims()
	
	if aCols != bCols {
		return b // In case of dimension mismatch, return new values
	}
	
	result := mat.NewDense(aRows+bRows, aCols, nil)
	
	for i := 0; i < aRows; i++ {
		for j := 0; j < aCols; j++ {
			result.Set(i, j, a.At(i, j))
		}
	}
	
	for i := 0; i < bRows; i++ {
		for j := 0; j < bCols; j++ {
			result.Set(aRows+i, j, b.At(i, j))
		}
	}
	
	return result
}

func applyMask(scores, mask *mat.Dense) {
	r, c := scores.Dims()
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			if mask.At(i, j) == 0 {
				scores.Set(i, j, math.Inf(-1))
			}
		}
	}
}

func softmax(m *mat.Dense) {
	r, c := m.Dims()
	for i := 0; i < r; i++ {
		row := mat.Row(nil, i, m)
		maxVal := max64(row)
		sumExp := 0.0
		
		for j := 0; j < c; j++ {
			val := math.Exp(m.At(i, j) - maxVal)
			m.Set(i, j, val)
			sumExp += val
		}
		
		for j := 0; j < c; j++ {
			m.Set(i, j, m.At(i, j)/sumExp)
		}
	}
}

func dotProduct(a, b []float64) float64 {
	sum := 0.0
	for i := range a {
		if i < len(b) {
			sum += a[i] * b[i]
		}
	}
	return sum
}

func max64(vals []float64) float64 {
	if len(vals) == 0 {
		return 0
	}
	maxVal := vals[0]
	for _, v := range vals[1:] {
		if v > maxVal {
			maxVal = v
		}
	}
	return maxVal
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
