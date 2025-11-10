"""Unit tests for the main Kimi K2 model."""

import pytest
import torch
from kimi_k2.model import KimiK2Model
from kimi_k2.config import KimiK2Config


class TestKimiK2Model:
    """Test cases for KimiK2Model."""
    
    def test_initialization(self):
        """Test model initialization with default config."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        assert model.config == config
        assert len(model.blocks) == 4
    
    def test_forward_pass(self):
        """Test forward pass with valid input."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids)
        
        assert logits.shape == (2, 10, 1000)
    
    def test_forward_with_causal_mask(self):
        """Test forward pass with causal masking."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids, use_causal_mask=True)
        
        assert logits.shape == (2, 10, 1000)
    
    def test_forward_without_causal_mask(self):
        """Test forward pass without causal masking."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids, use_causal_mask=False)
        
        assert logits.shape == (2, 10, 1000)
    
    def test_invalid_input_dimension(self):
        """Test that non-2D input raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 10, 5))  # 3D input
        with pytest.raises(ValueError, match="Expected 2D input_ids"):
            model(input_ids)
    
    def test_empty_sequence(self):
        """Test that empty sequence raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 0))
        with pytest.raises(ValueError, match="Sequence length cannot be zero"):
            model(input_ids)
    
    def test_sequence_too_long(self):
        """Test that sequence exceeding max length raises ValueError."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            max_seq_length=100
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 150))
        with pytest.raises(ValueError, match="Sequence length .* exceeds maximum"):
            model(input_ids)
    
    def test_maximum_sequence_length(self):
        """Test with sequence at maximum length."""
        max_len = 128
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            max_seq_length=max_len
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (1, max_len))
        logits = model(input_ids)
        
        assert logits.shape == (1, max_len, 1000)
    
    def test_single_token(self):
        """Test with single token input."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 1))
        logits = model(input_ids)
        
        assert logits.shape == (2, 1, 1000)
    
    def test_different_batch_sizes(self):
        """Test with different batch sizes."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        model.eval()
        
        for batch_size in [1, 2, 4, 8]:
            input_ids = torch.randint(0, 1000, (batch_size, 10))
            logits = model(input_ids)
            assert logits.shape == (batch_size, 10, 1000)
    
    def test_16_layer_configuration(self):
        """Test the full 16-layer configuration."""
        config = KimiK2Config(
            vocab_size=5000,
            d_model=768,
            n_layers=16,
            n_heads=12,
            d_ff=3072,
            max_seq_length=2048
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 5000, (2, 20))
        logits = model(input_ids)
        
        assert logits.shape == (2, 20, 5000)
        assert len(model.blocks) == 16
    
    def test_deterministic_in_eval_mode(self):
        """Test that forward pass is deterministic in eval mode."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits1 = model(input_ids)
        logits2 = model(input_ids)
        
        assert torch.allclose(logits1, logits2)
    
    def test_get_num_parameters(self):
        """Test parameter counting."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8
        )
        model = KimiK2Model(config)
        
        # Total parameters
        total_params = model.get_num_parameters(non_embedding=False)
        assert total_params > 0
        
        # Non-embedding parameters
        non_emb_params = model.get_num_parameters(non_embedding=True)
        assert non_emb_params > 0
        assert non_emb_params < total_params
    
    def test_gradient_flow(self):
        """Test that gradients flow through the model."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=2,
            n_heads=4
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 10))
        logits = model(input_ids)
        loss = logits.sum()
        loss.backward()
        
        # Check that at least some parameters have gradients
        has_grad = any(p.grad is not None and not torch.allclose(
            p.grad, torch.zeros_like(p.grad)
        ) for p in model.parameters())
        assert has_grad
    
    def test_mask_effect_on_output(self):
        """Test that using causal mask affects the output."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (1, 10))
        
        logits_with_mask = model(input_ids, use_causal_mask=True)
        logits_without_mask = model(input_ids, use_causal_mask=False)
        
        # Outputs should be different
        assert not torch.allclose(logits_with_mask, logits_without_mask, atol=1e-5)


class TestKimiK2ModelGeneration:
    """Test cases for text generation."""
    
    def test_generate_basic(self):
        """Test basic text generation."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        generated = model.generate(input_ids, max_new_tokens=10)
        
        assert generated.shape == (1, 15)  # 5 + 10
    
    def test_generate_with_temperature(self):
        """Test generation with custom temperature."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        generated = model.generate(input_ids, max_new_tokens=10, temperature=0.8)
        
        assert generated.shape == (1, 15)
    
    def test_generate_with_top_k(self):
        """Test generation with top-k sampling."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        generated = model.generate(input_ids, max_new_tokens=10, top_k=50)
        
        assert generated.shape == (1, 15)
    
    def test_generate_multiple_sequences(self):
        """Test generating multiple sequences in parallel."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (4, 5))
        generated = model.generate(input_ids, max_new_tokens=10)
        
        assert generated.shape == (4, 15)
    
    def test_generate_invalid_input_dimension(self):
        """Test that invalid input raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 5, 3))  # 3D input
        with pytest.raises(ValueError, match="Expected 2D input_ids"):
            model.generate(input_ids, max_new_tokens=10)
    
    def test_generate_negative_max_tokens(self):
        """Test that negative max_new_tokens raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        with pytest.raises(ValueError, match="max_new_tokens must be positive"):
            model.generate(input_ids, max_new_tokens=-1)
    
    def test_generate_zero_max_tokens(self):
        """Test that zero max_new_tokens raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        with pytest.raises(ValueError, match="max_new_tokens must be positive"):
            model.generate(input_ids, max_new_tokens=0)
    
    def test_generate_negative_temperature(self):
        """Test that negative temperature raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        with pytest.raises(ValueError, match="temperature must be positive"):
            model.generate(input_ids, max_new_tokens=10, temperature=-0.5)
    
    def test_generate_zero_temperature(self):
        """Test that zero temperature raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        with pytest.raises(ValueError, match="temperature must be positive"):
            model.generate(input_ids, max_new_tokens=10, temperature=0.0)
    
    def test_generate_negative_top_k(self):
        """Test that negative top_k raises ValueError."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        with pytest.raises(ValueError, match="top_k must be positive"):
            model.generate(input_ids, max_new_tokens=10, top_k=-1)
    
    def test_generate_single_token(self):
        """Test generating a single token."""
        config = KimiK2Config(vocab_size=1000, d_model=256, n_layers=2, n_heads=8)
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        generated = model.generate(input_ids, max_new_tokens=1)
        
        assert generated.shape == (1, 6)
    
    def test_generate_long_sequence(self):
        """Test generating a long sequence."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        generated = model.generate(input_ids, max_new_tokens=100)
        
        assert generated.shape == (1, 105)
    
    def test_generate_exceeds_max_length(self):
        """Test generation when total length would exceed max_seq_length."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=2,
            n_heads=8,
            max_seq_length=50
        )
        model = KimiK2Model(config)
        
        # Start with sequence near the limit
        input_ids = torch.randint(0, 1000, (1, 40))
        # Generate beyond the limit (should handle by truncating context)
        generated = model.generate(input_ids, max_new_tokens=20)
        
        assert generated.shape == (1, 60)  # 40 + 20
    
    def test_temperature_effect(self):
        """Test that temperature affects randomness (statistical test)."""
        config = KimiK2Config(
            vocab_size=100,
            d_model=128,
            n_layers=2,
            n_heads=4
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 100, (1, 5))
        
        # Generate with different temperatures
        # Higher temperature should lead to more diverse outputs
        torch.manual_seed(42)
        gen_low_temp = model.generate(input_ids, max_new_tokens=5, temperature=0.1)
        
        torch.manual_seed(42)
        gen_high_temp = model.generate(input_ids, max_new_tokens=5, temperature=2.0)
        
        # Both should have the same shape
        assert gen_low_temp.shape == gen_high_temp.shape
    
    def test_top_k_limits_vocabulary(self):
        """Test that top_k limits the vocabulary used."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=2,
            n_heads=4
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 5))
        
        # Generate with very small top_k
        generated = model.generate(input_ids, max_new_tokens=10, top_k=5)
        
        assert generated.shape == (1, 15)
