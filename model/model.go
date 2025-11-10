package model

import (
	"fmt"
	"math/rand"
)

// Transformer16 represents a 16-layer transformer model
type Transformer16 struct {
	Config    *Config
	Embedding *Embedding
	PosEnc    *PositionalEncoding
	Layers    []*TransformerBlock
	LMHead    *LMHead
}

// Embedding layer for token embeddings
type Embedding struct {
	VocabSize  int
	HiddenSize int
	Weights    Matrix
}

// NewEmbedding creates a new embedding layer
func NewEmbedding(vocabSize, hiddenSize int) *Embedding {
	return &Embedding{
		VocabSize:  vocabSize,
		HiddenSize: hiddenSize,
		Weights:    NewMatrix(vocabSize, hiddenSize),
	}
}

// Forward looks up embeddings for input tokens
func (e *Embedding) Forward(tokens []int) [][]float64 {
	embeddings := make([][]float64, len(tokens))
	for i, token := range tokens {
		if token >= 0 && token < e.VocabSize {
			embeddings[i] = make([]float64, e.HiddenSize)
			copy(embeddings[i], e.Weights[token])
		} else {
			embeddings[i] = make([]float64, e.HiddenSize)
		}
	}
	return embeddings
}

// LMHead is the language modeling head for final predictions
type LMHead struct {
	HiddenSize int
	VocabSize  int
	Weights    Matrix
	Bias       []float64
}

// NewLMHead creates a new language modeling head
func NewLMHead(hiddenSize, vocabSize int) *LMHead {
	return &LMHead{
		HiddenSize: hiddenSize,
		VocabSize:  vocabSize,
		Weights:    NewMatrix(hiddenSize, vocabSize),
		Bias:       make([]float64, vocabSize),
	}
}

// Forward computes logits for vocabulary
func (lm *LMHead) Forward(hidden []float64) []float64 {
	return AddVectors(VectorMatMul(hidden, lm.Weights), lm.Bias)
}

// NewTransformer16 creates a new 16-layer transformer model
func NewTransformer16(config *Config) (*Transformer16, error) {
	if err := config.Validate(); err != nil {
		return nil, err
	}

	model := &Transformer16{
		Config:    config,
		Embedding: NewEmbedding(config.VocabSize, config.HiddenSize),
		PosEnc:    NewPositionalEncoding(config.MaxSeqLength, config.HiddenSize),
		Layers:    make([]*TransformerBlock, config.NumLayers),
		LMHead:    NewLMHead(config.HiddenSize, config.VocabSize),
	}

	// Initialize all 16 transformer layers
	for i := 0; i < config.NumLayers; i++ {
		model.Layers[i] = NewTransformerBlock(config)
	}

	return model, nil
}

// Forward performs a forward pass through the model
// tokens: input token IDs [seqLen]
// Returns: logits for each position [seqLen][vocabSize]
func (t *Transformer16) Forward(tokens []int) ([][]float64, error) {
	if len(tokens) == 0 {
		return nil, fmt.Errorf("empty input tokens")
	}
	if len(tokens) > t.Config.MaxSeqLength {
		return nil, fmt.Errorf("sequence length %d exceeds maximum %d", len(tokens), t.Config.MaxSeqLength)
	}

	// 1. Embed tokens
	hidden := t.Embedding.Forward(tokens)

	// 2. Add positional encodings
	hidden = t.PosEnc.Forward(hidden)

	// 3. Create causal mask for autoregressive generation
	seqLen := len(tokens)
	mask := NewMatrix(seqLen, seqLen)
	for i := 0; i < seqLen; i++ {
		for j := 0; j <= i; j++ {
			mask[i][j] = 1.0 // Allow attention to current and previous positions
		}
	}

	// 4. Pass through all 16 transformer layers
	for i := 0; i < t.Config.NumLayers; i++ {
		hidden = t.Layers[i].Forward(hidden, mask)
	}

	// 5. Apply LM head to get logits
	logits := make([][]float64, seqLen)
	for i := 0; i < seqLen; i++ {
		logits[i] = t.LMHead.Forward(hidden[i])
	}

	return logits, nil
}

// Generate generates the next token given input tokens
func (t *Transformer16) Generate(tokens []int, temperature float64) (int, error) {
	logits, err := t.Forward(tokens)
	if err != nil {
		return 0, err
	}

	// Get logits for the last position
	lastLogits := logits[len(logits)-1]

	// Apply temperature
	if temperature > 0 {
		for i := range lastLogits {
			lastLogits[i] /= temperature
		}
	}

	// Apply softmax to get probabilities
	probs := Softmax(lastLogits)

	// Sample from the distribution
	r := rand.Float64()
	cumProb := 0.0
	for i, p := range probs {
		cumProb += p
		if r <= cumProb {
			return i, nil
		}
	}

	return len(probs) - 1, nil
}

// NumParameters returns the approximate number of parameters in the model
func (t *Transformer16) NumParameters() int {
	params := 0

	// Embedding
	params += t.Config.VocabSize * t.Config.HiddenSize

	// Each layer
	layerParams := 0
	// Attention: 4 weight matrices (Q, K, V, O)
	layerParams += 4 * t.Config.HiddenSize * t.Config.HiddenSize
	// Attention biases
	layerParams += 4 * t.Config.HiddenSize
	// FFN: 2 weight matrices
	layerParams += t.Config.HiddenSize * t.Config.IntermediateSize
	layerParams += t.Config.IntermediateSize * t.Config.HiddenSize
	// FFN biases
	layerParams += t.Config.IntermediateSize + t.Config.HiddenSize
	// Layer norms: 2 * (gamma + beta)
	layerParams += 4 * t.Config.HiddenSize

	params += t.Config.NumLayers * layerParams

	// LM head
	params += t.Config.HiddenSize * t.Config.VocabSize
	params += t.Config.VocabSize

	return params
}
