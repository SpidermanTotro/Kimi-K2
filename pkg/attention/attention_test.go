package attention

import (
	"testing"

	"gonum.org/v1/gonum/mat"
)

func TestNewAttention(t *testing.T) {
	hiddenDim := 256
	numHeads := 8
	numKVHeads := 4
	
	attn := NewAttention(hiddenDim, numHeads, numKVHeads, true, 4)
	
	if attn.numHeads != numHeads {
		t.Errorf("numHeads = %d, want %d", attn.numHeads, numHeads)
	}
	
	if attn.numKVHeads != numKVHeads {
		t.Errorf("numKVHeads = %d, want %d", attn.numKVHeads, numKVHeads)
	}
	
	expectedHeadDim := hiddenDim / numHeads
	if attn.headDim != expectedHeadDim {
		t.Errorf("headDim = %d, want %d", attn.headDim, expectedHeadDim)
	}
}

func TestAttentionInitWeights(t *testing.T) {
	attn := NewAttention(256, 8, 4, false, 2)
	attn.InitWeights()
	
	if attn.qProj == nil {
		t.Error("qProj should be initialized")
	}
	if attn.kProj == nil {
		t.Error("kProj should be initialized")
	}
	if attn.vProj == nil {
		t.Error("vProj should be initialized")
	}
	if attn.oProj == nil {
		t.Error("oProj should be initialized")
	}
	
	// Check dimensions
	r, c := attn.qProj.Dims()
	if r != 256 || c != 256 {
		t.Errorf("qProj dims = (%d, %d), want (256, 256)", r, c)
	}
}

func TestKVCacheNew(t *testing.T) {
	numLayers := 12
	cache := NewKVCache(numLayers)
	
	if cache == nil {
		t.Fatal("NewKVCache returned nil")
	}
	
	if len(cache.keys) != numLayers {
		t.Errorf("keys length = %d, want %d", len(cache.keys), numLayers)
	}
	
	if len(cache.values) != numLayers {
		t.Errorf("values length = %d, want %d", len(cache.values), numLayers)
	}
	
	if cache.seqLen != 0 {
		t.Errorf("initial seqLen = %d, want 0", cache.seqLen)
	}
}

func TestKVCacheUpdate(t *testing.T) {
	cache := NewKVCache(1)
	
	k := mat.NewDense(2, 4, []float64{1, 2, 3, 4, 5, 6, 7, 8})
	v := mat.NewDense(2, 4, []float64{9, 10, 11, 12, 13, 14, 15, 16})
	
	cache.Update(0, k, v)
	
	cachedK, cachedV := cache.Get(0)
	
	if cachedK == nil {
		t.Error("cached key is nil")
	}
	if cachedV == nil {
		t.Error("cached value is nil")
	}
	
	if cache.seqLen != 4 {
		t.Errorf("seqLen = %d, want 4", cache.seqLen)
	}
}

func TestKVCacheClear(t *testing.T) {
	cache := NewKVCache(2)
	
	k := mat.NewDense(2, 4, nil)
	v := mat.NewDense(2, 4, nil)
	
	cache.Update(0, k, v)
	cache.Update(1, k, v)
	
	cache.Clear()
	
	if cache.seqLen != 0 {
		t.Errorf("seqLen after clear = %d, want 0", cache.seqLen)
	}
	
	cachedK, cachedV := cache.Get(0)
	if cachedK != nil {
		t.Error("cached key should be nil after clear")
	}
	if cachedV != nil {
		t.Error("cached value should be nil after clear")
	}
}

func TestAttentionForward(t *testing.T) {
	hiddenDim := 64
	attn := NewAttention(hiddenDim, 4, 2, false, 2)
	attn.InitWeights()
	
	// Create input: (batch=1, hiddenDim)
	x := mat.NewDense(1, hiddenDim, nil)
	for i := 0; i < hiddenDim; i++ {
		x.Set(0, i, float64(i)/float64(hiddenDim))
	}
	
	// No mask for this test
	var mask *mat.Dense
	
	output, err := attn.Forward(x, mask, 0, nil)
	
	if err != nil {
		t.Fatalf("Forward failed: %v", err)
	}
	
	if output == nil {
		t.Fatal("Forward returned nil output")
	}
	
	r, c := output.Dims()
	if r != 1 || c != hiddenDim {
		t.Errorf("Output dims = (%d, %d), want (1, %d)", r, c, hiddenDim)
	}
}

func TestAttentionForwardWithCache(t *testing.T) {
	hiddenDim := 64
	attn := NewAttention(hiddenDim, 4, 2, false, 2)
	attn.InitWeights()
	
	cache := NewKVCache(1)
	
	x := mat.NewDense(1, hiddenDim, nil)
	for i := 0; i < hiddenDim; i++ {
		x.Set(0, i, float64(i)/float64(hiddenDim))
	}
	
	// First forward pass
	_, err := attn.Forward(x, nil, 0, cache)
	if err != nil {
		t.Fatalf("First forward failed: %v", err)
	}
	
	// Second forward pass with cache
	_, err = attn.Forward(x, nil, 0, cache)
	if err != nil {
		t.Fatalf("Second forward with cache failed: %v", err)
	}
	
	// Check cache was updated
	k, v := cache.Get(0)
	if k == nil || v == nil {
		t.Error("Cache should be populated")
	}
}

func TestFlashAttention(t *testing.T) {
	hiddenDim := 64
	attn := NewAttention(hiddenDim, 4, 2, true, 2)
	attn.InitWeights()
	
	x := mat.NewDense(1, hiddenDim, nil)
	for i := 0; i < hiddenDim; i++ {
		x.Set(0, i, float64(i)/float64(hiddenDim))
	}
	
	output, err := attn.Forward(x, nil, 0, nil)
	
	if err != nil {
		t.Fatalf("FlashAttention forward failed: %v", err)
	}
	
	if output == nil {
		t.Fatal("FlashAttention returned nil output")
	}
}

func TestHelperFunctions(t *testing.T) {
	// Test dotProduct
	a := []float64{1, 2, 3}
	b := []float64{4, 5, 6}
	result := dotProduct(a, b)
	expected := 1*4 + 2*5 + 3*6
	if result != float64(expected) {
		t.Errorf("dotProduct = %f, want %f", result, float64(expected))
	}
	
	// Test max64
	vals := []float64{1.5, 3.2, 2.1, 4.8, 2.3}
	maxVal := max64(vals)
	if maxVal != 4.8 {
		t.Errorf("max64 = %f, want 4.8", maxVal)
	}
	
	// Test max and min
	if max(5, 3) != 5 {
		t.Error("max(5, 3) should be 5")
	}
	if min(5, 3) != 3 {
		t.Error("min(5, 3) should be 3")
	}
}

func TestConcatenate(t *testing.T) {
	a := mat.NewDense(2, 3, []float64{1, 2, 3, 4, 5, 6})
	b := mat.NewDense(2, 3, []float64{7, 8, 9, 10, 11, 12})
	
	result := concatenate(a, b)
	
	r, c := result.Dims()
	if r != 4 || c != 3 {
		t.Errorf("concatenate result dims = (%d, %d), want (4, 3)", r, c)
	}
	
	// Check first element of a
	if result.At(0, 0) != 1 {
		t.Errorf("result[0,0] = %f, want 1", result.At(0, 0))
	}
	
	// Check first element of b (should be at row 2)
	if result.At(2, 0) != 7 {
		t.Errorf("result[2,0] = %f, want 7", result.At(2, 0))
	}
}

func TestSoftmax(t *testing.T) {
	m := mat.NewDense(2, 3, []float64{
		1, 2, 3,
		4, 5, 6,
	})
	
	softmax(m)
	
	// Check that each row sums to approximately 1
	for i := 0; i < 2; i++ {
		sum := 0.0
		for j := 0; j < 3; j++ {
			sum += m.At(i, j)
		}
		if sum < 0.99 || sum > 1.01 {
			t.Errorf("Row %d sum = %f, want ~1.0", i, sum)
		}
	}
}

func BenchmarkAttentionForward(b *testing.B) {
	hiddenDim := 256
	attn := NewAttention(hiddenDim, 8, 4, false, 4)
	attn.InitWeights()
	
	x := mat.NewDense(1, hiddenDim, nil)
	for i := 0; i < hiddenDim; i++ {
		x.Set(0, i, float64(i)/float64(hiddenDim))
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = attn.Forward(x, nil, 0, nil)
	}
}

func BenchmarkFlashAttention(b *testing.B) {
	hiddenDim := 256
	attn := NewAttention(hiddenDim, 8, 4, true, 4)
	attn.InitWeights()
	
	x := mat.NewDense(1, hiddenDim, nil)
	for i := 0; i < hiddenDim; i++ {
		x.Set(0, i, float64(i)/float64(hiddenDim))
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = attn.Forward(x, nil, 0, nil)
	}
}
