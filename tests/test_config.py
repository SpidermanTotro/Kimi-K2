"""Unit tests for configuration."""

import pytest
from kimi_k2.config import KimiK2Config


class TestKimiK2Config:
    """Test cases for KimiK2Config."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = KimiK2Config()
        assert config.vocab_size == 50000
        assert config.d_model == 768
        assert config.n_layers == 16
        assert config.n_heads == 12
        assert config.d_ff == 3072
        assert config.max_seq_length == 2048
        assert config.dropout == 0.1
        assert config.layer_norm_eps == 1e-5
        assert config.temperature == 1.0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = KimiK2Config(
            vocab_size=30000,
            d_model=512,
            n_layers=8,
            n_heads=8,
            d_ff=2048,
            max_seq_length=1024,
            dropout=0.2,
            temperature=0.8
        )
        assert config.vocab_size == 30000
        assert config.d_model == 512
        assert config.n_layers == 8
        assert config.n_heads == 8
        assert config.d_ff == 2048
        assert config.max_seq_length == 1024
        assert config.dropout == 0.2
        assert config.temperature == 0.8
    
    def test_negative_vocab_size(self):
        """Test that negative vocab_size raises ValueError."""
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            KimiK2Config(vocab_size=-1)
    
    def test_zero_vocab_size(self):
        """Test that zero vocab_size raises ValueError."""
        with pytest.raises(ValueError, match="vocab_size must be positive"):
            KimiK2Config(vocab_size=0)
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            KimiK2Config(d_model=-1)
    
    def test_negative_n_layers(self):
        """Test that negative n_layers raises ValueError."""
        with pytest.raises(ValueError, match="n_layers must be positive"):
            KimiK2Config(n_layers=-1)
    
    def test_negative_n_heads(self):
        """Test that negative n_heads raises ValueError."""
        with pytest.raises(ValueError, match="n_heads must be positive"):
            KimiK2Config(n_heads=-1)
    
    def test_d_model_not_divisible_by_n_heads(self):
        """Test that d_model must be divisible by n_heads."""
        with pytest.raises(ValueError, match="d_model .* must be divisible by n_heads"):
            KimiK2Config(d_model=768, n_heads=7)
    
    def test_negative_d_ff(self):
        """Test that negative d_ff raises ValueError."""
        with pytest.raises(ValueError, match="d_ff must be positive"):
            KimiK2Config(d_ff=-1)
    
    def test_negative_max_seq_length(self):
        """Test that negative max_seq_length raises ValueError."""
        with pytest.raises(ValueError, match="max_seq_length must be positive"):
            KimiK2Config(max_seq_length=-1)
    
    def test_dropout_below_zero(self):
        """Test that dropout below 0 raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            KimiK2Config(dropout=-0.1)
    
    def test_dropout_above_one(self):
        """Test that dropout above 1 raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            KimiK2Config(dropout=1.1)
    
    def test_negative_temperature(self):
        """Test that negative temperature raises ValueError."""
        with pytest.raises(ValueError, match="temperature must be positive"):
            KimiK2Config(temperature=-0.1)
    
    def test_zero_temperature(self):
        """Test that zero temperature raises ValueError."""
        with pytest.raises(ValueError, match="temperature must be positive"):
            KimiK2Config(temperature=0.0)
    
    def test_valid_edge_values(self):
        """Test valid edge case values."""
        config = KimiK2Config(
            vocab_size=1,
            d_model=2,
            n_layers=1,
            n_heads=1,
            d_ff=1,
            max_seq_length=1,
            dropout=0.0,
            temperature=0.01
        )
        assert config.vocab_size == 1
        assert config.dropout == 0.0
        
    def test_dropout_exactly_one(self):
        """Test that dropout of exactly 1.0 is valid."""
        config = KimiK2Config(dropout=1.0)
        assert config.dropout == 1.0
    
    def test_large_values(self):
        """Test with very large configuration values."""
        config = KimiK2Config(
            vocab_size=1000000,
            d_model=4096,
            n_layers=100,
            n_heads=64,
            d_ff=16384,
            max_seq_length=100000
        )
        assert config.vocab_size == 1000000
        assert config.n_layers == 100
