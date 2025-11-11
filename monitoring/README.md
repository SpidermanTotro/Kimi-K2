# Kimi K2 Monitoring and Security

This directory contains monitoring configurations and security tools for Kimi K2 deployments.

## Features

- **System Monitoring**: Track resource usage, performance metrics, and health
- **Security Scanning**: Automated vulnerability detection and security audits
- **Kubernetes Auto-scaling**: Dynamic resource allocation based on load
- **Alert Management**: Proactive notifications for issues

## Directory Structure

```
monitoring/
├── kubernetes/       # Kubernetes configurations and auto-scaling
├── security/         # Security scanning and best practices
└── README.md         # This file
```

## System Monitoring

### Metrics Collected

- **Performance Metrics**:
  - Request latency (P50, P95, P99)
  - Throughput (requests/second)
  - Token generation speed
  - GPU utilization
  - Memory usage

- **Resource Metrics**:
  - CPU usage per pod
  - Memory consumption
  - Network I/O
  - Disk I/O

- **Business Metrics**:
  - Active users
  - Request types distribution
  - Error rates
  - SLA compliance

### Visualization

Metrics are visualized using:
- Grafana dashboards (see `../benchmarks/dashboards/`)
- Prometheus metrics export
- Custom logging and reporting

## Security Monitoring

### Security Scans

Regular security scans include:
- Dependency vulnerability scanning
- Container image scanning
- Code security analysis
- API security testing
- Secrets detection

### Best Practices

See [security/SECURITY_BEST_PRACTICES.md](security/SECURITY_BEST_PRACTICES.md) for detailed security guidelines.

## Kubernetes Auto-scaling

### Horizontal Pod Autoscaling (HPA)

Configure HPA based on:
- CPU utilization
- Memory usage
- Custom metrics (requests/second)
- GPU utilization

### Vertical Pod Autoscaling (VPA)

Automatically adjust resource requests and limits based on actual usage.

### Cluster Autoscaling

Dynamically add/remove nodes based on workload demands.

## Configuration

### Prometheus Configuration

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kimi-k2'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: kimi-k2
```

### Alert Rules

```yaml
# alert-rules.yaml
groups:
  - name: kimi-k2-alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, kimi_k2_latency_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
```

## Quick Start

### Deploy Monitoring Stack

```bash
# Deploy Prometheus
kubectl apply -f kubernetes/prometheus/

# Deploy Grafana
kubectl apply -f kubernetes/grafana/

# Apply auto-scaling configurations
kubectl apply -f kubernetes/autoscaling/
```

### View Dashboards

1. Access Grafana: `kubectl port-forward svc/grafana 3000:3000`
2. Open browser: `http://localhost:3000`
3. Default credentials: admin/admin

### Run Security Scan

```bash
# Scan dependencies
python security/scan_dependencies.py

# Scan containers
python security/scan_containers.py

# Generate security report
python security/generate_report.py
```

## Alerting

Alerts can be sent to:
- Email
- Slack
- PagerDuty
- Custom webhooks

Configure alerts in `kubernetes/alertmanager/config.yaml`.

## Performance Optimization

See [PERFORMANCE_TUNING.md](PERFORMANCE_TUNING.md) for optimization guidelines.
