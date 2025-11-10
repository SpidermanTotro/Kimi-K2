"""16GB Optimized GPT Model with advanced attention mechanisms"""

from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class GroupedQueryAttention(nn.Module):
    """
    Grouped Query Attention (GQA) for memory-efficient multi-head attention.
    Uses fewer KV heads than query heads for reduced memory usage.
    """

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        num_kv_heads: int,
        dropout: float = 0.1,
    ):
        """
        Initialize Grouped Query Attention.

        Args:
            embed_dim: Embedding dimension
            num_heads: Number of query heads
            num_kv_heads: Number of key/value heads (< num_heads for GQA)
            dropout: Dropout probability
        """
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        assert (
            num_heads % num_kv_heads == 0
        ), "num_heads must be divisible by num_kv_heads"

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = embed_dim // num_heads
        self.num_queries_per_kv = num_heads // num_kv_heads

        # Projections
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.k_proj = nn.Linear(embed_dim, num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(embed_dim, num_kv_heads * self.head_dim, bias=False)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=False)

        self.dropout = nn.Dropout(dropout)
        self.scale = 1.0 / math.sqrt(self.head_dim)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """
        Forward pass with optional KV caching.

        Args:
            x: Input tensor [batch, seq_len, embed_dim]
            attention_mask: Optional attention mask
            kv_cache: Optional cached (key, value) tensors
            use_cache: Whether to return KV cache

        Returns:
            Tuple of (output, new_kv_cache)
        """
        batch_size, seq_len, _ = x.shape

        # Project queries, keys, values
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)

        # Reshape for multi-head attention
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_kv_heads, self.head_dim).transpose(
            1, 2
        )
        v = v.view(batch_size, seq_len, self.num_kv_heads, self.head_dim).transpose(
            1, 2
        )

        # Handle KV cache
        if kv_cache is not None:
            cached_k, cached_v = kv_cache
            k = torch.cat([cached_k, k], dim=2)
            v = torch.cat([cached_v, v], dim=2)

        new_kv_cache = (k, v) if use_cache else None

        # Expand KV heads to match query heads (for GQA)
        if self.num_queries_per_kv > 1:
            k = k.repeat_interleave(self.num_queries_per_kv, dim=1)
            v = v.repeat_interleave(self.num_queries_per_kv, dim=1)

        # Compute attention scores
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) * self.scale

        if attention_mask is not None:
            attn_weights = attn_weights.masked_fill(
                attention_mask == 0, float("-inf")
            )

        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # Apply attention to values
        attn_output = torch.matmul(attn_weights, v)

        # Reshape and project output
        attn_output = (
            attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        )
        output = self.out_proj(attn_output)

        return output, new_kv_cache


class FlashAttentionWrapper(nn.Module):
    """
    Wrapper for FlashAttention-style efficient attention.
    Note: This is a simplified implementation. Full FlashAttention requires custom CUDA kernels.
    """

    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        """
        Initialize FlashAttention wrapper.

        Args:
            embed_dim: Embedding dimension
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.dropout = dropout

    def forward(
        self, x: torch.Tensor, attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass using memory-efficient attention.

        Args:
            x: Input tensor [batch, seq_len, embed_dim]
            attention_mask: Optional attention mask

        Returns:
            Output tensor
        """
        batch_size, seq_len, _ = x.shape

        # Project to Q, K, V
        qkv = self.qkv_proj(x)
        qkv = qkv.view(batch_size, seq_len, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # [3, batch, heads, seq, head_dim]
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Use PyTorch's scaled_dot_product_attention if available (more efficient)
        if hasattr(F, "scaled_dot_product_attention"):
            attn_output = F.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=attention_mask,
                dropout_p=self.dropout if self.training else 0.0,
            )
        else:
            # Fallback to standard attention
            scale = 1.0 / math.sqrt(self.head_dim)
            attn_weights = torch.matmul(q, k.transpose(-2, -1)) * scale
            if attention_mask is not None:
                attn_weights = attn_weights.masked_fill(
                    attention_mask == 0, float("-inf")
                )
            attn_weights = F.softmax(attn_weights, dim=-1)
            attn_weights = F.dropout(
                attn_weights, p=self.dropout, training=self.training
            )
            attn_output = torch.matmul(attn_weights, v)

        # Reshape and project
        attn_output = (
            attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len, -1)
        )
        output = self.out_proj(attn_output)

        return output


class OptimizedGPT(nn.Module):
    """
    16GB Optimized GPT Model with grouped query attention,
    KV caching, and FlashAttention integration.
    """

    def __init__(
        self,
        vocab_size: int = 50257,
        embed_dim: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        num_kv_heads: int = 4,
        ffn_dim: int = 3072,
        max_seq_len: int = 2048,
        dropout: float = 0.1,
        use_flash_attention: bool = False,
    ):
        """
        Initialize the Optimized GPT model.

        Args:
            vocab_size: Vocabulary size
            embed_dim: Embedding dimension
            num_layers: Number of transformer layers
            num_heads: Number of query attention heads
            num_kv_heads: Number of KV heads (for GQA)
            ffn_dim: Feed-forward network dimension
            max_seq_len: Maximum sequence length
            dropout: Dropout probability
            use_flash_attention: Whether to use FlashAttention
        """
        super().__init__()

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len

        # Token and position embeddings
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)

        # Transformer layers
        self.layers = nn.ModuleList(
            [
                TransformerBlock(
                    embed_dim,
                    num_heads,
                    num_kv_heads,
                    ffn_dim,
                    dropout,
                    use_flash_attention,
                )
                for _ in range(num_layers)
            ]
        )

        self.ln_final = nn.LayerNorm(embed_dim)
        self.lm_head = nn.Linear(embed_dim, vocab_size, bias=False)

        # Tie weights
        self.lm_head.weight = self.token_embedding.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        kv_cache: Optional[list] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[list]]:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Optional attention mask
            kv_cache: Optional list of cached KV tensors for each layer
            use_cache: Whether to return KV cache

        Returns:
            Tuple of (logits, new_kv_cache)
        """
        batch_size, seq_len = input_ids.shape

        # Get embeddings
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        x = self.token_embedding(input_ids) + self.position_embedding(positions)

        # Initialize cache if needed
        if use_cache and kv_cache is None:
            kv_cache = [None] * self.num_layers

        new_kv_cache = [] if use_cache else None

        # Pass through transformer layers
        for i, layer in enumerate(self.layers):
            layer_cache = kv_cache[i] if kv_cache else None
            x, layer_new_cache = layer(x, attention_mask, layer_cache, use_cache)
            if use_cache:
                new_kv_cache.append(layer_new_cache)

        # Final layer norm and projection
        x = self.ln_final(x)
        logits = self.lm_head(x)

        return logits, new_kv_cache

    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
    ) -> torch.Tensor:
        """
        Generate tokens autoregressively.

        Args:
            input_ids: Starting token IDs [batch, seq_len]
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_k: Optional top-k sampling

        Returns:
            Generated token IDs
        """
        self.eval()
        kv_cache = None

        for _ in range(max_new_tokens):
            # Forward pass with caching
            with torch.no_grad():
                logits, kv_cache = self(
                    input_ids[:, -1:] if kv_cache else input_ids,
                    kv_cache=kv_cache,
                    use_cache=True,
                )

            # Get next token logits
            next_token_logits = logits[:, -1, :] / temperature

            # Apply top-k filtering if specified
            if top_k is not None:
                v, _ = torch.topk(next_token_logits, min(top_k, next_token_logits.size(-1)))
                next_token_logits[next_token_logits < v[:, [-1]]] = float("-inf")

            # Sample next token
            probs = F.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)

        return input_ids


class TransformerBlock(nn.Module):
    """Single transformer block with attention and FFN."""

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        num_kv_heads: int,
        ffn_dim: int,
        dropout: float,
        use_flash_attention: bool,
    ):
        super().__init__()

        # Attention layer
        if use_flash_attention:
            self.attention = FlashAttentionWrapper(embed_dim, num_heads, dropout)
            self.use_flash = True
        else:
            self.attention = GroupedQueryAttention(
                embed_dim, num_heads, num_kv_heads, dropout
            )
            self.use_flash = False

        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ffn_dim),
            nn.GELU(),
            nn.Linear(ffn_dim, embed_dim),
            nn.Dropout(dropout),
        )

        self.ln1 = nn.LayerNorm(embed_dim)
        self.ln2 = nn.LayerNorm(embed_dim)

    def forward(
        self,
        x: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        use_cache: bool = False,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        """Forward pass through transformer block."""
        # Attention with residual
        if self.use_flash:
            attn_out = self.attention(self.ln1(x), attention_mask)
            new_cache = None
        else:
            attn_out, new_cache = self.attention(
                self.ln1(x), attention_mask, kv_cache, use_cache
            )

        x = x + attn_out

        # FFN with residual
        x = x + self.ffn(self.ln2(x))

        return x, new_cache
