"""16-Layer Transformer Model with memory efficiency and autoregressive generation"""

from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class EfficientAttention(nn.Module):
    """Memory-efficient attention mechanism."""

    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)

        self.qkv_proj = nn.Linear(embed_dim, 3 * embed_dim, bias=False)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Efficient attention forward pass.

        Args:
            x: Input tensor [batch, seq_len, embed_dim]
            mask: Optional attention mask

        Returns:
            Output tensor
        """
        batch_size, seq_len, _ = x.shape

        # Project and split into Q, K, V
        qkv = self.qkv_proj(x)
        qkv = qkv.reshape(batch_size, seq_len, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Compute attention
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale

        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float("-inf"))

        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # Apply attention to values
        out = torch.matmul(attn_weights, v)
        out = out.transpose(1, 2).contiguous()
        out = out.reshape(batch_size, seq_len, self.embed_dim)

        return self.out_proj(out)


class FeedForward(nn.Module):
    """Feed-forward network with GELU activation."""

    def __init__(self, embed_dim: int, ffn_dim: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(embed_dim, ffn_dim)
        self.fc2 = nn.Linear(ffn_dim, embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        x = self.fc1(x)
        x = F.gelu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class TransformerLayer(nn.Module):
    """Single transformer layer with attention and feed-forward."""

    def __init__(
        self, embed_dim: int, num_heads: int, ffn_dim: int, dropout: float = 0.1
    ):
        super().__init__()
        self.attention = EfficientAttention(embed_dim, num_heads, dropout)
        self.ffn = FeedForward(embed_dim, ffn_dim, dropout)
        self.ln1 = nn.LayerNorm(embed_dim)
        self.ln2 = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self, x: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with residual connections."""
        # Attention block
        residual = x
        x = self.ln1(x)
        x = self.attention(x, mask)
        x = self.dropout(x)
        x = residual + x

        # FFN block
        residual = x
        x = self.ln2(x)
        x = self.ffn(x)
        x = self.dropout(x)
        x = residual + x

        return x


class TransformerModel(nn.Module):
    """
    16-Layer Transformer Model with memory efficiency and autoregressive generation.
    Optimized for reduced memory footprint while maintaining performance.
    """

    def __init__(
        self,
        vocab_size: int = 50257,
        embed_dim: int = 512,
        num_layers: int = 16,
        num_heads: int = 8,
        ffn_dim: int = 2048,
        max_seq_len: int = 1024,
        dropout: float = 0.1,
        gradient_checkpointing: bool = False,
    ):
        """
        Initialize the 16-layer transformer model.

        Args:
            vocab_size: Size of vocabulary
            embed_dim: Embedding dimension
            num_layers: Number of transformer layers (default 16)
            num_heads: Number of attention heads
            ffn_dim: Feed-forward network dimension
            max_seq_len: Maximum sequence length
            dropout: Dropout probability
            gradient_checkpointing: Enable gradient checkpointing for memory savings
        """
        super().__init__()

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        self.gradient_checkpointing = gradient_checkpointing

        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        self.dropout = nn.Dropout(dropout)

        # Transformer layers
        self.layers = nn.ModuleList(
            [
                TransformerLayer(embed_dim, num_heads, ffn_dim, dropout)
                for _ in range(num_layers)
            ]
        )

        # Output layers
        self.ln_final = nn.LayerNorm(embed_dim)
        self.output_projection = nn.Linear(embed_dim, vocab_size, bias=False)

        # Tie embeddings
        self.output_projection.weight = self.token_embedding.weight

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights using normal distribution."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.ones_(module.weight)
            torch.nn.init.zeros_(module.bias)

    def get_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """
        Create causal attention mask.

        Args:
            seq_len: Sequence length
            device: Device to create mask on

        Returns:
            Causal mask tensor
        """
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        mask = mask.view(1, 1, seq_len, seq_len)
        return mask

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        return_hidden_states: bool = False,
    ) -> Tuple[torch.Tensor, Optional[list]]:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs [batch, seq_len]
            attention_mask: Optional attention mask
            return_hidden_states: Whether to return all hidden states

        Returns:
            Tuple of (logits, optional hidden_states)
        """
        batch_size, seq_len = input_ids.shape
        device = input_ids.device

        # Get embeddings
        token_embeds = self.token_embedding(input_ids)
        positions = torch.arange(seq_len, device=device).unsqueeze(0)
        position_embeds = self.position_embedding(positions)

        x = self.dropout(token_embeds + position_embeds)

        # Create causal mask
        if attention_mask is None:
            attention_mask = self.get_causal_mask(seq_len, device)

        # Store hidden states if requested
        hidden_states = [] if return_hidden_states else None

        # Pass through transformer layers
        for layer in self.layers:
            if self.gradient_checkpointing and self.training:
                # Use gradient checkpointing to save memory
                x = torch.utils.checkpoint.checkpoint(layer, x, attention_mask)
            else:
                x = layer(x, attention_mask)

            if return_hidden_states:
                hidden_states.append(x)

        # Final layer norm and projection
        x = self.ln_final(x)
        logits = self.output_projection(x)

        return logits, hidden_states

    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 50,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        do_sample: bool = True,
    ) -> torch.Tensor:
        """
        Autoregressive generation.

        Args:
            input_ids: Starting token IDs [batch, seq_len]
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            do_sample: Whether to sample (vs. greedy)

        Returns:
            Generated token IDs
        """
        self.eval()

        for _ in range(max_new_tokens):
            # Truncate if sequence is too long
            input_chunk = (
                input_ids
                if input_ids.size(1) <= self.max_seq_len
                else input_ids[:, -self.max_seq_len :]
            )

            # Forward pass
            with torch.no_grad():
                logits, _ = self(input_chunk)

            # Get logits for last token
            next_token_logits = logits[:, -1, :] / temperature

            # Apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(next_token_logits, min(top_k, next_token_logits.size(-1)))
                next_token_logits[next_token_logits < v[:, [-1]]] = float("-inf")

            # Apply top-p (nucleus) filtering
            if top_p is not None:
                sorted_logits, sorted_indices = torch.sort(
                    next_token_logits, descending=True
                )
                cumulative_probs = torch.cumsum(
                    F.softmax(sorted_logits, dim=-1), dim=-1
                )

                # Remove tokens with cumulative probability above threshold
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
                sorted_indices_to_remove[:, 0] = 0

                indices_to_remove = sorted_indices_to_remove.scatter(
                    1, sorted_indices, sorted_indices_to_remove
                )
                next_token_logits[indices_to_remove] = float("-inf")

            # Sample or take argmax
            if do_sample:
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)

        return input_ids

    def count_parameters(self) -> int:
        """Count the number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def estimate_memory_usage(self, batch_size: int = 1, seq_len: int = 512) -> dict:
        """
        Estimate memory usage for the model.

        Args:
            batch_size: Batch size for estimation
            seq_len: Sequence length for estimation

        Returns:
            Dictionary with memory estimates in MB
        """
        param_memory = sum(p.numel() * p.element_size() for p in self.parameters())
        param_memory_mb = param_memory / (1024 ** 2)

        # Rough activation memory estimate
        activation_per_layer = batch_size * seq_len * self.embed_dim * 4  # 4 bytes per float
        total_activation = activation_per_layer * self.num_layers * 4  # Multiple tensors per layer
        activation_memory_mb = total_activation / (1024 ** 2)

        return {
            "parameters_mb": param_memory_mb,
            "activations_mb": activation_memory_mb,
            "total_estimate_mb": param_memory_mb + activation_memory_mb,
        }
