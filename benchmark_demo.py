#!/usr/bin/env python3
"""
Demonstration of Kimi K2 + FORGE Benchmark System

This script demonstrates the complete benchmark validation workflow:
1. Running benchmarks
2. Generating reports
3. Creating dashboards
4. Showing statistics
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show output"""
    print("\n" + "="*70)
    print(f"🔄 {description}")
    print("="*70)
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode


def main():
    """Run demonstration"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║     KIMI K2 + FORGE BENCHMARK VALIDATION SYSTEM DEMONSTRATION          ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check we're in the right directory
    if not Path("benchmark_cli.py").exists():
        print("❌ Error: Please run this script from the Kimi-K2 directory")
        return 1
    
    # 1. List available benchmarks
    run_command(
        ["python3", "benchmark_cli.py", "list"],
        "Listing available benchmarks"
    )
    
    # 2. Run a sample benchmark
    run_command(
        ["python3", "benchmark_cli.py", "run", "--benchmark", "livecode"],
        "Running LiveCodeBench (sample)"
    )
    
    # 3. Show statistics
    run_command(
        ["python3", "benchmark_cli.py", "stats"],
        "Showing benchmark statistics"
    )
    
    # 4. Generate report
    run_command(
        ["python3", "benchmark_cli.py", "report"],
        "Generating markdown report"
    )
    
    # 5. Generate dashboard
    run_command(
        ["python3", "benchmark_cli.py", "dashboard"],
        "Generating HTML dashboard"
    )
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                      ✅ DEMONSTRATION COMPLETE                          ║
╚════════════════════════════════════════════════════════════════════════╝

📁 Generated Files:
  • benchmark_results/benchmark_results.json - Raw results
  • benchmark_results/benchmark_report.md - Markdown report
  • benchmark_results/dashboard.html - HTML dashboard
  • benchmark_results/charts/ - Performance charts

📖 Documentation:
  • BENCHMARK_GUIDE.md - Complete usage guide
  • KIMI_K2_FORGE_INTEGRATION.md - Integration guide

🚀 Next Steps:
  1. Run all benchmarks: python3 benchmark_cli.py run --all
  2. Review the dashboard in a browser
  3. Analyze results and optimize
  4. Re-run benchmarks to track improvements

💡 The benchmark system is ready to validate the expected 6-15%
   performance improvements from the FORGE + Kimi K2 integration!
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
