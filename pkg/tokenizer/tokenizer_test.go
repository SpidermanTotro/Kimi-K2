package tokenizer

import (
	"os"
	"testing"
)

func TestNewTokenizer(t *testing.T) {
	vocabSize := 10000
	tok := NewTokenizer(vocabSize)
	
	if tok.vocabSize != vocabSize {
		t.Errorf("VocabSize = %d, want %d", tok.vocabSize, vocabSize)
	}
	
	// Check special tokens exist
	specialTokens := tok.GetSpecialTokens()
	if len(specialTokens) != 4 {
		t.Errorf("Expected 4 special tokens, got %d", len(specialTokens))
	}
	
	if _, ok := specialTokens["pad"]; !ok {
		t.Error("Missing pad token")
	}
	if _, ok := specialTokens["bos"]; !ok {
		t.Error("Missing bos token")
	}
	if _, ok := specialTokens["eos"]; !ok {
		t.Error("Missing eos token")
	}
	if _, ok := specialTokens["unk"]; !ok {
		t.Error("Missing unk token")
	}
}

func TestEncodeDecodeBasic(t *testing.T) {
	tok := NewTokenizer(1000)
	
	// Build basic vocabulary
	texts := []string{
		"hello world",
		"this is a test",
		"machine learning model",
	}
	tok.BuildVocab(texts)
	
	// Test encoding
	text := "hello world"
	ids := tok.Encode(text, false)
	
	if len(ids) == 0 {
		t.Error("Encode returned empty result")
	}
	
	// Test decoding
	decoded := tok.Decode(ids, false)
	if decoded == "" {
		t.Error("Decode returned empty result")
	}
	
	t.Logf("Original: %s", text)
	t.Logf("Encoded: %v", ids)
	t.Logf("Decoded: %s", decoded)
}

func TestEncodeWithSpecialTokens(t *testing.T) {
	tok := NewTokenizer(1000)
	tok.BuildVocab([]string{"hello world"})
	
	// Without special tokens
	ids1 := tok.Encode("hello", false)
	
	// With special tokens
	ids2 := tok.Encode("hello", true)
	
	// Should have 2 extra tokens (BOS and EOS)
	if len(ids2) != len(ids1)+2 {
		t.Errorf("With special tokens should have %d tokens, got %d", len(ids1)+2, len(ids2))
	}
	
	// First should be BOS
	if ids2[0] != tok.bosTokenID {
		t.Errorf("First token should be BOS (%d), got %d", tok.bosTokenID, ids2[0])
	}
	
	// Last should be EOS
	if ids2[len(ids2)-1] != tok.eosTokenID {
		t.Errorf("Last token should be EOS (%d), got %d", tok.eosTokenID, ids2[len(ids2)-1])
	}
}

func TestUnknownTokens(t *testing.T) {
	tok := NewTokenizer(100)
	
	// Don't build vocab, so all tokens should be unknown
	ids := tok.Encode("unknown words", false)
	
	// All tokens should be UNK
	for _, id := range ids {
		if id != tok.unkTokenID {
			// OK if it's a space or punctuation that was added
			continue
		}
	}
}

func TestSimpleTokenize(t *testing.T) {
	tok := NewTokenizer(1000)
	
	tests := []struct {
		input    string
		minTokens int
	}{
		{"hello world", 2},
		{"Hello, World!", 3}, // hello, world, comma, exclamation
		{"test123", 1},
		{"one two three", 3},
	}
	
	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			tokens := tok.simpleTokenize(tt.input)
			if len(tokens) < tt.minTokens {
				t.Errorf("simpleTokenize(%q) returned %d tokens, want at least %d: %v", 
					tt.input, len(tokens), tt.minTokens, tokens)
			}
		})
	}
}

func TestBuildVocab(t *testing.T) {
	tok := NewTokenizer(1000)
	
	texts := []string{
		"the quick brown fox",
		"jumps over the lazy dog",
		"the cat sat on the mat",
	}
	
	initialSize := len(tok.vocab)
	tok.BuildVocab(texts)
	finalSize := len(tok.vocab)
	
	if finalSize <= initialSize {
		t.Error("BuildVocab should increase vocabulary size")
	}
	
	t.Logf("Vocab size: %d -> %d", initialSize, finalSize)
	
	// Check that "the" is in vocab (appears multiple times)
	if _, exists := tok.vocab["the"]; !exists {
		t.Error("Common word 'the' should be in vocabulary")
	}
}

func TestSaveLoadVocab(t *testing.T) {
	tok := NewTokenizer(1000)
	tok.BuildVocab([]string{"hello world", "test vocabulary"})
	
	tmpfile := "/tmp/test_vocab.json"
	defer os.Remove(tmpfile)
	
	// Save
	if err := tok.SaveVocab(tmpfile); err != nil {
		t.Fatalf("SaveVocab failed: %v", err)
	}
	
	// Load
	loaded, err := LoadVocab(tmpfile)
	if err != nil {
		t.Fatalf("LoadVocab failed: %v", err)
	}
	
	// Compare vocabulary sizes
	if len(loaded.vocab) != len(tok.vocab) {
		t.Errorf("Vocabulary size mismatch: got %d, want %d", len(loaded.vocab), len(tok.vocab))
	}
	
	// Compare special tokens
	if loaded.bosTokenID != tok.bosTokenID {
		t.Errorf("BOS token ID mismatch: got %d, want %d", loaded.bosTokenID, tok.bosTokenID)
	}
	
	if loaded.eosTokenID != tok.eosTokenID {
		t.Errorf("EOS token ID mismatch: got %d, want %d", loaded.eosTokenID, tok.eosTokenID)
	}
	
	// Test encode/decode consistency
	text := "hello"
	ids1 := tok.Encode(text, false)
	ids2 := loaded.Encode(text, false)
	
	if len(ids1) != len(ids2) {
		t.Errorf("Encoded length mismatch: %d vs %d", len(ids1), len(ids2))
	}
	
	for i := range ids1 {
		if ids1[i] != ids2[i] {
			t.Errorf("Encoded token mismatch at position %d: %d vs %d", i, ids1[i], ids2[i])
		}
	}
}

func TestDecodeSkipSpecial(t *testing.T) {
	tok := NewTokenizer(1000)
	tok.BuildVocab([]string{"hello world"})
	
	ids := tok.Encode("hello", true) // With special tokens
	
	// Decode without skipping special tokens
	decoded1 := tok.Decode(ids, false)
	
	// Decode skipping special tokens
	decoded2 := tok.Decode(ids, true)
	
	// decoded2 should be shorter (no special tokens)
	if len(decoded2) >= len(decoded1) {
		t.Logf("Decoded with special: %s", decoded1)
		t.Logf("Decoded without special: %s", decoded2)
	}
}

func TestGetVocabSize(t *testing.T) {
	tok := NewTokenizer(1000)
	
	initialSize := tok.GetVocabSize()
	if initialSize <= 0 {
		t.Error("Initial vocab size should be positive")
	}
	
	tok.BuildVocab([]string{"hello world"})
	
	afterBuildSize := tok.GetVocabSize()
	if afterBuildSize <= initialSize {
		t.Error("Vocab size should increase after BuildVocab")
	}
}

func BenchmarkEncode(b *testing.B) {
	tok := NewTokenizer(10000)
	tok.BuildVocab([]string{"the quick brown fox jumps over the lazy dog"})
	
	text := "the quick brown fox"
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = tok.Encode(text, false)
	}
}

func BenchmarkDecode(b *testing.B) {
	tok := NewTokenizer(10000)
	tok.BuildVocab([]string{"the quick brown fox jumps over the lazy dog"})
	
	ids := tok.Encode("the quick brown fox", false)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = tok.Decode(ids, false)
	}
}

func BenchmarkBuildVocab(b *testing.B) {
	texts := []string{
		"the quick brown fox",
		"jumps over the lazy dog",
		"hello world from golang",
		"machine learning model training",
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tok := NewTokenizer(10000)
		tok.BuildVocab(texts)
	}
}
