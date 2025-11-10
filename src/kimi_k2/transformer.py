"""Transformer block implementation."""

import torch
import torch.nn as nn

from .attention import MultiHeadAttention
from .feedforward import FeedForwardNetwork, ResidualConnection


class TransformerBlock(nn.Module):
    """Single transformer block with self-attention and feed-forward network."""
    
    def __init__(
        self,
        d_model: int,
        n_heads: int,
        d_ff: int,
        dropout: float = 0.1,
        layer_norm_eps: float = 1e-5
    ):
        """Initialize transformer block.
        
        Args:
            d_model: Dimension of the model
            n_heads: Number of attention heads
            d_ff: Dimension of the feed-forward layer
            dropout: Dropout rate
            layer_norm_eps: Epsilon for layer normalization
        """
        super().__init__()
        
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.feed_forward = FeedForwardNetwork(d_model, d_ff, dropout)
        
        self.residual1 = ResidualConnection(d_model, dropout, layer_norm_eps)
        self.residual2 = ResidualConnection(d_model, dropout, layer_norm_eps)
        
    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Forward pass for transformer block.
        
        Args:
            x: Input tensor, shape (batch_size, seq_length, d_model)
            mask: Attention mask, shape (batch_size, seq_length, seq_length) or None
            
        Returns:
            Output tensor, shape (batch_size, seq_length, d_model)
        """
        # Self-attention with residual connection
        x = self.residual1(x, lambda x: self.attention(x, mask))
        
        # Feed-forward with residual connection
        x = self.residual2(x, self.feed_forward)
        
        return x
