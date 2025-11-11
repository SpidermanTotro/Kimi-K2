#!/usr/bin/env python3
"""
Kimi K2 Benchmark Runner
THE FORGE AI - Phase 2: Benchmark Optimization

This script runs comprehensive benchmarks for LiveCodeBench, SWE-bench, and AIME
to measure and optimize Kimi K2's performance.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from openai import OpenAI

# Add benchmark modules to path
sys.path.insert(0, str(Path(__file__).parent))


class BenchmarkRunner:
    """Main benchmark orchestration class."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the benchmark runner with configuration."""
        self.config = self._load_config(config_path)
        self.client = self._initialize_client()
        self.results_dir = Path(self.config['output']['results_dir'])
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Expand environment variables
        if 'api_key' in config['model']:
            api_key = config['model']['api_key']
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]
                config['model']['api_key'] = os.getenv(env_var, '')
        
        return config
    
    def _initialize_client(self) -> OpenAI:
        """Initialize OpenAI client for model interaction."""
        return OpenAI(
            base_url=self.config['model']['endpoint'],
            api_key=self.config['model']['api_key']
        )
    
    def run_benchmark(self, benchmark_name: str) -> Dict:
        """Run a specific benchmark."""
        print(f"\n{'='*60}")
        print(f"Running {benchmark_name.upper()} Benchmark")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        if benchmark_name == 'livecodebench':
            from livecodebench.runner import LiveCodeBenchRunner
            runner = LiveCodeBenchRunner(self.config, self.client)
            results = runner.run()
        elif benchmark_name == 'swebench':
            from swebench.runner import SWEBenchRunner
            runner = SWEBenchRunner(self.config, self.client)
            results = runner.run()
        elif benchmark_name == 'aime':
            from aime.runner import AIMERunner
            runner = AIMERunner(self.config, self.client)
            results = runner.run()
        else:
            raise ValueError(f"Unknown benchmark: {benchmark_name}")
        
        elapsed_time = time.time() - start_time
        results['elapsed_time'] = elapsed_time
        results['timestamp'] = datetime.now().isoformat()
        
        self._save_results(benchmark_name, results)
        self._print_summary(benchmark_name, results)
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, Dict]:
        """Run all enabled benchmarks."""
        all_results = {}
        
        for benchmark_name, config in self.config['benchmarks'].items():
            if config.get('enabled', False):
                try:
                    results = self.run_benchmark(benchmark_name)
                    all_results[benchmark_name] = results
                except Exception as e:
                    print(f"Error running {benchmark_name}: {e}")
                    all_results[benchmark_name] = {'error': str(e)}
        
        self._generate_report(all_results)
        return all_results
    
    def _save_results(self, benchmark_name: str, results: Dict):
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"{benchmark_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
    
    def _print_summary(self, benchmark_name: str, results: Dict):
        """Print benchmark summary."""
        print(f"\n{'-'*60}")
        print(f"{benchmark_name.upper()} Summary")
        print(f"{'-'*60}")
        print(f"Pass Rate: {results.get('pass_rate', 0):.2f}%")
        print(f"Total Tests: {results.get('total_tests', 0)}")
        print(f"Passed: {results.get('passed', 0)}")
        print(f"Failed: {results.get('failed', 0)}")
        print(f"Elapsed Time: {results.get('elapsed_time', 0):.2f}s")
        print(f"{'-'*60}\n")
    
    def _generate_report(self, all_results: Dict[str, Dict]):
        """Generate comprehensive benchmark report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"benchmark_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model': self.config['model']['name'],
            'benchmarks': all_results,
            'summary': self._calculate_summary(all_results)
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*60}")
        print("COMPREHENSIVE BENCHMARK REPORT")
        print(f"{'='*60}")
        print(f"Report saved to: {report_file}")
        print(f"\nOverall Performance:")
        for benchmark, summary in report['summary'].items():
            print(f"  {benchmark}: {summary.get('pass_rate', 0):.2f}%")
        print(f"{'='*60}\n")
    
    def _calculate_summary(self, all_results: Dict[str, Dict]) -> Dict:
        """Calculate summary statistics across all benchmarks."""
        summary = {}
        for benchmark_name, results in all_results.items():
            if 'error' not in results:
                summary[benchmark_name] = {
                    'pass_rate': results.get('pass_rate', 0),
                    'total_tests': results.get('total_tests', 0),
                    'improvement': results.get('improvement_over_baseline', 0)
                }
        return summary


def main():
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(
        description='Run Kimi K2 benchmarks for THE FORGE AI'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--benchmark',
        choices=['livecodebench', 'swebench', 'aime', 'all'],
        default='all',
        help='Specific benchmark to run'
    )
    parser.add_argument(
        '--output-dir',
        help='Override output directory from config'
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = BenchmarkRunner(args.config)
    
    # Override output directory if specified
    if args.output_dir:
        runner.results_dir = Path(args.output_dir)
        runner.results_dir.mkdir(parents=True, exist_ok=True)
    
    # Run benchmarks
    if args.benchmark == 'all':
        runner.run_all_benchmarks()
    else:
        runner.run_benchmark(args.benchmark)


if __name__ == '__main__':
    main()
