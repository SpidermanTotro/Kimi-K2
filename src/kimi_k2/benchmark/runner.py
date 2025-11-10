"""Benchmarking utilities for Kimi-K2."""

import time
import statistics
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

from kimi_k2.client import KimiClient

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    prompt: str
    response: str
    latency_ms: float
    tokens_generated: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BenchmarkRunner:
    """Run benchmarks on Kimi-K2 models."""

    def __init__(self, client: KimiClient):
        """Initialize benchmark runner.

        Args:
            client: KimiClient instance to benchmark
        """
        self.client = client
        self.results: List[BenchmarkResult] = []

    def run_latency_test(
        self, prompts: List[str], num_runs: int = 3, warmup: bool = True
    ) -> Dict[str, Any]:
        """Run latency benchmarks.

        Args:
            prompts: List of prompts to test
            num_runs: Number of runs per prompt
            warmup: Whether to do a warmup run

        Returns:
            Dictionary with benchmark statistics
        """
        if warmup:
            logger.info("Running warmup...")
            self.client.simple_chat("Hello")

        latencies = []

        for prompt in prompts:
            for run in range(num_runs):
                logger.info(
                    f"Testing prompt {prompts.index(prompt) + 1}/{len(prompts)}, run {run + 1}/{num_runs}"
                )

                start_time = time.time()
                response = self.client.simple_chat(prompt)
                end_time = time.time()

                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

                result = BenchmarkResult(
                    prompt=prompt,
                    response=response,
                    latency_ms=latency_ms,
                    tokens_generated=len(response.split()),  # Rough estimate
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                )
                self.results.append(result)

        return {
            "num_tests": len(latencies),
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "stdev_latency_ms": (
                statistics.stdev(latencies) if len(latencies) > 1 else 0
            ),
        }

    def run_throughput_test(
        self, prompts: List[str], duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """Run throughput benchmark.

        Args:
            prompts: List of prompts to cycle through
            duration_seconds: How long to run the test

        Returns:
            Dictionary with throughput statistics
        """
        start_time = time.time()
        end_time = start_time + duration_seconds

        num_requests = 0
        total_tokens = 0

        while time.time() < end_time:
            prompt = prompts[num_requests % len(prompts)]

            response = self.client.simple_chat(prompt)
            num_requests += 1
            total_tokens += len(response.split())  # Rough estimate

        actual_duration = time.time() - start_time

        return {
            "duration_seconds": actual_duration,
            "total_requests": num_requests,
            "total_tokens": total_tokens,
            "requests_per_second": num_requests / actual_duration,
            "tokens_per_second": total_tokens / actual_duration,
        }

    def export_results(self, filepath: str):
        """Export results to JSON file.

        Args:
            filepath: Path to save results
        """
        with open(filepath, "w") as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

        logger.info(f"Results exported to {filepath}")


def main():
    """Run benchmarks from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Kimi-K2")
    parser.add_argument("--url", required=True, help="Base URL of service")
    parser.add_argument("--model", default="kimi-k2", help="Model name")
    parser.add_argument("--prompts", nargs="+", help="Test prompts")
    parser.add_argument("--runs", type=int, default=3, help="Runs per prompt")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    # Default prompts if none provided
    if not args.prompts:
        args.prompts = [
            "What is the capital of France?",
            "Explain quantum computing in simple terms.",
            "Write a Python function to calculate fibonacci numbers.",
        ]

    client = KimiClient(base_url=args.url, model_name=args.model)
    runner = BenchmarkRunner(client)

    print("Running latency benchmark...")
    stats = runner.run_latency_test(args.prompts, num_runs=args.runs)

    print("\n=== Benchmark Results ===")
    for key, value in stats.items():
        print(f"{key}: {value:.2f}")

    if args.output:
        runner.export_results(args.output)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
