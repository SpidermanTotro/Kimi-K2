"""
Example: Using the Optimized GPT Model

This example demonstrates the optimized GPT model with grouped query attention,
KV caching, and FlashAttention.
"""

import torch
from kimi_k2.models import OptimizedGPT


def main():
    """Run the optimized GPT example."""
    print("=== Optimized GPT Model Example ===\n")
    
    # Create a small model for demonstration
    print("1. Creating Optimized GPT model...\n")
    model = OptimizedGPT(
        vocab_size=1000,
        embed_dim=256,
        num_layers=6,
        num_heads=8,
        num_kv_heads=4,  # Grouped Query Attention
        ffn_dim=1024,
        max_seq_len=512,
        dropout=0.1,
        use_flash_attention=False,
    )
    
    print(f"   Model configuration:")
    print(f"   - Vocabulary size: {model.vocab_size}")
    print(f"   - Embedding dimension: {model.embed_dim}")
    print(f"   - Number of layers: {model.num_layers}")
    print(f"   - Attention heads: {model.layers[0].attention.num_heads}")
    print(f"   - KV heads: {model.layers[0].attention.num_kv_heads}")
    print(f"   - Max sequence length: {model.max_seq_len}\n")
    
    # Forward pass without caching
    print("2. Forward pass without KV caching...\n")
    batch_size = 2
    seq_len = 20
    
    input_ids = torch.randint(0, 1000, (batch_size, seq_len))
    
    with torch.no_grad():
        logits, cache = model(input_ids, use_cache=False)
    
    print(f"   Input shape: {input_ids.shape}")
    print(f"   Output logits shape: {logits.shape}")
    print(f"   Cache: {cache}\n")
    
    # Forward pass with caching
    print("3. Forward pass with KV caching...\n")
    
    with torch.no_grad():
        logits, cache = model(input_ids, use_cache=True)
    
    print(f"   Output logits shape: {logits.shape}")
    print(f"   Cache layers: {len(cache) if cache else 0}")
    if cache:
        k, v = cache[0]
        print(f"   First layer cache shapes: K={k.shape}, V={v.shape}\n")
    
    # Generation with greedy decoding
    print("4. Text generation (greedy)...\n")
    
    prompt = torch.randint(0, 1000, (1, 10))
    model.eval()
    
    with torch.no_grad():
        generated = model.generate(
            prompt,
            max_new_tokens=20,
            temperature=1.0,
            top_k=None,
        )
    
    print(f"   Prompt length: {prompt.shape[1]}")
    print(f"   Generated length: {generated.shape[1]}")
    print(f"   New tokens: {generated.shape[1] - prompt.shape[1]}\n")
    
    # Generation with top-k sampling
    print("5. Text generation with top-k sampling...\n")
    
    with torch.no_grad():
        generated_topk = model.generate(
            prompt,
            max_new_tokens=20,
            temperature=0.8,
            top_k=50,
        )
    
    print(f"   Generated with top-k=50: {generated_topk.shape}\n")
    
    # Demonstrate memory efficiency
    print("6. Memory efficiency comparison...\n")
    
    # Standard attention would use num_heads KV heads
    # GQA uses fewer KV heads for reduced memory
    reduction_factor = model.layers[0].attention.num_heads / model.layers[0].attention.num_kv_heads
    print(f"   Attention heads: {model.layers[0].attention.num_heads}")
    print(f"   KV heads: {model.layers[0].attention.num_kv_heads}")
    print(f"   Memory reduction factor: {reduction_factor:.2f}x\n")
    
    # FlashAttention model
    print("7. Creating model with FlashAttention...\n")
    
    flash_model = OptimizedGPT(
        vocab_size=1000,
        embed_dim=256,
        num_layers=6,
        num_heads=8,
        num_kv_heads=4,
        ffn_dim=1024,
        use_flash_attention=True,
    )
    
    flash_model.eval()
    
    with torch.no_grad():
        logits_flash, _ = flash_model(input_ids)
    
    print(f"   FlashAttention model created")
    print(f"   Forward pass successful: {logits_flash.shape}\n")
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
