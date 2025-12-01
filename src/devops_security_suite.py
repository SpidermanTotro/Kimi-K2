"""
THE FORGE AI - DevOps and Security Suite
Complete CI/CD, deployment, security, and monitoring tools
"""

import os
import json
import subprocess
import datetime
from typing import Dict, List, Any
import random

class DevOpsSecuritySuite:
    """Comprehensive DevOps and security platform"""
    
    def __init__(self):
        self.pipelines = {}
        self.deployments = {}
        self.security_scans = {}
        self.monitoring_data = {}
        self.ci_cd_tools = CITools()
        self.security_tools = SecurityTools()
        self.monitoring = MonitoringTools()
        self.container_tools = ContainerTools()
    
    def create_ci_cd_pipeline(self, name: str, project_type: str, 
                             config: Dict = None) -> Dict[str, Any]:
        """Create CI/CD pipeline"""
        return self.ci_cd_tools.create_pipeline(name, project_type, config)
    
    def deploy_application(self, app_name: str, environment: str, 
                           deployment_config: Dict) -> Dict[str, Any]:
        """Deploy application to specified environment"""
        try:
            deployment_id = f"deploy_{len(self.deployments) + 1}"
            
            # Create deployment directory
            deploy_dir = f"/workspace/deployments/{app_name}_{environment}"
            os.makedirs(deploy_dir, exist_ok=True)
            
            # Generate deployment scripts
            self.create_deployment_scripts(deploy_dir, app_name, environment, deployment_config)
            
            deployment_info = {
                "deployment_id": deployment_id,
                "app_name": app_name,
                "environment": environment,
                "deploy_dir": deploy_dir,
                "status": "preparing",
                "created_at": datetime.datetime.now().isoformat(),
                "config": deployment_config,
                "logs": [],
                "rollback_available": True
            }
            
            self.deployments[deployment_id] = deployment_info
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "app_name": app_name,
                "environment": environment,
                "deployment_prepared": True,
                "next_steps": [
                    "Review deployment configuration",
                    "Run deployment script",
                    "Monitor deployment status",
                    "Verify application health"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_deployment_scripts(self, deploy_dir: str, app_name: str, 
                                 environment: str, config: Dict):
        """Create deployment scripts"""
        # Create deployment script
        deploy_script = f'''#!/bin/bash
# Deployment script for {app_name} to {environment}

echo "Starting deployment of {app_name} to {environment}..."

# Environment-specific setup
if [ "{environment}" = "production" ]; then
    echo "Production deployment detected - enabling safety checks"
    # Add production-specific commands
elif [ "{environment}" = "staging" ]; then
    echo "Staging deployment detected"
    # Add staging-specific commands
else
    echo "Development deployment detected"
fi

# Build application
echo "Building application..."
# Add build commands here

# Run tests
echo "Running tests..."
# Add test commands here

# Deploy application
echo "Deploying application..."
# Add deployment commands here

# Health check
echo "Performing health check..."
# Add health check commands here

echo "Deployment completed successfully!"
'''
        
        with open(f"{deploy_dir}/deploy.sh", 'w') as f:
            f.write(deploy_script)
        
        # Make script executable
        os.chmod(f"{deploy_dir}/deploy.sh", 0o755)
        
        # Create rollback script
        rollback_script = f'''#!/bin/bash
# Rollback script for {app_name} from {environment}

echo "Starting rollback of {app_name} from {environment}..."

# Stop current version
echo "Stopping current version..."

# Restore previous version
echo "Restoring previous version..."

# Restart services
echo "Restarting services..."

# Health check
echo "Performing health check after rollback..."

echo "Rollback completed successfully!"
'''
        
        with open(f"{deploy_dir}/rollback.sh", 'w') as f:
            f.write(rollback_script)
        
        os.chmod(f"{deploy_dir}/rollback.sh", 0o755)
        
        # Create Docker configuration
        dockerfile = f'''# Dockerfile for {app_name}
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
'''
        
        with open(f"{deploy_dir}/Dockerfile", 'w') as f:
            f.write(dockerfile)
        
        # Create docker-compose.yml
        compose_file = f'''version: '3.8'

services:
  {app_name.lower()}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV={environment}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
'''
        
        with open(f"{deploy_dir}/docker-compose.yml", 'w') as f:
            f.write(compose_file)
    
    def run_security_scan(self, target: str, scan_type: str = "comprehensive") -> Dict[str, Any]:
        """Run security scan on target"""
        return self.security_tools.run_scan(target, scan_type)
    
    def setup_monitoring(self, app_name: str, metrics_config: Dict) -> Dict[str, Any]:
        """Set up monitoring for application"""
        return self.monitoring.setup_monitoring(app_name, metrics_config)
    
    def create_container_environment(self, app_name: str, container_type: str = "docker") -> Dict[str, Any]:
        """Create containerized environment"""
        return self.container_tools.create_environment(app_name, container_type)
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status"""
        try:
            if deployment_id not in self.deployments:
                return {"success": False, "error": "Deployment not found"}
            
            deployment = self.deployments[deployment_id]
            
            # Simulate deployment progress
            status_progress = {
                "preparing": {"progress": 10, "message": "Preparing deployment"},
                "building": {"progress": 30, "message": "Building application"},
                "testing": {"progress": 60, "message": "Running tests"},
                "deploying": {"progress": 80, "message": "Deploying application"},
                "verifying": {"progress": 95, "message": "Verifying deployment"},
                "completed": {"progress": 100, "message": "Deployment completed"},
                "failed": {"progress": 0, "message": "Deployment failed"}
            }
            
            current_status = deployment["status"]
            progress_info = status_progress.get(current_status, {"progress": 0, "message": "Unknown status"})
            
            # Add log entries
            log_entries = [
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Deployment started",
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Building application...",
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Running tests...",
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Deploying to {deployment['environment']}..."
            ]
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": current_status,
                "progress": progress_info["progress"],
                "message": progress_info["message"],
                "logs": log_entries,
                "environment": deployment["environment"],
                "rollback_available": deployment["rollback_available"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


class CITools:
    """CI/CD pipeline management tools"""
    
    def __init__(self):
        self.pipeline_templates = self.load_pipeline_templates()
    
    def load_pipeline_templates(self) -> Dict[str, Dict]:
        """Load CI/CD pipeline templates"""
        return {
            "python": {
                "name": "Python Application Pipeline",
                "stages": ["lint", "test", "build", "deploy"],
                "tools": ["pytest", "black", "flake8", "docker", "kubernetes"],
                "triggers": ["push", "pull_request"],
                "environment": ["python:3.9", "node:16"]
            },
            "javascript": {
                "name": "JavaScript Application Pipeline",
                "stages": ["install", "lint", "test", "build", "deploy"],
                "tools": ["npm", "eslint", "jest", "webpack", "docker"],
                "triggers": ["push", "pull_request"],
                "environment": ["node:16", "alpine"]
            },
            "web": {
                "name": "Web Application Pipeline",
                "stages": ["setup", "lint", "test", "build", "deploy"],
                "tools": ["npm", "eslint", "cypress", "webpack", "netlify"],
                "triggers": ["push", "pull_request"],
                "environment": ["node:16", "ubuntu:20.04"]
            }
        }
    
    def create_pipeline(self, name: str, project_type: str, config: Dict = None) -> Dict[str, Any]:
        """Create CI/CD pipeline"""
        try:
            if project_type not in self.pipeline_templates:
                return {"success": False, "error": f"Project type {project_type} not supported"}
            
            template = self.pipeline_templates[project_type]
            pipeline_id = f"pipeline_{len(self.pipelines) + 1}"
            
            # Create pipeline directory
            pipeline_dir = f"/workspace/ci_cd/{name}"
            os.makedirs(pipeline_dir, exist_ok=True)
            
            # Generate pipeline configuration
            self.generate_pipeline_config(pipeline_dir, name, project_type, template, config)
            
            pipeline_info = {
                "pipeline_id": pipeline_id,
                "name": name,
                "type": project_type,
                "pipeline_dir": pipeline_dir,
                "stages": template["stages"],
                "tools": template["tools"],
                "status": "created",
                "created_at": datetime.datetime.now().isoformat()
            }
            
            self.pipelines[pipeline_id] = pipeline_info
            
            return {
                "success": True,
                "pipeline_id": pipeline_id,
                "name": name,
                "type": project_type,
                "stages": len(template["stages"]),
                "pipeline_created": True,
                "configuration_files": [
                    ".github/workflows/ci.yml",
                    "Dockerfile",
                    "docker-compose.yml"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_pipeline_config(self, pipeline_dir: str, name: str, 
                                project_type: str, template: Dict, config: Dict):
        """Generate pipeline configuration files"""
        # Create GitHub Actions workflow
        github_workflow = f'''name: CI/CD Pipeline for {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
'''
        
        # Add jobs for each stage
        for i, stage in enumerate(template["stages"]):
            job_name = stage.capitalize()
            github_workflow += f'''
  {stage}:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Environment
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: {job_name}
      run: |
        echo "Running {stage} stage..."
        # Add {stage} commands here
'''
        
        # Create workflow directory and file
        workflow_dir = f"{pipeline_dir}/.github/workflows"
        os.makedirs(workflow_dir, exist_ok=True)
        
        with open(f"{workflow_dir}/ci.yml", 'w') as f:
            f.write(github_workflow)
        
        # Create Jenkinsfile (alternative CI system)
        jenkinsfile = f'''pipeline {{
    agent any
    
    stages {{
'''
        
        for stage in template["stages"]:
            jenkinsfile += f'''        stage('{stage.capitalize()}') {{
            steps {{
                echo 'Running {stage}...'
                // Add {stage} steps here
            }}
        }}
'''
        
        jenkinsfile += '''    }
    
    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}'''
        
        with open(f"{pipeline_dir}/Jenkinsfile", 'w') as f:
            f.write(jenkinsfile)
        
        # Create Azure DevOps pipeline
        azure_pipeline = f'''# Azure DevOps Pipeline for {name}

trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

steps:
'''
        
        for stage in template["stages"]:
            azure_pipeline += f'''- task: {stage}Task@1
  displayName: '{stage.capitalize()}'
  inputs:
    command: 'run'
    arguments: '{stage}'
'''
        
        with open(f"{pipeline_dir}/azure-pipelines.yml", 'w') as f:
            f.write(azure_pipeline)


class SecurityTools:
    """Security scanning and analysis tools"""
    
    def __init__(self):
        self.scan_types = ["vulnerability", "dependency", "code", "container", "network"]
        self.vulnerability_database = self.load_vulnerability_database()
    
    def load_vulnerability_database(self) -> Dict[str, List]:
        """Load vulnerability database"""
        return {
            "cve": [
                {"id": "CVE-2024-0001", "severity": "high", "package": "requests", "version": "<2.25.0"},
                {"id": "CVE-2024-0002", "severity": "medium", "package": "flask", "version": "<1.0.2"},
                {"id": "CVE-2024-0003", "severity": "low", "package": "numpy", "version": "<1.19.0"}
            ],
            "owasp": [
                {"category": "injection", "risk": "high", "description": "SQL injection vulnerability"},
                {"category": "broken_auth", "risk": "high", "description": "Weak authentication mechanisms"},
                {"category": "sensitive_data", "risk": "medium", "description": "Data exposure risk"}
            ]
        }
    
    def run_scan(self, target: str, scan_type: str = "comprehensive") -> Dict[str, Any]:
        """Run security scan"""
        try:
            scan_id = f"scan_{len(self.security_scans) + 1}"
            
            # Initialize scan results
            scan_results = {
                "scan_id": scan_id,
                "target": target,
                "scan_type": scan_type,
                "started_at": datetime.datetime.now().isoformat(),
                "status": "running",
                "vulnerabilities": [],
                "recommendations": [],
                "risk_score": 0
            }
            
            # Run different types of scans
            if scan_type in ["comprehensive", "vulnerability"]:
                vuln_results = self.run_vulnerability_scan(target)
                scan_results["vulnerabilities"].extend(vuln_results["vulnerabilities"])
            
            if scan_type in ["comprehensive", "dependency"]:
                dep_results = self.run_dependency_scan(target)
                scan_results["vulnerabilities"].extend(dep_results["vulnerabilities"])
            
            if scan_type in ["comprehensive", "code"]:
                code_results = self.run_code_analysis(target)
                scan_results["vulnerabilities"].extend(code_results["vulnerabilities"])
            
            # Calculate risk score
            scan_results["risk_score"] = self.calculate_risk_score(scan_results["vulnerabilities"])
            
            # Generate recommendations
            scan_results["recommendations"] = self.generate_security_recommendations(scan_results["vulnerabilities"])
            
            # Update status
            scan_results["status"] = "completed"
            scan_results["completed_at"] = datetime.datetime.now().isoformat()
            
            self.security_scans[scan_id] = scan_results
            
            return {
                "success": True,
                "scan_id": scan_id,
                "target": target,
                "scan_type": scan_type,
                "vulnerabilities_found": len(scan_results["vulnerabilities"]),
                "risk_score": scan_results["risk_score"],
                "high_risk_issues": len([v for v in scan_results["vulnerabilities"] if v.get("severity") == "high"]),
                "recommendations": len(scan_results["recommendations"])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_vulnerability_scan(self, target: str) -> Dict[str, Any]:
        """Run vulnerability scan"""
        # Simulate vulnerability detection
        vulnerabilities = []
        
        for cve in self.vulnerability_database["cve"]:
            if random.random() > 0.7:  # 30% chance of finding each vulnerability
                vulnerabilities.append({
                    "type": "cve",
                    "id": cve["id"],
                    "severity": cve["severity"],
                    "package": cve["package"],
                    "affected_version": cve["version"],
                    "description": f"Security issue in {cve['package']}",
                    "fix_available": True
                })
        
        return {"vulnerabilities": vulnerabilities}
    
    def run_dependency_scan(self, target: str) -> Dict[str, Any]:
        """Run dependency scan"""
        # Simulate dependency vulnerabilities
        vulnerabilities = [
            {
                "type": "dependency",
                "package": "requests",
                "version": "2.24.0",
                "severity": "medium",
                "issue": "Outdated dependency with known issues",
                "recommended_version": "2.31.0"
            }
        ]
        
        return {"vulnerabilities": vulnerabilities}
    
    def run_code_analysis(self, target: str) -> Dict[str, Any]:
        """Run static code analysis"""
        # Simulate code security issues
        vulnerabilities = [
            {
                "type": "code",
                "file": "app.py",
                "line": 45,
                "issue": "Hardcoded credentials detected",
                "severity": "high",
                "recommendation": "Use environment variables for secrets"
            }
        ]
        
        return {"vulnerabilities": vulnerabilities}
    
    def calculate_risk_score(self, vulnerabilities: List[Dict]) -> int:
        """Calculate overall risk score"""
        severity_weights = {"low": 1, "medium": 5, "high": 10}
        total_score = 0
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            total_score += severity_weights.get(severity, 1)
        
        return min(100, total_score)
    
    def generate_security_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Analyze vulnerabilities and generate recommendations
        issue_types = set(v["type"] for v in vulnerabilities)
        
        if "cve" in issue_types:
            recommendations.append("Update packages to latest secure versions")
        
        if "dependency" in issue_types:
            recommendations.append("Regularly update dependencies")
        
        if "code" in issue_types:
            recommendations.append("Implement secure coding practices")
        
        # Add general recommendations
        recommendations.extend([
            "Enable automatic security updates",
            "Implement regular security scanning",
            "Use secrets management for sensitive data",
            "Set up security monitoring and alerts"
        ])
        
        return list(set(recommendations))  # Remove duplicates


class MonitoringTools:
    """Application and infrastructure monitoring tools"""
    
    def __init__(self):
        self.metrics_collectors = ["prometheus", "grafana", "elasticsearch", "logstash"]
        self.alert_types = ["cpu_high", "memory_high", "disk_low", "response_time", "error_rate"]
    
    def setup_monitoring(self, app_name: str, metrics_config: Dict) -> Dict[str, Any]:
        """Set up monitoring for application"""
        try:
            monitoring_id = f"monitor_{len(self.monitoring_data) + 1}"
            
            # Create monitoring configuration
            monitoring_config = {
                "monitoring_id": monitoring_id,
                "app_name": app_name,
                "metrics": {
                    "system_metrics": ["cpu_usage", "memory_usage", "disk_usage", "network_io"],
                    "application_metrics": ["response_time", "request_count", "error_rate", "throughput"],
                    "business_metrics": metrics_config.get("business_metrics", [])
                },
                "collection_interval": metrics_config.get("interval", "60s"),
                "retention_period": metrics_config.get("retention", "30d"),
                "alerts": self.setup_alerts(metrics_config.get("alerts", {}))
            }
            
            # Generate monitoring stack configuration
            self.create_monitoring_config(app_name, monitoring_config)
            
            self.monitoring_data[monitoring_id] = monitoring_config
            
            return {
                "success": True,
                "monitoring_id": monitoring_id,
                "app_name": app_name,
                "metrics_count": len(monitoring_config["metrics"]["system_metrics"]) + 
                                len(monitoring_config["metrics"]["application_metrics"]),
                "alerts_configured": len(monitoring_config["alerts"]),
                "monitoring_stack": ["Prometheus", "Grafana", "AlertManager"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_alerts(self, alert_config: Dict) -> List[Dict]:
        """Set up monitoring alerts"""
        default_alerts = [
            {
                "name": "High CPU Usage",
                "condition": "cpu_usage > 80%",
                "severity": "warning",
                "action": "send_notification"
            },
            {
                "name": "High Memory Usage", 
                "condition": "memory_usage > 85%",
                "severity": "critical",
                "action": "send_alert"
            },
            {
                "name": "High Error Rate",
                "condition": "error_rate > 5%",
                "severity": "critical",
                "action": "send_alert"
            },
            {
                "name": "Slow Response Time",
                "condition": "response_time > 2s",
                "severity": "warning",
                "action": "send_notification"
            }
        ]
        
        # Add custom alerts if provided
        if alert_config:
            custom_alerts = []
            for name, config in alert_config.items():
                custom_alerts.append({
                    "name": name,
                    "condition": config.get("condition", "default"),
                    "severity": config.get("severity", "warning"),
                    "action": config.get("action", "send_notification")
                })
            default_alerts.extend(custom_alerts)
        
        return default_alerts
    
    def create_monitoring_config(self, app_name: str, config: Dict):
        """Create monitoring configuration files"""
        monitoring_dir = f"/workspace/monitoring/{app_name}"
        os.makedirs(monitoring_dir, exist_ok=True)
        
        # Create Prometheus configuration
        prometheus_config = f'''global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: '{app_name}'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: {config["collection_interval"]}
'''
        
        with open(f"{monitoring_dir}/prometheus.yml", 'w') as f:
            f.write(prometheus_config)
        
        # Create alert rules
        alert_rules = '''groups:
- name: application_alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      
  - alert: HighMemoryUsage
    expr: memory_usage > 85
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage detected"
      
  - alert: HighErrorRate
    expr: error_rate > 5
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
'''
        
        with open(f"{monitoring_dir}/alert_rules.yml", 'w') as f:
            f.write(alert_rules)
        
        # Create Grafana dashboard configuration
        dashboard_config = f'''{{
  "dashboard": {{
    "title": "{app_name} Dashboard",
    "panels": [
      {{
        "title": "CPU Usage",
        "type": "stat",
        "targets": [
          {{
            "expr": "cpu_usage",
            "legendFormat": "CPU %"
          }}
        ]
      }},
      {{
        "title": "Memory Usage",
        "type": "stat", 
        "targets": [
          {{
            "expr": "memory_usage",
            "legendFormat": "Memory %"
          }}
        ]
      }},
      {{
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {{
            "expr": "rate(requests_total[5m])",
            "legendFormat": "Requests/sec"
          }}
        ]
      }}
    ]
  }}
}}'''
        
        with open(f"{monitoring_dir}/dashboard.json", 'w') as f:
            f.write(dashboard_config)


class ContainerTools:
    """Container management and orchestration tools"""
    
    def __init__(self):
        self.container_types = ["docker", "kubernetes", "docker-compose"]
        self.orchestration_tools = ["kubernetes", "docker-swarm", "openshift"]
    
    def create_environment(self, app_name: str, container_type: str = "docker") -> Dict[str, Any]:
        """Create containerized environment"""
        try:
            if container_type not in self.container_types:
                return {"success": False, "error": f"Container type {container_type} not supported"}
            
            env_id = f"container_{len(self.container_types) + 1}"
            
            # Create container directory
            container_dir = f"/workspace/containers/{app_name}"
            os.makedirs(container_dir, exist_ok=True)
            
            # Generate container configurations
            configs = self.generate_container_configs(app_name, container_type, container_dir)
            
            environment_info = {
                "env_id": env_id,
                "app_name": app_name,
                "container_type": container_type,
                "container_dir": container_dir,
                "created_at": datetime.datetime.now().isoformat(),
                "configurations": configs,
                "orchestration": container_type in self.orchestration_tools
            }
            
            return {
                "success": True,
                "env_id": env_id,
                "app_name": app_name,
                "container_type": container_type,
                "environment_created": True,
                "config_files": list(configs.keys()),
                "ready_for_deployment": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_container_configs(self, app_name: str, container_type: str, 
                                  container_dir: str) -> Dict[str, str]:
        """Generate container configuration files"""
        configs = {}
        
        if container_type == "docker":
            # Create Dockerfile
            dockerfile = f'''# Optimized Dockerfile for {app_name}
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "app.py"]
'''
            
            configs["Dockerfile"] = dockerfile
            
            # Create .dockerignore
            dockerignore = '''# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.venv

# IDE
.vscode
.idea

# OS
.DS_Store
Thumbs.db
'''
            
            configs[".dockerignore"] = dockerignore
        
        elif container_type == "docker-compose":
            # Create docker-compose.yml
            compose_file = f'''version: '3.8'

services:
  {app_name.lower()}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://db:5432/myapp
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    depends_on:
      - db
      - redis
    networks:
      - app-network

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:6-alpine
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - {app_name.lower()}
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
'''
            
            configs["docker-compose.yml"] = compose_file
        
        elif container_type == "kubernetes":
            # Create Kubernetes deployment
            deployment = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name.lower()}
  labels:
    app: {app_name.lower()}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {app_name.lower()}
  template:
    metadata:
      labels:
        app: {app_name.lower()}
    spec:
      containers:
      - name: {app_name.lower()}
        image: {app_name.lower()}:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {app_name.lower()}-service
spec:
  selector:
    app: {app_name.lower()}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name.lower()}-ingress
spec:
  rules:
  - host: {app_name.lower()}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app_name.lower()}-service
            port:
              number: 80
'''
            
            configs["k8s-deployment.yaml"] = deployment
        
        # Write configuration files
        for filename, content in configs.items():
            with open(f"{container_dir}/{filename}", 'w') as f:
                f.write(content)
        
        return configs


# Initialize the DevOps and security suite
devops_security_suite = DevOpsSecuritySuite()