# Kimi-K2 for Linux

## Overview

Kimi-K2 on Linux provides a fully feature-rich AI assistant optimized for various Linux distributions. This guide covers installation, deployment, and integration with Linux-native tools and workflows.

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+, or other modern Linux distributions
- **CPU**: x86_64 with AVX2 support or ARM64
- **RAM**: 64GB minimum (128GB+ recommended for optimal performance)
- **GPU**: NVIDIA GPU with 48GB+ VRAM (A100, H100, H200, or L40S recommended)
- **Storage**: 500GB SSD for model weights and cache
- **CUDA**: 12.1+ (for NVIDIA GPUs)

### Recommended Configuration
- **OS**: Ubuntu 22.04 LTS or Rocky Linux 9
- **CPU**: AMD EPYC 7763 or Intel Xeon Platinum 8380
- **RAM**: 256GB DDR4/DDR5
- **GPU**: 8x NVIDIA H100 80GB or H200 141GB
- **Storage**: 2TB NVMe SSD
- **Network**: 100Gbps InfiniBand for multi-node deployments

## Installation

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools and dependencies
sudo apt install -y \
    build-essential \
    git \
    wget \
    curl \
    python3.10 \
    python3-pip \
    python3-venv \
    libssl-dev \
    libffi-dev \
    libnccl2 \
    libnccl-dev

# Install NVIDIA drivers and CUDA (if not already installed)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-4
```

#### RHEL/CentOS/Rocky Linux
```bash
# Update system
sudo dnf update -y

# Install EPEL repository
sudo dnf install -y epel-release

# Install build tools and dependencies
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y \
    git \
    wget \
    curl \
    python3.10 \
    python3-pip \
    openssl-devel \
    libffi-devel

# Install NVIDIA drivers and CUDA
sudo dnf config-manager --add-repo \
    https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
sudo dnf install -y cuda-toolkit-12-4
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv kimi-k2-env
source kimi-k2-env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install inference engine (choose one)
# Option 1: vLLM
pip install vllm==0.10.0rc1

# Option 2: SGLang
pip install sglang[all]

# Install additional dependencies
pip install transformers accelerate bitsandbytes
```

### 3. Download Model Weights

```bash
# Install Hugging Face CLI
pip install -U "huggingface_hub[cli]"

# Login to Hugging Face (optional, required for gated models)
huggingface-cli login

# Download Kimi-K2-Instruct model
huggingface-cli download moonshotai/Kimi-K2-Instruct \
    --local-dir ./kimi-k2-instruct \
    --local-dir-use-symlinks False
```

## Deployment Options

### Single-Node Deployment (TP16)

For systems with 16 GPUs on a single node:

```bash
# Using vLLM
vllm serve ./kimi-k2-instruct \
    --port 8000 \
    --served-model-name kimi-k2 \
    --trust-remote-code \
    --tensor-parallel-size 16 \
    --enable-auto-tool-choice \
    --tool-call-parser kimi_k2 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 131072
```

### Multi-Node Deployment (DP+EP)

For distributed deployments across multiple nodes:

```bash
# Node 0 (master)
vllm serve ./kimi-k2-instruct \
    --port 8000 \
    --served-model-name kimi-k2 \
    --trust-remote-code \
    --data-parallel-size 16 \
    --data-parallel-size-local 8 \
    --data-parallel-address $MASTER_IP \
    --data-parallel-rpc-port 29500 \
    --enable-expert-parallel \
    --max-num-batched-tokens 8192 \
    --max-num-seqs 256 \
    --gpu-memory-utilization 0.85 \
    --enable-auto-tool-choice \
    --tool-call-parser kimi_k2

# Node 1 (worker)
vllm serve ./kimi-k2-instruct \
    --headless \
    --data-parallel-start-rank 8 \
    --port 8000 \
    --served-model-name kimi-k2 \
    --trust-remote-code \
    --data-parallel-size 16 \
    --data-parallel-size-local 8 \
    --data-parallel-address $MASTER_IP \
    --data-parallel-rpc-port 29500 \
    --enable-expert-parallel \
    --max-num-batched-tokens 8192 \
    --max-num-seqs 256 \
    --gpu-memory-utilization 0.85 \
    --enable-auto-tool-choice \
    --tool-call-parser kimi_k2
```

### Lightweight CPU-Only Deployment

For resource-constrained environments or testing:

```bash
# Install llama.cpp for CPU inference
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)

# Note: You'll need GGUF format weights for CPU deployment
# This is suitable for development/testing only
./server -m /path/to/kimi-k2-gguf -c 4096 --port 8000
```

## Linux System Integration

### Systemd Service Configuration

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/kimi-k2.service
```

Add the following content:

```ini
[Unit]
Description=Kimi-K2 AI Assistant
After=network.target

[Service]
Type=simple
User=kimi
Group=kimi
WorkingDirectory=/opt/kimi-k2
Environment="PATH=/opt/kimi-k2/kimi-k2-env/bin:/usr/local/bin:/usr/bin"
ExecStart=/opt/kimi-k2/kimi-k2-env/bin/vllm serve /opt/kimi-k2/models/kimi-k2-instruct \
    --port 8000 \
    --served-model-name kimi-k2 \
    --trust-remote-code \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser kimi_k2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=kimi-k2

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kimi-k2
sudo systemctl start kimi-k2
sudo systemctl status kimi-k2
```

### Shell Integration

Create a command-line client for easy interaction:

```bash
# Create CLI wrapper script
sudo nano /usr/local/bin/kimi
```

Add the following content:

```bash
#!/bin/bash
# Kimi-K2 CLI Wrapper

KIMI_ENDPOINT="${KIMI_ENDPOINT:-http://localhost:8000/v1}"
KIMI_MODEL="${KIMI_MODEL:-kimi-k2}"

if [ $# -eq 0 ]; then
    echo "Usage: kimi <prompt>"
    echo "Example: kimi 'Explain how Linux process scheduling works'"
    exit 1
fi

PROMPT="$*"

curl -s "$KIMI_ENDPOINT/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$KIMI_MODEL\",
        \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}],
        \"temperature\": 0.6,
        \"max_tokens\": 2048
    }" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

Make it executable:

```bash
sudo chmod +x /usr/local/bin/kimi
```

Usage:

```bash
kimi "What are the latest kernel features in Linux 6.7?"
```

### Bash Completion

Enable tab completion for the Kimi CLI:

```bash
# Create completion script
sudo nano /etc/bash_completion.d/kimi
```

Add the following:

```bash
_kimi_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Basic completion for common prompts
    if [ ${#COMP_WORDS[@]} -eq 2 ]; then
        opts="help explain analyze debug optimize"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}

complete -F _kimi_completion kimi
```

### Integration with Development Tools

#### Git Integration

Create a git alias for AI-powered commit messages:

```bash
git config --global alias.kimi-commit '!f() { \
    DIFF=$(git diff --staged); \
    MSG=$(kimi "Generate a concise git commit message for these changes: $DIFF"); \
    git commit -m "$MSG"; \
}; f'
```

Usage:

```bash
git add .
git kimi-commit
```

#### Vim/Neovim Integration

Add Kimi-K2 as a code assistant in your `.vimrc`:

```vim
function! KimiExplain()
    let l:code = getline(1, '$')
    let l:prompt = 'Explain this code: ' . join(l:code, '\n')
    let l:response = system('kimi "' . l:prompt . '"')
    echo l:response
endfunction

command! KimiExplain call KimiExplain()
nnoremap <leader>ke :KimiExplain<CR>
```

## Performance Optimization

### GPU Memory Optimization

```bash
# Monitor GPU usage
nvidia-smi -l 1

# For systems with limited VRAM, use quantization
vllm serve ./kimi-k2-instruct \
    --quantization fp8 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 65536
```

### CPU Affinity and NUMA Optimization

For multi-socket systems:

```bash
# Check NUMA topology
numactl --hardware

# Pin vLLM to specific NUMA node
numactl --cpunodebind=0 --membind=0 vllm serve ./kimi-k2-instruct \
    --port 8000 \
    --served-model-name kimi-k2 \
    --trust-remote-code \
    --tensor-parallel-size 8
```

### Network Optimization for Multi-Node

```bash
# Enable NCCL optimizations
export NCCL_IB_DISABLE=0
export NCCL_IB_HCA=mlx5_0,mlx5_1
export NCCL_SOCKET_IFNAME=eth0
export NCCL_DEBUG=INFO

# For InfiniBand
export NCCL_IB_GID_INDEX=3
export NCCL_IB_TC=106
```

## Monitoring and Logging

### Prometheus Metrics

Export vLLM metrics for monitoring:

```bash
vllm serve ./kimi-k2-instruct \
    --port 8000 \
    --prometheus-port 9090 \
    --served-model-name kimi-k2 \
    --trust-remote-code
```

### Log Aggregation

Configure logging to journald:

```bash
# View logs
journalctl -u kimi-k2 -f

# Filter by priority
journalctl -u kimi-k2 -p err

# Export logs
journalctl -u kimi-k2 --since "1 hour ago" > kimi-k2.log
```

## Security Considerations

### Firewall Configuration

```bash
# Allow API access from specific network
sudo firewall-cmd --permanent --add-rich-rule='
  rule family="ipv4"
  source address="192.168.1.0/24"
  port protocol="tcp" port="8000" accept'
sudo firewall-cmd --reload
```

### SELinux Configuration

For RHEL-based systems with SELinux:

```bash
# Create custom policy if needed
sudo ausearch -c 'python3' --raw | audit2allow -M kimi-k2-policy
sudo semodule -i kimi-k2-policy.pp
```

### Secure API Access

Use nginx as reverse proxy with SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name kimi.example.com;

    ssl_certificate /etc/ssl/certs/kimi.crt;
    ssl_certificate_key /etc/ssl/private/kimi.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Rate limiting
        limit_req zone=kimi_limit burst=10 nodelay;
    }
}
```

## Troubleshooting

### Common Issues

#### Out of Memory Errors

```bash
# Reduce batch size and context length
vllm serve ./kimi-k2-instruct \
    --max-num-batched-tokens 4096 \
    --max-num-seqs 128 \
    --gpu-memory-utilization 0.85
```

#### CUDA Out of Memory

```bash
# Enable memory pooling and reduce cache
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

#### Slow Inference

```bash
# Enable FlashAttention and optimizations
pip install flash-attn --no-build-isolation
```

### Performance Profiling

```bash
# Profile GPU usage
nsys profile -o kimi-profile vllm serve ./kimi-k2-instruct

# Analyze memory usage
nvidia-smi --query-gpu=timestamp,memory.used,memory.free \
    --format=csv -l 1 > gpu_memory.csv
```

## Best Practices

1. **Use Latest Drivers**: Keep NVIDIA drivers and CUDA toolkit updated
2. **Monitor Resources**: Set up monitoring for GPU, CPU, and memory usage
3. **Regular Backups**: Back up model configurations and customizations
4. **Version Control**: Track deployment configurations in Git
5. **Testing**: Test updates in staging before production deployment
6. **Documentation**: Document custom configurations and integrations

## Platform-Specific Optimizations

### Ubuntu-Specific

- Use Ubuntu Pro for extended security updates
- Leverage Canonical's optimized CUDA packages
- Use `snap` for containerized deployments: `snap install kimi-k2 --classic`

### RHEL/Rocky Linux-Specific

- Utilize Red Hat Performance Tuning Guide
- Enable tuned profile: `tuned-adm profile throughput-performance`
- Use RHEL AI tools for enhanced performance

### Arch Linux-Specific

- Use AUR packages for latest dependencies
- Optimize kernel with `linux-zen` for better performance
- Build from source with native CPU optimizations

## Container Deployment

### Docker

```dockerfile
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip git
RUN pip3 install vllm==0.10.0rc1 transformers

WORKDIR /app
COPY ./kimi-k2-instruct /app/kimi-k2-instruct

CMD ["vllm", "serve", "/app/kimi-k2-instruct", \
     "--port", "8000", \
     "--served-model-name", "kimi-k2", \
     "--trust-remote-code", \
     "--tensor-parallel-size", "8"]
```

### Kubernetes

See [kubernetes-deployment.yaml](./kubernetes-deployment.yaml) for full configuration.

## Support and Resources

- [General Deployment Guide](../../docs/deploy_guidance.md)
- [Tool Calling Guide](../../docs/tool_call_guidance.md)
- [Community Forum](https://discord.gg/TYU2fdJykW)
- [Bug Reports](https://github.com/moonshotai/Kimi-K2/issues)

## Next Steps

- Explore [iOS deployment](../ios/README.md) for mobile integration
- Check [Android deployment](../android/README.md) for mobile deployment
- Review [lightweight deployment options](../shared/lightweight-deployment.md)
