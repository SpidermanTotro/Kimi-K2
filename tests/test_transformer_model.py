"""Tests for 16-Layer Transformer Model"""

import pytest
import torch
from kimi_k2.models import TransformerModel


class TestTransformerModel:
    """Test suite for TransformerModel class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a small model for testing
        self.model = TransformerModel(
            vocab_size=1000,
            embed_dim=128,
            num_layers=4,  # Use 4 layers for testing
            num_heads=4,
            ffn_dim=256,
            max_seq_len=256,
            dropout=0.1,
        )

    def test_initialization(self):
        """Test model initialization."""
        assert self.model is not None
        assert self.model.vocab_size == 1000
        assert self.model.embed_dim == 128
        assert self.model.num_layers == 4

    def test_16_layer_model(self):
        """Test that 16-layer model can be created."""
        model_16 = TransformerModel(
            vocab_size=1000,
            embed_dim=128,
            num_layers=16,
            num_heads=8,
            ffn_dim=512,
        )
        
        assert model_16.num_layers == 16
        assert len(model_16.layers) == 16

    def test_forward_pass(self):
        """Test forward pass."""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        logits, hidden_states = self.model(input_ids)
        
        assert logits.shape == (batch_size, seq_len, 1000)
        assert hidden_states is None  # Not returned by default

    def test_forward_pass_with_hidden_states(self):
        """Test forward pass returning hidden states."""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        logits, hidden_states = self.model(input_ids, return_hidden_states=True)
        
        assert logits.shape == (batch_size, seq_len, 1000)
        assert hidden_states is not None
        assert len(hidden_states) == self.model.num_layers

    def test_causal_mask(self):
        """Test causal mask generation."""
        seq_len = 5
        mask = self.model.get_causal_mask(seq_len, torch.device("cpu"))
        
        assert mask.shape == (1, 1, seq_len, seq_len)
        # Check it's lower triangular
        assert torch.all(mask[0, 0].tril() == mask[0, 0])

    def test_generate_basic(self):
        """Test basic text generation."""
        batch_size = 1
        seq_len = 5
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        generated = self.model.generate(input_ids, max_new_tokens=10)
        
        assert generated.shape[0] == batch_size
        assert generated.shape[1] == seq_len + 10

    def test_generate_greedy(self):
        """Test greedy generation."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        generated = self.model.generate(
            input_ids, max_new_tokens=5, do_sample=False
        )
        
        assert generated.shape[1] == 10

    def test_generate_with_sampling(self):
        """Test generation with sampling."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        generated = self.model.generate(
            input_ids, max_new_tokens=5, do_sample=True, temperature=1.0
        )
        
        assert generated.shape[1] == 10

    def test_generate_with_top_k(self):
        """Test generation with top-k sampling."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        generated = self.model.generate(
            input_ids, max_new_tokens=5, top_k=10
        )
        
        assert generated.shape[1] == 10

    def test_generate_with_top_p(self):
        """Test generation with top-p (nucleus) sampling."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        generated = self.model.generate(
            input_ids, max_new_tokens=5, top_p=0.9
        )
        
        assert generated.shape[1] == 10

    def test_generate_with_temperature(self):
        """Test generation with different temperatures."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        # Low temperature
        generated_low = self.model.generate(
            input_ids, max_new_tokens=5, temperature=0.5
        )
        
        # High temperature
        generated_high = self.model.generate(
            input_ids, max_new_tokens=5, temperature=1.5
        )
        
        assert generated_low.shape == generated_high.shape

    def test_count_parameters(self):
        """Test parameter counting."""
        param_count = self.model.count_parameters()
        
        assert param_count > 0
        assert isinstance(param_count, int)

    def test_estimate_memory_usage(self):
        """Test memory usage estimation."""
        memory = self.model.estimate_memory_usage(batch_size=4, seq_len=128)
        
        assert "parameters_mb" in memory
        assert "activations_mb" in memory
        assert "total_estimate_mb" in memory
        
        assert memory["parameters_mb"] > 0
        assert memory["activations_mb"] > 0
        assert memory["total_estimate_mb"] > 0

    def test_gradient_checkpointing(self):
        """Test model with gradient checkpointing."""
        model = TransformerModel(
            vocab_size=1000,
            embed_dim=128,
            num_layers=4,
            num_heads=4,
            ffn_dim=256,
            gradient_checkpointing=True,
        )
        
        assert model.gradient_checkpointing is True
        
        # Forward pass should still work
        input_ids = torch.randint(0, 1000, (1, 10))
        logits, _ = model(input_ids)
        assert logits is not None

    def test_max_seq_len_truncation(self):
        """Test that long sequences are truncated during generation."""
        # Create model with small max_seq_len
        model = TransformerModel(
            vocab_size=1000,
            embed_dim=64,
            num_layers=2,
            num_heads=4,
            ffn_dim=128,
            max_seq_len=20,
        )
        
        # Start with a sequence close to max length
        input_ids = torch.randint(0, 1000, (1, 18))
        generated = model.generate(input_ids, max_new_tokens=5)
        
        # Should have generated successfully
        assert generated.shape[1] == 23

    def test_model_eval_mode(self):
        """Test model in eval mode."""
        self.model.eval()
        input_ids = torch.randint(0, 1000, (1, 5))
        
        with torch.no_grad():
            logits, _ = self.model(input_ids)
        
        assert logits is not None


class TestTransformerComponents:
    """Test individual transformer components."""

    def test_efficient_attention(self):
        """Test EfficientAttention module."""
        from kimi_k2.models.transformer_model import EfficientAttention
        
        attn = EfficientAttention(embed_dim=64, num_heads=4)
        x = torch.randn(2, 10, 64)
        output = attn(x)
        
        assert output.shape == (2, 10, 64)

    def test_feed_forward(self):
        """Test FeedForward module."""
        from kimi_k2.models.transformer_model import FeedForward
        
        ffn = FeedForward(embed_dim=64, ffn_dim=128)
        x = torch.randn(2, 10, 64)
        output = ffn(x)
        
        assert output.shape == (2, 10, 64)

    def test_transformer_layer(self):
        """Test TransformerLayer module."""
        from kimi_k2.models.transformer_model import TransformerLayer
        
        layer = TransformerLayer(embed_dim=64, num_heads=4, ffn_dim=128)
        x = torch.randn(2, 10, 64)
        output = layer(x)
        
        assert output.shape == (2, 10, 64)

    def test_transformer_layer_with_mask(self):
        """Test TransformerLayer with attention mask."""
        from kimi_k2.models.transformer_model import TransformerLayer
        
        layer = TransformerLayer(embed_dim=64, num_heads=4, ffn_dim=128)
        x = torch.randn(2, 10, 64)
        mask = torch.ones(1, 1, 10, 10)
        output = layer(x, mask)
        
        assert output.shape == (2, 10, 64)
