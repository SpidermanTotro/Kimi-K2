# Kimi K2 Benchmarking Framework

This directory contains the benchmarking framework for Kimi K2, extending beyond the standard LiveCodeBench, SWE-bench, and AIME benchmarks.

## Directory Structure

- **datasets/**: Additional benchmarking datasets
- **tools/**: Benchmarking execution tools and utilities
- **dashboards/**: Real-time metrics visualization configurations

## Supported Benchmarks

### Coding Tasks
- LiveCodeBench v6 (Aug 24 - May 25)
- SWE-bench Verified (Agentless & Agentic)
- SWE-bench Multilingual
- OJBench
- MultiPL-E
- TerminalBench
- Aider-Polyglot
- EvalPlus

### Tool Use Tasks
- Tau2 (retail, airline, telecom)
- AceBench

### Math & STEM Tasks
- AIME 2024/2025
- MATH-500
- HMMT 2025
- CNMO 2024
- PolyMath-en
- ZebraLogic
- AutoLogi
- GPQA-Diamond
- SuperGPQA

### General Tasks
- MMLU / MMLU-Redux / MMLU-Pro
- IFEval
- Multi-Challenge
- SimpleQA
- Livebench

## Additional Datasets

This framework includes support for:
- Custom domain-specific benchmarks
- Multilingual evaluation datasets
- Real-world task simulation datasets
- Chain-of-thought reasoning benchmarks

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a benchmark
python tools/run_benchmark.py --dataset <dataset_name> --model <model_path>

# View results in Grafana
docker-compose -f dashboards/docker-compose.yml up -d
```

## Metrics Visualization

Real-time benchmarking metrics are available through Grafana dashboards. See `dashboards/` for configuration details.

## Adding New Benchmarks

1. Create a dataset configuration in `datasets/<benchmark_name>/config.yaml`
2. Implement the evaluation logic in `tools/evaluators/<benchmark_name>.py`
3. Update the dashboard configuration to include new metrics
4. Submit a PR with your benchmark following the contribution guidelines
