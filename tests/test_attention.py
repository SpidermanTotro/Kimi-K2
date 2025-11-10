"""Unit tests for attention mechanisms."""

import pytest
import torch
from kimi_k2.attention import MultiHeadAttention, create_causal_mask


class TestMultiHeadAttention:
    """Test cases for MultiHeadAttention."""
    
    def test_initialization(self):
        """Test multi-head attention initialization."""
        attn = MultiHeadAttention(d_model=768, n_heads=12)
        assert attn.d_model == 768
        assert attn.n_heads == 12
        assert attn.d_k == 64
    
    def test_negative_d_model(self):
        """Test that negative d_model raises ValueError."""
        with pytest.raises(ValueError, match="d_model must be positive"):
            MultiHeadAttention(d_model=-1, n_heads=12)
    
    def test_negative_n_heads(self):
        """Test that negative n_heads raises ValueError."""
        with pytest.raises(ValueError, match="n_heads must be positive"):
            MultiHeadAttention(d_model=768, n_heads=-1)
    
    def test_d_model_not_divisible(self):
        """Test that d_model must be divisible by n_heads."""
        with pytest.raises(ValueError, match="d_model .* must be divisible by n_heads"):
            MultiHeadAttention(d_model=768, n_heads=7)
    
    def test_invalid_dropout(self):
        """Test that invalid dropout raises ValueError."""
        with pytest.raises(ValueError, match="dropout must be between 0 and 1"):
            MultiHeadAttention(d_model=768, n_heads=12, dropout=1.5)
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(2, 10, 768)  # batch_size=2, seq_length=10
        output = attn(x)
        assert output.shape == (2, 10, 768)
    
    def test_invalid_input_dimension(self):
        """Test that non-3D input raises ValueError."""
        attn = MultiHeadAttention(d_model=768, n_heads=12)
        x = torch.randn(2, 10)  # 2D input
        with pytest.raises(ValueError, match="Expected 3D input"):
            attn(x)
    
    def test_invalid_d_model_dimension(self):
        """Test that mismatched d_model raises ValueError."""
        attn = MultiHeadAttention(d_model=768, n_heads=12)
        x = torch.randn(2, 10, 512)  # d_model=512, expected 768
        with pytest.raises(ValueError, match="Expected last dimension to be 768"):
            attn(x)
    
    def test_with_causal_mask(self):
        """Test attention with causal mask."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(2, 10, 768)
        mask = create_causal_mask(10)
        output = attn(x, mask=mask)
        assert output.shape == (2, 10, 768)
    
    def test_mask_shapes(self):
        """Test attention with different mask shapes."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(2, 10, 768)
        
        # 2D mask
        mask_2d = torch.ones(10, 10)
        output_2d = attn(x, mask=mask_2d)
        assert output_2d.shape == (2, 10, 768)
        
        # 3D mask
        mask_3d = torch.ones(2, 10, 10)
        output_3d = attn(x, mask=mask_3d)
        assert output_3d.shape == (2, 10, 768)
        
        # 4D mask (already properly expanded)
        mask_4d = torch.ones(2, 12, 10, 10)
        output_4d = attn(x, mask=mask_4d)
        assert output_4d.shape == (2, 10, 768)
    
    def test_return_attention_weights(self):
        """Test returning attention weights."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(2, 10, 768)
        output, weights = attn(x, return_attention=True)
        
        assert output.shape == (2, 10, 768)
        assert weights.shape == (2, 12, 10, 10)  # (batch, heads, seq, seq)
    
    def test_attention_weights_sum_to_one(self):
        """Test that attention weights sum to 1 along the last dimension."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(1, 5, 768)
        _, weights = attn(x, return_attention=True)
        
        # Sum along the last dimension (attending to other positions)
        sums = weights.sum(dim=-1)
        assert torch.allclose(sums, torch.ones_like(sums), atol=1e-5)
    
    def test_single_head(self):
        """Test with single attention head."""
        attn = MultiHeadAttention(d_model=64, n_heads=1, dropout=0.0)
        x = torch.randn(2, 10, 64)
        output = attn(x)
        assert output.shape == (2, 10, 64)
    
    def test_many_heads(self):
        """Test with many attention heads."""
        attn = MultiHeadAttention(d_model=768, n_heads=64, dropout=0.0)
        x = torch.randn(2, 10, 768)
        output = attn(x)
        assert output.shape == (2, 10, 768)
    
    def test_sequence_length_one(self):
        """Test with sequence length of 1."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(2, 1, 768)
        output = attn(x)
        assert output.shape == (2, 1, 768)
    
    def test_long_sequence(self):
        """Test with long sequence."""
        attn = MultiHeadAttention(d_model=768, n_heads=12, dropout=0.0)
        x = torch.randn(1, 1000, 768)
        output = attn(x)
        assert output.shape == (1, 1000, 768)
    
    def test_causal_mask_prevents_future_attention(self):
        """Test that causal mask prevents attending to future positions."""
        attn = MultiHeadAttention(d_model=64, n_heads=4, dropout=0.0)
        x = torch.randn(1, 5, 64)
        mask = create_causal_mask(5)
        _, weights = attn(x, mask=mask, return_attention=True)
        
        # Average across heads and batch
        avg_weights = weights.mean(dim=(0, 1))  # (seq, seq)
        
        # Check that upper triangular part (future) has very small weights
        for i in range(5):
            for j in range(i + 1, 5):
                # Future positions should have near-zero attention
                assert avg_weights[i, j] < 1e-5
    
    def test_no_mask_allows_all_attention(self):
        """Test that without mask, all positions can attend to each other."""
        attn = MultiHeadAttention(d_model=64, n_heads=4, dropout=0.0)
        x = torch.randn(1, 5, 64)
        _, weights = attn(x, mask=None, return_attention=True)
        
        # All weights should be positive
        assert torch.all(weights > 0)


class TestCreateCausalMask:
    """Test cases for create_causal_mask."""
    
    def test_basic_mask(self):
        """Test basic causal mask creation."""
        mask = create_causal_mask(5)
        assert mask.shape == (5, 5)
        assert mask.dtype == torch.float32
    
    def test_mask_is_lower_triangular(self):
        """Test that mask is lower triangular."""
        mask = create_causal_mask(5)
        
        # Lower triangular (including diagonal) should be 1
        for i in range(5):
            for j in range(i + 1):
                assert mask[i, j] == 1
        
        # Upper triangular should be 0
        for i in range(5):
            for j in range(i + 1, 5):
                assert mask[i, j] == 0
    
    def test_negative_seq_length(self):
        """Test that negative seq_length raises ValueError."""
        with pytest.raises(ValueError, match="seq_length must be positive"):
            create_causal_mask(-1)
    
    def test_zero_seq_length(self):
        """Test that zero seq_length raises ValueError."""
        with pytest.raises(ValueError, match="seq_length must be positive"):
            create_causal_mask(0)
    
    def test_mask_size_one(self):
        """Test mask with size 1."""
        mask = create_causal_mask(1)
        assert mask.shape == (1, 1)
        assert mask[0, 0] == 1
    
    def test_large_mask(self):
        """Test creating a large mask."""
        mask = create_causal_mask(1000)
        assert mask.shape == (1000, 1000)
        # Check a few positions
        assert mask[0, 0] == 1
        assert mask[999, 999] == 1
        assert mask[0, 999] == 0
        assert mask[500, 499] == 1
        assert mask[500, 501] == 0
    
    def test_mask_device(self):
        """Test mask creation on specific device."""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            mask = create_causal_mask(5, device=device)
            assert mask.device.type == 'cuda'
        
        # CPU device
        device = torch.device('cpu')
        mask = create_causal_mask(5, device=device)
        assert mask.device.type == 'cpu'
    
    def test_mask_values(self):
        """Test specific mask values for small mask."""
        mask = create_causal_mask(3)
        expected = torch.tensor([
            [1, 0, 0],
            [1, 1, 0],
            [1, 1, 1]
        ], dtype=torch.float32)
        assert torch.equal(mask, expected)
