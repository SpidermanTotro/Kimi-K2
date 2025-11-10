"""Unit tests for transformer blocks."""

import pytest
import torch
from kimi_k2.transformer import TransformerBlock
from kimi_k2.attention import create_causal_mask


class TestTransformerBlock:
    """Test cases for TransformerBlock."""
    
    def test_initialization(self):
        """Test transformer block initialization."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.1
        )
        assert block.attention is not None
        assert block.feed_forward is not None
        assert block.residual1 is not None
        assert block.residual2 is not None
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(2, 10, 768)
        output = block(x)
        assert output.shape == (2, 10, 768)
    
    def test_with_causal_mask(self):
        """Test transformer block with causal mask."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(2, 10, 768)
        mask = create_causal_mask(10)
        output = block(x, mask=mask)
        assert output.shape == (2, 10, 768)
    
    def test_without_mask(self):
        """Test transformer block without mask."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(2, 10, 768)
        output = block(x, mask=None)
        assert output.shape == (2, 10, 768)
    
    def test_output_different_from_input(self):
        """Test that output is different from input."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(2, 10, 768)
        output = block(x)
        
        # Output should be different due to transformations
        assert not torch.allclose(output, x)
    
    def test_deterministic_in_eval_mode(self):
        """Test that output is deterministic in eval mode."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        block.eval()
        
        x = torch.randn(2, 10, 768)
        output1 = block(x)
        output2 = block(x)
        
        assert torch.allclose(output1, output2)
    
    def test_different_configurations(self):
        """Test transformer blocks with different configurations."""
        configs = [
            (256, 4, 1024, 0.1),
            (512, 8, 2048, 0.2),
            (1024, 16, 4096, 0.0),
        ]
        
        for d_model, n_heads, d_ff, dropout in configs:
            block = TransformerBlock(d_model, n_heads, d_ff, dropout)
            x = torch.randn(2, 10, d_model)
            output = block(x)
            assert output.shape == (2, 10, d_model)
    
    def test_single_token_sequence(self):
        """Test with single token sequence."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(2, 1, 768)
        output = block(x)
        assert output.shape == (2, 1, 768)
    
    def test_long_sequence(self):
        """Test with long sequence."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        x = torch.randn(1, 500, 768)
        output = block(x)
        assert output.shape == (1, 500, 768)
    
    def test_batch_size_variations(self):
        """Test with different batch sizes."""
        block = TransformerBlock(
            d_model=768,
            n_heads=12,
            d_ff=3072,
            dropout=0.0
        )
        
        for batch_size in [1, 2, 4, 8, 16]:
            x = torch.randn(batch_size, 10, 768)
            output = block(x)
            assert output.shape == (batch_size, 10, 768)
    
    def test_sequential_blocks(self):
        """Test stacking multiple transformer blocks."""
        num_layers = 4
        blocks = [
            TransformerBlock(
                d_model=256,
                n_heads=8,
                d_ff=1024,
                dropout=0.0
            )
            for _ in range(num_layers)
        ]
        
        x = torch.randn(2, 10, 256)
        for block in blocks:
            x = block(x)
        
        assert x.shape == (2, 10, 256)
    
    def test_layer_norm_eps(self):
        """Test transformer block with custom layer norm epsilon."""
        for eps in [1e-5, 1e-6, 1e-4]:
            block = TransformerBlock(
                d_model=768,
                n_heads=12,
                d_ff=3072,
                dropout=0.0,
                layer_norm_eps=eps
            )
            x = torch.randn(2, 10, 768)
            output = block(x)
            assert output.shape == (2, 10, 768)
    
    def test_residual_connections_active(self):
        """Test that residual connections are working."""
        block = TransformerBlock(
            d_model=128,
            n_heads=4,
            d_ff=512,
            dropout=0.0
        )
        
        # Create input
        x = torch.randn(1, 5, 128)
        
        # Forward pass
        output = block(x)
        
        # The output should contain information from the input
        # (due to residual connections)
        # This is hard to test directly, but we can verify
        # that the output is not independent of the input
        x_modified = x + 10.0
        output_modified = block(x_modified)
        
        # Outputs should be different
        assert not torch.allclose(output, output_modified)
    
    def test_gradient_flow(self):
        """Test that gradients flow through the block."""
        block = TransformerBlock(
            d_model=128,
            n_heads=4,
            d_ff=512,
            dropout=0.0
        )
        
        x = torch.randn(2, 10, 128, requires_grad=True)
        output = block(x)
        loss = output.sum()
        loss.backward()
        
        # Check that gradients exist
        assert x.grad is not None
        assert not torch.allclose(x.grad, torch.zeros_like(x.grad))
    
    def test_mask_effect(self):
        """Test that mask has an effect on the output."""
        block = TransformerBlock(
            d_model=128,
            n_heads=4,
            d_ff=512,
            dropout=0.0
        )
        block.eval()
        
        x = torch.randn(1, 10, 128)
        
        # Output without mask
        output_no_mask = block(x, mask=None)
        
        # Output with causal mask
        mask = create_causal_mask(10)
        output_with_mask = block(x, mask=mask)
        
        # Outputs should be different
        assert not torch.allclose(output_no_mask, output_with_mask, atol=1e-5)
