# Kimi K2 Benchmark Suite

This directory contains the benchmarking infrastructure for evaluating Kimi K2's performance across various tasks as part of **THE FORGE AI** initiative.

## Phase 2: Benchmark Optimization

The benchmarking suite focuses on three key areas with a target performance improvement of 6-15%:

### Supported Benchmarks

1. **LiveCodeBench** - Live coding problem evaluation
2. **SWE-bench** - Software engineering benchmark
3. **AIME** - AI Math Evaluation benchmark

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all benchmarks
python run_benchmarks.py --config config.yaml

# Run specific benchmark
python run_benchmarks.py --benchmark livecodebench
python run_benchmarks.py --benchmark swebench
python run_benchmarks.py --benchmark aime
```

## Configuration

Edit `config.yaml` to customize:
- Model endpoints
- Test parameters
- Output directories
- Performance targets

## Results

Benchmark results are stored in `results/` directory with timestamps and detailed metrics for tracking improvements over baseline.

## Directory Structure

```
benchmarks/
├── livecodebench/      # LiveCodeBench tests
├── swebench/           # SWE-bench tests
├── aime/               # AIME benchmark tests
├── config.yaml         # Benchmark configuration
├── run_benchmarks.py   # Main runner script
├── requirements.txt    # Python dependencies
└── results/            # Test results and reports
```

## Performance Targets

| Benchmark | Current (Baseline) | Target Improvement | Target Score |
|-----------|-------------------|-------------------|--------------|
| LiveCodeBench v6 | 53.7% | +6-15% | 57-62% |
| SWE-bench Verified | 65.8% | +6-15% | 70-76% |
| AIME 2024 | 69.6% | +6-15% | 74-80% |

## Contributing

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for guidelines on adding new benchmarks or improving existing ones.
