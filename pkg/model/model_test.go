package model

import (
	"testing"

	"github.com/SpidermanTotro/Kimi-K2/pkg/config"
	"gonum.org/v1/gonum/mat"
)

func TestNewGPTModel(t *testing.T) {
	cfg := config.SmallConfig()
	
	m, err := NewGPTModel(cfg)
	if err != nil {
		t.Fatalf("NewGPTModel failed: %v", err)
	}
	
	if m == nil {
		t.Fatal("NewGPTModel returned nil")
	}
	
	if len(m.layers) != cfg.NumLayers {
		t.Errorf("Number of layers = %d, want %d", len(m.layers), cfg.NumLayers)
	}
	
	if m.tokenEmbedding == nil {
		t.Error("Token embedding is nil")
	}
	
	if m.posEmbedding == nil {
		t.Error("Position embedding is nil")
	}
}

func TestNewGPTModelInvalidConfig(t *testing.T) {
	cfg := &config.ModelConfig{
		VocabSize: -1, // Invalid
		HiddenDim: 128,
	}
	
	_, err := NewGPTModel(cfg)
	if err == nil {
		t.Error("Expected error for invalid config, got nil")
	}
}

func TestGPTModelForward(t *testing.T) {
	cfg := &config.ModelConfig{
		VocabSize:       1000,
		HiddenDim:       128,
		IntermediateDim: 256,
		NumLayers:       2,
		NumHeads:        4,
		NumKVHeads:      2,
		MaxSeqLen:       64,
		UseFP16:         false,
		UseFlashAttention: false,
		UseKVCache:      false,
		MaxMemoryGB:     1.0,
		ActivationFn:    "swiglu",
		LayerNormEps:    1e-5,
		NumWorkers:      2,
	}
	
	m, err := NewGPTModel(cfg)
	if err != nil {
		t.Fatalf("Failed to create model: %v", err)
	}
	
	// Test with short sequence
	inputIDs := []int{1, 2, 3, 4, 5}
	
	logits, err := m.Forward(inputIDs, false)
	if err != nil {
		t.Fatalf("Forward failed: %v", err)
	}
	
	if logits == nil {
		t.Fatal("Forward returned nil logits")
	}
	
	rows, cols := logits.Dims()
	if rows != len(inputIDs) {
		t.Errorf("Logits rows = %d, want %d", rows, len(inputIDs))
	}
	
	if cols != cfg.VocabSize {
		t.Errorf("Logits cols = %d, want %d", cols, cfg.VocabSize)
	}
}

func TestGPTModelForwardTooLong(t *testing.T) {
	cfg := &config.ModelConfig{
		VocabSize:       1000,
		HiddenDim:       128,
		IntermediateDim: 256,
		NumLayers:       2,
		NumHeads:        4,
		NumKVHeads:      2,
		MaxSeqLen:       10,
		UseFP16:         false,
		UseFlashAttention: false,
		UseKVCache:      false,
		MaxMemoryGB:     1.0,
		ActivationFn:    "swiglu",
		LayerNormEps:    1e-5,
		NumWorkers:      2,
	}
	
	m, err := NewGPTModel(cfg)
	if err != nil {
		t.Fatalf("Failed to create model: %v", err)
	}
	
	// Sequence longer than max
	inputIDs := make([]int, 20)
	
	_, err = m.Forward(inputIDs, false)
	if err == nil {
		t.Error("Expected error for sequence too long, got nil")
	}
}

func TestGPTModelGenerate(t *testing.T) {
	cfg := &config.ModelConfig{
		VocabSize:       100,
		HiddenDim:       64,
		IntermediateDim: 128,
		NumLayers:       2,
		NumHeads:        4,
		NumKVHeads:      2,
		MaxSeqLen:       32,
		UseFP16:         false,
		UseFlashAttention: false,
		UseKVCache:      true,
		MaxMemoryGB:     1.0,
		ActivationFn:    "swiglu",
		LayerNormEps:    1e-5,
		NumWorkers:      2,
	}
	
	m, err := NewGPTModel(cfg)
	if err != nil {
		t.Fatalf("Failed to create model: %v", err)
	}
	
	inputIDs := []int{1, 2, 3}
	maxNewTokens := 5
	
	outputIDs, err := m.Generate(inputIDs, maxNewTokens, 1.0)
	if err != nil {
		t.Fatalf("Generate failed: %v", err)
	}
	
	expectedLen := len(inputIDs) + maxNewTokens
	if len(outputIDs) != expectedLen {
		t.Errorf("Output length = %d, want %d", len(outputIDs), expectedLen)
	}
	
	// Check that input is preserved
	for i := 0; i < len(inputIDs); i++ {
		if outputIDs[i] != inputIDs[i] {
			t.Errorf("Input token %d changed: got %d, want %d", i, outputIDs[i], inputIDs[i])
		}
	}
}

func TestLayerNorm(t *testing.T) {
	ln := newLayerNorm(128, 1e-5)
	
	if ln == nil {
		t.Fatal("newLayerNorm returned nil")
	}
	
	if ln.weight == nil {
		t.Error("LayerNorm weight is nil")
	}
	
	if ln.bias == nil {
		t.Error("LayerNorm bias is nil")
	}
	
	// Test forward
	x := make([]float64, 128)
	for i := range x {
		x[i] = float64(i) / 128.0
	}
	
	input := matFromSlice([][]float64{x})
	output := ln.Forward(input)
	
	if output == nil {
		t.Error("LayerNorm forward returned nil")
	}
	
	r, c := output.Dims()
	if r != 1 || c != 128 {
		t.Errorf("Output dims = (%d, %d), want (1, 128)", r, c)
	}
}

func TestFeedForward(t *testing.T) {
	hiddenDim := 64
	intermediateDim := 128
	
	ffn := newFeedForward(hiddenDim, intermediateDim, 2)
	
	if ffn == nil {
		t.Fatal("newFeedForward returned nil")
	}
	
	// Test forward
	x := make([]float64, hiddenDim)
	for i := range x {
		x[i] = float64(i) / float64(hiddenDim)
	}
	
	input := matFromSlice([][]float64{x})
	output := ffn.Forward(input)
	
	if output == nil {
		t.Error("FFN forward returned nil")
	}
	
	r, c := output.Dims()
	if r != 1 || c != hiddenDim {
		t.Errorf("Output dims = (%d, %d), want (1, %d)", r, c, hiddenDim)
	}
}

func TestTransformerLayer(t *testing.T) {
	cfg := &config.ModelConfig{
		HiddenDim:       64,
		IntermediateDim: 128,
		NumLayers:       1,
		NumHeads:        4,
		NumKVHeads:      2,
		UseFlashAttention: false,
		LayerNormEps:    1e-5,
		NumWorkers:      2,
	}
	
	layer := newTransformerLayer(cfg)
	
	if layer == nil {
		t.Fatal("newTransformerLayer returned nil")
	}
	
	if layer.attention == nil {
		t.Error("Attention is nil")
	}
	
	if layer.ffn == nil {
		t.Error("FFN is nil")
	}
	
	if layer.attnNorm == nil {
		t.Error("Attention norm is nil")
	}
	
	if layer.ffnNorm == nil {
		t.Error("FFN norm is nil")
	}
}

func TestHelperFunctions(t *testing.T) {
	// Test argmax
	vals := []float64{1.0, 3.5, 2.0, 5.0, 1.5}
	idx := argmax(vals)
	if idx != 3 {
		t.Errorf("argmax = %d, want 3", idx)
	}
	
	// Test createCausalMask
	mask := createCausalMask(4)
	r, c := mask.Dims()
	if r != 4 || c != 4 {
		t.Errorf("Mask dims = (%d, %d), want (4, 4)", r, c)
	}
	
	// Check causal property: mask[i][j] = 1 if j <= i
	for i := 0; i < 4; i++ {
		for j := 0; j < 4; j++ {
			expected := 0.0
			if j <= i {
				expected = 1.0
			}
			if mask.At(i, j) != expected {
				t.Errorf("mask[%d][%d] = %f, want %f", i, j, mask.At(i, j), expected)
			}
		}
	}
}

// Helper function to create matrix from slice
func matFromSlice(data [][]float64) *mat.Dense {
	if len(data) == 0 {
		return mat.NewDense(0, 0, nil)
	}
	
	rows := len(data)
	cols := len(data[0])
	flat := make([]float64, rows*cols)
	
	for i, row := range data {
		for j, val := range row {
			flat[i*cols+j] = val
		}
	}
	
	return mat.NewDense(rows, cols, flat)
}

func BenchmarkModelForward(b *testing.B) {
	cfg := config.SmallConfig()
	m, err := NewGPTModel(cfg)
	if err != nil {
		b.Fatalf("Failed to create model: %v", err)
	}
	
	inputIDs := []int{1, 2, 3, 4, 5}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = m.Forward(inputIDs, false)
	}
}

func BenchmarkModelGenerate(b *testing.B) {
	cfg := &config.ModelConfig{
		VocabSize:       100,
		HiddenDim:       64,
		IntermediateDim: 128,
		NumLayers:       2,
		NumHeads:        4,
		NumKVHeads:      2,
		MaxSeqLen:       32,
		UseFP16:         false,
		UseFlashAttention: false,
		UseKVCache:      true,
		MaxMemoryGB:     1.0,
		ActivationFn:    "swiglu",
		LayerNormEps:    1e-5,
		NumWorkers:      2,
	}
	
	m, err := NewGPTModel(cfg)
	if err != nil {
		b.Fatalf("Failed to create model: %v", err)
	}
	
	inputIDs := []int{1, 2, 3}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = m.Generate(inputIDs, 5, 1.0)
	}
}
