# Deployment Guide for Kimi-K2 16-Layer Model

This guide provides deployment instructions specifically for the **Kimi-K2 16-Layer** variant, optimized for 16GB GPU memory.

## System Requirements

### Minimum Requirements
- **GPU**: 16GB VRAM (e.g., RTX 4080, A10G, L4, T4)
- **RAM**: 32GB system memory
- **Storage**: 50GB for model + datasets
- **OS**: Linux (Ubuntu 20.04+) or Windows with WSL2

### Recommended Requirements
- **GPU**: 24GB VRAM (e.g., RTX 4090, A5000, L40)
- **RAM**: 64GB system memory
- **Storage**: 100GB SSD
- **OS**: Linux (Ubuntu 22.04+)

## Installation

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv kimi-k2-env
source kimi-k2-env/bin/activate  # On Windows: kimi-k2-env\Scripts\activate

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install -r requirements.txt

# Install Flash Attention (requires CUDA)
pip install flash-attn --no-build-isolation
```

### 2. Model Download

```bash
# Download from Hugging Face (example)
# Replace with actual model path when available
from huggingface_hub import snapshot_download

model_path = snapshot_download(
    repo_id="moonshotai/kimi-k2-16-layer",
    cache_dir="./models",
    resume_download=True
)
```

## Deployment Options

### Option 1: vLLM (Recommended for Production)

vLLM provides high-throughput inference with optimized memory management.

```bash
# Install vLLM
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
  --model /path/to/kimi-k2-16-layer \
  --dtype bfloat16 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.90 \
  --served-model-name kimi-k2-16 \
  --port 8000 \
  --trust-remote-code
```

**Configuration Options:**
- `--dtype`: Use `bfloat16` or `float16` (default: auto)
- `--max-model-len`: Maximum sequence length (default: from config)
- `--gpu-memory-utilization`: Fraction of GPU memory to use (0.85-0.95)
- `--tensor-parallel-size`: Number of GPUs for tensor parallelism (default: 1)

**Memory Optimization:**
```bash
# For 16GB GPU, use these settings
vllm serve /path/to/kimi-k2-16-layer \
  --dtype bfloat16 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.85 \
  --max-num-seqs 32 \
  --max-num-batched-tokens 8192
```

### Option 2: Transformers + Accelerate

For development and testing.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
import torch

# Load with automatic device mapping
model = AutoModelForCausalLM.from_pretrained(
    "/path/to/kimi-k2-16-layer",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True
)

tokenizer = AutoTokenizer.from_pretrained("/path/to/kimi-k2-16-layer")

# Set to evaluation mode
model.eval()

# Example inference
prompt = "Write a Python function to sort a list:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Option 3: Text Generation Inference (TGI)

Hugging Face's production-ready inference server.

```bash
# Pull Docker image
docker pull ghcr.io/huggingface/text-generation-inference:latest

# Run server
docker run --gpus all --shm-size 1g -p 8080:80 \
  -v /path/to/models:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id /data/kimi-k2-16-layer \
  --dtype bfloat16 \
  --max-input-length 8192 \
  --max-total-tokens 16384
```

### Option 4: SGLang

For high-performance multi-request serving.

```bash
# Install SGLang
pip install sglang

# Start server
python -m sglang.launch_server \
  --model-path /path/to/kimi-k2-16-layer \
  --host 0.0.0.0 \
  --port 8000 \
  --tp 1 \
  --trust-remote-code
```

## Quantization for Smaller Memory Footprint

### 8-bit Quantization (bitsandbytes)

Reduces memory to ~8GB:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# 8-bit quantization config
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_has_fp16_weight=False
)

model = AutoModelForCausalLM.from_pretrained(
    "/path/to/kimi-k2-16-layer",
    quantization_config=quantization_config,
    device_map="auto",
    trust_remote_code=True
)
```

### 4-bit Quantization (QLoRA)

Reduces memory to ~4GB:

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 4-bit quantization config
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

model = AutoModelForCausalLM.from_pretrained(
    "/path/to/kimi-k2-16-layer",
    quantization_config=quantization_config,
    device_map="auto",
    trust_remote_code=True
)
```

### FP8 Quantization

For H100 or newer GPUs:

```bash
# Using vLLM with FP8
vllm serve /path/to/kimi-k2-16-layer \
  --quantization fp8 \
  --dtype auto
```

## API Usage

### OpenAI-Compatible API

```python
from openai import OpenAI

# Connect to local server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # Not required for local
)

# Chat completion
response = client.chat.completions.create(
    model="kimi-k2-16",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to implement binary search."}
    ],
    temperature=0.7,
    max_tokens=512
)

print(response.choices[0].message.content)
```

### Streaming Response

```python
stream = client.chat.completions.create(
    model="kimi-k2-16",
    messages=[
        {"role": "user", "content": "Explain recursion with examples."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Performance Tuning

### Batch Size Optimization

```python
# For single requests (low latency)
max_num_seqs = 1
max_num_batched_tokens = 2048

# For high throughput
max_num_seqs = 64
max_num_batched_tokens = 16384
```

### KV Cache Configuration

```bash
# Adjust based on available memory
vllm serve /path/to/kimi-k2-16-layer \
  --kv-cache-dtype auto \
  --max-model-len 32768 \
  --block-size 16
```

### GPU Memory Monitoring

```python
import torch

def log_memory_usage():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        print(f"GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
        
        if allocated > 14.0:
            print("Warning: Approaching 16GB limit!")
```

## Multi-Domain Task Examples

### Programming Task

```python
response = client.chat.completions.create(
    model="kimi-k2-16",
    messages=[
        {"role": "user", "content": "Write a JavaScript function to debounce user input."}
    ],
    temperature=0.6
)
```

### Writing Task

```python
response = client.chat.completions.create(
    model="kimi-k2-16",
    messages=[
        {"role": "user", "content": "Write a formal essay about climate change with citations."}
    ],
    temperature=0.8
)
```

### Animation/Screenplay Task

```python
response = client.chat.completions.create(
    model="kimi-k2-16",
    messages=[
        {"role": "user", "content": "Write a screenplay scene with dialogue and camera directions for a thriller movie."}
    ],
    temperature=0.9
)
```

## Monitoring and Logging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Monitor inference
logger = logging.getLogger(__name__)
logger.info("Starting inference...")
```

### Prometheus Metrics (vLLM)

vLLM exposes metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

## Troubleshooting

### Out of Memory

1. Reduce `max-model-len`:
   ```bash
   --max-model-len 16384  # Instead of 32768
   ```

2. Lower GPU memory utilization:
   ```bash
   --gpu-memory-utilization 0.80  # Instead of 0.90
   ```

3. Use quantization (8-bit or 4-bit)

4. Reduce batch size:
   ```bash
   --max-num-seqs 16  # Instead of 32
   ```

### Slow Inference

1. Enable Flash Attention (should be automatic with proper installation)

2. Optimize batch size for your workload

3. Use tensor parallelism if you have multiple GPUs:
   ```bash
   --tensor-parallel-size 2
   ```

### Model Loading Errors

1. Verify model files are complete:
   ```bash
   ls -lh /path/to/kimi-k2-16-layer/
   ```

2. Check CUDA version compatibility:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. Install with `trust_remote_code=True` if using custom code

## Cloud Deployment

### AWS (EC2 g5.xlarge)

```bash
# Instance: g5.xlarge (1x A10G 24GB)
# AMI: Deep Learning AMI

# Install and run
pip install vllm
vllm serve /path/to/kimi-k2-16-layer \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.85
```

### Google Cloud (n1-standard-4 + T4)

```bash
# Instance: n1-standard-4 with 1x T4 (16GB)
# Image: Deep Learning VM

# May need to reduce context length for 16GB T4
vllm serve /path/to/kimi-k2-16-layer \
  --dtype bfloat16 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.80
```

### Azure (NC6s_v3)

```bash
# Instance: NC6s_v3 (1x V100 16GB)

vllm serve /path/to/kimi-k2-16-layer \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.85
```

## Production Checklist

- [ ] Install all dependencies
- [ ] Download and verify model files
- [ ] Test with sample requests
- [ ] Configure appropriate memory limits
- [ ] Set up monitoring (logs, metrics)
- [ ] Configure load balancing (if needed)
- [ ] Set up automatic restarts
- [ ] Document API endpoints
- [ ] Set up rate limiting
- [ ] Configure HTTPS (for production)

## Support

For deployment issues:
- Check logs: vLLM logs at `/tmp/vllm/`
- Memory issues: See troubleshooting section
- Performance: Try different batch sizes and memory settings

## References

- [vLLM Documentation](https://docs.vllm.ai/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Flash Attention](https://github.com/Dao-AILab/flash-attention)
