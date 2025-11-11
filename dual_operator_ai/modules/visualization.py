"""
Visualization Module

Provides visualization and dashboard capabilities for decision transparency
in the dual-operator AI system.
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class DecisionVisualizer:
    """
    Visualizes decision-making processes and audit trails.
    
    This class generates visual representations of how decisions are made,
    showing contributions from both users and the fusion process.
    """
    
    def __init__(self):
        """Initialize the decision visualizer."""
        self.visualization_cache: Dict[str, Any] = {}
        
    def generate_decision_summary(
        self,
        decision: Dict[str, Any],
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a visual summary of a decision.
        
        Args:
            decision: Decision dictionary
            include_details: Whether to include detailed information
            
        Returns:
            Summary dictionary with visualization data
        """
        summary = {
            'timestamp': decision.get('timestamp', datetime.now().isoformat()),
            'strategy': decision.get('strategy', 'unknown'),
            'participants': [],
            'consensus_level': 0.0,
            'visualization_data': {}
        }
        
        # Extract participant information
        if 'decisions' in decision:
            for dec in decision['decisions']:
                summary['participants'].append({
                    'user_id': dec.get('user_id', 'unknown'),
                    'weight': dec.get('weight', 1.0),
                    'expertise': dec.get('expertise', [])
                })
        
        # Calculate consensus
        if 'consensus_level' in decision:
            summary['consensus_level'] = decision['consensus_level']
        
        # Generate visualization data
        summary['visualization_data'] = self._generate_chart_data(decision)
        
        if include_details:
            summary['details'] = decision
        
        return summary
    
    def _generate_chart_data(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate chart data for visualization.
        
        Args:
            decision: Decision dictionary
            
        Returns:
            Chart data dictionary
        """
        chart_data = {
            'type': 'decision_breakdown',
            'data': []
        }
        
        if 'decisions' in decision:
            for dec in decision['decisions']:
                chart_data['data'].append({
                    'user': dec.get('user_id', 'unknown'),
                    'weight': dec.get('weight', 1.0),
                    'contribution': len(dec.get('content', {}))
                })
        
        return chart_data
    
    def generate_audit_dashboard(
        self,
        audit_trail: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive audit dashboard.
        
        Args:
            audit_trail: Audit trail data
            
        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            'session_id': audit_trail.get('session_id', 'unknown'),
            'overview': {},
            'user_contributions': {},
            'decision_timeline': [],
            'context_analysis': {},
            'fusion_statistics': {}
        }
        
        # Overview statistics
        dashboard['overview'] = {
            'total_decisions': len(audit_trail.get('decision_history', [])),
            'context_entries': audit_trail.get('context_summary', {}).get('total_entries', 0),
            'fusion_strategy': audit_trail.get('fusion_strategy', 'unknown'),
            'users': audit_trail.get('users', {})
        }
        
        # User contributions
        users = audit_trail.get('users', {})
        for user_key, user_data in users.items():
            dashboard['user_contributions'][user_data['id']] = {
                'name': user_data['name'],
                'weight': user_data['weight'],
                'strengths': user_data['strengths'],
                'decision_count': self._count_user_decisions(
                    audit_trail.get('decision_history', []),
                    user_data['id']
                )
            }
        
        # Decision timeline
        for decision in audit_trail.get('decision_history', []):
            timeline_entry = {
                'timestamp': decision.get('timestamp', ''),
                'strategy': decision.get('strategy', ''),
                'participants': len(decision.get('decisions', []))
            }
            dashboard['decision_timeline'].append(timeline_entry)
        
        # Context analysis
        context_summary = audit_trail.get('context_summary', {})
        dashboard['context_analysis'] = {
            'total_entries': context_summary.get('total_entries', 0),
            'modality_breakdown': context_summary.get('modality_counts', {}),
            'role_breakdown': context_summary.get('role_counts', {}),
            'shared_entries': context_summary.get('shared_entries', 0)
        }
        
        # Fusion statistics
        dashboard['fusion_statistics'] = self._calculate_fusion_stats(
            audit_trail.get('decision_history', [])
        )
        
        return dashboard
    
    def _count_user_decisions(
        self,
        decision_history: List[Dict[str, Any]],
        user_id: str
    ) -> int:
        """
        Count decisions involving a specific user.
        
        Args:
            decision_history: List of decisions
            user_id: User ID to count
            
        Returns:
            Count of decisions
        """
        count = 0
        for decision in decision_history:
            for dec in decision.get('decisions', []):
                if dec.get('user_id') == user_id:
                    count += 1
                    break
        return count
    
    def _calculate_fusion_stats(
        self,
        decision_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics about decision fusion.
        
        Args:
            decision_history: List of decisions
            
        Returns:
            Fusion statistics
        """
        stats = {
            'total_fusions': len(decision_history),
            'strategies_used': {},
            'average_consensus': 0.0,
            'consensus_decisions': 0
        }
        
        consensus_sum = 0.0
        consensus_count = 0
        
        for decision in decision_history:
            strategy = decision.get('strategy', 'unknown')
            stats['strategies_used'][strategy] = stats['strategies_used'].get(strategy, 0) + 1
            
            if 'consensus_level' in decision:
                consensus_sum += decision['consensus_level']
                consensus_count += 1
                if decision['consensus_level'] >= 0.8:
                    stats['consensus_decisions'] += 1
        
        if consensus_count > 0:
            stats['average_consensus'] = consensus_sum / consensus_count
        
        return stats
    
    def export_visualization(
        self,
        dashboard: Dict[str, Any],
        filepath: str,
        format: str = 'json'
    ) -> None:
        """
        Export visualization data to a file.
        
        Args:
            dashboard: Dashboard data
            filepath: Path to save the file
            format: Export format (json, html, etc.)
        """
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(dashboard, f, indent=2)
        elif format == 'html':
            html_content = self._generate_html_dashboard(dashboard)
            with open(filepath, 'w') as f:
                f.write(html_content)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_dashboard(self, dashboard: Dict[str, Any]) -> str:
        """
        Generate HTML dashboard.
        
        Args:
            dashboard: Dashboard data
            
        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Dual Operator AI Dashboard - {dashboard['session_id']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1783ff;
            border-bottom: 2px solid #1783ff;
            padding-bottom: 10px;
        }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #1783ff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #1783ff;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Dual Operator AI Dashboard</h1>
        <p>Session ID: {dashboard['session_id']}</p>
        
        <div class="section">
            <h2>Overview</h2>
            <div class="metric">
                <span class="metric-label">Total Decisions:</span>
                <span class="metric-value">{dashboard['overview']['total_decisions']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Context Entries:</span>
                <span class="metric-value">{dashboard['overview']['context_entries']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Fusion Strategy:</span>
                <span class="metric-value">{dashboard['overview']['fusion_strategy']}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>User Contributions</h2>
            <table>
                <tr>
                    <th>User</th>
                    <th>Weight</th>
                    <th>Strengths</th>
                    <th>Decisions</th>
                </tr>
"""
        
        for user_id, user_data in dashboard['user_contributions'].items():
            html += f"""
                <tr>
                    <td>{user_data['name']}</td>
                    <td>{user_data['weight']:.2f}</td>
                    <td>{', '.join(user_data['strengths'])}</td>
                    <td>{user_data['decision_count']}</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>Fusion Statistics</h2>
"""
        
        fusion_stats = dashboard['fusion_statistics']
        html += f"""
            <div class="metric">
                <span class="metric-label">Total Fusions:</span>
                <span class="metric-value">{fusion_stats['total_fusions']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Average Consensus:</span>
                <span class="metric-value">{fusion_stats['average_consensus']:.2%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">High Consensus Decisions:</span>
                <span class="metric-value">{fusion_stats['consensus_decisions']}</span>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html
