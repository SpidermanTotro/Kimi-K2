package tokenizer

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"unicode"
)

// Tokenizer provides text tokenization for the model
type Tokenizer struct {
	vocab        map[string]int
	reverseVocab map[int]string
	vocabSize    int
	
	// Special tokens
	padToken string
	bosToken string
	eosToken string
	unkToken string
	
	padTokenID int
	bosTokenID int
	eosTokenID int
	unkTokenID int
}

// NewTokenizer creates a new tokenizer with the given vocabulary size
func NewTokenizer(vocabSize int) *Tokenizer {
	t := &Tokenizer{
		vocab:        make(map[string]int),
		reverseVocab: make(map[int]string),
		vocabSize:    vocabSize,
		padToken:     "<|pad|>",
		bosToken:     "<|begin|>",
		eosToken:     "<|end|>",
		unkToken:     "<|unk|>",
	}
	
	// Add special tokens
	t.addToken(t.padToken)
	t.addToken(t.bosToken)
	t.addToken(t.eosToken)
	t.addToken(t.unkToken)
	
	t.padTokenID = t.vocab[t.padToken]
	t.bosTokenID = t.vocab[t.bosToken]
	t.eosTokenID = t.vocab[t.eosToken]
	t.unkTokenID = t.vocab[t.unkToken]
	
	return t
}

// addToken adds a token to the vocabulary
func (t *Tokenizer) addToken(token string) {
	if _, exists := t.vocab[token]; !exists {
		id := len(t.vocab)
		t.vocab[token] = id
		t.reverseVocab[id] = token
	}
}

// BuildVocab builds vocabulary from a list of texts
func (t *Tokenizer) BuildVocab(texts []string) {
	// Count token frequencies
	freq := make(map[string]int)
	
	for _, text := range texts {
		tokens := t.simpleTokenize(text)
		for _, token := range tokens {
			freq[token]++
		}
	}
	
	// Add most frequent tokens to vocabulary
	// Sort by frequency (simplified - just iterate)
	for token := range freq {
		if len(t.vocab) < t.vocabSize {
			t.addToken(token)
		}
	}
	
	// Fill remaining slots with common words
	commonWords := []string{
		"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
		"of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
		"have", "has", "had", "do", "does", "did", "will", "would", "could",
		"should", "may", "might", "can", "must", "i", "you", "he", "she", "it",
		"we", "they", "this", "that", "these", "those", "what", "which", "who",
	}
	
	for _, word := range commonWords {
		if len(t.vocab) < t.vocabSize {
			t.addToken(word)
		}
	}
}

// simpleTokenize performs basic tokenization
func (t *Tokenizer) simpleTokenize(text string) []string {
	text = strings.ToLower(text)
	
	var tokens []string
	var current strings.Builder
	
	for _, r := range text {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			current.WriteRune(r)
		} else if unicode.IsSpace(r) {
			if current.Len() > 0 {
				tokens = append(tokens, current.String())
				current.Reset()
			}
		} else {
			// Handle punctuation
			if current.Len() > 0 {
				tokens = append(tokens, current.String())
				current.Reset()
			}
			tokens = append(tokens, string(r))
		}
	}
	
	if current.Len() > 0 {
		tokens = append(tokens, current.String())
	}
	
	return tokens
}

// Encode converts text to token IDs
func (t *Tokenizer) Encode(text string, addSpecial bool) []int {
	tokens := t.simpleTokenize(text)
	ids := make([]int, 0, len(tokens)+2)
	
	if addSpecial {
		ids = append(ids, t.bosTokenID)
	}
	
	for _, token := range tokens {
		if id, exists := t.vocab[token]; exists {
			ids = append(ids, id)
		} else {
			ids = append(ids, t.unkTokenID)
		}
	}
	
	if addSpecial {
		ids = append(ids, t.eosTokenID)
	}
	
	return ids
}

// Decode converts token IDs to text
func (t *Tokenizer) Decode(ids []int, skipSpecial bool) string {
	var tokens []string
	
	specialIDs := map[int]bool{
		t.padTokenID: true,
		t.bosTokenID: true,
		t.eosTokenID: true,
	}
	
	for _, id := range ids {
		if skipSpecial && specialIDs[id] {
			continue
		}
		
		if token, exists := t.reverseVocab[id]; exists {
			tokens = append(tokens, token)
		} else {
			tokens = append(tokens, t.unkToken)
		}
	}
	
	return strings.Join(tokens, " ")
}

// GetVocabSize returns the vocabulary size
func (t *Tokenizer) GetVocabSize() int {
	return len(t.vocab)
}

// GetSpecialTokens returns the special token IDs
func (t *Tokenizer) GetSpecialTokens() map[string]int {
	return map[string]int{
		"pad": t.padTokenID,
		"bos": t.bosTokenID,
		"eos": t.eosTokenID,
		"unk": t.unkTokenID,
	}
}

// SaveVocab saves the vocabulary to a JSON file
func (t *Tokenizer) SaveVocab(filename string) error {
	data := struct {
		Vocab        map[string]int `json:"vocab"`
		VocabSize    int            `json:"vocab_size"`
		SpecialTokens map[string]string `json:"special_tokens"`
	}{
		Vocab:     t.vocab,
		VocabSize: t.vocabSize,
		SpecialTokens: map[string]string{
			"pad": t.padToken,
			"bos": t.bosToken,
			"eos": t.eosToken,
			"unk": t.unkToken,
		},
	}
	
	encoded, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal vocab: %w", err)
	}
	
	if err := os.WriteFile(filename, encoded, 0644); err != nil {
		return fmt.Errorf("failed to write vocab file: %w", err)
	}
	
	return nil
}

// LoadVocab loads the vocabulary from a JSON file
func LoadVocab(filename string) (*Tokenizer, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read vocab file: %w", err)
	}
	
	var vocabData struct {
		Vocab        map[string]int `json:"vocab"`
		VocabSize    int            `json:"vocab_size"`
		SpecialTokens map[string]string `json:"special_tokens"`
	}
	
	if err := json.Unmarshal(data, &vocabData); err != nil {
		return nil, fmt.Errorf("failed to unmarshal vocab: %w", err)
	}
	
	t := &Tokenizer{
		vocab:        vocabData.Vocab,
		reverseVocab: make(map[int]string),
		vocabSize:    vocabData.VocabSize,
		padToken:     vocabData.SpecialTokens["pad"],
		bosToken:     vocabData.SpecialTokens["bos"],
		eosToken:     vocabData.SpecialTokens["eos"],
		unkToken:     vocabData.SpecialTokens["unk"],
	}
	
	// Build reverse vocab
	for token, id := range t.vocab {
		t.reverseVocab[id] = token
	}
	
	// Set special token IDs
	t.padTokenID = t.vocab[t.padToken]
	t.bosTokenID = t.vocab[t.bosToken]
	t.eosTokenID = t.vocab[t.eosToken]
	t.unkTokenID = t.vocab[t.unkToken]
	
	return t, nil
}
