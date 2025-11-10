"""Tests for Optimized GPT Model"""

import pytest
import torch
from kimi_k2.models import OptimizedGPT


class TestOptimizedGPT:
    """Test suite for OptimizedGPT class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a small model for testing
        self.model = OptimizedGPT(
            vocab_size=1000,
            embed_dim=64,
            num_layers=2,
            num_heads=4,
            num_kv_heads=2,
            ffn_dim=128,
            max_seq_len=128,
            dropout=0.1,
        )

    def test_initialization(self):
        """Test model initialization."""
        assert self.model is not None
        assert self.model.vocab_size == 1000
        assert self.model.embed_dim == 64
        assert self.model.num_layers == 2

    def test_forward_pass(self):
        """Test forward pass without caching."""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        logits, cache = self.model(input_ids, use_cache=False)
        
        assert logits.shape == (batch_size, seq_len, 1000)
        assert cache is None

    def test_forward_pass_with_cache(self):
        """Test forward pass with KV caching."""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        logits, cache = self.model(input_ids, use_cache=True)
        
        assert logits.shape == (batch_size, seq_len, 1000)
        assert cache is not None
        assert len(cache) == self.model.num_layers

    def test_forward_pass_with_attention_mask(self):
        """Test forward pass with attention mask."""
        batch_size = 2
        seq_len = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, 1, seq_len, seq_len)
        
        logits, _ = self.model(input_ids, attention_mask=attention_mask)
        assert logits.shape == (batch_size, seq_len, 1000)

    def test_generate_basic(self):
        """Test basic text generation."""
        batch_size = 1
        seq_len = 5
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        generated = self.model.generate(input_ids, max_new_tokens=10)
        
        assert generated.shape[0] == batch_size
        assert generated.shape[1] == seq_len + 10

    def test_generate_with_temperature(self):
        """Test generation with different temperatures."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        # Low temperature should be more deterministic
        generated_low = self.model.generate(
            input_ids, max_new_tokens=5, temperature=0.5
        )
        
        # High temperature should be more random
        generated_high = self.model.generate(
            input_ids, max_new_tokens=5, temperature=1.5
        )
        
        assert generated_low.shape == generated_high.shape

    def test_generate_with_top_k(self):
        """Test generation with top-k sampling."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        generated = self.model.generate(
            input_ids, max_new_tokens=5, top_k=10
        )
        
        assert generated.shape[1] == 10

    def test_grouped_query_attention(self):
        """Test that grouped query attention works."""
        # GQA should have fewer KV heads than query heads
        assert self.model.layers[0].attention.num_kv_heads < \
               self.model.layers[0].attention.num_heads
        
        # Forward pass should work
        input_ids = torch.randint(0, 1000, (1, 10))
        logits, _ = self.model(input_ids)
        assert logits is not None

    def test_model_eval_mode(self):
        """Test model in eval mode."""
        self.model.eval()
        input_ids = torch.randint(0, 1000, (1, 5))
        
        with torch.no_grad():
            logits, _ = self.model(input_ids)
        
        assert logits is not None

    def test_flash_attention_model(self):
        """Test model with FlashAttention enabled."""
        flash_model = OptimizedGPT(
            vocab_size=1000,
            embed_dim=64,
            num_layers=2,
            num_heads=4,
            num_kv_heads=2,
            ffn_dim=128,
            use_flash_attention=True,
        )
        
        input_ids = torch.randint(0, 1000, (1, 10))
        logits, _ = flash_model(input_ids)
        
        assert logits is not None
        assert logits.shape == (1, 10, 1000)

    def test_cache_reuse(self):
        """Test that cache can be reused across forward passes."""
        input_ids = torch.randint(0, 1000, (1, 5))
        
        # First pass with cache
        logits1, cache = self.model(input_ids, use_cache=True)
        
        # Second pass with same cache (simulating incremental generation)
        new_input = torch.randint(0, 1000, (1, 1))
        logits2, new_cache = self.model(new_input, kv_cache=cache, use_cache=True)
        
        assert logits2.shape == (1, 1, 1000)
        assert new_cache is not None


class TestGroupedQueryAttention:
    """Test suite for GroupedQueryAttention."""

    def test_gqa_initialization(self):
        """Test GQA initialization."""
        from kimi_k2.models.optimized_gpt import GroupedQueryAttention
        
        gqa = GroupedQueryAttention(
            embed_dim=64,
            num_heads=8,
            num_kv_heads=2,
        )
        
        assert gqa.num_heads == 8
        assert gqa.num_kv_heads == 2
        assert gqa.num_queries_per_kv == 4

    def test_gqa_forward(self):
        """Test GQA forward pass."""
        from kimi_k2.models.optimized_gpt import GroupedQueryAttention
        
        gqa = GroupedQueryAttention(
            embed_dim=64,
            num_heads=8,
            num_kv_heads=2,
        )
        
        x = torch.randn(2, 10, 64)
        output, cache = gqa(x, use_cache=True)
        
        assert output.shape == (2, 10, 64)
        assert cache is not None


class TestFlashAttentionWrapper:
    """Test suite for FlashAttentionWrapper."""

    def test_flash_attention_forward(self):
        """Test FlashAttention forward pass."""
        from kimi_k2.models.optimized_gpt import FlashAttentionWrapper
        
        flash = FlashAttentionWrapper(embed_dim=64, num_heads=8)
        
        x = torch.randn(2, 10, 64)
        output = flash(x)
        
        assert output.shape == (2, 10, 64)
