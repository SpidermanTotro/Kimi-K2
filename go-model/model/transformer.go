package model

import "math"

// Transformer represents the complete transformer model with 16 layers
type Transformer struct {
	Config    *Config
	Embedding *Embedding
	PosEnc    *PositionalEncoding
	Blocks    []*TransformerBlock
	FinalNorm *LayerNorm
	Output    *Tensor // Output projection weights [hidden_size, vocab_size]
}

// NewTransformer creates a new transformer model
func NewTransformer(config *Config) (*Transformer, error) {
	// Validate configuration
	if err := config.Validate(); err != nil {
		return nil, err
	}

	// Create embedding layer
	embedding := NewEmbedding(config.VocabSize, config.HiddenSize)

	// Create positional encoding
	var posEnc *PositionalEncoding
	if config.UsePositionEnc {
		posEnc = NewPositionalEncoding(config.MaxSeqLen, config.HiddenSize)
	}

	// Create transformer blocks
	blocks := make([]*TransformerBlock, config.NumLayers)
	for i := 0; i < config.NumLayers; i++ {
		blocks[i] = NewTransformerBlock(config)
	}

	// Create final layer normalization
	finalNorm := NewLayerNorm(config.HiddenSize, config.EpsilonLN)

	// Create output projection (language modeling head)
	output := NewTensor(config.HiddenSize, config.VocabSize)
	scale := math.Sqrt(1.0 / float64(config.HiddenSize))
	for i := range output.Data {
		output.Data[i] = (float64(i%100)/100.0 - 0.5) * scale
	}

	return &Transformer{
		Config:    config,
		Embedding: embedding,
		PosEnc:    posEnc,
		Blocks:    blocks,
		FinalNorm: finalNorm,
		Output:    output,
	}, nil
}

// Forward performs a forward pass through the transformer
// Input: token IDs [seq_len] as slice
// Output: logits [seq_len, vocab_size]
func (t *Transformer) Forward(tokenIDs []int) *Tensor {
	if len(tokenIDs) == 0 {
		panic("input token IDs cannot be empty")
	}
	if len(tokenIDs) > t.Config.MaxSeqLen {
		panic("input sequence length exceeds maximum sequence length")
	}

	// Step 1: Embedding lookup
	hidden := t.Embedding.Forward(tokenIDs)

	// Step 2: Add positional encoding
	if t.Config.UsePositionEnc && t.PosEnc != nil {
		hidden = t.PosEnc.Forward(hidden)
	}

	// Step 3: Pass through transformer blocks
	for i := 0; i < t.Config.NumLayers; i++ {
		hidden = t.Blocks[i].Forward(hidden)
	}

	// Step 4: Final layer normalization
	hidden = t.FinalNorm.Forward(hidden)

	// Step 5: Output projection to vocabulary
	logits := hidden.MatMul(t.Output)

	return logits
}

// Predict generates predictions for the next token
// Input: token IDs [seq_len] as slice
// Output: probability distribution over vocabulary [vocab_size]
func (t *Transformer) Predict(tokenIDs []int) *Tensor {
	// Get logits for all positions
	logits := t.Forward(tokenIDs)

	// Extract logits for the last position
	seqLen := len(tokenIDs)
	vocabSize := t.Config.VocabSize

	lastLogits := NewTensor(vocabSize)
	for i := 0; i < vocabSize; i++ {
		lastLogits.Data[i] = logits.Data[(seqLen-1)*vocabSize+i]
	}

	// Apply softmax to get probabilities
	probs := lastLogits.Softmax()

	return probs
}

// GetTopK returns the top-k token IDs with highest probabilities
func (t *Transformer) GetTopK(probs *Tensor, k int) []int {
	if k <= 0 || k > len(probs.Data) {
		k = len(probs.Data)
	}

	// Create indices array
	indices := make([]int, len(probs.Data))
	for i := range indices {
		indices[i] = i
	}

	// Simple selection sort for top-k (can be optimized with heap)
	for i := 0; i < k; i++ {
		maxIdx := i
		for j := i + 1; j < len(probs.Data); j++ {
			if probs.Data[indices[j]] > probs.Data[indices[maxIdx]] {
				maxIdx = j
			}
		}
		indices[i], indices[maxIdx] = indices[maxIdx], indices[i]
	}

	return indices[:k]
}

// NumParameters returns the total number of parameters in the model
func (t *Transformer) NumParameters() int {
	total := 0

	// Embedding
	total += t.Embedding.Weights.Size()

	// Transformer blocks
	for _, block := range t.Blocks {
		// Attention
		total += block.Attention.QueryWeight.Size()
		total += block.Attention.KeyWeight.Size()
		total += block.Attention.ValueWeight.Size()
		total += block.Attention.OutWeight.Size()

		// Feed-forward
		total += block.FeedForward.Weight1.Size()
		total += block.FeedForward.Bias1.Size()
		total += block.FeedForward.Weight2.Size()
		total += block.FeedForward.Bias2.Size()

		// Layer norms
		total += block.LayerNorm1.Gamma.Size()
		total += block.LayerNorm1.Beta.Size()
		total += block.LayerNorm2.Gamma.Size()
		total += block.LayerNorm2.Beta.Size()
	}

	// Final norm
	total += t.FinalNorm.Gamma.Size()
	total += t.FinalNorm.Beta.Size()

	// Output projection
	total += t.Output.Size()

	return total
}
