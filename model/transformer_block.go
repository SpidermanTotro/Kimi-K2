package model

// TransformerBlock represents a single transformer layer
type TransformerBlock struct {
	Attention    *MultiHeadAttention
	FeedForward  *FeedForward
	LayerNorm1   *LayerNorm
	LayerNorm2   *LayerNorm
	DropoutRate  float64
}

// NewTransformerBlock creates a new transformer block
func NewTransformerBlock(config *Config) *TransformerBlock {
	return &TransformerBlock{
		Attention:   NewMultiHeadAttention(config.HiddenSize, config.NumHeads),
		FeedForward: NewFeedForward(config.HiddenSize, config.IntermediateSize, config.ActivationType),
		LayerNorm1:  NewLayerNorm(config.HiddenSize, config.LayerNormEps),
		LayerNorm2:  NewLayerNorm(config.HiddenSize, config.LayerNormEps),
		DropoutRate: config.DropoutRate,
	}
}

// Forward performs the forward pass through the transformer block
func (tb *TransformerBlock) Forward(input [][]float64, mask [][]float64) [][]float64 {
	seqLen := len(input)
	
	// Multi-head attention with residual connection and layer norm
	attnOutput := tb.Attention.Forward(input, mask)
	
	// Add residual connection
	for i := 0; i < seqLen; i++ {
		attnOutput[i] = AddVectors(attnOutput[i], input[i])
		// Apply layer normalization
		attnOutput[i] = tb.LayerNorm1.Forward(attnOutput[i])
	}
	
	// Feed-forward network with residual connection and layer norm
	ffOutput := make([][]float64, seqLen)
	for i := 0; i < seqLen; i++ {
		ffOutput[i] = tb.FeedForward.Forward(attnOutput[i])
		// Add residual connection
		ffOutput[i] = AddVectors(ffOutput[i], attnOutput[i])
		// Apply layer normalization
		ffOutput[i] = tb.LayerNorm2.Forward(ffOutput[i])
	}
	
	return ffOutput
}
