"""Main Kimi K2 model implementation."""

import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import KimiK2Config
from .embeddings import EmbeddingLayer
from .transformer import TransformerBlock
from .attention import create_causal_mask


class KimiK2Model(nn.Module):
    """Kimi K2 Transformer Model.
    
    This is a simplified 16-layer transformer implementation for testing purposes.
    """
    
    def __init__(self, config: KimiK2Config):
        """Initialize Kimi K2 model.
        
        Args:
            config: Model configuration
        """
        super().__init__()
        self.config = config
        
        # Embedding layer
        self.embedding = EmbeddingLayer(
            vocab_size=config.vocab_size,
            d_model=config.d_model,
            max_seq_length=config.max_seq_length,
            dropout=config.dropout
        )
        
        # Transformer blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(
                d_model=config.d_model,
                n_heads=config.n_heads,
                d_ff=config.d_ff,
                dropout=config.dropout,
                layer_norm_eps=config.layer_norm_eps
            )
            for _ in range(config.n_layers)
        ])
        
        # Final layer normalization
        self.ln_f = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        
        # Output projection
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        """Initialize weights for the model."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        use_causal_mask: bool = True
    ) -> torch.Tensor:
        """Forward pass through the model.
        
        Args:
            input_ids: Input token indices, shape (batch_size, seq_length)
            use_causal_mask: Whether to use causal masking for autoregressive generation
            
        Returns:
            Logits over vocabulary, shape (batch_size, seq_length, vocab_size)
        """
        if input_ids.dim() != 2:
            raise ValueError(f"Expected 2D input_ids, got {input_ids.dim()}D")
        
        batch_size, seq_length = input_ids.size()
        
        if seq_length == 0:
            raise ValueError("Sequence length cannot be zero")
        if seq_length > self.config.max_seq_length:
            raise ValueError(
                f"Sequence length {seq_length} exceeds maximum {self.config.max_seq_length}"
            )
        
        # Embed tokens
        x = self.embedding(input_ids)
        
        # Create causal mask if requested
        mask = None
        if use_causal_mask:
            mask = create_causal_mask(seq_length, device=input_ids.device)
        
        # Apply transformer blocks
        for block in self.blocks:
            x = block(x, mask)
        
        # Final layer normalization
        x = self.ln_f(x)
        
        # Project to vocabulary
        logits = self.lm_head(x)
        
        return logits
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int,
        temperature: float | None = None,
        top_k: int | None = None
    ) -> torch.Tensor:
        """Generate tokens autoregressively.
        
        Args:
            input_ids: Initial token indices, shape (batch_size, seq_length)
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature (uses config default if None)
            top_k: Number of top tokens to consider for sampling
            
        Returns:
            Generated token indices, shape (batch_size, seq_length + max_new_tokens)
        """
        if input_ids.dim() != 2:
            raise ValueError(f"Expected 2D input_ids, got {input_ids.dim()}D")
        if max_new_tokens <= 0:
            raise ValueError(f"max_new_tokens must be positive, got {max_new_tokens}")
        
        temp = temperature if temperature is not None else self.config.temperature
        if temp <= 0:
            raise ValueError(f"temperature must be positive, got {temp}")
        
        self.eval()
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Get current sequence length
                seq_length = input_ids.size(1)
                
                # Truncate if exceeds max length
                if seq_length > self.config.max_seq_length:
                    input_ids_context = input_ids[:, -self.config.max_seq_length:]
                else:
                    input_ids_context = input_ids
                
                # Forward pass
                logits = self.forward(input_ids_context, use_causal_mask=True)
                
                # Get logits for the last position
                logits = logits[:, -1, :] / temp
                
                # Apply top-k filtering if requested
                if top_k is not None:
                    if top_k <= 0:
                        raise ValueError(f"top_k must be positive, got {top_k}")
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = float('-inf')
                
                # Sample from the distribution
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Append to the sequence
                input_ids = torch.cat([input_ids, next_token], dim=1)
        
        return input_ids
    
    def get_num_parameters(self, non_embedding: bool = True) -> int:
        """Get the number of parameters in the model.
        
        Args:
            non_embedding: If True, exclude embedding parameters
            
        Returns:
            Number of parameters
        """
        n_params = sum(p.numel() for p in self.parameters())
        if non_embedding:
            n_params -= self.embedding.token_embedding.embedding.weight.numel()
        return n_params
