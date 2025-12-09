#!/usr/bin/env python3
"""
Layer-Wise Visual Debugging Module
Visualization tools for layer performance, activation maps, and bottleneck detection
"""

import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class LayerMetrics:
    """Performance metrics for a layer"""
    layer_name: str
    forward_time_ms: float
    backward_time_ms: float
    memory_mb: float
    activation_mean: float
    activation_std: float
    gradient_norm: float
    sparsity: float  # Percentage of zero activations


@dataclass
class BottleneckInfo:
    """Information about a computational bottleneck"""
    layer_name: str
    bottleneck_type: str  # "memory", "compute", "communication"
    severity: str  # "low", "medium", "high"
    impact_ms: float
    suggestion: str


class LayerWiseDebugger:
    """Visual debugging and performance analysis for neural network layers"""
    
    def __init__(self, model_id: str, output_dir: str = "debug_visualizations"):
        self.model_id = model_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.layer_metrics: Dict[str, LayerMetrics] = {}
        self.bottlenecks: List[BottleneckInfo] = []
        self.activation_maps: Dict[str, np.ndarray] = {}
    
    def profile_layer(
        self,
        layer_name: str,
        simulate: bool = True
    ) -> LayerMetrics:
        """Profile performance of a specific layer"""
        
        if simulate:
            # Simulate layer profiling
            metrics = LayerMetrics(
                layer_name=layer_name,
                forward_time_ms=np.random.uniform(1.0, 50.0),
                backward_time_ms=np.random.uniform(2.0, 100.0),
                memory_mb=np.random.uniform(100, 5000),
                activation_mean=np.random.normal(0, 1),
                activation_std=np.random.uniform(0.5, 2.0),
                gradient_norm=np.random.uniform(0.001, 1.0),
                sparsity=np.random.uniform(0.1, 0.6)
            )
        else:
            # In real implementation, would profile actual layer
            metrics = LayerMetrics(
                layer_name=layer_name,
                forward_time_ms=0.0,
                backward_time_ms=0.0,
                memory_mb=0.0,
                activation_mean=0.0,
                activation_std=0.0,
                gradient_norm=0.0,
                sparsity=0.0
            )
        
        self.layer_metrics[layer_name] = metrics
        return metrics
    
    def generate_activation_map(
        self,
        layer_name: str,
        input_shape: Tuple[int, ...] = (32, 7168),
        simulate: bool = True
    ) -> np.ndarray:
        """Generate activation map for visualization"""
        
        if simulate:
            # Simulate activation map
            activation_map = np.random.randn(*input_shape)
            # Add some patterns
            activation_map = np.abs(activation_map)
            activation_map = activation_map / activation_map.max()
        else:
            # In real implementation, would extract actual activations
            activation_map = np.zeros(input_shape)
        
        self.activation_maps[layer_name] = activation_map
        return activation_map
    
    def detect_bottlenecks(
        self,
        threshold_ms: float = 20.0
    ) -> List[BottleneckInfo]:
        """Detect computational bottlenecks in the model"""
        
        bottlenecks = []
        
        for layer_name, metrics in self.layer_metrics.items():
            # Check forward pass bottleneck
            if metrics.forward_time_ms > threshold_ms:
                severity = "high" if metrics.forward_time_ms > threshold_ms * 2 else "medium"
                bottleneck = BottleneckInfo(
                    layer_name=layer_name,
                    bottleneck_type="compute",
                    severity=severity,
                    impact_ms=metrics.forward_time_ms - threshold_ms,
                    suggestion="Consider layer optimization, quantization, or pruning"
                )
                bottlenecks.append(bottleneck)
            
            # Check backward pass bottleneck
            if metrics.backward_time_ms > threshold_ms * 1.5:
                severity = "high" if metrics.backward_time_ms > threshold_ms * 3 else "medium"
                bottleneck = BottleneckInfo(
                    layer_name=layer_name,
                    bottleneck_type="compute",
                    severity=severity,
                    impact_ms=metrics.backward_time_ms - threshold_ms * 1.5,
                    suggestion="Optimize gradient computation or use gradient checkpointing"
                )
                bottlenecks.append(bottleneck)
            
            # Check memory bottleneck
            if metrics.memory_mb > 4000:
                severity = "high" if metrics.memory_mb > 6000 else "medium"
                bottleneck = BottleneckInfo(
                    layer_name=layer_name,
                    bottleneck_type="memory",
                    severity=severity,
                    impact_ms=0.0,
                    suggestion="Consider activation checkpointing or mixed precision training"
                )
                bottlenecks.append(bottleneck)
        
        self.bottlenecks = bottlenecks
        return bottlenecks
    
    def visualize_layer_performance(self) -> Dict[str, Any]:
        """Create performance visualization data"""
        
        layers = list(self.layer_metrics.keys())
        forward_times = [m.forward_time_ms for m in self.layer_metrics.values()]
        backward_times = [m.backward_time_ms for m in self.layer_metrics.values()]
        memory_usage = [m.memory_mb for m in self.layer_metrics.values()]
        
        return {
            "chart_type": "layer_performance",
            "layers": layers,
            "forward_pass": {
                "data": forward_times,
                "unit": "milliseconds",
                "total": sum(forward_times),
                "average": np.mean(forward_times),
                "max": max(forward_times) if forward_times else 0
            },
            "backward_pass": {
                "data": backward_times,
                "unit": "milliseconds",
                "total": sum(backward_times),
                "average": np.mean(backward_times),
                "max": max(backward_times) if backward_times else 0
            },
            "memory": {
                "data": memory_usage,
                "unit": "megabytes",
                "total": sum(memory_usage),
                "average": np.mean(memory_usage),
                "peak": max(memory_usage) if memory_usage else 0
            }
        }
    
    def create_activation_heatmap(
        self,
        layer_name: str
    ) -> Dict[str, Any]:
        """Create heatmap data for layer activations"""
        
        if layer_name not in self.activation_maps:
            return {"error": f"No activation map for {layer_name}"}
        
        activation_map = self.activation_maps[layer_name]
        
        # Calculate statistics
        return {
            "chart_type": "activation_heatmap",
            "layer_name": layer_name,
            "shape": activation_map.shape,
            "statistics": {
                "mean": float(np.mean(activation_map)),
                "std": float(np.std(activation_map)),
                "min": float(np.min(activation_map)),
                "max": float(np.max(activation_map)),
                "sparsity": float(np.sum(activation_map == 0) / activation_map.size)
            },
            "heatmap_data": {
                "values": activation_map.tolist()[:32][:32],  # Limit size for JSON
                "colormap": "viridis",
                "interpolation": "nearest"
            },
            "distribution": {
                "histogram": np.histogram(activation_map, bins=50)[0].tolist(),
                "bins": np.histogram(activation_map, bins=50)[1].tolist()
            }
        }
    
    def analyze_gradient_flow(self) -> Dict[str, Any]:
        """Analyze gradient flow through the network"""
        
        layers = list(self.layer_metrics.keys())
        gradient_norms = [m.gradient_norm for m in self.layer_metrics.values()]
        
        # Detect vanishing/exploding gradients
        issues = []
        for layer, norm in zip(layers, gradient_norms):
            if norm < 0.001:
                issues.append({
                    "layer": layer,
                    "issue": "vanishing_gradient",
                    "severity": "high" if norm < 0.0001 else "medium",
                    "gradient_norm": norm
                })
            elif norm > 10.0:
                issues.append({
                    "layer": layer,
                    "issue": "exploding_gradient",
                    "severity": "high" if norm > 100.0 else "medium",
                    "gradient_norm": norm
                })
        
        return {
            "chart_type": "gradient_flow",
            "layers": layers,
            "gradient_norms": gradient_norms,
            "average_norm": float(np.mean(gradient_norms)),
            "issues": issues,
            "recommendations": self._generate_gradient_recommendations(issues)
        }
    
    def profile_full_pass(
        self,
        num_layers: int = 61
    ) -> Dict[str, Any]:
        """Profile a complete forward and backward pass"""
        
        print(f"Profiling {num_layers} layers...")
        
        # Profile each layer
        for i in range(num_layers):
            layer_name = f"layer_{i}"
            self.profile_layer(layer_name)
            
            # Generate activation map for visualization
            if i % 10 == 0:  # Every 10th layer
                self.generate_activation_map(layer_name)
        
        # Detect bottlenecks
        bottlenecks = self.detect_bottlenecks()
        
        # Create visualizations
        performance_viz = self.visualize_layer_performance()
        gradient_flow = self.analyze_gradient_flow()
        
        return {
            "model_id": self.model_id,
            "timestamp": datetime.now().isoformat(),
            "total_layers": num_layers,
            "total_forward_time_ms": performance_viz["forward_pass"]["total"],
            "total_backward_time_ms": performance_viz["backward_pass"]["total"],
            "peak_memory_mb": performance_viz["memory"]["peak"],
            "bottlenecks_found": len(bottlenecks),
            "gradient_issues": len(gradient_flow["issues"]),
            "performance_visualization": performance_viz,
            "gradient_flow": gradient_flow,
            "bottlenecks": [asdict(b) for b in bottlenecks]
        }
    
    def _generate_gradient_recommendations(
        self,
        issues: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on gradient issues"""
        
        recommendations = []
        
        if any(i["issue"] == "vanishing_gradient" for i in issues):
            recommendations.append("Add residual connections or use gradient clipping")
            recommendations.append("Consider using batch normalization or layer normalization")
        
        if any(i["issue"] == "exploding_gradient" for i in issues):
            recommendations.append("Implement gradient clipping with appropriate threshold")
            recommendations.append("Reduce learning rate or use adaptive optimizers")
        
        if len(issues) > 5:
            recommendations.append("Consider architectural changes to improve gradient flow")
        
        return recommendations if recommendations else ["Gradient flow is healthy"]
    
    def export_debug_report(self, output_path: str) -> None:
        """Export comprehensive debugging report"""
        
        report = {
            "model_id": self.model_id,
            "timestamp": datetime.now().isoformat(),
            "layer_metrics": {k: asdict(v) for k, v in self.layer_metrics.items()},
            "bottlenecks": [asdict(b) for b in self.bottlenecks],
            "performance_summary": self.visualize_layer_performance(),
            "gradient_analysis": self.analyze_gradient_flow(),
            "activation_maps_available": list(self.activation_maps.keys())
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def generate_html_visualization(self, output_path: str) -> None:
        """Generate interactive HTML visualization"""
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Layer-Wise Debug Visualization - {model_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        .bottleneck {{ background: #ffe6e6; padding: 10px; margin: 5px 0; border-left: 4px solid #ff4444; }}
        .healthy {{ background: #e6ffe6; padding: 10px; margin: 5px 0; border-left: 4px solid #44ff44; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
    </style>
</head>
<body>
    <h1>Layer-Wise Debug Visualization</h1>
    <p>Model: {model_id}</p>
    <p>Generated: {timestamp}</p>
    
    <h2>Performance Summary</h2>
    <div class="metric">
        <strong>Total Forward Pass:</strong> {forward_time:.2f} ms<br>
        <strong>Total Backward Pass:</strong> {backward_time:.2f} ms<br>
        <strong>Peak Memory:</strong> {peak_memory:.2f} MB
    </div>
    
    <h2>Bottlenecks Detected</h2>
    {bottlenecks_html}
    
    <h2>Gradient Flow</h2>
    {gradient_html}
</body>
</html>
"""
        
        performance = self.visualize_layer_performance()
        
        bottlenecks_html = ""
        for b in self.bottlenecks:
            bottlenecks_html += f'<div class="bottleneck">'
            bottlenecks_html += f'<strong>{b.layer_name}</strong> - {b.bottleneck_type} '
            bottlenecks_html += f'({b.severity}): {b.suggestion}</div>'
        
        if not self.bottlenecks:
            bottlenecks_html = '<div class="healthy">No bottlenecks detected!</div>'
        
        gradient_flow = self.analyze_gradient_flow()
        gradient_html = ""
        for issue in gradient_flow["issues"]:
            gradient_html += f'<div class="bottleneck">'
            gradient_html += f'<strong>{issue["layer"]}</strong>: {issue["issue"]} '
            gradient_html += f'(norm: {issue["gradient_norm"]:.6f})</div>'
        
        if not gradient_flow["issues"]:
            gradient_html = '<div class="healthy">Gradient flow is healthy!</div>'
        
        html_content = html_template.format(
            model_id=self.model_id,
            timestamp=datetime.now().isoformat(),
            forward_time=performance["forward_pass"]["total"],
            backward_time=performance["backward_pass"]["total"],
            peak_memory=performance["memory"]["peak"],
            bottlenecks_html=bottlenecks_html,
            gradient_html=gradient_html
        )
        
        with open(output_path, 'w') as f:
            f.write(html_content)


if __name__ == "__main__":
    # Example usage
    debugger = LayerWiseDebugger("kimi-k2-instruct")
    
    print("🔍 Layer-Wise Visual Debugging")
    print("=" * 60)
    
    # Profile full model
    print("\n1. Profiling full model (61 layers)...")
    profile_result = debugger.profile_full_pass(num_layers=61)
    
    print(f"\n   Performance Summary:")
    print(f"   - Forward pass: {profile_result['total_forward_time_ms']:.2f} ms")
    print(f"   - Backward pass: {profile_result['total_backward_time_ms']:.2f} ms")
    print(f"   - Peak memory: {profile_result['peak_memory_mb']:.2f} MB")
    print(f"   - Bottlenecks found: {profile_result['bottlenecks_found']}")
    print(f"   - Gradient issues: {profile_result['gradient_issues']}")
    
    # Create activation heatmap
    print("\n2. Creating activation heatmaps...")
    for layer in ["layer_0", "layer_30", "layer_60"]:
        if layer in debugger.activation_maps:
            heatmap = debugger.create_activation_heatmap(layer)
            print(f"   ✓ {layer}: sparsity={heatmap['statistics']['sparsity']:.2f}")
    
    # Export reports
    print("\n3. Exporting debug reports...")
    debugger.export_debug_report("debug_report.json")
    print("   ✓ JSON report: debug_report.json")
    
    debugger.generate_html_visualization("debug_visualization.html")
    print("   ✓ HTML visualization: debug_visualization.html")
    
    print("\n✅ Layer-wise debugging complete!")
