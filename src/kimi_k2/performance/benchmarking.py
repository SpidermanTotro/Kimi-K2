"""
Benchmarking Tools
Performance measurement and comparison utilities
"""

from typing import Dict, List, Optional, Any, Callable
import time
from datetime import datetime


class BenchmarkingTools:
    """
    Tools for benchmarking AI system performance.
    
    Features:
    - Latency measurement
    - Throughput testing
    - Quality metrics
    - Comparative analysis
    """
    
    def __init__(self):
        """Initialize benchmarking tools."""
        self.benchmark_results: List[Dict[str, Any]] = []
    
    def measure_latency(
        self,
        func: Callable,
        *args,
        iterations: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Measure function execution latency.
        
        Args:
            func: Function to benchmark
            iterations: Number of iterations
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Latency measurements
        """
        latencies = []
        results = []
        
        for i in range(iterations):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            results.append(result)
        
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        benchmark_result = {
            "metric": "latency",
            "iterations": iterations,
            "average_ms": avg_latency * 1000,
            "min_ms": min_latency * 1000,
            "max_ms": max_latency * 1000,
            "all_latencies_ms": [l * 1000 for l in latencies],
            "timestamp": datetime.now().isoformat()
        }
        
        self.benchmark_results.append(benchmark_result)
        
        return benchmark_result
    
    def measure_throughput(
        self,
        func: Callable,
        test_data: List[Any],
        duration_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Measure throughput (requests per second).
        
        Args:
            func: Function to test
            test_data: List of test inputs
            duration_seconds: Optional time limit
            
        Returns:
            Throughput measurements
        """
        start_time = time.time()
        completed = 0
        errors = 0
        
        for data in test_data:
            try:
                func(data)
                completed += 1
            except Exception:
                errors += 1
            
            if duration_seconds:
                elapsed = time.time() - start_time
                if elapsed >= duration_seconds:
                    break
        
        total_time = time.time() - start_time
        throughput = completed / total_time if total_time > 0 else 0
        
        benchmark_result = {
            "metric": "throughput",
            "completed": completed,
            "errors": errors,
            "duration_seconds": total_time,
            "requests_per_second": throughput,
            "timestamp": datetime.now().isoformat()
        }
        
        self.benchmark_results.append(benchmark_result)
        
        return benchmark_result
    
    def compare_performance(
        self,
        systems: Dict[str, Callable],
        test_input: Any,
        iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        Compare performance across multiple systems.
        
        Args:
            systems: Dictionary mapping system names to functions
            test_input: Input to test with
            iterations: Number of iterations per system
            
        Returns:
            Comparative results
        """
        comparison = {}
        
        for system_name, system_func in systems.items():
            result = self.measure_latency(
                system_func,
                test_input,
                iterations=iterations
            )
            
            comparison[system_name] = {
                "average_latency_ms": result["average_ms"],
                "min_latency_ms": result["min_ms"],
                "max_latency_ms": result["max_ms"]
            }
        
        # Rank by average latency
        ranked = sorted(
            comparison.items(),
            key=lambda x: x[1]["average_latency_ms"]
        )
        
        return {
            "comparison": comparison,
            "ranked": [{"system": name, **metrics} for name, metrics in ranked],
            "fastest": ranked[0][0],
            "timestamp": datetime.now().isoformat()
        }
    
    def quality_benchmark(
        self,
        func: Callable,
        test_cases: List[Dict[str, Any]],
        evaluator: Callable[[Any, Any], float],
    ) -> Dict[str, Any]:
        """
        Benchmark output quality.
        
        Args:
            func: Function to test
            test_cases: List of test cases with 'input' and 'expected'
            evaluator: Function to score quality (returns 0-1)
            
        Returns:
            Quality metrics
        """
        scores = []
        
        for test_case in test_cases:
            test_input = test_case["input"]
            expected = test_case.get("expected")
            
            result = func(test_input)
            score = evaluator(result, expected)
            
            scores.append({
                "input": str(test_input)[:50],
                "score": score
            })
        
        avg_score = sum(s["score"] for s in scores) / len(scores)
        
        benchmark_result = {
            "metric": "quality",
            "test_cases": len(test_cases),
            "average_score": avg_score,
            "min_score": min(s["score"] for s in scores),
            "max_score": max(s["score"] for s in scores),
            "scores": scores,
            "timestamp": datetime.now().isoformat()
        }
        
        self.benchmark_results.append(benchmark_result)
        
        return benchmark_result
    
    def get_benchmark_history(
        self,
        metric_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get benchmark history.
        
        Args:
            metric_type: Optional filter by metric type
            
        Returns:
            Benchmark history
        """
        if metric_type:
            return [
                r for r in self.benchmark_results 
                if r["metric"] == metric_type
            ]
        return self.benchmark_results
    
    def generate_report(self) -> str:
        """
        Generate a benchmark report.
        
        Returns:
            Formatted report string
        """
        if not self.benchmark_results:
            return "No benchmark results available."
        
        report = "Benchmark Report\n"
        report += "=" * 50 + "\n\n"
        
        # Group by metric type
        by_metric = {}
        for result in self.benchmark_results:
            metric = result["metric"]
            if metric not in by_metric:
                by_metric[metric] = []
            by_metric[metric].append(result)
        
        # Latency summary
        if "latency" in by_metric:
            report += "Latency Benchmarks:\n"
            report += "-" * 30 + "\n"
            
            for result in by_metric["latency"][-5:]:  # Last 5
                report += f"  Avg: {result['average_ms']:.2f}ms "
                report += f"(min: {result['min_ms']:.2f}ms, max: {result['max_ms']:.2f}ms)\n"
            report += "\n"
        
        # Throughput summary
        if "throughput" in by_metric:
            report += "Throughput Benchmarks:\n"
            report += "-" * 30 + "\n"
            
            for result in by_metric["throughput"][-5:]:
                report += f"  {result['requests_per_second']:.2f} req/s "
                report += f"({result['completed']} completed, {result['errors']} errors)\n"
            report += "\n"
        
        # Quality summary
        if "quality" in by_metric:
            report += "Quality Benchmarks:\n"
            report += "-" * 30 + "\n"
            
            for result in by_metric["quality"][-5:]:
                report += f"  Avg score: {result['average_score']:.3f} "
                report += f"({result['test_cases']} test cases)\n"
            report += "\n"
        
        report += f"Total benchmarks run: {len(self.benchmark_results)}\n"
        
        return report
