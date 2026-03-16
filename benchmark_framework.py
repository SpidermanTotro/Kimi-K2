#!/usr/bin/env python3
"""
Kimi K2 + FORGE Benchmark Testing Framework

Provides infrastructure for:
- Running benchmark tests
- Tracking performance metrics
- Comparing baseline vs FORGE-enhanced results
- Generating improvement reports
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import subprocess


class BenchmarkFramework:
    """Framework for running and tracking benchmark tests"""
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results_file = self.output_dir / "benchmark_results.json"
        self.results = self._load_results()
        
    def _load_results(self) -> Dict[str, Any]:
        """Load existing benchmark results"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return {
            "runs": [],
            "summary": {},
            "metadata": {
                "framework_version": "1.0.0",
                "created": datetime.now().isoformat()
            }
        }
    
    def _save_results(self):
        """Save benchmark results to disk"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def run_benchmark(
        self,
        name: str,
        category: str,
        runner_func: Callable,
        baseline_score: Optional[float] = None,
        target_score: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a single benchmark test
        
        Args:
            name: Benchmark name (e.g., "LiveCodeBench v6")
            category: Category (coding, math, tool_use, etc.)
            runner_func: Function that runs the benchmark and returns a score
            baseline_score: Known baseline score (optional)
            target_score: Target score to achieve (optional)
            **kwargs: Additional arguments to pass to runner_func
        
        Returns:
            Dictionary with benchmark results
        """
        print(f"\n{'='*70}")
        print(f"🧪 Running Benchmark: {name}")
        print(f"📊 Category: {category}")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        try:
            # Run the benchmark
            score = runner_func(**kwargs)
            status = "success"
            error = None
        except Exception as e:
            score = None
            status = "failed"
            error = str(e)
            print(f"❌ Benchmark failed: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate improvement
        improvement = None
        improvement_pct = None
        if baseline_score and score:
            improvement = score - baseline_score
            improvement_pct = (improvement / baseline_score) * 100
        
        # Check if target was met
        target_met = None
        if target_score and score:
            target_met = score >= target_score
        
        result = {
            "name": name,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "score": score,
            "baseline_score": baseline_score,
            "target_score": target_score,
            "improvement": improvement,
            "improvement_pct": improvement_pct,
            "target_met": target_met,
            "status": status,
            "error": error
        }
        
        # Save result
        self.results["runs"].append(result)
        self._save_results()
        
        # Print summary
        self._print_result(result)
        
        return result
    
    def _print_result(self, result: Dict[str, Any]):
        """Print formatted benchmark result"""
        print(f"\n{'='*70}")
        print(f"✅ Benchmark Complete: {result['name']}")
        print(f"{'='*70}")
        
        if result['status'] == 'success':
            print(f"📊 Score: {result['score']:.2f}%")
            if result['baseline_score']:
                print(f"📈 Baseline: {result['baseline_score']:.2f}%")
            if result['improvement_pct']:
                symbol = "📈" if result['improvement'] > 0 else "📉"
                print(f"{symbol} Improvement: {result['improvement_pct']:+.2f}%")
            if result['target_score']:
                symbol = "✅" if result['target_met'] else "⚠️"
                print(f"{symbol} Target: {result['target_score']:.2f}% ({'MET' if result['target_met'] else 'NOT MET'})")
        else:
            print(f"❌ Status: {result['status']}")
            print(f"⚠️ Error: {result['error']}")
        
        print(f"⏱️ Duration: {result['duration_seconds']:.2f}s")
        print(f"{'='*70}\n")
    
    def run_benchmark_suite(
        self,
        benchmarks: List[Dict[str, Any]],
        suite_name: str = "Default Suite"
    ) -> Dict[str, Any]:
        """
        Run multiple benchmarks as a suite
        
        Args:
            benchmarks: List of benchmark configurations
            suite_name: Name for this benchmark suite
        
        Returns:
            Summary of all benchmark results
        """
        print(f"\n{'='*70}")
        print(f"🚀 Starting Benchmark Suite: {suite_name}")
        print(f"📊 Total Benchmarks: {len(benchmarks)}")
        print(f"{'='*70}\n")
        
        suite_start = time.time()
        results = []
        
        for benchmark in benchmarks:
            result = self.run_benchmark(**benchmark)
            results.append(result)
        
        suite_duration = time.time() - suite_start
        
        # Generate summary
        summary = self._generate_summary(results, suite_name, suite_duration)
        
        return summary
    
    def _generate_summary(
        self,
        results: List[Dict[str, Any]],
        suite_name: str,
        duration: float
    ) -> Dict[str, Any]:
        """Generate summary statistics for a benchmark suite"""
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total - successful
        
        # Calculate average improvement
        improvements = [r['improvement_pct'] for r in results 
                       if r['improvement_pct'] is not None]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Count targets met
        targets_met = sum(1 for r in results if r['target_met'])
        targets_total = sum(1 for r in results if r['target_score'] is not None)
        
        summary = {
            "suite_name": suite_name,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "total_benchmarks": total,
            "successful": successful,
            "failed": failed,
            "targets_met": targets_met,
            "targets_total": targets_total,
            "average_improvement_pct": round(avg_improvement, 2),
            "results": results
        }
        
        # Save to results
        self.results["summary"] = summary
        self._save_results()
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print formatted suite summary"""
        print(f"\n{'='*70}")
        print(f"📊 BENCHMARK SUITE SUMMARY: {summary['suite_name']}")
        print(f"{'='*70}")
        print(f"✅ Successful: {summary['successful']}/{summary['total_benchmarks']}")
        print(f"❌ Failed: {summary['failed']}/{summary['total_benchmarks']}")
        if summary['targets_total'] > 0:
            print(f"🎯 Targets Met: {summary['targets_met']}/{summary['targets_total']}")
        print(f"📈 Average Improvement: {summary['average_improvement_pct']:+.2f}%")
        print(f"⏱️ Total Duration: {summary['duration_seconds']:.2f}s")
        print(f"{'='*70}\n")
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a detailed markdown report of benchmark results
        
        Args:
            output_file: Optional output file path
        
        Returns:
            Report content as string
        """
        if output_file is None:
            output_file = self.output_dir / "benchmark_report.md"
        
        report = self._create_report_content()
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Report generated: {output_file}")
        return report
    
    def _create_report_content(self) -> str:
        """Create markdown report content"""
        summary = self.results.get("summary", {})
        runs = self.results.get("runs", [])
        
        report = f"""# Kimi K2 + FORGE Benchmark Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

"""
        
        if summary:
            report += f"""- **Suite**: {summary.get('suite_name', 'N/A')}
- **Total Benchmarks**: {summary.get('total_benchmarks', 0)}
- **Successful**: {summary.get('successful', 0)}
- **Failed**: {summary.get('failed', 0)}
- **Average Improvement**: {summary.get('average_improvement_pct', 0):+.2f}%
- **Targets Met**: {summary.get('targets_met', 0)}/{summary.get('targets_total', 0)}

"""
        
        report += """## Benchmark Results by Category

"""
        
        # Group by category
        by_category = {}
        for run in runs:
            category = run.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(run)
        
        for category, category_runs in by_category.items():
            report += f"### {category.upper()}\n\n"
            report += "| Benchmark | Score | Baseline | Improvement | Target | Status |\n"
            report += "|-----------|-------|----------|-------------|--------|--------|\n"
            
            for run in category_runs:
                name = run['name']
                score = f"{run['score']:.1f}%" if run['score'] else "N/A"
                baseline = f"{run['baseline_score']:.1f}%" if run['baseline_score'] else "N/A"
                improvement = f"{run['improvement_pct']:+.1f}%" if run['improvement_pct'] else "N/A"
                target = f"{run['target_score']:.1f}%" if run['target_score'] else "N/A"
                
                if run['status'] == 'success':
                    if run['target_met']:
                        status = "✅ Met"
                    elif run['target_met'] is False:
                        status = "⚠️ Not Met"
                    else:
                        status = "✅ Pass"
                else:
                    status = "❌ Failed"
                
                report += f"| {name} | {score} | {baseline} | {improvement} | {target} | {status} |\n"
            
            report += "\n"
        
        report += """## Recommendations

Based on the benchmark results:

1. **Focus Areas**: Identify benchmarks below target and create improvement strategies
2. **Strengths**: Leverage successful areas for cross-benchmark optimization
3. **Training Data**: Use results to guide FORGE training data enhancement
4. **Documentation**: Document successful optimization techniques

## Next Steps

1. Analyze failed or underperforming benchmarks
2. Review FORGE integration for optimization opportunities
3. Update training data based on benchmark insights
4. Re-run benchmarks after improvements

---

*Report generated by Kimi K2 + FORGE Benchmark Framework v1.0.0*
"""
        
        return report
    
    def compare_runs(self, run_id1: int, run_id2: int) -> Dict[str, Any]:
        """Compare two benchmark runs"""
        runs = self.results.get("runs", [])
        
        if run_id1 >= len(runs) or run_id2 >= len(runs):
            raise ValueError("Invalid run IDs")
        
        run1 = runs[run_id1]
        run2 = runs[run_id2]
        
        comparison = {
            "run1": run1,
            "run2": run2,
            "score_delta": run2['score'] - run1['score'] if run1['score'] and run2['score'] else None,
            "improvement_delta": run2['improvement_pct'] - run1['improvement_pct'] 
                               if run1['improvement_pct'] and run2['improvement_pct'] else None
        }
        
        return comparison


# Example benchmark runner functions
def mock_benchmark_runner(expected_score: float = 75.0, **kwargs) -> float:
    """Mock benchmark runner for testing"""
    import random
    # Simulate some variance
    return expected_score + random.uniform(-2.0, 2.0)


def main():
    """Example usage of the benchmark framework"""
    print("=" * 70)
    print("🔥 KIMI K2 + FORGE BENCHMARK FRAMEWORK")
    print("=" * 70)
    print()
    
    framework = BenchmarkFramework()
    
    # Define benchmark suite from ROADMAP.md Phase 1
    benchmarks = [
        {
            "name": "LiveCodeBench v6",
            "category": "coding",
            "runner_func": mock_benchmark_runner,
            "baseline_score": 53.7,
            "target_score": 60.0,
            "expected_score": 58.5  # Mock improvement
        },
        {
            "name": "SWE-bench Verified",
            "category": "coding",
            "runner_func": mock_benchmark_runner,
            "baseline_score": 65.8,
            "target_score": 75.0,
            "expected_score": 72.0
        },
        {
            "name": "AIME 2024",
            "category": "math",
            "runner_func": mock_benchmark_runner,
            "baseline_score": 69.6,
            "target_score": 75.0,
            "expected_score": 73.2
        },
        {
            "name": "Tau2 retail",
            "category": "tool_use",
            "runner_func": mock_benchmark_runner,
            "baseline_score": 70.6,
            "target_score": 75.0,
            "expected_score": 78.5
        }
    ]
    
    # Run the benchmark suite
    summary = framework.run_benchmark_suite(
        benchmarks,
        suite_name="FORGE Integration Validation"
    )
    
    # Generate report
    framework.generate_report()
    
    print("\n✅ Benchmark framework demonstration complete!")
    print(f"📁 Results saved to: {framework.output_dir}")
    print(f"📄 View report: {framework.output_dir}/benchmark_report.md")


if __name__ == "__main__":
    main()
