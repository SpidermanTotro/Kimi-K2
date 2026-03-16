#!/usr/bin/env python3
"""
Kimi K2 + FORGE Performance Tracking Dashboard

Web-based dashboard for visualizing benchmark performance over time
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


class PerformanceDashboard:
    """Performance tracking and visualization dashboard"""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.results_file = self.results_dir / "benchmark_results.json"
        self.charts_dir = self.results_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
    
    def load_results(self) -> Dict[str, Any]:
        """Load benchmark results"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                return json.load(f)
        return {"runs": [], "summary": {}}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate overall statistics"""
        data = self.load_results()
        runs = data.get("runs", [])
        
        if not runs:
            return {
                "total_runs": 0,
                "success_rate": 0,
                "avg_score": 0,
                "avg_improvement": 0,
                "targets_met": 0
            }
        
        successful_runs = [r for r in runs if r['status'] == 'success']
        scores = [r['score'] for r in successful_runs if r['score']]
        improvements = [r['improvement_pct'] for r in successful_runs 
                       if r['improvement_pct'] is not None]
        targets_met = sum(1 for r in runs if r.get('target_met'))
        
        return {
            "total_runs": len(runs),
            "successful_runs": len(successful_runs),
            "success_rate": (len(successful_runs) / len(runs)) * 100,
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "avg_improvement": sum(improvements) / len(improvements) if improvements else 0,
            "targets_met": targets_met,
            "targets_total": sum(1 for r in runs if r.get('target_score'))
        }
    
    def get_category_breakdown(self) -> Dict[str, List[Dict]]:
        """Group results by category"""
        data = self.load_results()
        runs = data.get("runs", [])
        
        by_category = {}
        for run in runs:
            category = run.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(run)
        
        return by_category
    
    def generate_charts(self):
        """Generate visualization charts"""
        data = self.load_results()
        runs = data.get("runs", [])
        
        if not runs:
            print("⚠️ No data available for chart generation")
            return
        
        # Chart 1: Score comparison
        self._generate_score_chart(runs)
        
        # Chart 2: Improvement chart
        self._generate_improvement_chart(runs)
        
        # Chart 3: Category breakdown
        self._generate_category_chart(runs)
        
        print(f"✅ Charts generated in {self.charts_dir}")
    
    def _generate_score_chart(self, runs: List[Dict]):
        """Generate score comparison chart"""
        # Filter successful runs with scores
        valid_runs = [r for r in runs if r['status'] == 'success' and r['score']]
        
        if not valid_runs:
            return
        
        names = [r['name'] for r in valid_runs]
        scores = [r['score'] for r in valid_runs]
        baselines = [r.get('baseline_score', 0) for r in valid_runs]
        targets = [r.get('target_score', 0) for r in valid_runs]
        
        plt.figure(figsize=(14, 6))
        x = range(len(names))
        width = 0.25
        
        plt.bar([i - width for i in x], baselines, width, label='Baseline', alpha=0.7)
        plt.bar(x, scores, width, label='Current Score', alpha=0.7)
        plt.bar([i + width for i in x], targets, width, label='Target', alpha=0.7)
        
        plt.xlabel('Benchmark')
        plt.ylabel('Score (%)')
        plt.title('Benchmark Scores: Baseline vs Current vs Target')
        plt.xticks(x, names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.grid(axis='y', alpha=0.3)
        
        plt.savefig(self.charts_dir / 'score_comparison.png', dpi=150)
        plt.close()
    
    def _generate_improvement_chart(self, runs: List[Dict]):
        """Generate improvement percentage chart"""
        valid_runs = [r for r in runs if r.get('improvement_pct') is not None]
        
        if not valid_runs:
            return
        
        names = [r['name'] for r in valid_runs]
        improvements = [r['improvement_pct'] for r in valid_runs]
        
        plt.figure(figsize=(12, 6))
        colors = ['green' if i > 0 else 'red' for i in improvements]
        plt.bar(range(len(names)), improvements, color=colors, alpha=0.7)
        
        plt.xlabel('Benchmark')
        plt.ylabel('Improvement (%)')
        plt.title('Performance Improvement by Benchmark')
        plt.xticks(range(len(names)), names, rotation=45, ha='right')
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.tight_layout()
        plt.grid(axis='y', alpha=0.3)
        
        plt.savefig(self.charts_dir / 'improvement_chart.png', dpi=150)
        plt.close()
    
    def _generate_category_chart(self, runs: List[Dict]):
        """Generate category breakdown pie chart"""
        by_category = {}
        for run in runs:
            category = run.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(run)
        
        categories = list(by_category.keys())
        counts = [len(by_category[c]) for c in categories]
        
        plt.figure(figsize=(10, 8))
        plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Benchmarks by Category')
        plt.axis('equal')
        
        plt.savefig(self.charts_dir / 'category_breakdown.png', dpi=150)
        plt.close()
    
    def create_html_dashboard(self, output_file: str = None):
        """Create a standalone HTML dashboard"""
        if output_file is None:
            output_file = self.results_dir / "dashboard.html"
        
        stats = self.get_statistics()
        by_category = self.get_category_breakdown()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kimi K2 + FORGE Performance Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1783ff;
            border-bottom: 3px solid #1783ff;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .charts {{
            margin: 30px 0;
        }}
        .chart-image {{
            width: 100%;
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #1783ff;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .success {{ color: #22c55e; }}
        .warning {{ color: #f59e0b; }}
        .error {{ color: #ef4444; }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Kimi K2 + FORGE Performance Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Runs</div>
                <div class="stat-value">{stats['total_runs']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{stats['success_rate']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Score</div>
                <div class="stat-value">{stats['avg_score']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Improvement</div>
                <div class="stat-value">+{stats['avg_improvement']:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Targets Met</div>
                <div class="stat-value">{stats['targets_met']}/{stats['targets_total']}</div>
            </div>
        </div>
        
        <h2>📊 Performance Charts</h2>
        <div class="charts">
            <img src="charts/score_comparison.png" alt="Score Comparison" class="chart-image">
            <img src="charts/improvement_chart.png" alt="Improvement Chart" class="chart-image">
            <img src="charts/category_breakdown.png" alt="Category Breakdown" class="chart-image">
        </div>
        
        <h2>📋 Results by Category</h2>
"""
        
        for category, runs in by_category.items():
            html += f"""
        <h3>{category.upper()}</h3>
        <table>
            <tr>
                <th>Benchmark</th>
                <th>Score</th>
                <th>Baseline</th>
                <th>Improvement</th>
                <th>Target</th>
                <th>Status</th>
            </tr>
"""
            for run in runs:
                score = f"{run['score']:.1f}%" if run.get('score') else "N/A"
                baseline = f"{run['baseline_score']:.1f}%" if run.get('baseline_score') else "N/A"
                improvement = f"+{run['improvement_pct']:.1f}%" if run.get('improvement_pct') else "N/A"
                target = f"{run['target_score']:.1f}%" if run.get('target_score') else "N/A"
                
                if run['status'] == 'success':
                    if run.get('target_met'):
                        status = '<span class="success">✅ Met</span>'
                    elif run.get('target_met') is False:
                        status = '<span class="warning">⚠️ Not Met</span>'
                    else:
                        status = '<span class="success">✅ Pass</span>'
                else:
                    status = '<span class="error">❌ Failed</span>'
                
                html += f"""
            <tr>
                <td>{run['name']}</td>
                <td>{score}</td>
                <td>{baseline}</td>
                <td>{improvement}</td>
                <td>{target}</td>
                <td>{status}</td>
            </tr>
"""
            html += "        </table>\n"
        
        html += f"""
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"✅ HTML dashboard created: {output_file}")
        return str(output_file)


def main():
    """Generate dashboard"""
    print("=" * 70)
    print("📊 KIMI K2 + FORGE PERFORMANCE DASHBOARD")
    print("=" * 70)
    print()
    
    dashboard = PerformanceDashboard()
    
    # Generate charts
    dashboard.generate_charts()
    
    # Create HTML dashboard
    html_file = dashboard.create_html_dashboard()
    
    print()
    print("✅ Dashboard generation complete!")
    print(f"📁 View dashboard: file://{Path(html_file).absolute()}")


if __name__ == "__main__":
    main()
