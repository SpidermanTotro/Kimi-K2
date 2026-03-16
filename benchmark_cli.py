#!/usr/bin/env python3
"""
Kimi K2 + FORGE Benchmark CLI

Command-line interface for running benchmarks, tracking performance,
and generating reports.

Usage:
    python benchmark_cli.py run --all
    python benchmark_cli.py run --benchmark livecode
    python benchmark_cli.py dashboard
    python benchmark_cli.py report
"""

import argparse
import sys
from pathlib import Path

# Import our benchmark modules
from benchmark_framework import BenchmarkFramework
from benchmark_runners import (
    BenchmarkRunnerFactory,
    run_all_benchmarks,
    LiveCodeBenchRunner,
    SWEBenchRunner,
    AIMERunner,
    Tau2Runner,
    AceBenchRunner,
)
from benchmark_dashboard import PerformanceDashboard


def run_benchmarks(args):
    """Run benchmark tests"""
    framework = BenchmarkFramework()
    
    if args.all:
        print("🚀 Running all benchmarks...")
        
        # Define all benchmarks from ROADMAP.md Phase 1
        benchmarks = [
            # Coding benchmarks
            {
                "name": "LiveCodeBench v6",
                "category": "coding",
                "runner_func": LiveCodeBenchRunner().run,
                "baseline_score": 53.7,
                "target_score": 60.0,
            },
            {
                "name": "SWE-bench Verified",
                "category": "coding",
                "runner_func": SWEBenchRunner().run,
                "baseline_score": 65.8,
                "target_score": 75.0,
            },
            # Math benchmarks
            {
                "name": "AIME 2024",
                "category": "math",
                "runner_func": lambda: AIMERunner().run(2024),
                "baseline_score": 69.6,
                "target_score": 75.0,
            },
            {
                "name": "AIME 2025",
                "category": "math",
                "runner_func": lambda: AIMERunner().run(2025),
                "baseline_score": 49.5,
                "target_score": 55.0,
            },
            # Tool use benchmarks
            {
                "name": "Tau2 retail",
                "category": "tool_use",
                "runner_func": lambda: Tau2Runner().run("retail"),
                "baseline_score": 70.6,
                "target_score": 75.0,
            },
            {
                "name": "Tau2 airline",
                "category": "tool_use",
                "runner_func": lambda: Tau2Runner().run("airline"),
                "baseline_score": 56.5,
                "target_score": 62.0,
            },
            {
                "name": "Tau2 telecom",
                "category": "tool_use",
                "runner_func": lambda: Tau2Runner().run("telecom"),
                "baseline_score": 65.8,
                "target_score": 72.0,
            },
            {
                "name": "AceBench",
                "category": "tool_use",
                "runner_func": AceBenchRunner().run,
                "baseline_score": 76.5,
                "target_score": 80.0,
            },
        ]
        
        # Run the suite
        summary = framework.run_benchmark_suite(
            benchmarks,
            suite_name="FORGE Integration Validation - Complete Suite"
        )
        
    elif args.benchmark:
        print(f"🧪 Running single benchmark: {args.benchmark}")
        
        # Map of benchmark names to configurations
        benchmark_map = {
            "livecode": {
                "name": "LiveCodeBench v6",
                "category": "coding",
                "runner_func": LiveCodeBenchRunner().run,
                "baseline_score": 53.7,
                "target_score": 60.0,
            },
            "swebench": {
                "name": "SWE-bench Verified",
                "category": "coding",
                "runner_func": SWEBenchRunner().run,
                "baseline_score": 65.8,
                "target_score": 75.0,
            },
            "aime2024": {
                "name": "AIME 2024",
                "category": "math",
                "runner_func": lambda: AIMERunner().run(2024),
                "baseline_score": 69.6,
                "target_score": 75.0,
            },
            "tau2": {
                "name": "Tau2 retail",
                "category": "tool_use",
                "runner_func": lambda: Tau2Runner().run("retail"),
                "baseline_score": 70.6,
                "target_score": 75.0,
            },
            "acebench": {
                "name": "AceBench",
                "category": "tool_use",
                "runner_func": AceBenchRunner().run,
                "baseline_score": 76.5,
                "target_score": 80.0,
            },
        }
        
        config = benchmark_map.get(args.benchmark.lower())
        if not config:
            print(f"❌ Unknown benchmark: {args.benchmark}")
            print(f"Available benchmarks: {', '.join(benchmark_map.keys())}")
            return 1
        
        result = framework.run_benchmark(**config)
    
    else:
        print("❌ Please specify --all or --benchmark <name>")
        return 1
    
    print("\n✅ Benchmarks complete! Results saved.")
    return 0


def show_dashboard(args):
    """Generate and display dashboard"""
    print("📊 Generating performance dashboard...")
    
    dashboard = PerformanceDashboard()
    
    # Generate charts
    dashboard.generate_charts()
    
    # Create HTML dashboard
    html_file = dashboard.create_html_dashboard()
    
    print()
    print("✅ Dashboard ready!")
    print(f"📁 Open in browser: file://{Path(html_file).absolute()}")
    
    return 0


def generate_report(args):
    """Generate benchmark report"""
    print("📄 Generating benchmark report...")
    
    framework = BenchmarkFramework()
    report = framework.generate_report()
    
    print()
    print("✅ Report generated!")
    print(f"📁 View report: {framework.output_dir}/benchmark_report.md")
    
    if args.show:
        print("\n" + "="*70)
        print(report)
    
    return 0


def list_benchmarks(args):
    """List available benchmarks"""
    print("📋 Available Benchmarks:")
    print()
    
    benchmarks = {
        "Coding": [
            "livecode - LiveCodeBench v6",
            "swebench - SWE-bench Verified",
            "multiple - MultiPL-E",
        ],
        "Math & STEM": [
            "aime2024 - AIME 2024",
            "aime2025 - AIME 2025",
            "math500 - MATH-500",
            "gpqa - GPQA-Diamond",
        ],
        "Tool Use": [
            "tau2 - Tau2 (retail/airline/telecom)",
            "acebench - AceBench",
        ],
    }
    
    for category, items in benchmarks.items():
        print(f"{category}:")
        for item in items:
            print(f"  • {item}")
        print()
    
    return 0


def show_stats(args):
    """Show benchmark statistics"""
    dashboard = PerformanceDashboard()
    stats = dashboard.get_statistics()
    
    print("=" * 70)
    print("📊 BENCHMARK STATISTICS")
    print("=" * 70)
    print(f"Total Runs:       {stats['total_runs']}")
    print(f"Successful:       {stats['successful_runs']}")
    print(f"Success Rate:     {stats['success_rate']:.1f}%")
    print(f"Avg Score:        {stats['avg_score']:.1f}%")
    print(f"Avg Improvement:  {stats['avg_improvement']:+.1f}%")
    print(f"Targets Met:      {stats['targets_met']}/{stats['targets_total']}")
    print("=" * 70)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Kimi K2 + FORGE Benchmark CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run --all                    Run all benchmarks
  %(prog)s run --benchmark livecode     Run LiveCodeBench only
  %(prog)s dashboard                    Generate performance dashboard
  %(prog)s report                       Generate markdown report
  %(prog)s list                         List available benchmarks
  %(prog)s stats                        Show statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run benchmarks')
    run_group = run_parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument('--all', action='store_true', help='Run all benchmarks')
    run_group.add_argument('--benchmark', type=str, help='Run specific benchmark')
    run_parser.add_argument('--model', type=str, default='kimi-k2-instruct',
                           help='Model path (default: kimi-k2-instruct)')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Generate dashboard')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--show', action='store_true', help='Show report content')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available benchmarks')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate handler
    handlers = {
        'run': run_benchmarks,
        'dashboard': show_dashboard,
        'report': generate_report,
        'list': list_benchmarks,
        'stats': show_stats,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
