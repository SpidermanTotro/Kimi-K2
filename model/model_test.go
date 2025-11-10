package model

import (
	"testing"
)

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name    string
		config  *Config
		wantErr bool
	}{
		{
			name:    "valid default config",
			config:  NewDefaultConfig(),
			wantErr: false,
		},
		{
			name: "invalid vocab size",
			config: &Config{
				VocabSize:  -1,
				HiddenSize: 768,
				NumLayers:  16,
				NumHeads:   12,
			},
			wantErr: true,
		},
		{
			name: "hidden size not divisible by num heads",
			config: &Config{
				VocabSize:  50257,
				HiddenSize: 770,
				NumLayers:  16,
				NumHeads:   12,
			},
			wantErr: true,
		},
		{
			name: "invalid number of layers",
			config: &Config{
				VocabSize:  50257,
				HiddenSize: 768,
				NumLayers:  24,
				NumHeads:   12,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.config.Validate()
			if (err != nil) != tt.wantErr {
				t.Errorf("Config.Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestLayerNorm(t *testing.T) {
	ln := NewLayerNorm(4, 1e-5)
	input := []float64{1.0, 2.0, 3.0, 4.0}
	output := ln.Forward(input)

	if len(output) != len(input) {
		t.Errorf("LayerNorm output length = %d, want %d", len(output), len(input))
	}

	// Check that output has mean ~0 and variance ~1
	mean := 0.0
	for _, v := range output {
		mean += v
	}
	mean /= float64(len(output))

	if mean > 0.1 || mean < -0.1 {
		t.Errorf("LayerNorm output mean = %f, want ~0", mean)
	}
}

func TestSoftmax(t *testing.T) {
	input := []float64{1.0, 2.0, 3.0, 4.0}
	output := Softmax(input)

	// Check that probabilities sum to 1
	sum := 0.0
	for _, v := range output {
		sum += v
	}

	if sum < 0.99 || sum > 1.01 {
		t.Errorf("Softmax sum = %f, want ~1.0", sum)
	}

	// Check that probabilities are monotonically increasing
	for i := 1; i < len(output); i++ {
		if output[i] < output[i-1] {
			t.Errorf("Softmax not monotonic: output[%d]=%f < output[%d]=%f", i, output[i], i-1, output[i-1])
		}
	}
}

func TestMatMul(t *testing.T) {
	a := Matrix{{1, 2}, {3, 4}}
	b := Matrix{{5, 6}, {7, 8}}
	c := MatMul(a, b)

	expected := Matrix{{19, 22}, {43, 50}}

	if len(c) != len(expected) || len(c[0]) != len(expected[0]) {
		t.Errorf("MatMul dimensions incorrect")
		return
	}

	for i := range c {
		for j := range c[i] {
			if c[i][j] != expected[i][j] {
				t.Errorf("MatMul[%d][%d] = %f, want %f", i, j, c[i][j], expected[i][j])
			}
		}
	}
}

func TestEmbedding(t *testing.T) {
	emb := NewEmbedding(100, 64)

	// Initialize some weights
	for i := 0; i < 10; i++ {
		for j := 0; j < 64; j++ {
			emb.Weights[i][j] = float64(i)
		}
	}

	tokens := []int{0, 1, 2, 3}
	output := emb.Forward(tokens)

	if len(output) != len(tokens) {
		t.Errorf("Embedding output length = %d, want %d", len(output), len(tokens))
	}

	for i, vec := range output {
		if len(vec) != 64 {
			t.Errorf("Embedding vector length = %d, want 64", len(vec))
		}
		// Check that we got the right embedding
		if i < 10 && vec[0] != float64(tokens[i]) {
			t.Errorf("Embedding[%d][0] = %f, want %f", i, vec[0], float64(tokens[i]))
		}
	}
}

func TestPositionalEncoding(t *testing.T) {
	pe := NewPositionalEncoding(10, 64)
	input := [][]float64{
		make([]float64, 64),
		make([]float64, 64),
		make([]float64, 64),
	}

	output := pe.Forward(input)

	if len(output) != len(input) {
		t.Errorf("PositionalEncoding output length = %d, want %d", len(output), len(input))
	}

	// Check that output is different from input (positional encodings added)
	allZero := true
	for i := range output {
		for j := range output[i] {
			if output[i][j] != 0 {
				allZero = false
				break
			}
		}
	}

	if allZero {
		t.Error("PositionalEncoding did not add any values")
	}
}

func TestTransformer16Creation(t *testing.T) {
	config := NewDefaultConfig()
	model, err := NewTransformer16(config)

	if err != nil {
		t.Errorf("NewTransformer16() error = %v", err)
	}

	if model == nil {
		t.Fatal("NewTransformer16() returned nil model")
	}

	if len(model.Layers) != 16 {
		t.Errorf("NewTransformer16() created %d layers, want 16", len(model.Layers))
	}
}

func TestTransformer16Forward(t *testing.T) {
	config := &Config{
		VocabSize:        1000,
		HiddenSize:       64,
		NumLayers:        16,
		NumHeads:         4,
		IntermediateSize: 256,
		MaxSeqLength:     128,
		DropoutRate:      0.0,
		LayerNormEps:     1e-5,
		ActivationType:   "gelu",
	}

	model, err := NewTransformer16(config)
	if err != nil {
		t.Fatalf("NewTransformer16() error = %v", err)
	}

	// Test forward pass with a small sequence
	tokens := []int{1, 2, 3, 4, 5}
	logits, err := model.Forward(tokens)

	if err != nil {
		t.Errorf("Forward() error = %v", err)
	}

	if len(logits) != len(tokens) {
		t.Errorf("Forward() output length = %d, want %d", len(logits), len(tokens))
	}

	for i, logit := range logits {
		if len(logit) != config.VocabSize {
			t.Errorf("Forward() logits[%d] length = %d, want %d", i, len(logit), config.VocabSize)
		}
	}
}

func TestTransformer16NumParameters(t *testing.T) {
	config := NewDefaultConfig()
	model, _ := NewTransformer16(config)

	numParams := model.NumParameters()

	if numParams <= 0 {
		t.Errorf("NumParameters() = %d, want > 0", numParams)
	}

	// For default config with 16 layers, we expect millions of parameters
	expectedMin := 1000000 // At least 1M parameters
	if numParams < expectedMin {
		t.Errorf("NumParameters() = %d, want > %d", numParams, expectedMin)
	}
}

func TestTransformer16EmptyInput(t *testing.T) {
	config := NewDefaultConfig()
	model, _ := NewTransformer16(config)

	tokens := []int{}
	_, err := model.Forward(tokens)

	if err == nil {
		t.Error("Forward() with empty input should return error")
	}
}

func TestTransformer16TooLongInput(t *testing.T) {
	config := NewDefaultConfig()
	model, _ := NewTransformer16(config)

	// Create input longer than max sequence length
	tokens := make([]int, config.MaxSeqLength+10)
	for i := range tokens {
		tokens[i] = i % config.VocabSize
	}

	_, err := model.Forward(tokens)

	if err == nil {
		t.Error("Forward() with too long input should return error")
	}
}
