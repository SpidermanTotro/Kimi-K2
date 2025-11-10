package model

// Config defines the configuration for the transformer model
type Config struct {
	VocabSize      int     // Size of the vocabulary
	HiddenSize     int     // Dimension of hidden states
	NumLayers      int     // Number of transformer layers
	NumHeads       int     // Number of attention heads
	FFNHiddenSize  int     // Hidden dimension in feed-forward network
	MaxSeqLen      int     // Maximum sequence length
	DropoutProb    float64 // Dropout probability
	EpsilonLN      float64 // Epsilon for layer normalization
	UsePositionEnc bool    // Whether to use positional encoding
}

// NewDefaultConfig returns a default configuration for a 16-layer transformer
func NewDefaultConfig() *Config {
	return &Config{
		VocabSize:      50000, // Default vocabulary size
		HiddenSize:     768,   // Standard BERT-base hidden size
		NumLayers:      16,    // 16 transformer layers as specified
		NumHeads:       12,    // 12 attention heads
		FFNHiddenSize:  3072,  // 4x hidden size (standard practice)
		MaxSeqLen:      512,   // Standard max sequence length
		DropoutProb:    0.1,   // 10% dropout
		EpsilonLN:      1e-12, // Small epsilon for numerical stability
		UsePositionEnc: true,  // Enable positional encoding
	}
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	if c.VocabSize <= 0 {
		return &ConfigError{"VocabSize must be positive"}
	}
	if c.HiddenSize <= 0 {
		return &ConfigError{"HiddenSize must be positive"}
	}
	if c.NumLayers <= 0 {
		return &ConfigError{"NumLayers must be positive"}
	}
	if c.NumHeads <= 0 {
		return &ConfigError{"NumHeads must be positive"}
	}
	if c.HiddenSize%c.NumHeads != 0 {
		return &ConfigError{"HiddenSize must be divisible by NumHeads"}
	}
	if c.FFNHiddenSize <= 0 {
		return &ConfigError{"FFNHiddenSize must be positive"}
	}
	if c.MaxSeqLen <= 0 {
		return &ConfigError{"MaxSeqLen must be positive"}
	}
	if c.DropoutProb < 0 || c.DropoutProb > 1 {
		return &ConfigError{"DropoutProb must be between 0 and 1"}
	}
	return nil
}

// ConfigError represents a configuration error
type ConfigError struct {
	Message string
}

func (e *ConfigError) Error() string {
	return e.Message
}
