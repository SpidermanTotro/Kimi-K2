package model

import (
	"testing"
)

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name        string
		config      *Config
		shouldError bool
	}{
		{
			name:        "valid default config",
			config:      NewDefaultConfig(),
			shouldError: false,
		},
		{
			name: "invalid vocab size",
			config: &Config{
				VocabSize:      -1,
				HiddenSize:     768,
				NumLayers:      16,
				NumHeads:       12,
				FFNHiddenSize:  3072,
				MaxSeqLen:      512,
				DropoutProb:    0.1,
				EpsilonLN:      1e-12,
				UsePositionEnc: true,
			},
			shouldError: true,
		},
		{
			name: "hidden size not divisible by num heads",
			config: &Config{
				VocabSize:      50000,
				HiddenSize:     770,
				NumLayers:      16,
				NumHeads:       12,
				FFNHiddenSize:  3072,
				MaxSeqLen:      512,
				DropoutProb:    0.1,
				EpsilonLN:      1e-12,
				UsePositionEnc: true,
			},
			shouldError: true,
		},
		{
			name: "invalid dropout probability",
			config: &Config{
				VocabSize:      50000,
				HiddenSize:     768,
				NumLayers:      16,
				NumHeads:       12,
				FFNHiddenSize:  3072,
				MaxSeqLen:      512,
				DropoutProb:    1.5,
				EpsilonLN:      1e-12,
				UsePositionEnc: true,
			},
			shouldError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if tt.shouldError && err == nil {
				t.Errorf("expected error but got none")
			}
			if !tt.shouldError && err != nil {
				t.Errorf("expected no error but got: %v", err)
			}
		})
	}
}

func TestNewDefaultConfig(t *testing.T) {
	config := NewDefaultConfig()

	if config.NumLayers != 16 {
		t.Errorf("expected 16 layers, got %d", config.NumLayers)
	}

	if config.HiddenSize%config.NumHeads != 0 {
		t.Errorf("hidden size %d not divisible by num heads %d", config.HiddenSize, config.NumHeads)
	}

	if err := config.Validate(); err != nil {
		t.Errorf("default config should be valid: %v", err)
	}
}
