# Examples Directory

This directory contains example scripts and guides for using the Kimi-K2 16-Layer model.

## Contents

### Training Scripts

#### `train_kimi_16layer.py`
Main training script for the Kimi-K2 16-layer model with memory optimization.

**Usage:**
```bash
# Verify memory footprint
python train_kimi_16layer.py \
  --training_config ../configs/training/programming_skills.yaml \
  --verify_only

# Start training
python train_kimi_16layer.py \
  --model_config ../configs/model/kimi_k2_16_layer.json \
  --training_config ../configs/training/programming_skills.yaml \
  --optimization_config ../configs/optimization/memory_optimization.yaml
```

**Features:**
- Memory usage monitoring and validation
- Support for all training configurations
- Automatic memory optimization
- Progress logging

### Benchmark Scripts

#### `benchmark_kimi_16layer.py`
Comprehensive benchmark suite to validate memory usage and performance.

**Usage:**
```bash
# Run all benchmarks
python benchmark_kimi_16layer.py \
  --model_path /path/to/checkpoint \
  --output benchmark_results.json \
  --memory_limit 16.0
```

**Tests:**
- Programming code generation
- Writing and knowledge tasks
- Animation and screenplay generation
- Long context processing (32K tokens)
- Batch inference

**Output:**
- JSON file with detailed results
- Console summary with pass/fail status
- Memory usage statistics

### Inference Scripts

#### `inference_example.py`
Simple inference examples for different task types.

**Usage:**
```bash
# Programming task
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task programming

# Writing task
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task writing

# Animation/Screenplay task
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task animation

# Custom prompt
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task custom \
  --prompt "Your custom prompt here" \
  --max_tokens 1024 \
  --temperature 0.8
```

### Guides

#### `datasets/DATASET_PREPARATION.md`
Comprehensive guide for preparing and organizing datasets.

**Topics Covered:**
- Dataset sources and downloads
- Data preprocessing
- Quality filtering
- Dataset mixing strategies
- Storage optimization

**Domains:**
- Programming datasets (The Stack, CodeParrot, Code Contests, etc.)
- Writing datasets (Wikipedia, BookCorpus, ArXiv, etc.)
- Animation datasets (Movie scripts, dialogues, web animation code)

## Quick Examples

### Example 1: Train on Programming Tasks

```bash
# 1. Verify memory
python train_kimi_16layer.py \
  --training_config ../configs/training/programming_skills.yaml \
  --verify_only

# 2. Start training
python train_kimi_16layer.py \
  --training_config ../configs/training/programming_skills.yaml

# 3. Monitor progress (logs will show memory usage)
```

### Example 2: Multi-Domain Training

```bash
# Train on all domains simultaneously
python train_kimi_16layer.py \
  --training_config ../configs/training/multitask_combined.yaml
```

### Example 3: Benchmark Memory Usage

```bash
# Run benchmarks
python benchmark_kimi_16layer.py --output results.json

# View results
cat results.json | python -m json.tool
```

### Example 4: Test Inference

```bash
# Test with programming prompt
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task programming \
  --max_tokens 512

# Test with writing prompt
python inference_example.py \
  --model_path /path/to/checkpoint \
  --task writing \
  --max_tokens 1024 \
  --temperature 0.8
```

## Configuration Files

The scripts use configuration files from the `configs/` directory:

- **Model Config**: `configs/model/kimi_k2_16_layer.json`
- **Optimization Config**: `configs/optimization/memory_optimization.yaml`
- **Training Configs**: 
  - `configs/training/programming_skills.yaml`
  - `configs/training/writing_and_knowledge.yaml`
  - `configs/training/animation_and_moviemaking.yaml`
  - `configs/training/multitask_combined.yaml`

## Requirements

Install dependencies:
```bash
pip install -r ../requirements.txt
```

Minimum requirements:
- Python 3.8+
- PyTorch 2.0+
- CUDA 11.8+ (for GPU)
- 16GB GPU memory (or use CPU mode with quantization)

## Expected Outputs

### Training Script
```
2025-01-10 10:00:00 - INFO - Loading model from configs/model/kimi_k2_16_layer.json
2025-01-10 10:00:01 - INFO - Enabling mixed precision training with bf16
2025-01-10 10:00:01 - INFO - Enabling gradient checkpointing
2025-01-10 10:00:01 - INFO - Using Flash Attention for memory efficiency
2025-01-10 10:00:02 - INFO - Verifying memory footprint...
2025-01-10 10:00:02 - INFO - Estimated model size: 8.50GB (30.00B parameters)
2025-01-10 10:00:02 - INFO - Estimated total training memory: 14.50GB
2025-01-10 10:00:02 - INFO - ✓ Memory footprint within 16GB constraint (14.50GB)
```

### Benchmark Script
```
================================================================================
Starting Kimi-K2 16-Layer Benchmark Suite
================================================================================

--- Programming Tasks Benchmark ---
✓ Programming Code Generation
  Memory: 12.30GB (peak: 12.45GB)
  Time: 150.23ms
  Throughput: 45.20 tokens/sec

--- Writing Tasks Benchmark ---
✓ Writing and Knowledge
  Memory: 13.80GB (peak: 13.95GB)
  Time: 180.45ms
  Throughput: 38.70 tokens/sec

...

================================================================================
BENCHMARK SUMMARY
================================================================================
Total Tests: 5
Passed: 5
Failed: 0

Memory Usage:
  Maximum: 15.20GB
  Average: 13.42GB
  Limit: 16.00GB

✓ ALL TESTS WITHIN 16GB MEMORY LIMIT
```

### Inference Script
```
Loading model from /path/to/checkpoint...
Model loaded successfully!
Device: cuda:0

================================================================================
PROMPT:
================================================================================
Write a Python function to implement a binary search tree...

================================================================================
GENERATING...
================================================================================

================================================================================
RESPONSE:
================================================================================
Here's a complete implementation of a binary search tree in Python:

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        ...

GPU Memory Used: 9.45GB
```

## Troubleshooting

### Out of Memory
If you encounter OOM errors:
1. Reduce batch size in training config
2. Enable CPU offloading
3. Reduce max sequence length
4. Use gradient checkpointing (should be enabled by default)

### Slow Performance
1. Verify Flash Attention is installed: `pip install flash-attn --no-build-isolation`
2. Check GPU utilization: `nvidia-smi`
3. Increase num_workers in data loader config

### Import Errors
Install missing dependencies:
```bash
pip install -r ../requirements.txt
```

## Additional Resources

- **Quick Start Guide**: `../QUICKSTART.md`
- **Full Documentation**: `../docs/KIMI_K2_16_LAYER.md`
- **Deployment Guide**: `../docs/DEPLOYMENT_16_LAYER.md`
- **Dataset Guide**: `datasets/DATASET_PREPARATION.md`

## Contributing

When adding new examples:
1. Follow existing code style
2. Include comprehensive docstrings
3. Add usage examples in this README
4. Test with verify mode before committing
