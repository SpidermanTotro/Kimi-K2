# Production Deployment - Phase 4

This directory contains containerization, orchestration, and deployment infrastructure for Kimi K2.

## Overview

Phase 4 focuses on:
- Kubernetes deployment manifests
- Docker containerization
- Performance optimization
- Production monitoring
- User documentation

## Directory Structure

```
deployment/
├── docker/             # Docker configurations
├── kubernetes/         # Kubernetes manifests
├── scripts/           # Deployment automation
├── monitoring/        # Monitoring configs
└── README.md         # This file
```

## Quick Start

### Docker Deployment

```bash
# Build Docker image
cd docker
docker build -t kimi-k2:latest .

# Run container
docker run -p 8000:8000 \
  -v /path/to/model:/models \
  kimi-k2:latest
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Check status
kubectl get pods -n kimi-k2
```

## Configuration

### Docker

Edit `docker/Dockerfile` and `docker/docker-compose.yml` for:
- Base image selection
- Resource limits
- Port mappings
- Volume mounts

### Kubernetes

Edit manifests in `kubernetes/` for:
- Replica count
- Resource requests/limits
- Node selectors
- Storage configuration

## Performance Optimization

### Resource Allocation

```yaml
resources:
  requests:
    memory: "64Gi"
    nvidia.com/gpu: "8"
  limits:
    memory: "128Gi"
    nvidia.com/gpu: "8"
```

### Autoscaling

```bash
kubectl apply -f kubernetes/hpa.yaml
```

## Monitoring

- Prometheus metrics endpoint: `/metrics`
- Health check: `/health`
- Readiness probe: `/ready`

## Security

- Use secrets for API keys
- Enable TLS/SSL
- Implement rate limiting
- Configure network policies

## Documentation

User-friendly guides available in `docs/`:
- Deployment guide
- Configuration reference
- Troubleshooting
- Best practices
