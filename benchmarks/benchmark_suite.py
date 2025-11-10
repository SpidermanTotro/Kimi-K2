"""Benchmarking suite for Kimi-K2 Framework."""

import time
import statistics
from typing import Callable, List, Dict, Any
from dataclasses import dataclass
import json

from kimi_k2 import Framework, Config


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    name: str
    runs: int
    mean: float
    median: float
    stdev: float
    min_time: float
    max_time: float


class Benchmark:
    """Benchmark runner for framework components."""
    
    def __init__(self, framework: Framework):
        """Initialize benchmark.
        
        Args:
            framework: Framework instance to benchmark
        """
        self.framework = framework
        self.results: List[BenchmarkResult] = []
        
    def run(self, name: str, func: Callable, runs: int = 10) -> BenchmarkResult:
        """Run a benchmark.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            runs: Number of runs
            
        Returns:
            Benchmark result
        """
        times = []
        
        print(f"Running benchmark: {name} ({runs} runs)...")
        for i in range(runs):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            
        result = BenchmarkResult(
            name=name,
            runs=runs,
            mean=statistics.mean(times),
            median=statistics.median(times),
            stdev=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time=min(times),
            max_time=max(times)
        )
        
        self.results.append(result)
        return result
        
    def print_results(self) -> None:
        """Print all benchmark results."""
        print("\n" + "=" * 80)
        print("BENCHMARK RESULTS")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n{result.name}:")
            print(f"  Runs:     {result.runs}")
            print(f"  Mean:     {result.mean*1000:.3f} ms")
            print(f"  Median:   {result.median*1000:.3f} ms")
            print(f"  Std Dev:  {result.stdev*1000:.3f} ms")
            print(f"  Min:      {result.min_time*1000:.3f} ms")
            print(f"  Max:      {result.max_time*1000:.3f} ms")
            
    def save_results(self, filename: str) -> None:
        """Save results to JSON file.
        
        Args:
            filename: Output filename
        """
        data = []
        for result in self.results:
            data.append({
                'name': result.name,
                'runs': result.runs,
                'mean_ms': result.mean * 1000,
                'median_ms': result.median * 1000,
                'stdev_ms': result.stdev * 1000,
                'min_ms': result.min_time * 1000,
                'max_ms': result.max_time * 1000
            })
            
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"\nResults saved to: {filename}")


def benchmark_animation(framework: Framework, runs: int = 10) -> None:
    """Benchmark animation operations.
    
    Args:
        framework: Framework instance
        runs: Number of benchmark runs
    """
    benchmark = Benchmark(framework)
    animation = framework.get_module('animation')
    
    # Benchmark project creation
    counter = [0]
    def create_project():
        animation.create_project(name=f"bench_{counter[0]}")
        counter[0] += 1
        
    benchmark.run("Animation: Create Project", create_project, runs)
    
    # Benchmark rendering
    animation.create_project(name="render_bench")
    benchmark.run(
        "Animation: Render Project",
        lambda: animation.render_project("render_bench"),
        runs
    )
    
    # Benchmark timeline operations
    def timeline_ops():
        editor = animation.timeline_editor
        editor.add_clip({'data': 'test'}, 0.0)
        editor.add_clip({'data': 'test'}, 1.0)
        editor.remove_clip(0)
        
    benchmark.run("Animation: Timeline Operations", timeline_ops, runs)
    
    benchmark.print_results()
    benchmark.save_results("benchmarks/animation_results.json")


def benchmark_commands(framework: Framework, runs: int = 10) -> None:
    """Benchmark command operations.
    
    Args:
        framework: Framework instance
        runs: Number of benchmark runs
    """
    benchmark = Benchmark(framework)
    commands = framework.get_module('commands')
    
    # Benchmark command execution
    benchmark.run(
        "Commands: Execute Help",
        lambda: commands.execute_command("help"),
        runs
    )
    
    benchmark.run(
        "Commands: Execute LS",
        lambda: commands.execute_command("ls"),
        runs
    )
    
    # Benchmark script generation
    benchmark.run(
        "Commands: Generate Script",
        lambda: commands.script_generator.generate_script("test script", "bash"),
        runs
    )
    
    benchmark.print_results()
    benchmark.save_results("benchmarks/commands_results.json")


def benchmark_models(framework: Framework, runs: int = 10) -> None:
    """Benchmark AI model operations.
    
    Args:
        framework: Framework instance
        runs: Number of benchmark runs
    """
    benchmark = Benchmark(framework)
    models = framework.get_module('models')
    
    # Benchmark model loading
    benchmark.run(
        "Models: Load Lightweight",
        lambda: models.load_model("lightweight"),
        runs
    )
    
    # Benchmark generation
    models.load_model("lightweight")
    benchmark.run(
        "Models: Generate (Lightweight)",
        lambda: models.generate("Test prompt", max_tokens=50),
        runs
    )
    
    # Benchmark heavy model
    benchmark.run(
        "Models: Load Heavy",
        lambda: models.load_model("heavy"),
        runs
    )
    
    models.load_model("heavy")
    benchmark.run(
        "Models: Generate (Heavy)",
        lambda: models.generate("Test prompt", max_tokens=50),
        runs
    )
    
    benchmark.print_results()
    benchmark.save_results("benchmarks/models_results.json")


def main():
    """Run all benchmarks."""
    print("=" * 80)
    print("KIMI-K2 FRAMEWORK BENCHMARKS")
    print("=" * 80)
    
    config = Config.default()
    framework = Framework(config)
    framework.initialize()
    
    try:
        # Run benchmarks
        benchmark_animation(framework, runs=10)
        print("\n")
        benchmark_commands(framework, runs=10)
        print("\n")
        benchmark_models(framework, runs=10)
        
        print("\n" + "=" * 80)
        print("ALL BENCHMARKS COMPLETE")
        print("=" * 80)
        
    finally:
        framework.shutdown()


if __name__ == '__main__':
    main()
