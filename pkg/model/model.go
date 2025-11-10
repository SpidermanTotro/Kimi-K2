package model

import (
	"fmt"
	"math"

	"github.com/SpidermanTotro/Kimi-K2/pkg/attention"
	"github.com/SpidermanTotro/Kimi-K2/pkg/config"
	"gonum.org/v1/gonum/mat"
)

// GPTModel represents the 16GB optimized GPT model
type GPTModel struct {
	config *config.ModelConfig
	
	// Embedding layer
	tokenEmbedding *mat.Dense
	posEmbedding   *mat.Dense
	
	// Transformer layers
	layers []*TransformerLayer
	
	// Output layer
	outputNorm *LayerNorm
	outputProj *mat.Dense
	
	// KV cache for inference
	kvCache *attention.KVCache
}

// TransformerLayer represents a single transformer block
type TransformerLayer struct {
	// Pre-normalization
	attnNorm *LayerNorm
	ffnNorm  *LayerNorm
	
	// Attention
	attention *attention.Attention
	
	// Feed-forward network
	ffn *FeedForward
}

// LayerNorm implements layer normalization
type LayerNorm struct {
	weight *mat.VecDense
	bias   *mat.VecDense
	eps    float64
}

// FeedForward implements the feed-forward network with SwiGLU activation
type FeedForward struct {
	gateProj *mat.Dense
	upProj   *mat.Dense
	downProj *mat.Dense
	
	hiddenDim       int
	intermediateDim int
	numWorkers      int
}

// NewGPTModel creates a new GPT model with the given configuration
func NewGPTModel(cfg *config.ModelConfig) (*GPTModel, error) {
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}
	
	model := &GPTModel{
		config:  cfg,
		kvCache: attention.NewKVCache(cfg.NumLayers),
	}
	
	// Initialize embeddings
	model.tokenEmbedding = mat.NewDense(cfg.VocabSize, cfg.HiddenDim, nil)
	model.posEmbedding = mat.NewDense(cfg.MaxSeqLen, cfg.HiddenDim, nil)
	
	initEmbedding(model.tokenEmbedding)
	initPositionalEmbedding(model.posEmbedding)
	
	// Initialize transformer layers
	model.layers = make([]*TransformerLayer, cfg.NumLayers)
	for i := 0; i < cfg.NumLayers; i++ {
		model.layers[i] = newTransformerLayer(cfg)
	}
	
	// Initialize output layer
	model.outputNorm = newLayerNorm(cfg.HiddenDim, cfg.LayerNormEps)
	model.outputProj = mat.NewDense(cfg.HiddenDim, cfg.VocabSize, nil)
	initMatrix(model.outputProj, math.Sqrt(2.0/float64(cfg.HiddenDim)))
	
	return model, nil
}

// Forward performs a forward pass through the model
func (m *GPTModel) Forward(inputIDs []int, useCache bool) (*mat.Dense, error) {
	seqLen := len(inputIDs)
	if seqLen > m.config.MaxSeqLen {
		return nil, fmt.Errorf("sequence length %d exceeds maximum %d", seqLen, m.config.MaxSeqLen)
	}
	
	// Get token embeddings
	embeddings := m.getEmbeddings(inputIDs)
	
	// Add positional embeddings
	for i := 0; i < seqLen; i++ {
		for j := 0; j < m.config.HiddenDim; j++ {
			val := embeddings.At(i, j) + m.posEmbedding.At(i, j)
			embeddings.Set(i, j, val)
		}
	}
	
	// Create causal mask
	mask := createCausalMask(seqLen)
	
	// Pass through transformer layers
	hidden := embeddings
	var cache *attention.KVCache
	if useCache && m.config.UseKVCache {
		cache = m.kvCache
	}
	
	for layerIdx, layer := range m.layers {
		var err error
		hidden, err = layer.Forward(hidden, mask, layerIdx, cache)
		if err != nil {
			return nil, fmt.Errorf("layer %d forward failed: %w", layerIdx, err)
		}
	}
	
	// Apply output normalization
	hidden = m.outputNorm.Forward(hidden)
	
	// Project to vocabulary
	logits := mat.NewDense(seqLen, m.config.VocabSize, nil)
	logits.Mul(hidden, m.outputProj)
	
	return logits, nil
}

// Generate generates tokens autoregressively
func (m *GPTModel) Generate(inputIDs []int, maxNewTokens int, temperature float64) ([]int, error) {
	if m.config.UseKVCache {
		m.kvCache.Clear()
	}
	
	generated := make([]int, len(inputIDs))
	copy(generated, inputIDs)
	
	for i := 0; i < maxNewTokens; i++ {
		// Get logits for the sequence
		logits, err := m.Forward(generated, true)
		if err != nil {
			return nil, err
		}
		
		// Get logits for the last token
		lastRow, _ := logits.Dims()
		lastLogits := mat.Row(nil, lastRow-1, logits)
		
		// Apply temperature
		if temperature > 0 {
			for i := range lastLogits {
				lastLogits[i] /= temperature
			}
		}
		
		// Sample next token (greedy for now)
		nextToken := argmax(lastLogits)
		generated = append(generated, nextToken)
	}
	
	return generated, nil
}

// getEmbeddings retrieves embeddings for the input token IDs
func (m *GPTModel) getEmbeddings(inputIDs []int) *mat.Dense {
	seqLen := len(inputIDs)
	embeddings := mat.NewDense(seqLen, m.config.HiddenDim, nil)
	
	for i, tokenID := range inputIDs {
		if tokenID >= 0 && tokenID < m.config.VocabSize {
			for j := 0; j < m.config.HiddenDim; j++ {
				embeddings.Set(i, j, m.tokenEmbedding.At(tokenID, j))
			}
		}
	}
	
	return embeddings
}

// newTransformerLayer creates a new transformer layer
func newTransformerLayer(cfg *config.ModelConfig) *TransformerLayer {
	return &TransformerLayer{
		attnNorm:  newLayerNorm(cfg.HiddenDim, cfg.LayerNormEps),
		ffnNorm:   newLayerNorm(cfg.HiddenDim, cfg.LayerNormEps),
		attention: attention.NewAttention(cfg.HiddenDim, cfg.NumHeads, cfg.NumKVHeads, cfg.UseFlashAttention, cfg.NumWorkers),
		ffn:       newFeedForward(cfg.HiddenDim, cfg.IntermediateDim, cfg.NumWorkers),
	}
}

// Forward performs forward pass through the transformer layer
func (l *TransformerLayer) Forward(x *mat.Dense, mask *mat.Dense, layerIdx int, cache *attention.KVCache) (*mat.Dense, error) {
	// Pre-norm for attention
	normed := l.attnNorm.Forward(x)
	
	// Initialize attention weights if needed
	if l.attention == nil {
		return nil, fmt.Errorf("attention layer not initialized")
	}
	
	// Attention with residual connection
	attnOut, err := l.attention.Forward(normed, mask, layerIdx, cache)
	if err != nil {
		return nil, err
	}
	
	// Residual connection
	x = addMatrices(x, attnOut)
	
	// Pre-norm for FFN
	normed = l.ffnNorm.Forward(x)
	
	// FFN with residual connection
	ffnOut := l.ffn.Forward(normed)
	x = addMatrices(x, ffnOut)
	
	return x, nil
}

// newLayerNorm creates a new layer normalization
func newLayerNorm(size int, eps float64) *LayerNorm {
	weight := mat.NewVecDense(size, nil)
	bias := mat.NewVecDense(size, nil)
	
	// Initialize to ones and zeros
	for i := 0; i < size; i++ {
		weight.SetVec(i, 1.0)
		bias.SetVec(i, 0.0)
	}
	
	return &LayerNorm{
		weight: weight,
		bias:   bias,
		eps:    eps,
	}
}

// Forward applies layer normalization
func (ln *LayerNorm) Forward(x *mat.Dense) *mat.Dense {
	rows, cols := x.Dims()
	output := mat.NewDense(rows, cols, nil)
	
	for i := 0; i < rows; i++ {
		row := mat.Row(nil, i, x)
		
		// Compute mean and variance
		mean := 0.0
		for _, v := range row {
			mean += v
		}
		mean /= float64(len(row))
		
		variance := 0.0
		for _, v := range row {
			diff := v - mean
			variance += diff * diff
		}
		variance /= float64(len(row))
		
		// Normalize
		std := math.Sqrt(variance + ln.eps)
		for j, v := range row {
			normalized := (v - mean) / std
			scaled := normalized*ln.weight.AtVec(j) + ln.bias.AtVec(j)
			output.Set(i, j, scaled)
		}
	}
	
	return output
}

// newFeedForward creates a new feed-forward network
func newFeedForward(hiddenDim, intermediateDim, numWorkers int) *FeedForward {
	ffn := &FeedForward{
		gateProj:        mat.NewDense(hiddenDim, intermediateDim, nil),
		upProj:          mat.NewDense(hiddenDim, intermediateDim, nil),
		downProj:        mat.NewDense(intermediateDim, hiddenDim, nil),
		hiddenDim:       hiddenDim,
		intermediateDim: intermediateDim,
		numWorkers:      numWorkers,
	}
	
	scale := math.Sqrt(2.0 / float64(hiddenDim))
	initMatrix(ffn.gateProj, scale)
	initMatrix(ffn.upProj, scale)
	initMatrix(ffn.downProj, math.Sqrt(2.0/float64(intermediateDim)))
	
	return ffn
}

// Forward performs forward pass through FFN with SwiGLU activation
func (ffn *FeedForward) Forward(x *mat.Dense) *mat.Dense {
	rows, _ := x.Dims()
	
	// Gate projection
	gate := mat.NewDense(rows, ffn.intermediateDim, nil)
	gate.Mul(x, ffn.gateProj)
	
	// Up projection
	up := mat.NewDense(rows, ffn.intermediateDim, nil)
	up.Mul(x, ffn.upProj)
	
	// SwiGLU: gate * silu(up) where silu(x) = x * sigmoid(x)
	swiglu := mat.NewDense(rows, ffn.intermediateDim, nil)
	for i := 0; i < rows; i++ {
		for j := 0; j < ffn.intermediateDim; j++ {
			gateVal := gate.At(i, j)
			upVal := up.At(i, j)
			siluVal := upVal / (1.0 + math.Exp(-upVal)) // silu activation
			swiglu.Set(i, j, gateVal*siluVal)
		}
	}
	
	// Down projection
	output := mat.NewDense(rows, ffn.hiddenDim, nil)
	output.Mul(swiglu, ffn.downProj)
	
	return output
}

// Helper functions

func initEmbedding(m *mat.Dense) {
	r, c := m.Dims()
	scale := math.Sqrt(1.0 / float64(c))
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			val := (float64(i*c+j)/(float64(r*c)) - 0.5) * scale
			m.Set(i, j, val)
		}
	}
}

func initPositionalEmbedding(m *mat.Dense) {
	seqLen, dim := m.Dims()
	
	// Sinusoidal positional encoding
	for pos := 0; pos < seqLen; pos++ {
		for i := 0; i < dim; i++ {
			angle := float64(pos) / math.Pow(10000.0, float64(2*i)/float64(dim))
			if i%2 == 0 {
				m.Set(pos, i, math.Sin(angle))
			} else {
				m.Set(pos, i, math.Cos(angle))
			}
		}
	}
}

func initMatrix(m *mat.Dense, scale float64) {
	r, c := m.Dims()
	for i := 0; i < r; i++ {
		for j := 0; j < c; j++ {
			val := (float64(i*c+j)/(float64(r*c)) - 0.5) * scale
			m.Set(i, j, val)
		}
	}
}

func createCausalMask(seqLen int) *mat.Dense {
	mask := mat.NewDense(seqLen, seqLen, nil)
	for i := 0; i < seqLen; i++ {
		for j := 0; j <= i; j++ {
			mask.Set(i, j, 1.0)
		}
	}
	return mask
}

func addMatrices(a, b *mat.Dense) *mat.Dense {
	r, c := a.Dims()
	result := mat.NewDense(r, c, nil)
	result.Add(a, b)
	return result
}

func argmax(vals []float64) int {
	if len(vals) == 0 {
		return 0
	}
	maxIdx := 0
	maxVal := vals[0]
	for i, v := range vals[1:] {
		if v > maxVal {
			maxVal = v
			maxIdx = i + 1
		}
	}
	return maxIdx
}
