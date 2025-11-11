# Kimi K2 Production Dockerfile
# THE FORGE AI - Phase 4: Production Deployment

FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create model directory
RUN mkdir -p /models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
     "--model", "/models/Kimi-K2-Instruct", \
     "--port", "8000", \
     "--trust-remote-code", \
     "--enable-auto-tool-choice", \
     "--tool-call-parser", "kimi_k2"]
