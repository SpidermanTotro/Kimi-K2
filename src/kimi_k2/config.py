"""Configuration for Kimi K2 model."""

from dataclasses import dataclass


@dataclass
class KimiK2Config:
    """Configuration class for Kimi K2 transformer model.
    
    This is a simplified configuration for a 16-layer transformer model
    for testing and demonstration purposes.
    """
    # Model architecture
    vocab_size: int = 50000
    d_model: int = 768
    n_layers: int = 16
    n_heads: int = 12
    d_ff: int = 3072
    max_seq_length: int = 2048
    dropout: float = 0.1
    
    # Layer normalization
    layer_norm_eps: float = 1e-5
    
    # Generation parameters
    temperature: float = 1.0
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.vocab_size <= 0:
            raise ValueError(f"vocab_size must be positive, got {self.vocab_size}")
        if self.d_model <= 0:
            raise ValueError(f"d_model must be positive, got {self.d_model}")
        if self.n_layers <= 0:
            raise ValueError(f"n_layers must be positive, got {self.n_layers}")
        if self.n_heads <= 0:
            raise ValueError(f"n_heads must be positive, got {self.n_heads}")
        if self.d_model % self.n_heads != 0:
            raise ValueError(
                f"d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
            )
        if self.d_ff <= 0:
            raise ValueError(f"d_ff must be positive, got {self.d_ff}")
        if self.max_seq_length <= 0:
            raise ValueError(f"max_seq_length must be positive, got {self.max_seq_length}")
        if not 0 <= self.dropout <= 1:
            raise ValueError(f"dropout must be between 0 and 1, got {self.dropout}")
        if self.temperature <= 0:
            raise ValueError(f"temperature must be positive, got {self.temperature}")
