#!/usr/bin/env python3
"""
Code Clinging Tool - The Ultimate AI-Powered Code Analysis System
===================================================================

This powerful tool "clings" to your codebase, finding EVERYTHING:
- Complete source code analysis down to every detail
- Vulnerability and weak spot detection
- Breaking large files into smaller, manageable pieces
- Deep semantic understanding like Google/ChatGPT but specialized for code
- Goes beyond traditional tools to find what others miss

Like a "hungry analyzing machine" that scans, searches, and rebuilds
understanding of your entire codebase.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

# Import our AI analyzer
from ai_code_analyzer import AICodeAnalyzer, AnalysisResult


@dataclass
class ClingReport:
    """Comprehensive "clinging" analysis report"""
    total_files: int
    total_lines: int
    total_code_lines: int
    total_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    average_quality_score: float
    average_complexity: float
    weak_spots: List[Dict[str, Any]]
    file_breakdown: Dict[str, Any]
    dependencies_graph: Dict[str, List[str]]
    recommendations: List[str]


class CodeClingingTool:
    """
    The Ultimate Code Clinging Tool
    
    This tool "clings" to your codebase like an AI that never lets go,
    analyzing every aspect:
    
    Features:
    ✅ Finds EVERYTHING in source code - even hidden patterns
    ✅ Detects vulnerabilities and weak spots automatically
    ✅ Breaks down huge files into smaller, manageable pieces
    ✅ Deep LLM-powered semantic understanding
    ✅ Beyond traditional static analysis tools
    ✅ Comprehensive scanning and searching
    ✅ Rebuilding and reorganization suggestions
    
    Like having an AI that hungrily analyzes your entire codebase!
    """
    
    def __init__(self):
        self.analyzer = AICodeAnalyzer()
        self.analysis_cache = {}
        print("🔧 Code Clinging Tool initialized")
        print("   Ready to analyze and find EVERYTHING in your code!")
    
    def cling_to_file(self, file_path: str) -> AnalysisResult:
        """
        "Cling" to a single file - deep analysis
        
        This performs comprehensive analysis that finds everything:
        - Every function, class, import
        - All vulnerabilities and weak spots
        - Complete dependency mapping
        - Quality and complexity metrics
        """
        print(f"\n🔍 Clinging to file: {file_path}")
        print("   Performing deep analysis...")
        
        result = self.analyzer.analyze_file(file_path)
        self.analysis_cache[file_path] = result
        
        print(f"✅ Analysis complete!")
        print(f"   Lines: {result.total_lines}")
        print(f"   Vulnerabilities: {len(result.vulnerabilities)}")
        print(f"   Quality Score: {result.quality_score:.1f}/100")
        
        return result
    
    def cling_to_directory(self, directory: str, recursive: bool = True) -> ClingReport:
        """
        "Cling" to entire directory - comprehensive scan
        
        Scans and analyzes EVERYTHING in the directory:
        - All source files
        - Complete dependency graphs
        - All vulnerabilities across project
        - Quality metrics for entire codebase
        """
        print(f"\n🔍 Clinging to directory: {directory}")
        print("   Scanning for all source files...")
        
        results = self.analyzer.analyze_directory(directory, recursive)
        
        print(f"✅ Found and analyzed {len(results)} files")
        print("   Generating comprehensive report...")
        
        # Generate comprehensive cling report
        report = self._generate_cling_report(results)
        
        print(f"\n📊 CLINGING ANALYSIS COMPLETE")
        print(f"   Total Files: {report.total_files}")
        print(f"   Total Lines: {report.total_lines:,}")
        print(f"   Vulnerabilities Found: {report.total_vulnerabilities}")
        print(f"   Critical Issues: {report.critical_vulnerabilities}")
        print(f"   Average Quality: {report.average_quality_score:.1f}/100")
        
        return report
    
    def find_weak_spots(self, directory: str = '.') -> List[Dict[str, Any]]:
        """
        Find all weak spots in codebase
        
        Identifies:
        - Security vulnerabilities
        - Code smells
        - High complexity areas
        - Low quality code
        - Missing documentation
        """
        print("\n🔍 Scanning for weak spots...")
        
        results = self.analyzer.analyze_directory(directory)
        weak_spots = []
        
        for file_path, result in results.items():
            # High complexity
            if result.complexity_score > 15:
                weak_spots.append({
                    'file': file_path,
                    'type': 'High Complexity',
                    'severity': 'medium',
                    'description': f'Complexity score: {result.complexity_score}',
                    'recommendation': 'Consider refactoring to reduce complexity'
                })
            
            # Low quality
            if result.quality_score < 60:
                weak_spots.append({
                    'file': file_path,
                    'type': 'Low Quality',
                    'severity': 'medium',
                    'description': f'Quality score: {result.quality_score:.1f}/100',
                    'recommendation': 'Improve code quality, add comments, fix issues'
                })
            
            # Vulnerabilities
            for vuln in result.vulnerabilities:
                weak_spots.append({
                    'file': file_path,
                    'type': vuln.type,
                    'severity': vuln.severity,
                    'description': vuln.description,
                    'location': vuln.location,
                    'recommendation': vuln.recommendation
                })
            
            # Large files without structure
            if result.total_lines > 500 and len(result.functions) < 5:
                weak_spots.append({
                    'file': file_path,
                    'type': 'Large Unstructured File',
                    'severity': 'low',
                    'description': f'{result.total_lines} lines with only {len(result.functions)} functions',
                    'recommendation': 'Consider breaking into smaller, more focused modules'
                })
        
        print(f"✅ Found {len(weak_spots)} weak spots")
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        weak_spots.sort(key=lambda x: severity_order.get(x['severity'], 4))
        
        return weak_spots
    
    def break_down_large_file(self, file_path: str, output_dir: str = None) -> List[str]:
        """
        Break down large files into smaller, manageable pieces
        
        This addresses the requirement to "create smaller files from huge"
        like Google/ChatGPT does when processing large documents.
        
        Returns list of created segment files.
        """
        print(f"\n🔪 Breaking down large file: {file_path}")
        
        result = self.analyzer.analyze_file(file_path)
        
        if result.total_lines < 100:
            print(f"   File is small ({result.total_lines} lines), no breakdown needed")
            return []
        
        if output_dir is None:
            output_dir = Path(file_path).parent / f"{Path(file_path).stem}_segments"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        created_files = []
        
        # Break down by segments
        for i, segment in enumerate(result.segments):
            segment_file = output_path / f"segment_{i+1:03d}_{segment.type}.{Path(file_path).suffix}"
            
            with open(segment_file, 'w', encoding='utf-8') as f:
                f.write(f"# Segment {i+1} from {Path(file_path).name}\n")
                f.write(f"# Type: {segment.type}\n")
                f.write(f"# Lines: {segment.start_line}-{segment.end_line}\n\n")
                f.write(segment.content)
            
            created_files.append(str(segment_file))
            print(f"   ✅ Created: {segment_file.name}")
        
        print(f"\n✅ Broke down into {len(created_files)} segments")
        print(f"   Output directory: {output_path}")
        
        return created_files
    
    def _generate_cling_report(self, results: Dict[str, AnalysisResult]) -> ClingReport:
        """Generate comprehensive clinging report"""
        total_files = len(results)
        total_lines = sum(r.total_lines for r in results.values())
        total_code_lines = sum(r.code_lines for r in results.values())
        
        all_vulns = []
        for r in results.values():
            all_vulns.extend(r.vulnerabilities)
        
        total_vulnerabilities = len(all_vulns)
        critical_vulnerabilities = sum(1 for v in all_vulns if v.severity == 'critical')
        high_vulnerabilities = sum(1 for v in all_vulns if v.severity == 'high')
        
        avg_quality = sum(r.quality_score for r in results.values()) / total_files if total_files > 0 else 0
        avg_complexity = sum(r.complexity_score for r in results.values()) / total_files if total_files > 0 else 0
        
        # Identify weak spots
        weak_spots = []
        for file_path, result in results.items():
            if result.quality_score < 60:
                weak_spots.append({
                    'file': file_path,
                    'quality': result.quality_score,
                    'issues': len(result.vulnerabilities)
                })
        
        # File breakdown
        file_breakdown = {}
        for file_path, result in results.items():
            file_breakdown[file_path] = {
                'lines': result.total_lines,
                'quality': result.quality_score,
                'vulnerabilities': len(result.vulnerabilities),
                'complexity': result.complexity_score
            }
        
        # Dependencies graph
        dependencies_graph = {}
        for file_path, result in results.items():
            if result.imports:
                dependencies_graph[file_path] = result.imports
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results)
        
        return ClingReport(
            total_files=total_files,
            total_lines=total_lines,
            total_code_lines=total_code_lines,
            total_vulnerabilities=total_vulnerabilities,
            critical_vulnerabilities=critical_vulnerabilities,
            high_vulnerabilities=high_vulnerabilities,
            average_quality_score=avg_quality,
            average_complexity=avg_complexity,
            weak_spots=weak_spots,
            file_breakdown=file_breakdown,
            dependencies_graph=dependencies_graph,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, results: Dict[str, AnalysisResult]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for critical vulnerabilities
        critical_count = sum(
            sum(1 for v in r.vulnerabilities if v.severity == 'critical')
            for r in results.values()
        )
        if critical_count > 0:
            recommendations.append(
                f"🚨 URGENT: Fix {critical_count} critical security vulnerabilities immediately"
            )
        
        # Check average quality
        avg_quality = sum(r.quality_score for r in results.values()) / len(results) if results else 0
        if avg_quality < 70:
            recommendations.append(
                f"📈 Improve overall code quality (current: {avg_quality:.1f}/100, target: 70+)"
            )
        
        # Check for large files
        large_files = [f for f, r in results.items() if r.total_lines > 500]
        if large_files:
            recommendations.append(
                f"📄 Consider breaking down {len(large_files)} large files into smaller modules"
            )
        
        # Check for low documentation
        low_doc_files = [
            f for f, r in results.items() 
            if r.code_lines > 0 and (r.comment_lines / (r.code_lines + r.comment_lines)) < 0.1
        ]
        if low_doc_files:
            recommendations.append(
                f"📝 Add documentation to {len(low_doc_files)} poorly documented files"
            )
        
        return recommendations
    
    def export_comprehensive_report(self, report: ClingReport, output_file: str = 'cling_report.json'):
        """Export comprehensive clinging report"""
        export_data = {
            'summary': {
                'total_files': report.total_files,
                'total_lines': report.total_lines,
                'total_code_lines': report.total_code_lines,
                'total_vulnerabilities': report.total_vulnerabilities,
                'critical_vulnerabilities': report.critical_vulnerabilities,
                'high_vulnerabilities': report.high_vulnerabilities,
                'average_quality_score': report.average_quality_score,
                'average_complexity': report.average_complexity
            },
            'weak_spots': report.weak_spots,
            'file_breakdown': report.file_breakdown,
            'dependencies_graph': report.dependencies_graph,
            'recommendations': report.recommendations
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n📊 Comprehensive report exported to: {output_file}")
    
    def print_summary(self, report: ClingReport):
        """Print human-readable summary"""
        print("\n" + "=" * 80)
        print("🔍 CODE CLINGING ANALYSIS - COMPLETE SUMMARY")
        print("=" * 80)
        print(f"\n📊 OVERVIEW")
        print(f"   Files Analyzed: {report.total_files}")
        print(f"   Total Lines: {report.total_lines:,}")
        print(f"   Code Lines: {report.total_code_lines:,}")
        print(f"   Average Quality: {report.average_quality_score:.1f}/100")
        print(f"   Average Complexity: {report.average_complexity:.2f}")
        
        print(f"\n🔒 SECURITY")
        print(f"   Total Vulnerabilities: {report.total_vulnerabilities}")
        print(f"   Critical: {report.critical_vulnerabilities}")
        print(f"   High: {report.high_vulnerabilities}")
        
        if report.weak_spots:
            print(f"\n⚠️  WEAK SPOTS")
            for spot in report.weak_spots[:5]:
                print(f"   • {spot['file']}: Quality {spot['quality']:.1f}/100")
        
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 80)


def main():
    """CLI interface for the Code Clinging Tool"""
    if len(sys.argv) < 2:
        print("=" * 80)
        print("🔍 CODE CLINGING TOOL - The Ultimate AI Code Analysis System")
        print("=" * 80)
        print("\nLike an AI that never lets go - finds EVERYTHING in your code!")
        print("\nFeatures:")
        print("  ✅ Complete source code analysis")
        print("  ✅ Vulnerability and weak spot detection")
        print("  ✅ Break down large files into smaller pieces")
        print("  ✅ Deep semantic understanding")
        print("  ✅ Beyond traditional static analysis")
        print("\nUsage:")
        print("  python code_clinging_tool.py <directory>           - Analyze entire directory")
        print("  python code_clinging_tool.py <file>                - Analyze single file")
        print("  python code_clinging_tool.py --weak-spots <dir>    - Find all weak spots")
        print("  python code_clinging_tool.py --break-down <file>   - Break large file into pieces")
        print("\nExamples:")
        print("  python code_clinging_tool.py .")
        print("  python code_clinging_tool.py mycode.py")
        print("  python code_clinging_tool.py --weak-spots src/")
        print("  python code_clinging_tool.py --break-down large_file.py")
        print("=" * 80)
        return
    
    tool = CodeClingingTool()
    
    # Parse arguments
    if sys.argv[1] == '--weak-spots':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        weak_spots = tool.find_weak_spots(directory)
        
        print("\n" + "=" * 80)
        print("⚠️  WEAK SPOTS FOUND")
        print("=" * 80)
        
        for i, spot in enumerate(weak_spots[:20], 1):
            print(f"\n{i}. [{spot['severity'].upper()}] {spot['type']}")
            print(f"   File: {spot['file']}")
            if 'location' in spot:
                print(f"   Location: {spot['location']}")
            print(f"   Description: {spot['description']}")
            print(f"   💡 {spot['recommendation']}")
        
        if len(weak_spots) > 20:
            print(f"\n... and {len(weak_spots) - 20} more weak spots")
        
        # Export
        with open('weak_spots.json', 'w') as f:
            json.dump(weak_spots, f, indent=2)
        print(f"\n📊 Full report saved to: weak_spots.json")
    
    elif sys.argv[1] == '--break-down':
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a file to break down")
            return
        
        file_path = sys.argv[2]
        created_files = tool.break_down_large_file(file_path)
        
        if created_files:
            print(f"\n✅ Success! Created {len(created_files)} segment files")
    
    else:
        target = sys.argv[1]
        path = Path(target)
        
        if path.is_file():
            # Analyze single file
            result = tool.cling_to_file(target)
            print(tool.analyzer.generate_report(result))
            
            if result.vulnerabilities:
                print("\n💡 TOP RECOMMENDATIONS:")
                for v in result.vulnerabilities[:5]:
                    print(f"  • {v.recommendation}")
        
        elif path.is_dir():
            # Analyze directory
            report = tool.cling_to_directory(target)
            tool.print_summary(report)
            tool.export_comprehensive_report(report)
        
        else:
            print(f"❌ Error: {target} not found")


if __name__ == '__main__':
    main()
