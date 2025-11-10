package config

import (
	"encoding/json"
	"fmt"
	"os"
)

// ModelConfig defines the configuration for the 16GB optimized Kimi-K2 model
type ModelConfig struct {
	// Core architecture parameters optimized for 16GB memory
	VocabSize         int     `json:"vocab_size"`          // Vocabulary size
	HiddenDim         int     `json:"hidden_dim"`          // Hidden dimension size
	IntermediateDim   int     `json:"intermediate_dim"`    // Feed-forward intermediate dimension
	NumLayers         int     `json:"num_layers"`          // Number of transformer layers
	NumHeads          int     `json:"num_heads"`           // Number of attention heads
	NumKVHeads        int     `json:"num_kv_heads"`        // Number of key-value heads for GQA
	MaxSeqLen         int     `json:"max_seq_len"`         // Maximum sequence length
	
	// Precision and optimization settings
	UseFP16           bool    `json:"use_fp16"`            // Use FP16 precision
	UseBF16           bool    `json:"use_bf16"`            // Use BF16 precision
	UseFlashAttention bool    `json:"use_flash_attention"` // Enable FlashAttention
	UseKVCache        bool    `json:"use_kv_cache"`        // Enable KV caching
	
	// Memory constraints (in GB)
	MaxMemoryGB       float64 `json:"max_memory_gb"`       // Maximum memory usage
	
	// Activation function
	ActivationFn      string  `json:"activation_fn"`       // Activation function (swiglu, gelu, etc.)
	
	// Dropout and regularization
	DropoutRate       float64 `json:"dropout_rate"`        // Dropout rate
	LayerNormEps      float64 `json:"layer_norm_eps"`      // Layer normalization epsilon
	
	// Parallelization
	NumWorkers        int     `json:"num_workers"`         // Number of goroutines for parallel processing
}

// Default16GBConfig returns a default configuration optimized for 16GB memory
func Default16GBConfig() *ModelConfig {
	return &ModelConfig{
		// Optimized parameters for 16GB memory constraint
		// Approximately 7-8B activated parameters
		VocabSize:         100000,  // 100K vocabulary
		HiddenDim:         3072,    // Hidden dimension
		IntermediateDim:   8192,    // FFN intermediate dimension (SwiGLU)
		NumLayers:         28,      // Number of layers
		NumHeads:          24,      // Attention heads
		NumKVHeads:        8,       // KV heads for Grouped Query Attention
		MaxSeqLen:         8192,    // 8K context length
		
		// Enable optimizations
		UseFP16:           true,    // Use FP16 for reduced memory
		UseBF16:           false,   // Alternative to FP16
		UseFlashAttention: true,    // Enable FlashAttention
		UseKVCache:        true,    // Enable KV caching
		
		// Memory constraint
		MaxMemoryGB:       16.0,    // 16GB limit
		
		// Standard settings
		ActivationFn:      "swiglu",
		DropoutRate:       0.0,     // No dropout during inference
		LayerNormEps:      1e-5,
		
		// Parallelization
		NumWorkers:        8,       // Parallel goroutines
	}
}

// SmallConfig returns a smaller configuration for testing (uses ~4GB)
func SmallConfig() *ModelConfig {
	return &ModelConfig{
		VocabSize:         50000,
		HiddenDim:         1024,
		IntermediateDim:   2816,
		NumLayers:         12,
		NumHeads:          8,
		NumKVHeads:        4,
		MaxSeqLen:         2048,
		
		UseFP16:           true,
		UseBF16:           false,
		UseFlashAttention: true,
		UseKVCache:        true,
		
		MaxMemoryGB:       4.0,
		
		ActivationFn:      "swiglu",
		DropoutRate:       0.0,
		LayerNormEps:      1e-5,
		
		NumWorkers:        4,
	}
}

// Validate checks if the configuration is valid
func (c *ModelConfig) Validate() error {
	if c.VocabSize <= 0 {
		return fmt.Errorf("vocab_size must be positive, got %d", c.VocabSize)
	}
	if c.HiddenDim <= 0 {
		return fmt.Errorf("hidden_dim must be positive, got %d", c.HiddenDim)
	}
	if c.HiddenDim%c.NumHeads != 0 {
		return fmt.Errorf("hidden_dim (%d) must be divisible by num_heads (%d)", c.HiddenDim, c.NumHeads)
	}
	if c.NumLayers <= 0 {
		return fmt.Errorf("num_layers must be positive, got %d", c.NumLayers)
	}
	if c.NumHeads <= 0 {
		return fmt.Errorf("num_heads must be positive, got %d", c.NumHeads)
	}
	if c.NumKVHeads <= 0 || c.NumKVHeads > c.NumHeads {
		return fmt.Errorf("num_kv_heads must be positive and <= num_heads, got %d", c.NumKVHeads)
	}
	if c.MaxSeqLen <= 0 {
		return fmt.Errorf("max_seq_len must be positive, got %d", c.MaxSeqLen)
	}
	if c.MaxMemoryGB <= 0 {
		return fmt.Errorf("max_memory_gb must be positive, got %f", c.MaxMemoryGB)
	}
	if c.NumWorkers <= 0 {
		return fmt.Errorf("num_workers must be positive, got %d", c.NumWorkers)
	}
	return nil
}

// EstimateMemoryUsage estimates the memory usage in GB for this configuration
func (c *ModelConfig) EstimateMemoryUsage() float64 {
	// Calculate parameter count
	embeddingParams := c.VocabSize * c.HiddenDim
	
	// Per-layer parameters
	// Attention: Q, K, V projections + output projection
	attentionParams := 4 * c.HiddenDim * c.HiddenDim
	
	// Feed-forward: 2 layers in SwiGLU (gate + up, then down)
	ffnParams := 3 * c.HiddenDim * c.IntermediateDim
	
	// Layer norm: 2 per layer
	layerNormParams := 2 * c.HiddenDim
	
	perLayerParams := attentionParams + ffnParams + layerNormParams
	totalParams := embeddingParams + (c.NumLayers * perLayerParams)
	
	// Calculate memory based on precision
	bytesPerParam := 4.0 // FP32
	if c.UseFP16 || c.UseBF16 {
		bytesPerParam = 2.0 // FP16/BF16
	}
	
	// Model weights
	modelMemory := float64(totalParams) * bytesPerParam / (1024 * 1024 * 1024)
	
	// Activation memory (rough estimate for batch size 1)
	activationMemory := float64(c.NumLayers*c.HiddenDim*c.MaxSeqLen) * bytesPerParam / (1024 * 1024 * 1024)
	
	// KV cache memory
	kvCacheMemory := 0.0
	if c.UseKVCache {
		kvCacheMemory = 2.0 * float64(c.NumLayers*c.NumKVHeads*c.MaxSeqLen*(c.HiddenDim/c.NumHeads)) * bytesPerParam / (1024 * 1024 * 1024)
	}
	
	totalMemory := modelMemory + activationMemory + kvCacheMemory
	return totalMemory
}

// HeadDim returns the dimension of each attention head
func (c *ModelConfig) HeadDim() int {
	return c.HiddenDim / c.NumHeads
}

// SaveToFile saves the configuration to a JSON file
func (c *ModelConfig) SaveToFile(filename string) error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}
	
	if err := os.WriteFile(filename, data, 0644); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}
	
	return nil
}

// LoadFromFile loads the configuration from a JSON file
func LoadFromFile(filename string) (*ModelConfig, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}
	
	var config ModelConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}
	
	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid config: %w", err)
	}
	
	return &config, nil
}
