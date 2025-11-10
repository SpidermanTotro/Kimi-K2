"""Embedding layer implementation."""

import torch
import torch.nn as nn
import math


class TokenEmbedding(nn.Module):
    """Token embedding layer."""
    
    def __init__(self, vocab_size: int, d_model: int):
        """Initialize token embeddings.
        
        Args:
            vocab_size: Size of the vocabulary
            d_model: Dimension of the model
        """
        super().__init__()
        if vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {vocab_size}")
        if d_model <= 0:
            raise ValueError(f"d_model must be positive, got {d_model}")
        
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for token embedding.
        
        Args:
            x: Token indices, shape (batch_size, seq_length)
            
        Returns:
            Embedded tokens, shape (batch_size, seq_length, d_model)
        """
        if x.dim() != 2:
            raise ValueError(f"Expected 2D input, got {x.dim()}D")
        if torch.any(x < 0) or torch.any(x >= self.vocab_size):
            raise ValueError(f"Token indices must be in range [0, {self.vocab_size})")
        
        return self.embedding(x) * math.sqrt(self.d_model)


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    
    def __init__(self, d_model: int, max_seq_length: int, dropout: float = 0.1):
        """Initialize positional encoding.
        
        Args:
            d_model: Dimension of the model
            max_seq_length: Maximum sequence length
            dropout: Dropout rate
        """
        super().__init__()
        if d_model <= 0:
            raise ValueError(f"d_model must be positive, got {d_model}")
        if max_seq_length <= 0:
            raise ValueError(f"max_seq_length must be positive, got {max_seq_length}")
        if not 0 <= dropout <= 1:
            raise ValueError(f"dropout must be between 0 and 1, got {dropout}")
        
        self.d_model = d_model
        self.max_seq_length = max_seq_length
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_seq_length, d_model)
        position = torch.arange(0, max_seq_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_seq_length, d_model)
        
        self.register_buffer('pe', pe)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input.
        
        Args:
            x: Input tensor, shape (batch_size, seq_length, d_model)
            
        Returns:
            Output with positional encoding, shape (batch_size, seq_length, d_model)
        """
        if x.dim() != 3:
            raise ValueError(f"Expected 3D input, got {x.dim()}D")
        if x.size(2) != self.d_model:
            raise ValueError(
                f"Expected last dimension to be {self.d_model}, got {x.size(2)}"
            )
        seq_length = x.size(1)
        if seq_length > self.max_seq_length:
            raise ValueError(
                f"Sequence length {seq_length} exceeds maximum {self.max_seq_length}"
            )
        
        x = x + self.pe[:, :seq_length, :]
        return self.dropout(x)


class EmbeddingLayer(nn.Module):
    """Combined token and positional embedding layer."""
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        max_seq_length: int,
        dropout: float = 0.1
    ):
        """Initialize embedding layer.
        
        Args:
            vocab_size: Size of the vocabulary
            d_model: Dimension of the model
            max_seq_length: Maximum sequence length
            dropout: Dropout rate
        """
        super().__init__()
        self.token_embedding = TokenEmbedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_seq_length, dropout)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for embedding layer.
        
        Args:
            x: Token indices, shape (batch_size, seq_length)
            
        Returns:
            Embedded tokens with positional encoding, 
            shape (batch_size, seq_length, d_model)
        """
        x = self.token_embedding(x)
        x = self.positional_encoding(x)
        return x
