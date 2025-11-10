package model

// TransformerBlock implements a single transformer block
type TransformerBlock struct {
	Attention   *MultiHeadAttention
	FeedForward *FeedForward
	LayerNorm1  *LayerNorm
	LayerNorm2  *LayerNorm
}

// NewTransformerBlock creates a new transformer block
func NewTransformerBlock(config *Config) *TransformerBlock {
	attention := NewMultiHeadAttention(config.HiddenSize, config.NumHeads, config.DropoutProb)
	feedForward := NewFeedForward(config.HiddenSize, config.FFNHiddenSize, config.DropoutProb)
	layerNorm1 := NewLayerNorm(config.HiddenSize, config.EpsilonLN)
	layerNorm2 := NewLayerNorm(config.HiddenSize, config.EpsilonLN)

	return &TransformerBlock{
		Attention:   attention,
		FeedForward: feedForward,
		LayerNorm1:  layerNorm1,
		LayerNorm2:  layerNorm2,
	}
}

// Forward applies the transformer block transformation
// Uses pre-norm architecture: LayerNorm -> Sublayer -> Residual
// Input shape: [seq_len, hidden_size]
// Output shape: [seq_len, hidden_size]
func (tb *TransformerBlock) Forward(input *Tensor) *Tensor {
	// First sub-layer: Multi-head attention with residual connection
	// Normalize first (pre-norm)
	normalized1 := tb.LayerNorm1.Forward(input)

	// Apply attention
	attentionOutput := tb.Attention.Forward(normalized1)

	// Add residual connection
	residual1 := input.Add(attentionOutput)

	// Second sub-layer: Feed-forward network with residual connection
	// Normalize first (pre-norm)
	normalized2 := tb.LayerNorm2.Forward(residual1)

	// Apply feed-forward
	ffOutput := tb.FeedForward.Forward(normalized2)

	// Add residual connection
	output := residual1.Add(ffOutput)

	return output
}
