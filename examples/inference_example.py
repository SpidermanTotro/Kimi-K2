#!/usr/bin/env python3
"""
Simple inference example for Kimi-K2 16-Layer model
Demonstrates usage for programming, writing, and animation tasks
"""

import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_model(model_path: str, device: str = "auto"):
    """Load model and tokenizer"""
    print(f"Loading model from {model_path}...")
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    
    print(f"Model loaded successfully!")
    print(f"Device: {next(model.parameters()).device}")
    
    return model, tokenizer


def generate_response(model, tokenizer, prompt: str, max_tokens: int = 512, temperature: float = 0.7):
    """Generate response for a given prompt"""
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return response


def main():
    parser = argparse.ArgumentParser(description="Kimi-K2 16-Layer Inference Example")
    parser.add_argument(
        '--model_path',
        type=str,
        required=True,
        help='Path to model checkpoint'
    )
    parser.add_argument(
        '--task',
        type=str,
        choices=['programming', 'writing', 'animation', 'custom'],
        default='custom',
        help='Type of task (uses pre-defined prompts)'
    )
    parser.add_argument(
        '--prompt',
        type=str,
        help='Custom prompt (only used with --task custom)'
    )
    parser.add_argument(
        '--max_tokens',
        type=int,
        default=512,
        help='Maximum number of tokens to generate'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Sampling temperature'
    )
    
    args = parser.parse_args()
    
    # Load model
    model, tokenizer = load_model(args.model_path)
    
    # Define example prompts
    example_prompts = {
        'programming': "Write a Python function to implement a binary search tree with insert, search, and delete operations.",
        'writing': "Write a formal essay about the impact of artificial intelligence on modern society, including citations and references.",
        'animation': """Write a screenplay scene for a thriller movie:

INT. ABANDONED WAREHOUSE - NIGHT

Include dialogue between two characters and camera directions."""
    }
    
    # Get prompt
    if args.task == 'custom':
        if not args.prompt:
            print("Error: --prompt required when using --task custom")
            return 1
        prompt = args.prompt
    else:
        prompt = example_prompts[args.task]
    
    # Display prompt
    print("\n" + "=" * 80)
    print("PROMPT:")
    print("=" * 80)
    print(prompt)
    print()
    
    # Generate response
    print("=" * 80)
    print("GENERATING...")
    print("=" * 80)
    
    response = generate_response(
        model,
        tokenizer,
        prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )
    
    # Display response
    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(response)
    print()
    
    # Display stats
    if torch.cuda.is_available():
        memory_used = torch.cuda.memory_allocated() / 1e9
        print(f"GPU Memory Used: {memory_used:.2f}GB")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
