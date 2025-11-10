"""Example: Model comparison between lightweight and heavy models."""

from kimi_k2 import Framework, Config
import time


def benchmark_model(framework, model_name, prompt):
    """Benchmark a specific model."""
    models = framework.get_module('models')
    
    # Load model
    print(f"\nLoading {model_name} model...")
    start = time.time()
    models.load_model(model_name)
    load_time = time.time() - start
    
    # Generate text
    print(f"Generating with {model_name}...")
    start = time.time()
    result = models.generate(prompt, max_tokens=100)
    gen_time = time.time() - start
    
    # Get model info
    info = models.model_info[model_name]
    
    return {
        'model': model_name,
        'load_time': load_time,
        'gen_time': gen_time,
        'memory': info.memory_gb,
        'parameters': info.parameters,
        'result': result
    }


def main():
    """Compare lightweight and heavy models."""
    config = Config.default()
    framework = Framework(config)
    framework.initialize()
    
    prompt = "Explain the concept of artificial intelligence in simple terms."
    
    try:
        print("=" * 60)
        print("Model Comparison Benchmark")
        print("=" * 60)
        
        # Benchmark lightweight model
        lightweight_results = benchmark_model(framework, "lightweight", prompt)
        
        # Benchmark heavy model
        heavy_results = benchmark_model(framework, "heavy", prompt)
        
        # Display results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        for results in [lightweight_results, heavy_results]:
            print(f"\n{results['model'].upper()} Model:")
            print(f"  Parameters: {results['parameters']}")
            print(f"  Memory: {results['memory']}GB")
            print(f"  Load Time: {results['load_time']:.3f}s")
            print(f"  Generation Time: {results['gen_time']:.3f}s")
            print(f"  Response: {results['result'][:100]}...")
        
        # Comparison
        print("\n" + "=" * 60)
        print("COMPARISON")
        print("=" * 60)
        speedup = heavy_results['gen_time'] / lightweight_results['gen_time']
        print(f"Lightweight is {speedup:.2f}x faster for generation")
        
        memory_ratio = heavy_results['memory'] / lightweight_results['memory']
        print(f"Heavy model uses {memory_ratio:.1f}x more memory")
        
    finally:
        framework.shutdown()


if __name__ == '__main__':
    main()
