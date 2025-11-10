package config

import (
	"os"
	"testing"
)

func TestDefault16GBConfig(t *testing.T) {
	cfg := Default16GBConfig()
	
	if err := cfg.Validate(); err != nil {
		t.Fatalf("Default16GBConfig validation failed: %v", err)
	}
	
	// Check key parameters
	if cfg.VocabSize <= 0 {
		t.Errorf("VocabSize should be positive, got %d", cfg.VocabSize)
	}
	
	if cfg.HiddenDim <= 0 {
		t.Errorf("HiddenDim should be positive, got %d", cfg.HiddenDim)
	}
	
	if cfg.NumLayers <= 0 {
		t.Errorf("NumLayers should be positive, got %d", cfg.NumLayers)
	}
	
	if cfg.MaxMemoryGB != 16.0 {
		t.Errorf("MaxMemoryGB should be 16.0, got %f", cfg.MaxMemoryGB)
	}
	
	// Test memory estimation
	estimatedMem := cfg.EstimateMemoryUsage()
	if estimatedMem <= 0 {
		t.Errorf("Estimated memory should be positive, got %f", estimatedMem)
	}
	
	t.Logf("Estimated memory usage: %.2f GB", estimatedMem)
	
	// Should be within reasonable bounds for 16GB target
	if estimatedMem > 16.0 {
		t.Logf("Warning: Estimated memory %.2f GB exceeds 16GB target", estimatedMem)
	}
}

func TestSmallConfig(t *testing.T) {
	cfg := SmallConfig()
	
	if err := cfg.Validate(); err != nil {
		t.Fatalf("SmallConfig validation failed: %v", err)
	}
	
	estimatedMem := cfg.EstimateMemoryUsage()
	t.Logf("Small config estimated memory: %.2f GB", estimatedMem)
	
	if estimatedMem > 4.0 {
		t.Logf("Warning: Small config memory %.2f GB exceeds 4GB target", estimatedMem)
	}
}

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name    string
		config  *ModelConfig
		wantErr bool
	}{
		{
			name:    "valid config",
			config:  Default16GBConfig(),
			wantErr: false,
		},
		{
			name: "invalid vocab size",
			config: &ModelConfig{
				VocabSize: -1,
				HiddenDim: 128,
				NumLayers: 4,
				NumHeads:  4,
				NumKVHeads: 2,
				MaxSeqLen: 512,
				MaxMemoryGB: 1.0,
				NumWorkers: 2,
			},
			wantErr: true,
		},
		{
			name: "hidden dim not divisible by heads",
			config: &ModelConfig{
				VocabSize: 1000,
				HiddenDim: 127,
				NumLayers: 4,
				NumHeads:  4,
				NumKVHeads: 2,
				MaxSeqLen: 512,
				MaxMemoryGB: 1.0,
				NumWorkers: 2,
			},
			wantErr: true,
		},
		{
			name: "invalid kv heads",
			config: &ModelConfig{
				VocabSize: 1000,
				HiddenDim: 128,
				NumLayers: 4,
				NumHeads:  4,
				NumKVHeads: 8,
				MaxSeqLen: 512,
				MaxMemoryGB: 1.0,
				NumWorkers: 2,
			},
			wantErr: true,
		},
	}
	
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestHeadDim(t *testing.T) {
	cfg := &ModelConfig{
		HiddenDim: 768,
		NumHeads:  12,
	}
	
	expected := 64
	if got := cfg.HeadDim(); got != expected {
		t.Errorf("HeadDim() = %d, want %d", got, expected)
	}
}

func TestConfigSaveLoad(t *testing.T) {
	cfg := Default16GBConfig()
	
	tmpfile := "/tmp/test_config.json"
	defer os.Remove(tmpfile)
	
	// Save
	if err := cfg.SaveToFile(tmpfile); err != nil {
		t.Fatalf("SaveToFile failed: %v", err)
	}
	
	// Load
	loaded, err := LoadFromFile(tmpfile)
	if err != nil {
		t.Fatalf("LoadFromFile failed: %v", err)
	}
	
	// Compare key fields
	if loaded.VocabSize != cfg.VocabSize {
		t.Errorf("VocabSize mismatch: got %d, want %d", loaded.VocabSize, cfg.VocabSize)
	}
	
	if loaded.HiddenDim != cfg.HiddenDim {
		t.Errorf("HiddenDim mismatch: got %d, want %d", loaded.HiddenDim, cfg.HiddenDim)
	}
	
	if loaded.NumLayers != cfg.NumLayers {
		t.Errorf("NumLayers mismatch: got %d, want %d", loaded.NumLayers, cfg.NumLayers)
	}
	
	if loaded.MaxMemoryGB != cfg.MaxMemoryGB {
		t.Errorf("MaxMemoryGB mismatch: got %f, want %f", loaded.MaxMemoryGB, cfg.MaxMemoryGB)
	}
}

func TestEstimateMemoryUsage(t *testing.T) {
	tests := []struct {
		name   string
		config *ModelConfig
	}{
		{
			name:   "Default 16GB config",
			config: Default16GBConfig(),
		},
		{
			name:   "Small config",
			config: SmallConfig(),
		},
		{
			name: "Tiny config",
			config: &ModelConfig{
				VocabSize:       10000,
				HiddenDim:       256,
				IntermediateDim: 512,
				NumLayers:       6,
				NumHeads:        4,
				NumKVHeads:      2,
				MaxSeqLen:       512,
				UseFP16:         true,
				UseKVCache:      true,
				MaxMemoryGB:     1.0,
			},
		},
	}
	
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mem := tt.config.EstimateMemoryUsage()
			t.Logf("%s: Estimated memory = %.4f GB", tt.name, mem)
			
			if mem <= 0 {
				t.Errorf("Memory estimate should be positive, got %f", mem)
			}
		})
	}
}

func BenchmarkConfigValidation(b *testing.B) {
	cfg := Default16GBConfig()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = cfg.Validate()
	}
}

func BenchmarkEstimateMemory(b *testing.B) {
	cfg := Default16GBConfig()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = cfg.EstimateMemoryUsage()
	}
}
