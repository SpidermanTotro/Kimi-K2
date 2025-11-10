package model

// Config holds the configuration for the transformer model
type Config struct {
	// Model dimensions
	VocabSize      int     // Size of the vocabulary
	HiddenSize     int     // Hidden dimension size
	NumLayers      int     // Number of transformer layers (16 for this implementation)
	NumHeads       int     // Number of attention heads
	IntermediateSize int   // Size of the intermediate layer in FFN
	MaxSeqLength   int     // Maximum sequence length
	
	// Dropout and regularization
	DropoutRate    float64 // Dropout probability
	LayerNormEps   float64 // Layer normalization epsilon
	
	// Activation function
	ActivationType string  // Type of activation (e.g., "gelu", "swiglu")
}

// NewDefaultConfig creates a default configuration for a 16-layer model
func NewDefaultConfig() *Config {
	return &Config{
		VocabSize:        50257,  // GPT-2 vocab size as default
		HiddenSize:       768,    // Hidden dimension
		NumLayers:        16,     // 16 layers as requested
		NumHeads:         12,     // Number of attention heads
		IntermediateSize: 3072,   // 4 * HiddenSize
		MaxSeqLength:     1024,   // Maximum sequence length
		DropoutRate:      0.1,    // Dropout rate
		LayerNormEps:     1e-5,   // Layer norm epsilon
		ActivationType:   "gelu", // GELU activation
	}
}

// Validate checks if the configuration is valid
func (c *Config) Validate() error {
	if c.VocabSize <= 0 {
		return &ConfigError{Field: "VocabSize", Message: "must be positive"}
	}
	if c.HiddenSize <= 0 {
		return &ConfigError{Field: "HiddenSize", Message: "must be positive"}
	}
	if c.HiddenSize%c.NumHeads != 0 {
		return &ConfigError{Field: "HiddenSize", Message: "must be divisible by NumHeads"}
	}
	if c.NumLayers != 16 {
		return &ConfigError{Field: "NumLayers", Message: "must be 16 for this implementation"}
	}
	if c.NumHeads <= 0 {
		return &ConfigError{Field: "NumHeads", Message: "must be positive"}
	}
	return nil
}

// ConfigError represents a configuration validation error
type ConfigError struct {
	Field   string
	Message string
}

func (e *ConfigError) Error() string {
	return "config." + e.Field + ": " + e.Message
}
