"""Feed-forward network and layer components."""

import torch
import torch.nn as nn


class FeedForwardNetwork(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        """Initialize feed-forward network.
        
        Args:
            d_model: Dimension of the model
            d_ff: Dimension of the feed-forward layer
            dropout: Dropout rate
        """
        super().__init__()
        if d_model <= 0:
            raise ValueError(f"d_model must be positive, got {d_model}")
        if d_ff <= 0:
            raise ValueError(f"d_ff must be positive, got {d_ff}")
        if not 0 <= dropout <= 1:
            raise ValueError(f"dropout must be between 0 and 1, got {dropout}")
        
        self.d_model = d_model
        self.d_ff = d_ff
        
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(p=dropout)
        self.activation = nn.GELU()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for feed-forward network.
        
        Args:
            x: Input tensor, shape (batch_size, seq_length, d_model)
            
        Returns:
            Output tensor, shape (batch_size, seq_length, d_model)
        """
        if x.dim() != 3:
            raise ValueError(f"Expected 3D input, got {x.dim()}D")
        if x.size(2) != self.d_model:
            raise ValueError(
                f"Expected last dimension to be {self.d_model}, got {x.size(2)}"
            )
        
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x


class ResidualConnection(nn.Module):
    """Residual connection with layer normalization."""
    
    def __init__(self, d_model: int, dropout: float = 0.1, eps: float = 1e-5):
        """Initialize residual connection.
        
        Args:
            d_model: Dimension of the model
            dropout: Dropout rate
            eps: Epsilon for layer normalization
        """
        super().__init__()
        if d_model <= 0:
            raise ValueError(f"d_model must be positive, got {d_model}")
        if not 0 <= dropout <= 1:
            raise ValueError(f"dropout must be between 0 and 1, got {dropout}")
        
        self.norm = nn.LayerNorm(d_model, eps=eps)
        self.dropout = nn.Dropout(p=dropout)
        
    def forward(self, x: torch.Tensor, sublayer: nn.Module) -> torch.Tensor:
        """Apply residual connection with layer normalization.
        
        Args:
            x: Input tensor
            sublayer: Sublayer to apply
            
        Returns:
            Output with residual connection
        """
        return x + self.dropout(sublayer(self.norm(x)))
