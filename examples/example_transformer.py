"""
Example: Using the 16-Layer Transformer Model

This example demonstrates the memory-efficient 16-layer transformer model
with autoregressive generation capabilities.
"""

import torch
from kimi_k2.models import TransformerModel


def main():
    """Run the transformer model example."""
    print("=== 16-Layer Transformer Model Example ===\n")
    
    # Create the 16-layer model
    print("1. Creating 16-layer Transformer model...\n")
    model = TransformerModel(
        vocab_size=5000,
        embed_dim=512,
        num_layers=16,
        num_heads=8,
        ffn_dim=2048,
        max_seq_len=1024,
        dropout=0.1,
        gradient_checkpointing=False,
    )
    
    print(f"   Model configuration:")
    print(f"   - Vocabulary size: {model.vocab_size}")
    print(f"   - Embedding dimension: {model.embed_dim}")
    print(f"   - Number of layers: {model.num_layers}")
    print(f"   - Attention heads: {model.layers[0].attention.num_heads}")
    print(f"   - FFN dimension: {model.layers[0].ffn.fc1.out_features}")
    print(f"   - Max sequence length: {model.max_seq_len}\n")
    
    # Count parameters
    print("2. Model size and memory estimation...\n")
    
    param_count = model.count_parameters()
    print(f"   Trainable parameters: {param_count:,}")
    print(f"   Parameter count (M): {param_count / 1e6:.2f}M\n")
    
    memory_est = model.estimate_memory_usage(batch_size=4, seq_len=512)
    print(f"   Memory estimates (batch_size=4, seq_len=512):")
    print(f"   - Parameters: {memory_est['parameters_mb']:.2f} MB")
    print(f"   - Activations: {memory_est['activations_mb']:.2f} MB")
    print(f"   - Total estimate: {memory_est['total_estimate_mb']:.2f} MB\n")
    
    # Forward pass
    print("3. Forward pass...\n")
    
    batch_size = 2
    seq_len = 50
    input_ids = torch.randint(0, 5000, (batch_size, seq_len))
    
    model.eval()
    with torch.no_grad():
        logits, hidden_states = model(input_ids, return_hidden_states=False)
    
    print(f"   Input shape: {input_ids.shape}")
    print(f"   Output logits shape: {logits.shape}")
    print(f"   Hidden states returned: {hidden_states is not None}\n")
    
    # Forward pass with hidden states
    print("4. Forward pass with hidden states...\n")
    
    with torch.no_grad():
        logits, hidden_states = model(input_ids, return_hidden_states=True)
    
    print(f"   Number of hidden state layers: {len(hidden_states)}")
    print(f"   First hidden state shape: {hidden_states[0].shape}")
    print(f"   Last hidden state shape: {hidden_states[-1].shape}\n")
    
    # Causal mask
    print("5. Causal attention mask...\n")
    
    mask = model.get_causal_mask(10, torch.device("cpu"))
    print(f"   Mask shape: {mask.shape}")
    print(f"   Mask is causal (lower triangular): {torch.all(mask[0, 0].tril() == mask[0, 0])}\n")
    
    # Greedy generation
    print("6. Text generation (greedy decoding)...\n")
    
    prompt = torch.randint(0, 5000, (1, 10))
    
    with torch.no_grad():
        generated_greedy = model.generate(
            prompt,
            max_new_tokens=30,
            do_sample=False,  # Greedy
        )
    
    print(f"   Prompt length: {prompt.shape[1]}")
    print(f"   Generated length: {generated_greedy.shape[1]}")
    print(f"   Greedy generated IDs (first 20): {generated_greedy[0, :20].tolist()}\n")
    
    # Sampling generation
    print("7. Text generation (sampling)...\n")
    
    with torch.no_grad():
        generated_sample = model.generate(
            prompt,
            max_new_tokens=30,
            do_sample=True,
            temperature=0.8,
        )
    
    print(f"   Sampled generated length: {generated_sample.shape[1]}")
    print(f"   Sampled IDs (first 20): {generated_sample[0, :20].tolist()}\n")
    
    # Top-k sampling
    print("8. Text generation with top-k sampling...\n")
    
    with torch.no_grad():
        generated_topk = model.generate(
            prompt,
            max_new_tokens=30,
            do_sample=True,
            temperature=1.0,
            top_k=50,
        )
    
    print(f"   Top-k (k=50) generated length: {generated_topk.shape[1]}\n")
    
    # Top-p (nucleus) sampling
    print("9. Text generation with top-p sampling...\n")
    
    with torch.no_grad():
        generated_topp = model.generate(
            prompt,
            max_new_tokens=30,
            do_sample=True,
            temperature=1.0,
            top_p=0.9,
        )
    
    print(f"   Top-p (p=0.9) generated length: {generated_topp.shape[1]}\n")
    
    # Gradient checkpointing
    print("10. Model with gradient checkpointing...\n")
    
    model_gc = TransformerModel(
        vocab_size=5000,
        embed_dim=512,
        num_layers=16,
        num_heads=8,
        ffn_dim=2048,
        gradient_checkpointing=True,
    )
    
    print(f"   Gradient checkpointing enabled: {model_gc.gradient_checkpointing}")
    
    # Forward pass still works
    with torch.no_grad():
        logits_gc, _ = model_gc(input_ids)
    
    print(f"   Forward pass successful: {logits_gc.shape}\n")
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
