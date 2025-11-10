"""Unit tests for feed-forward network and residual connections."""

import pytest
import torch
import torch.nn as nn
from kimi_k2.feedforward import FeedForwardNetwork, ResidualConnection


class TestFeedForwardNetwork:
    """Test cases for FeedForwardNetwork."""
    
    def test_initialization(self):
        """Test feed-forward network initialization."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072)
        assert ffn.d_model == 768
        assert ffn.d_ff == 3072
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            FeedForwardNetwork(d_model=-1, d_ff=3072)
    
    def test_negative_d_ff(self):
        """Test that negative d_ff raises ValueError."""
        with pytest.raises(ValueError, match="d_ff must be positive"):
            FeedForwardNetwork(d_model=768, d_ff=-1)
    
    def test_invalid_dropout(self):
        """Test that invalid dropout raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            FeedForwardNetwork(d_model=768, d_ff=3072, dropout=1.5)
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072, dropout=0.0)
        x = torch.randn(2, 10, 768)
        output = ffn(x)
        assert output.shape == (2, 10, 768)
    
    def test_invalid_input_dimension(self):
        """Test that non-3D input raises ValueError."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072)
        x = torch.randn(2, 10)  # 2D input
        with pytest.raises(ValueError, match="Expected 3D input"):
            ffn(x)
    
    def test_invalid_d_model_dimension(self):
        """Test that mismatched d_model raises ValueError."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072)
        x = torch.randn(2, 10, 512)  # d_model=512, expected 768
        with pytest.raises(ValueError, match="Expected last dimension to be 768"):
            ffn(x)
    
    def test_output_shape_preserved(self):
        """Test that output shape matches input shape."""
        ffn = FeedForwardNetwork(d_model=256, d_ff=1024, dropout=0.0)
        for batch_size in [1, 2, 4]:
            for seq_length in [5, 10, 20]:
                x = torch.randn(batch_size, seq_length, 256)
                output = ffn(x)
                assert output.shape == x.shape
    
    def test_activation_function(self):
        """Test that GELU activation is applied."""
        ffn = FeedForwardNetwork(d_model=64, d_ff=256, dropout=0.0)
        assert isinstance(ffn.activation, nn.GELU)
    
    def test_expansion_and_projection(self):
        """Test that FFN expands and projects correctly."""
        d_model = 128
        d_ff = 512
        ffn = FeedForwardNetwork(d_model=d_model, d_ff=d_ff, dropout=0.0)
        
        # Check layer dimensions
        assert ffn.linear1.out_features == d_ff
        assert ffn.linear2.in_features == d_ff
        assert ffn.linear2.out_features == d_model
    
    def test_single_token(self):
        """Test with single token sequence."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072, dropout=0.0)
        x = torch.randn(2, 1, 768)
        output = ffn(x)
        assert output.shape == (2, 1, 768)
    
    def test_long_sequence(self):
        """Test with long sequence."""
        ffn = FeedForwardNetwork(d_model=768, d_ff=3072, dropout=0.0)
        x = torch.randn(1, 1000, 768)
        output = ffn(x)
        assert output.shape == (1, 1000, 768)
    
    def test_deterministic_without_dropout(self):
        """Test that output is deterministic without dropout."""
        ffn = FeedForwardNetwork(d_model=128, d_ff=512, dropout=0.0)
        ffn.eval()
        x = torch.randn(2, 10, 128)
        output1 = ffn(x)
        output2 = ffn(x)
        assert torch.allclose(output1, output2)
    
    def test_different_dropout_values(self):
        """Test initialization with different dropout values."""
        for dropout in [0.0, 0.1, 0.5, 1.0]:
            ffn = FeedForwardNetwork(d_model=128, d_ff=512, dropout=dropout)
            assert ffn.dropout.p == dropout


class TestResidualConnection:
    """Test cases for ResidualConnection."""
    
    def test_initialization(self):
        """Test residual connection initialization."""
        res = ResidualConnection(d_model=768)
        assert isinstance(res.norm, nn.LayerNorm)
        assert isinstance(res.dropout, nn.Dropout)
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            ResidualConnection(d_model=-1)
    
    def test_invalid_dropout(self):
        """Test that invalid dropout raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            ResidualConnection(d_model=768, dropout=1.5)
    
    def test_forward_with_identity_sublayer(self):
        """Test residual connection with identity sublayer."""
        res = ResidualConnection(d_model=768, dropout=0.0)
        x = torch.randn(2, 10, 768)
        
        # Identity sublayer (returns input unchanged)
        identity = lambda x: torch.zeros_like(x)
        output = res(x, identity)
        
        # Should be close to input (since sublayer returns zeros)
        # Output = x + dropout(sublayer(norm(x))) = x + dropout(0) = x
        assert output.shape == x.shape
    
    def test_residual_added(self):
        """Test that residual is actually added."""
        res = ResidualConnection(d_model=768, dropout=0.0)
        x = torch.randn(2, 10, 768)
        
        # Sublayer that returns fixed values
        sublayer = lambda x: torch.ones_like(x)
        output = res(x, sublayer)
        
        # Output should not equal input (sublayer adds ones)
        assert not torch.allclose(output, x)
    
    def test_layer_norm_applied(self):
        """Test that layer normalization is applied before sublayer."""
        res = ResidualConnection(d_model=768, dropout=0.0)
        x = torch.randn(2, 10, 768)
        
        # Track whether norm was applied
        norm_applied = False
        def checking_sublayer(x):
            nonlocal norm_applied
            # If norm was applied, mean should be close to 0, var close to 1
            mean = x.mean(dim=-1)
            var = x.var(dim=-1, unbiased=False)
            norm_applied = torch.allclose(mean, torch.zeros_like(mean), atol=1e-5) and \
                          torch.allclose(var, torch.ones_like(var), atol=1e-1)
            return torch.zeros_like(x)
        
        res(x, checking_sublayer)
        assert norm_applied
    
    def test_different_eps_values(self):
        """Test initialization with different epsilon values."""
        for eps in [1e-5, 1e-6, 1e-4]:
            res = ResidualConnection(d_model=768, eps=eps)
            assert res.norm.eps == eps
    
    def test_output_shape_preserved(self):
        """Test that output shape matches input shape."""
        res = ResidualConnection(d_model=256, dropout=0.0)
        sublayer = lambda x: x
        
        for batch_size in [1, 2, 4]:
            for seq_length in [5, 10, 20]:
                x = torch.randn(batch_size, seq_length, 256)
                output = res(x, sublayer)
                assert output.shape == x.shape
    
    def test_with_real_ffn(self):
        """Test residual connection with actual feed-forward network."""
        d_model = 768
        res = ResidualConnection(d_model=d_model, dropout=0.0)
        ffn = FeedForwardNetwork(d_model=d_model, d_ff=3072, dropout=0.0)
        
        x = torch.randn(2, 10, d_model)
        output = res(x, ffn)
        
        assert output.shape == x.shape
        # Output should be different from input
        assert not torch.allclose(output, x)
    
    def test_deterministic_without_dropout(self):
        """Test that output is deterministic without dropout."""
        res = ResidualConnection(d_model=128, dropout=0.0)
        res.eval()
        x = torch.randn(2, 10, 128)
        sublayer = lambda x: x
        
        output1 = res(x, sublayer)
        output2 = res(x, sublayer)
        assert torch.allclose(output1, output2)
    
    def test_single_element(self):
        """Test with single element in sequence."""
        res = ResidualConnection(d_model=768, dropout=0.0)
        x = torch.randn(1, 1, 768)
        sublayer = lambda x: x
        output = res(x, sublayer)
        assert output.shape == (1, 1, 768)
    
    def test_batch_size_one(self):
        """Test with batch size of 1."""
        res = ResidualConnection(d_model=768, dropout=0.0)
        x = torch.randn(1, 10, 768)
        sublayer = lambda x: torch.zeros_like(x)
        output = res(x, sublayer)
        assert output.shape == (1, 10, 768)
