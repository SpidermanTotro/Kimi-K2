"""Multi-head self-attention implementation."""

import torch
import torch.nn as nn
import math


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""
    
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        """Initialize multi-head attention.
        
        Args:
            d_model: Dimension of the model
            n_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        if d_model <= 0:
            raise ValueError(f"d_model must be positive, got {d_model}")
        if n_heads <= 0:
            raise ValueError(f"n_heads must be positive, got {n_heads}")
        if d_model % n_heads != 0:
            raise ValueError(
                f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"
            )
        if not 0 <= dropout <= 1:
            raise ValueError(f"dropout must be between 0 and 1, got {dropout}")
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(p=dropout)
        
    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor | None = None,
        return_attention: bool = False
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        """Forward pass for multi-head attention.
        
        Args:
            x: Input tensor, shape (batch_size, seq_length, d_model)
            mask: Attention mask, shape (batch_size, seq_length, seq_length) or None
            return_attention: Whether to return attention weights
            
        Returns:
            Output tensor, shape (batch_size, seq_length, d_model)
            If return_attention is True, also returns attention weights
        """
        if x.dim() != 3:
            raise ValueError(f"Expected 3D input, got {x.dim()}D")
        if x.size(2) != self.d_model:
            raise ValueError(
                f"Expected last dimension to be {self.d_model}, got {x.size(2)}"
            )
        
        batch_size, seq_length, _ = x.size()
        
        # Linear projections
        Q = self.W_q(x)  # (batch_size, seq_length, d_model)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, seq_length, self.n_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_length, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_length, self.n_heads, self.d_k).transpose(1, 2)
        # Shape: (batch_size, n_heads, seq_length, d_k)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        # Shape: (batch_size, n_heads, seq_length, seq_length)
        
        # Apply mask if provided
        if mask is not None:
            if mask.dim() == 2:
                # Expand mask for batch and heads
                mask = mask.unsqueeze(0).unsqueeze(0)
            elif mask.dim() == 3:
                # Expand mask for heads
                mask = mask.unsqueeze(1)
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        # Apply softmax
        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        out = torch.matmul(attention_weights, V)
        # Shape: (batch_size, n_heads, seq_length, d_k)
        
        # Concatenate heads
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model)
        
        # Final linear projection
        out = self.W_o(out)
        
        if return_attention:
            return out, attention_weights
        return out


def create_causal_mask(seq_length: int, device: torch.device | None = None) -> torch.Tensor:
    """Create a causal (lower triangular) mask for autoregressive generation.
    
    Args:
        seq_length: Length of the sequence
        device: Device to create the mask on
        
    Returns:
        Causal mask, shape (seq_length, seq_length)
    """
    if seq_length <= 0:
        raise ValueError(f"seq_length must be positive, got {seq_length}")
    
    mask = torch.tril(torch.ones(seq_length, seq_length, device=device))
    return mask
