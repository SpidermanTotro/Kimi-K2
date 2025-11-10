# Quick Start Guide: Kimi-K2 16-Layer

Get started with the Kimi-K2 16-Layer model in minutes!

## Prerequisites

- **GPU**: 16GB+ VRAM (RTX 4080, A10G, L4, or better)
- **Python**: 3.8 or higher
- **CUDA**: 11.8 or higher

## Installation (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# 2. Create virtual environment
python -m venv kimi-k2-env
source kimi-k2-env/bin/activate  # Windows: kimi-k2-env\Scripts\activate

# 3. Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

## Quick Test: Verify Installation

```bash
# Test that PyTorch can access your GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Expected output:
# CUDA available: True
# GPU: NVIDIA GeForce RTX 4080
```

## Option 1: Training (Recommended for Learning)

### Step 1: Verify Memory Footprint

```bash
# Check that model fits in 16GB
python examples/train_kimi_16layer.py \
  --training_config configs/training/programming_skills.yaml \
  --verify_only

# Expected output:
# ✓ Memory footprint within 16GB constraint (12.5GB)
```

### Step 2: Start Training

```bash
# Train on programming tasks
python examples/train_kimi_16layer.py \
  --training_config configs/training/programming_skills.yaml

# Or train on writing tasks
python examples/train_kimi_16layer.py \
  --training_config configs/training/writing_and_knowledge.yaml

# Or train on animation/moviemaking
python examples/train_kimi_16layer.py \
  --training_config configs/training/animation_and_moviemaking.yaml

# Or train on all tasks combined
python examples/train_kimi_16layer.py \
  --training_config configs/training/multitask_combined.yaml
```

### Step 3: Monitor Training

The script will output memory usage and training progress:

```
Memory Stats: Current=12.34GB, Peak=13.12GB, Reserved=14.50GB
Task: programming_skills
Training setup complete. Ready to begin training.
```

## Option 2: Benchmarking (Test Memory Usage)

```bash
# Run comprehensive benchmark suite
python examples/benchmark_kimi_16layer.py \
  --output benchmark_results.json \
  --memory_limit 16.0

# View results
cat benchmark_results.json
```

Expected output:
```
--- Programming Tasks Benchmark ---
✓ Programming Code Generation
  Memory: 12.30GB (peak: 12.45GB)
  Time: 150.23ms
  Throughput: 45.20 tokens/sec

--- Writing Tasks Benchmark ---
✓ Writing and Knowledge
  Memory: 13.80GB (peak: 13.95GB)
  ...

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

## Option 3: Inference (Once You Have a Model)

### Using Python API

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "path/to/checkpoint",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained("path/to/checkpoint")

# Programming example
prompt = "Write a Python function to implement quicksort:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# Writing example
prompt = "Write a formal essay about renewable energy:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=1024, temperature=0.8)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# Screenplay example
prompt = "Write a thriller movie scene with dialogue:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=768, temperature=0.9)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Using vLLM Server (Production)

```bash
# Install vLLM
pip install vllm

# Start server
vllm serve path/to/checkpoint \
  --dtype bfloat16 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90

# In another terminal, test the API
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-k2-16",
    "messages": [
      {"role": "user", "content": "Write a Python function to merge two sorted lists."}
    ],
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

## Understanding the Configurations

### Model Configuration
Location: `configs/model/kimi_k2_16_layer.json`

Key parameters:
- `num_layers: 16` - Reduced from 61 for memory efficiency
- `num_experts: 64` - MoE architecture with 64 experts
- `num_experts_per_tok: 4` - Activate 4 experts per token
- `hidden_size: 4096` - Model dimension

### Memory Optimization
Location: `configs/optimization/memory_optimization.yaml`

Key features:
- Mixed precision (BF16)
- Flash Attention
- Gradient checkpointing
- FP8 quantization support

### Training Configurations
- **Programming**: `configs/training/programming_skills.yaml`
- **Writing**: `configs/training/writing_and_knowledge.yaml`
- **Animation**: `configs/training/animation_and_moviemaking.yaml`
- **Multi-task**: `configs/training/multitask_combined.yaml`

## Common Issues & Solutions

### Issue: Out of Memory

**Solution 1**: Reduce batch size in config file
```yaml
per_device_train_batch_size: 1  # Instead of 2
gradient_accumulation_steps: 16  # Instead of 8
```

**Solution 2**: Enable CPU offloading
```yaml
advanced_optimization:
  cpu_offload: true
```

**Solution 3**: Use smaller sequence length
```yaml
sequence_length:
  max: 4096  # Instead of 8192
```

### Issue: Slow Training

**Solution 1**: Verify Flash Attention is installed
```bash
pip install flash-attn --no-build-isolation
```

**Solution 2**: Use more workers for data loading
```yaml
data_loader:
  num_workers: 8  # Increase from 4
  prefetch_factor: 4
```

### Issue: CUDA Not Available

```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Next Steps

1. **Explore Configurations**: Review the YAML files in `configs/` to understand options
2. **Prepare Datasets**: Follow [`examples/datasets/DATASET_PREPARATION.md`](examples/datasets/DATASET_PREPARATION.md)
3. **Read Full Documentation**: See [`docs/KIMI_K2_16_LAYER.md`](docs/KIMI_K2_16_LAYER.md)
4. **Deploy to Production**: See [`docs/DEPLOYMENT_16_LAYER.md`](docs/DEPLOYMENT_16_LAYER.md)

## Example Workflows

### Workflow 1: Train a Programming Model

```bash
# 1. Verify setup
python examples/train_kimi_16layer.py \
  --training_config configs/training/programming_skills.yaml \
  --verify_only

# 2. Start training
python examples/train_kimi_16layer.py \
  --training_config configs/training/programming_skills.yaml

# 3. Monitor with tensorboard (optional)
tensorboard --logdir logs/programming

# 4. Test the trained model
python examples/inference_example.py \
  --checkpoint checkpoints/programming/checkpoint-10000 \
  --prompt "Write a Python binary search function"
```

### Workflow 2: Multi-Domain Training

```bash
# Train on all domains simultaneously
python examples/train_kimi_16layer.py \
  --training_config configs/training/multitask_combined.yaml

# This will train on:
# - 40% programming tasks
# - 35% writing/knowledge tasks  
# - 25% animation/moviemaking tasks
```

### Workflow 3: Memory Profiling

```bash
# Run benchmarks to validate memory usage
python examples/benchmark_kimi_16layer.py \
  --memory_limit 16.0 \
  --output results.json

# Check specific task memory
python examples/benchmark_kimi_16layer.py \
  --memory_limit 16.0 | grep "Memory:"
```

## Getting Help

- **Documentation**: See `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/SpidermanTotro/Kimi-K2/issues)
- **Examples**: See `examples/` folder

## Quick Reference

| Task | Command | Config File |
|------|---------|-------------|
| Verify memory | `python examples/train_kimi_16layer.py --verify_only` | Any config |
| Train programming | `python examples/train_kimi_16layer.py --training_config configs/training/programming_skills.yaml` | programming_skills.yaml |
| Train writing | `python examples/train_kimi_16layer.py --training_config configs/training/writing_and_knowledge.yaml` | writing_and_knowledge.yaml |
| Train animation | `python examples/train_kimi_16layer.py --training_config configs/training/animation_and_moviemaking.yaml` | animation_and_moviemaking.yaml |
| Train multi-task | `python examples/train_kimi_16layer.py --training_config configs/training/multitask_combined.yaml` | multitask_combined.yaml |
| Benchmark | `python examples/benchmark_kimi_16layer.py` | N/A |
| Serve with vLLM | `vllm serve path/to/checkpoint` | N/A |

---

**Ready to get started?** Pick a training configuration and run the verify command!

```bash
python examples/train_kimi_16layer.py \
  --training_config configs/training/programming_skills.yaml \
  --verify_only
```
