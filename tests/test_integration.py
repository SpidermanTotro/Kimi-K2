"""Integration tests for the Kimi K2 model."""

import pytest
import torch
from kimi_k2.model import KimiK2Model
from kimi_k2.config import KimiK2Config


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline_small_model(self):
        """Test complete pipeline with a small model."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=4,
            n_heads=4,
            d_ff=512,
            max_seq_length=256,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        # Forward pass
        input_ids = torch.randint(0, 1000, (2, 20))
        logits = model(input_ids, use_causal_mask=True)
        assert logits.shape == (2, 20, 1000)
        
        # Generation
        generated = model.generate(input_ids, max_new_tokens=10, temperature=1.0)
        assert generated.shape == (2, 30)
    
    def test_full_pipeline_16_layer_model(self):
        """Test complete pipeline with 16-layer model."""
        config = KimiK2Config(
            vocab_size=5000,
            d_model=512,
            n_layers=16,
            n_heads=8,
            d_ff=2048,
            max_seq_length=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        # Forward pass
        input_ids = torch.randint(0, 5000, (1, 50))
        logits = model(input_ids, use_causal_mask=True)
        assert logits.shape == (1, 50, 5000)
        
        # Generation
        generated = model.generate(input_ids, max_new_tokens=20, temperature=0.8)
        assert generated.shape == (1, 70)
    
    def test_varying_input_lengths(self):
        """Test with varying input lengths."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=8,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        lengths = [1, 5, 10, 20, 50, 100, 200]
        for length in lengths:
            input_ids = torch.randint(0, 1000, (1, length))
            logits = model(input_ids)
            assert logits.shape == (1, length, 1000)
    
    def test_batch_processing(self):
        """Test processing batches of different sizes."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=256,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        batch_sizes = [1, 2, 4, 8, 16]
        for batch_size in batch_sizes:
            input_ids = torch.randint(0, 1000, (batch_size, 20))
            logits = model(input_ids)
            assert logits.shape == (batch_size, 20, 1000)
    
    def test_cumulative_transformer_blocks(self):
        """Test cumulative computation through transformer blocks."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=8,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        
        # Get embeddings
        x = model.embedding(input_ids)
        initial_representation = x.clone()
        
        # Apply each block sequentially and verify changes
        for i, block in enumerate(model.blocks):
            x_before = x.clone()
            x = block(x, mask=None)
            
            # Each block should transform the representation
            assert not torch.allclose(x, x_before), f"Block {i} did not transform input"
        
        # Final representation should be very different from initial
        assert not torch.allclose(x, initial_representation)
    
    def test_generation_with_temperature_scaling(self):
        """Test that temperature scaling works correctly in generation."""
        config = KimiK2Config(
            vocab_size=500,
            d_model=128,
            n_layers=4,
            n_heads=4,
            d_ff=512,
            max_seq_length=256
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 500, (1, 10))
        
        # Test with different temperatures
        temperatures = [0.5, 1.0, 1.5, 2.0]
        for temp in temperatures:
            generated = model.generate(
                input_ids,
                max_new_tokens=5,
                temperature=temp
            )
            assert generated.shape == (1, 15)
    
    def test_consistent_forward_backward(self):
        """Test that forward and backward passes are consistent."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 10))
        
        # Forward pass
        logits = model(input_ids)
        
        # Compute a simple loss
        target = torch.randint(0, 1000, (2, 10))
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, 1000),
            target.view(-1)
        )
        
        # Backward pass
        loss.backward()
        
        # Verify gradients exist for parameters
        for name, param in model.named_parameters():
            assert param.grad is not None, f"No gradient for {name}"
    
    def test_different_configurations(self):
        """Test various model configurations."""
        configurations = [
            # Small model
            (500, 128, 2, 4, 512, 128),
            # Medium model
            (2000, 256, 8, 8, 1024, 512),
            # Large model
            (5000, 512, 16, 8, 2048, 1024),
        ]
        
        for vocab_size, d_model, n_layers, n_heads, d_ff, max_len in configurations:
            config = KimiK2Config(
                vocab_size=vocab_size,
                d_model=d_model,
                n_layers=n_layers,
                n_heads=n_heads,
                d_ff=d_ff,
                max_seq_length=max_len,
                dropout=0.0
            )
            model = KimiK2Model(config)
            model.eval()
            
            input_ids = torch.randint(0, vocab_size, (2, 10))
            logits = model(input_ids)
            assert logits.shape == (2, 10, vocab_size)
    
    def test_training_mode_consistency(self):
        """Test model behavior in training vs eval mode."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.1  # Non-zero dropout
        )
        model = KimiK2Model(config)
        input_ids = torch.randint(0, 1000, (2, 10))
        
        # Training mode - outputs may vary due to dropout
        model.train()
        logits_train1 = model(input_ids)
        logits_train2 = model(input_ids)
        # May be different due to dropout
        assert logits_train1.shape == logits_train2.shape
        
        # Eval mode - outputs should be consistent
        model.eval()
        with torch.no_grad():
            logits_eval1 = model(input_ids)
            logits_eval2 = model(input_ids)
        assert torch.allclose(logits_eval1, logits_eval2)


class TestBoundaryConditions:
    """Tests for boundary conditions and edge cases."""
    
    def test_minimum_configuration(self):
        """Test with minimum valid configuration."""
        config = KimiK2Config(
            vocab_size=10,
            d_model=8,
            n_layers=1,
            n_heads=1,
            d_ff=16,
            max_seq_length=10,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 10, (1, 5))
        logits = model(input_ids)
        assert logits.shape == (1, 5, 10)
    
    def test_single_layer_model(self):
        """Test with single transformer layer."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=1,
            n_heads=8,
            d_ff=1024
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids)
        assert logits.shape == (2, 10, 1000)
    
    def test_maximum_sequence_length_boundary(self):
        """Test at exact maximum sequence length."""
        max_len = 256
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=2,
            n_heads=4,
            max_seq_length=max_len
        )
        model = KimiK2Model(config)
        model.eval()
        
        # Exactly at max length
        input_ids = torch.randint(0, 1000, (1, max_len))
        logits = model(input_ids)
        assert logits.shape == (1, max_len, 1000)
        
        # One over max length should fail
        input_ids_too_long = torch.randint(0, 1000, (1, max_len + 1))
        with pytest.raises(ValueError):
            model(input_ids_too_long)
    
    def test_zero_dropout(self):
        """Test model with zero dropout."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits1 = model(input_ids)
        logits2 = model(input_ids)
        
        # Should be deterministic with zero dropout
        assert torch.allclose(logits1, logits2)
    
    def test_maximum_dropout(self):
        """Test model with maximum dropout."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            dropout=1.0  # Maximum dropout
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 10))
        
        # Should still work (though output will be heavily affected)
        logits = model(input_ids)
        assert logits.shape == (2, 10, 1000)
    
    def test_single_head_attention(self):
        """Test with single attention head."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=64,
            n_layers=4,
            n_heads=1,
            d_ff=256
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids)
        assert logits.shape == (2, 10, 1000)
    
    def test_many_attention_heads(self):
        """Test with many attention heads."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=512,
            n_layers=4,
            n_heads=64,  # Many heads
            d_ff=2048
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids)
        assert logits.shape == (2, 10, 1000)
    
    def test_very_small_vocabulary(self):
        """Test with very small vocabulary."""
        config = KimiK2Config(
            vocab_size=5,
            d_model=32,
            n_layers=2,
            n_heads=2,
            d_ff=64
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 5, (2, 10))
        logits = model(input_ids)
        assert logits.shape == (2, 10, 5)
    
    def test_generation_at_context_limit(self):
        """Test generation when starting near context limit."""
        max_len = 50
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=2,
            n_heads=4,
            max_seq_length=max_len
        )
        model = KimiK2Model(config)
        
        # Start with sequence near the limit
        input_ids = torch.randint(0, 1000, (1, max_len - 5))
        
        # Generate a few more tokens
        generated = model.generate(input_ids, max_new_tokens=10)
        
        # Should handle truncation internally
        assert generated.shape[1] == max_len - 5 + 10
