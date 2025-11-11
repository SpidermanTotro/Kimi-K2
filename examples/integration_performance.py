"""
Example: Moon AI Integration and Performance
Demonstrates cross-AI integration and performance optimization
"""

import os
from kimi_k2 import KimiClient
from kimi_k2.integration import MoonAIIntegration
from kimi_k2.performance import BenchmarkingTools, OptimizationHelpers


def example_moon_ai_integration():
    """Example of Moon AI integration."""
    print("=" * 50)
    print("Example 1: Moon AI Integration")
    print("=" * 50)
    
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    integration = MoonAIIntegration(kimi_client=client)
    
    # Register integrations
    integration.register_integration("moon_ai", {
        "endpoint": "https://api.moonshot.ai",
        "features": ["reasoning", "chat", "tools"]
    })
    
    integration.register_integration("custom_ai", {
        "endpoint": "https://custom-ai.example.com",
        "features": ["specialized_domain"]
    })
    
    # Get status
    status = integration.get_integration_status()
    print(f"Active integrations: {status['integrations']}\n")
    
    # Unified query
    result = integration.unified_query(
        "What are the key features of modern AI systems?",
        combine_results=True
    )
    print(f"Unified query results from {len(result['individual_results'])} systems")
    print(f"Combined answer: {result.get('combined_result', 'N/A')[:200]}...\n")
    
    # Create AI pipeline
    pipeline_result = integration.create_ai_pipeline([
        {"system": "kimi_k2", "task": "Analyze the benefits of MoE architectures"},
        {"system": "kimi_k2", "task": "Summarize the previous analysis in 3 bullet points"}
    ])
    print(f"Pipeline completed with {pipeline_result['pipeline_steps']} steps")
    print(f"Final output: {pipeline_result['final_output'][:200]}...\n")


def example_benchmarking():
    """Example of performance benchmarking."""
    print("=" * 50)
    print("Example 2: Performance Benchmarking")
    print("=" * 50)
    
    benchmark = BenchmarkingTools()
    
    # Benchmark a simple function
    def sample_function(x):
        import time
        time.sleep(0.01)  # Simulate processing
        return x * 2
    
    # Measure latency
    latency_result = benchmark.measure_latency(
        sample_function,
        10,
        iterations=5
    )
    print(f"Latency benchmark:")
    print(f"  Average: {latency_result['average_ms']:.2f}ms")
    print(f"  Min: {latency_result['min_ms']:.2f}ms")
    print(f"  Max: {latency_result['max_ms']:.2f}ms\n")
    
    # Measure throughput
    test_data = list(range(100))
    throughput_result = benchmark.measure_throughput(
        sample_function,
        test_data
    )
    print(f"Throughput benchmark:")
    print(f"  Requests/sec: {throughput_result['requests_per_second']:.2f}")
    print(f"  Completed: {throughput_result['completed']}")
    print(f"  Errors: {throughput_result['errors']}\n")
    
    # Compare systems
    systems = {
        "system_a": lambda x: x * 2,
        "system_b": lambda x: x ** 2,
    }
    comparison = benchmark.compare_performance(systems, 100, iterations=3)
    print(f"Performance comparison:")
    print(f"  Fastest: {comparison['fastest']}")
    for rank in comparison['ranked']:
        print(f"    {rank['system']}: {rank['average_latency_ms']:.2f}ms")
    print()
    
    # Generate report
    report = benchmark.generate_report()
    print("Benchmark Report:")
    print(report)


def example_optimization():
    """Example of optimization helpers."""
    print("=" * 50)
    print("Example 3: Optimization Helpers")
    print("=" * 50)
    
    optimizer = OptimizationHelpers()
    
    # Cache decorator
    @optimizer.cache_response()
    def expensive_computation(n):
        import time
        time.sleep(0.1)  # Simulate expensive operation
        return n ** 2
    
    # First call (miss)
    import time
    start = time.time()
    result1 = expensive_computation(10)
    time1 = time.time() - start
    
    # Second call (hit)
    start = time.time()
    result2 = expensive_computation(10)
    time2 = time.time() - start
    
    print(f"Cache demonstration:")
    print(f"  First call: {time1*1000:.2f}ms")
    print(f"  Second call (cached): {time2*1000:.2f}ms")
    print(f"  Speedup: {time1/time2:.1f}x\n")
    
    # Batch processing
    items = list(range(50))
    batch_results = optimizer.batch_process(
        items,
        lambda batch: [x * 2 for x in batch],
        batch_size=10
    )
    print(f"Batch processing:")
    print(f"  Processed {len(batch_results)} items in batches of 10\n")
    
    # Optimize prompts
    long_prompt = "   This is a very long prompt with   extra   whitespace   " * 10
    optimized = optimizer.optimize_prompt(long_prompt, max_length=100)
    print(f"Prompt optimization:")
    print(f"  Original length: {len(long_prompt)}")
    print(f"  Optimized length: {len(optimized)}\n")
    
    # Token estimation
    text = "This is a sample text for token estimation."
    tokens = optimizer.estimate_tokens(text)
    print(f"Token estimation:")
    print(f"  Text: '{text}'")
    print(f"  Estimated tokens: {tokens}\n")
    
    # Batch optimization
    requests = [
        {"content": "Short request"},
        {"content": "A" * 1000},
        {"content": "Medium request with some text"},
        {"content": "B" * 2000},
    ]
    batches = optimizer.optimize_batch_requests(requests, max_tokens_per_batch=500)
    print(f"Batch optimization:")
    print(f"  {len(requests)} requests split into {len(batches)} optimized batches\n")


def example_integrated_performance():
    """Example of integrated performance monitoring."""
    print("=" * 50)
    print("Example 4: Integrated Performance Monitoring")
    print("=" * 50)
    
    benchmark = BenchmarkingTools()
    optimizer = OptimizationHelpers()
    
    # Simulate API calls with optimization
    @optimizer.cache_response()
    def simulated_api_call(query):
        import time
        time.sleep(0.05)  # Simulate network latency
        return f"Response to: {query}"
    
    # Benchmark with caching
    queries = ["query1", "query2", "query1", "query3", "query2"]
    
    latency = benchmark.measure_latency(
        lambda: [simulated_api_call(q) for q in queries],
        iterations=3
    )
    
    print(f"Performance with optimization:")
    print(f"  Average time for {len(queries)} queries: {latency['average_ms']:.2f}ms")
    print(f"  Effective time per query: {latency['average_ms']/len(queries):.2f}ms\n")
    
    # Get optimization stats
    stats = optimizer.get_optimization_stats()
    print(f"Optimization statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()


if __name__ == "__main__":
    print("Kimi K2 Integration and Performance Examples\n")
    
    if not os.getenv("MOONSHOT_API_KEY"):
        print("⚠️  MOONSHOT_API_KEY not set. Some examples will use mock data.")
        print("Set it with: export MOONSHOT_API_KEY='your-api-key'\n")
    
    example_moon_ai_integration()
    example_benchmarking()
    example_optimization()
    example_integrated_performance()
    
    print("Integration and performance examples completed!")
