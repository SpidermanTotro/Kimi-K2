"""Unit tests for embedding layers."""

import pytest
import torch
from kimi_k2.embeddings import TokenEmbedding, PositionalEncoding, EmbeddingLayer


class TestTokenEmbedding:
    """Test cases for TokenEmbedding."""
    
    def test_initialization(self):
        """Test token embedding initialization."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        assert emb.vocab_size == 1000
        assert emb.d_model == 128
    
    def test_negative_vocab_size(self):
        """Test that negative vocab_size raises ValueError."""
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            TokenEmbedding(vocab_size=-1, d_model=128)
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            TokenEmbedding(vocab_size=1000, d_model=-1)
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        x = torch.randint(0, 1000, (2, 10))  # batch_size=2, seq_length=10
        output = emb(x)
        assert output.shape == (2, 10, 128)
    
    def test_scaling(self):
        """Test that embeddings are scaled by sqrt(d_model)."""
        d_model = 128
        emb = TokenEmbedding(vocab_size=1000, d_model=d_model)
        x = torch.zeros((1, 1), dtype=torch.long)
        output = emb(x)
        
        # Check that scaling is applied
        raw_embedding = emb.embedding(x)
        expected = raw_embedding * (d_model ** 0.5)
        assert torch.allclose(output, expected)
    
    def test_invalid_dimension(self):
        """Test that non-2D input raises ValueError."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        x = torch.randint(0, 1000, (2, 10, 5))
        with pytest.raises(ValueError, match="Expected 2D input"):
            emb(x)
    
    def test_out_of_range_tokens_high(self):
        """Test that out-of-range tokens raise ValueError."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        x = torch.tensor([[0, 1000]])  # 1000 is out of range
        with pytest.raises(ValueError, match="Token indices must be in range"):
            emb(x)
    
    def test_out_of_range_tokens_negative(self):
        """Test that negative tokens raise ValueError."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        x = torch.tensor([[0, -1]])
        with pytest.raises(ValueError, match="Token indices must be in range"):
            emb(x)
    
    def test_single_token(self):
        """Test embedding a single token."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        x = torch.tensor([[5]])
        output = emb(x)
        assert output.shape == (1, 1, 128)
    
    def test_different_batch_sizes(self):
        """Test with different batch sizes."""
        emb = TokenEmbedding(vocab_size=1000, d_model=128)
        for batch_size in [1, 2, 4, 8]:
            x = torch.randint(0, 1000, (batch_size, 10))
            output = emb(x)
            assert output.shape == (batch_size, 10, 128)


class TestPositionalEncoding:
    """Test cases for PositionalEncoding."""
    
    def test_initialization(self):
        """Test positional encoding initialization."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512)
        assert pe.d_model == 128
        assert pe.max_seq_length == 512
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            PositionalEncoding(d_model=-1, max_seq_length=512)
    
    def test_negative_max_seq_length(self):
        """Test that negative max_seq_length raises ValueError."""
        with pytest.raises(ValueError, match="max_seq_length must be positive"):
            PositionalEncoding(d_model=128, max_seq_length=-1)
    
    def test_invalid_dropout(self):
        """Test that invalid dropout raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            PositionalEncoding(d_model=128, max_seq_length=512, dropout=1.5)
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512, dropout=0.0)
        x = torch.randn(2, 10, 128)  # batch_size=2, seq_length=10, d_model=128
        output = pe(x)
        assert output.shape == (2, 10, 128)
    
    def test_positional_encoding_added(self):
        """Test that positional encoding is added to input."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512, dropout=0.0)
        x = torch.zeros(1, 10, 128)
        output = pe(x)
        
        # Output should not be all zeros since PE is added
        assert not torch.allclose(output, x)
    
    def test_invalid_dimension(self):
        """Test that non-3D input raises ValueError."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512)
        x = torch.randn(2, 10)  # 2D input
        with pytest.raises(ValueError, match="Expected 3D input"):
            pe(x)
    
    def test_invalid_last_dimension(self):
        """Test that mismatched d_model raises ValueError."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512)
        x = torch.randn(2, 10, 64)  # d_model=64, expected 128
        with pytest.raises(ValueError, match="Expected last dimension to be 128"):
            pe(x)
    
    def test_sequence_too_long(self):
        """Test that sequence longer than max_seq_length raises ValueError."""
        pe = PositionalEncoding(d_model=128, max_seq_length=10)
        x = torch.randn(2, 20, 128)  # seq_length=20, max=10
        with pytest.raises(ValueError, match="Sequence length .* exceeds maximum"):
            pe(x)
    
    def test_maximum_sequence_length(self):
        """Test encoding at maximum sequence length."""
        max_len = 512
        pe = PositionalEncoding(d_model=128, max_seq_length=max_len, dropout=0.0)
        x = torch.randn(1, max_len, 128)
        output = pe(x)
        assert output.shape == (1, max_len, 128)
    
    def test_positional_encoding_deterministic(self):
        """Test that positional encoding is deterministic (without dropout)."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512, dropout=0.0)
        x = torch.randn(2, 10, 128)
        output1 = pe(x)
        output2 = pe(x)
        assert torch.allclose(output1, output2)
    
    def test_different_positions_different_encodings(self):
        """Test that different positions get different encodings."""
        pe = PositionalEncoding(d_model=128, max_seq_length=512, dropout=0.0)
        x = torch.zeros(1, 10, 128)
        output = pe(x)
        
        # Check that different positions have different values
        # (they shouldn't all be the same)
        for i in range(9):
            assert not torch.allclose(output[0, i], output[0, i+1])


class TestEmbeddingLayer:
    """Test cases for EmbeddingLayer."""
    
    def test_initialization(self):
        """Test embedding layer initialization."""
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=512,
            dropout=0.1
        )
        assert isinstance(emb.token_embedding, TokenEmbedding)
        assert isinstance(emb.positional_encoding, PositionalEncoding)
    
    def test_forward_pass(self):
        """Test forward pass through embedding layer."""
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=512,
            dropout=0.0
        )
        x = torch.randint(0, 1000, (2, 10))
        output = emb(x)
        assert output.shape == (2, 10, 128)
    
    def test_token_and_positional_combined(self):
        """Test that token and positional embeddings are combined."""
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=512,
            dropout=0.0
        )
        x = torch.randint(0, 1000, (1, 5))
        output = emb(x)
        
        # Should not be zero (combination of token and positional)
        assert not torch.allclose(output, torch.zeros_like(output))
    
    def test_invalid_input_propagates(self):
        """Test that invalid input is caught by token embedding."""
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=512
        )
        x = torch.tensor([[0, 1000]])  # Out of range
        with pytest.raises(ValueError):
            emb(x)
    
    def test_sequence_length_boundary(self):
        """Test at maximum sequence length boundary."""
        max_len = 100
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=max_len,
            dropout=0.0
        )
        x = torch.randint(0, 1000, (2, max_len))
        output = emb(x)
        assert output.shape == (2, max_len, 128)
    
    def test_batch_size_variations(self):
        """Test with various batch sizes."""
        emb = EmbeddingLayer(
            vocab_size=1000,
            d_model=128,
            max_seq_length=512,
            dropout=0.0
        )
        for batch_size in [1, 2, 4, 8, 16]:
            x = torch.randint(0, 1000, (batch_size, 10))
            output = emb(x)
            assert output.shape == (batch_size, 10, 128)
