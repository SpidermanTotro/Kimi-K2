#!/usr/bin/env python3
"""
AI Code Analyzer - Advanced Code Analysis and Clinging Tool
=============================================================

A comprehensive AI-powered code analysis tool that "clings" to source code,
finding everything including:
- Source code structure and dependencies
- Vulnerabilities and weak spots
- Breaking down large files into manageable chunks
- Deep semantic analysis
- Code quality assessment

This tool goes beyond traditional static analysis, using AI techniques
to understand code at a deeper level.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


@dataclass
class CodeSegment:
    """Represents a segment of code for analysis"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    type: str  # function, class, module, etc.
    complexity: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Vulnerability:
    """Represents a detected vulnerability or weakness"""
    severity: str  # critical, high, medium, low
    type: str
    description: str
    location: str
    line_number: int
    recommendation: str


@dataclass
class AnalysisResult:
    """Complete analysis results"""
    file_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    vulnerabilities: List[Vulnerability]
    segments: List[CodeSegment]
    complexity_score: float
    dependencies: Dict[str, List[str]]
    quality_score: float


class AICodeAnalyzer:
    """
    Advanced AI Code Analyzer - "Clings" to code to find everything
    
    Features:
    - Deep source code analysis
    - Vulnerability detection
    - Large file breakdown
    - Dependency mapping
    - Quality assessment
    - Semantic understanding
    """
    
    def __init__(self):
        self.analyzed_files = {}
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
        
    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict]]:
        """Load patterns for vulnerability detection"""
        return {
            'python': [
                {
                    'pattern': r'eval\s*\(',
                    'severity': 'critical',
                    'type': 'Code Injection',
                    'description': 'Use of eval() can lead to code injection',
                    'recommendation': 'Avoid eval(), use ast.literal_eval() or safer alternatives'
                },
                {
                    'pattern': r'exec\s*\(',
                    'severity': 'critical',
                    'type': 'Code Injection',
                    'description': 'Use of exec() can lead to code injection',
                    'recommendation': 'Avoid exec(), restructure code to avoid dynamic execution'
                },
                {
                    'pattern': r'pickle\.loads?\s*\(',
                    'severity': 'high',
                    'type': 'Deserialization',
                    'description': 'Pickle deserialization can execute arbitrary code',
                    'recommendation': 'Use json.loads() or validate pickle data source'
                },
                {
                    'pattern': r'os\.system\s*\(',
                    'severity': 'high',
                    'type': 'Command Injection',
                    'description': 'os.system() is vulnerable to command injection',
                    'recommendation': 'Use subprocess.run() with shell=False and list arguments'
                },
                {
                    'pattern': r'shell\s*=\s*True',
                    'severity': 'high',
                    'type': 'Command Injection',
                    'description': 'shell=True in subprocess is vulnerable',
                    'recommendation': 'Use shell=False and pass command as list'
                },
                {
                    'pattern': r'(?:md5|sha1)\s*\(',
                    'severity': 'medium',
                    'type': 'Weak Cryptography',
                    'description': 'MD5/SHA1 are cryptographically broken',
                    'recommendation': 'Use SHA256 or stronger hash functions'
                },
                {
                    'pattern': r'password\s*=\s*["\'][\w]+["\']',
                    'severity': 'critical',
                    'type': 'Hardcoded Credentials',
                    'description': 'Hardcoded password in source code',
                    'recommendation': 'Use environment variables or secure credential storage'
                },
                {
                    'pattern': r'(?:api_key|secret|token)\s*=\s*["\'][\w-]+["\']',
                    'severity': 'critical',
                    'type': 'Hardcoded Secrets',
                    'description': 'Hardcoded API key or secret in source code',
                    'recommendation': 'Use environment variables or secret management service'
                },
            ],
            'javascript': [
                {
                    'pattern': r'eval\s*\(',
                    'severity': 'critical',
                    'type': 'Code Injection',
                    'description': 'Use of eval() can lead to code injection',
                    'recommendation': 'Avoid eval(), use JSON.parse() or safer alternatives'
                },
                {
                    'pattern': r'innerHTML\s*=',
                    'severity': 'medium',
                    'type': 'XSS Vulnerability',
                    'description': 'innerHTML can lead to XSS attacks',
                    'recommendation': 'Use textContent or sanitize input'
                },
                {
                    'pattern': r'document\.write\s*\(',
                    'severity': 'medium',
                    'type': 'XSS Vulnerability',
                    'description': 'document.write can lead to XSS attacks',
                    'recommendation': 'Use modern DOM manipulation methods'
                },
            ]
        }
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Comprehensive analysis of a single file
        
        Performs deep "clinging" analysis to find everything:
        - Code structure
        - Vulnerabilities
        - Dependencies
        - Quality metrics
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        extension = file_path_obj.suffix
        
        # Basic line counting
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Count different types of lines
        code_lines, comment_lines, blank_lines = self._count_lines(lines, extension)
        
        # Extract structure (language-specific)
        functions, classes, imports = self._extract_structure(content, extension)
        
        # Detect vulnerabilities
        vulnerabilities = self._detect_vulnerabilities(content, lines, extension)
        
        # Break into segments
        segments = self._create_segments(content, lines, extension)
        
        # Calculate complexity
        complexity_score = self._calculate_complexity(content, functions, classes)
        
        # Map dependencies
        dependencies = self._map_dependencies(imports, content)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            code_lines, comment_lines, vulnerabilities, complexity_score
        )
        
        result = AnalysisResult(
            file_path=str(file_path),
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            functions=functions,
            classes=classes,
            imports=imports,
            vulnerabilities=vulnerabilities,
            segments=segments,
            complexity_score=complexity_score,
            dependencies=dependencies,
            quality_score=quality_score
        )
        
        self.analyzed_files[str(file_path)] = result
        return result
    
    def _count_lines(self, lines: List[str], extension: str) -> Tuple[int, int, int]:
        """Count code, comment, and blank lines"""
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                blank_lines += 1
                continue
            
            # Python/Ruby/Shell comments
            if extension in {'.py', '.rb', '.sh'}:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_multiline_comment = not in_multiline_comment
                    comment_lines += 1
                elif in_multiline_comment:
                    comment_lines += 1
                elif stripped.startswith('#'):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            # JavaScript/TypeScript/C/C++/Java comments
            elif extension in {'.js', '.ts', '.c', '.cpp', '.java', '.go', '.rs'}:
                if '/*' in stripped:
                    in_multiline_comment = True
                    comment_lines += 1
                elif '*/' in stripped:
                    in_multiline_comment = False
                    comment_lines += 1
                elif in_multiline_comment:
                    comment_lines += 1
                elif stripped.startswith('//'):
                    comment_lines += 1
                else:
                    code_lines += 1
            else:
                code_lines += 1
        
        return code_lines, comment_lines, blank_lines
    
    def _extract_structure(self, content: str, extension: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract functions, classes, and imports"""
        functions = []
        classes = []
        imports = []
        
        if extension == '.py':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
            except:
                # Fallback to regex if AST parsing fails
                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                classes = re.findall(r'class\s+(\w+)\s*[\(:]', content)
                imports = re.findall(r'(?:from\s+(\w+)|import\s+(\w+))', content)
                imports = [i[0] or i[1] for i in imports]
        
        elif extension in {'.js', '.ts'}:
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            functions += re.findall(r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', content)
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import.*from\s+["\']([^"\']+)["\']', content)
            imports += re.findall(r'require\(["\']([^"\']+)["\']\)', content)
        
        elif extension in {'.java', '.cpp', '.c'}:
            functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?[\w<>]+\s+(\w+)\s*\([^)]*\)\s*{', content)
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import\s+([\w.]+);', content)
        
        return functions, classes, imports
    
    def _detect_vulnerabilities(self, content: str, lines: List[str], extension: str) -> List[Vulnerability]:
        """Detect vulnerabilities and weak spots"""
        vulnerabilities = []
        
        # Get patterns for this file type
        lang = 'python' if extension == '.py' else 'javascript' if extension in {'.js', '.ts'} else None
        
        if not lang or lang not in self.vulnerability_patterns:
            return vulnerabilities
        
        patterns = self.vulnerability_patterns[lang]
        
        for i, line in enumerate(lines, 1):
            for pattern_def in patterns:
                if re.search(pattern_def['pattern'], line):
                    vuln = Vulnerability(
                        severity=pattern_def['severity'],
                        type=pattern_def['type'],
                        description=pattern_def['description'],
                        location=f"Line {i}",
                        line_number=i,
                        recommendation=pattern_def['recommendation']
                    )
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _create_segments(self, content: str, lines: List[str], extension: str) -> List[CodeSegment]:
        """Break down large files into manageable segments"""
        segments = []
        
        if extension == '.py':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        segment = CodeSegment(
                            file_path="",
                            start_line=node.lineno,
                            end_line=node.end_lineno or node.lineno,
                            content=ast.get_source_segment(content, node) or "",
                            type='function' if isinstance(node, ast.FunctionDef) else 'class'
                        )
                        segments.append(segment)
            except:
                pass
        
        # If no segments found or not Python, create chunks
        if not segments and len(lines) > 100:
            chunk_size = 100
            for i in range(0, len(lines), chunk_size):
                end = min(i + chunk_size, len(lines))
                segment = CodeSegment(
                    file_path="",
                    start_line=i + 1,
                    end_line=end,
                    content='\n'.join(lines[i:end]),
                    type='chunk'
                )
                segments.append(segment)
        
        return segments
    
    def _calculate_complexity(self, content: str, functions: List[str], classes: List[str]) -> float:
        """Calculate code complexity score"""
        # Simple complexity metrics
        complexity = 0
        
        # Cyclomatic complexity indicators
        complexity += content.count('if ')
        complexity += content.count('elif ')
        complexity += content.count('else:')
        complexity += content.count('for ')
        complexity += content.count('while ')
        complexity += content.count('try:')
        complexity += content.count('except ')
        
        # Normalize by lines
        lines = content.count('\n') + 1
        complexity_score = (complexity / lines) * 100 if lines > 0 else 0
        
        return round(complexity_score, 2)
    
    def _map_dependencies(self, imports: List[str], content: str) -> Dict[str, List[str]]:
        """Map dependencies and relationships"""
        dependencies = defaultdict(list)
        
        for imp in imports:
            # Categorize dependency
            if imp in {'os', 'sys', 'pathlib', 'subprocess'}:
                dependencies['system'].append(imp)
            elif imp in {'json', 'yaml', 'xml', 'csv'}:
                dependencies['data'].append(imp)
            elif imp in {'flask', 'django', 'fastapi', 'express'}:
                dependencies['web'].append(imp)
            elif imp in {'numpy', 'pandas', 'torch', 'tensorflow'}:
                dependencies['ml'].append(imp)
            else:
                dependencies['other'].append(imp)
        
        return dict(dependencies)
    
    def _calculate_quality_score(self, code_lines: int, comment_lines: int, 
                                 vulnerabilities: List[Vulnerability], complexity: float) -> float:
        """Calculate overall code quality score (0-100)"""
        score = 100.0
        
        # Deduct for lack of comments
        if code_lines > 0:
            comment_ratio = comment_lines / (code_lines + comment_lines)
            if comment_ratio < 0.1:  # Less than 10% comments
                score -= 10
        
        # Deduct for vulnerabilities
        for vuln in vulnerabilities:
            if vuln.severity == 'critical':
                score -= 20
            elif vuln.severity == 'high':
                score -= 10
            elif vuln.severity == 'medium':
                score -= 5
            else:
                score -= 2
        
        # Deduct for high complexity
        if complexity > 20:
            score -= 15
        elif complexity > 10:
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def analyze_directory(self, directory: str, recursive: bool = True) -> Dict[str, AnalysisResult]:
        """Analyze all supported files in a directory"""
        results = {}
        dir_path = Path(directory)
        
        pattern = '**/*' if recursive else '*'
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                try:
                    result = self.analyze_file(str(file_path))
                    results[str(file_path)] = result
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def generate_report(self, result: AnalysisResult) -> str:
        """Generate human-readable analysis report"""
        report = []
        report.append("=" * 80)
        report.append(f"AI Code Analysis Report: {result.file_path}")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY")
        report.append(f"  Total Lines: {result.total_lines}")
        report.append(f"  Code Lines: {result.code_lines}")
        report.append(f"  Comment Lines: {result.comment_lines}")
        report.append(f"  Blank Lines: {result.blank_lines}")
        report.append(f"  Quality Score: {result.quality_score:.1f}/100")
        report.append(f"  Complexity Score: {result.complexity_score}")
        report.append("")
        
        # Structure
        report.append("🏗️  STRUCTURE")
        report.append(f"  Functions: {len(result.functions)}")
        if result.functions[:5]:
            report.append(f"    Examples: {', '.join(result.functions[:5])}")
        report.append(f"  Classes: {len(result.classes)}")
        if result.classes[:5]:
            report.append(f"    Examples: {', '.join(result.classes[:5])}")
        report.append(f"  Imports: {len(result.imports)}")
        report.append("")
        
        # Vulnerabilities
        if result.vulnerabilities:
            report.append("🔒 VULNERABILITIES DETECTED")
            critical = [v for v in result.vulnerabilities if v.severity == 'critical']
            high = [v for v in result.vulnerabilities if v.severity == 'high']
            medium = [v for v in result.vulnerabilities if v.severity == 'medium']
            
            if critical:
                report.append(f"  ❌ CRITICAL: {len(critical)}")
                for v in critical[:3]:
                    report.append(f"     • {v.location}: {v.description}")
            if high:
                report.append(f"  ⚠️  HIGH: {len(high)}")
                for v in high[:3]:
                    report.append(f"     • {v.location}: {v.description}")
            if medium:
                report.append(f"  ⚡ MEDIUM: {len(medium)}")
        else:
            report.append("✅ NO VULNERABILITIES DETECTED")
        report.append("")
        
        # Dependencies
        if result.dependencies:
            report.append("📦 DEPENDENCIES")
            for category, deps in result.dependencies.items():
                report.append(f"  {category.upper()}: {', '.join(deps[:5])}")
        report.append("")
        
        # Segments
        report.append("📑 CODE SEGMENTS")
        report.append(f"  Total Segments: {len(result.segments)}")
        if result.segments:
            report.append(f"  Average Segment Size: {sum(s.end_line - s.start_line for s in result.segments) / len(result.segments):.1f} lines")
        report.append("")
        
        report.append("=" * 80)
        
        return '\n'.join(report)
    
    def export_results(self, output_file: str = 'analysis_results.json'):
        """Export all analysis results to JSON"""
        export_data = {
            'total_files_analyzed': len(self.analyzed_files),
            'files': {}
        }
        
        for file_path, result in self.analyzed_files.items():
            export_data['files'][file_path] = {
                'total_lines': result.total_lines,
                'code_lines': result.code_lines,
                'quality_score': result.quality_score,
                'complexity_score': result.complexity_score,
                'vulnerabilities': [
                    {
                        'severity': v.severity,
                        'type': v.type,
                        'description': v.description,
                        'location': v.location,
                        'recommendation': v.recommendation
                    }
                    for v in result.vulnerabilities
                ],
                'functions_count': len(result.functions),
                'classes_count': len(result.classes),
                'segments_count': len(result.segments)
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📊 Analysis results exported to: {output_file}")


def main():
    """CLI interface for the analyzer"""
    import sys
    
    analyzer = AICodeAnalyzer()
    
    if len(sys.argv) < 2:
        print("Usage: python ai_code_analyzer.py <file_or_directory>")
        print("\nAdvanced AI Code Analyzer - Finds everything in your code!")
        print("  • Deep source code analysis")
        print("  • Vulnerability detection")
        print("  • Large file breakdown")
        print("  • Dependency mapping")
        print("  • Quality assessment")
        return
    
    target = sys.argv[1]
    path = Path(target)
    
    if path.is_file():
        print(f"🔍 Analyzing file: {target}")
        result = analyzer.analyze_file(target)
        print(analyzer.generate_report(result))
        
        if result.vulnerabilities:
            print("\n💡 RECOMMENDATIONS:")
            for v in result.vulnerabilities[:5]:
                print(f"  • {v.recommendation}")
    
    elif path.is_dir():
        print(f"🔍 Analyzing directory: {target}")
        results = analyzer.analyze_directory(target)
        print(f"\n✅ Analyzed {len(results)} files")
        
        # Summary statistics
        total_vulns = sum(len(r.vulnerabilities) for r in results.values())
        avg_quality = sum(r.quality_score for r in results.values()) / len(results) if results else 0
        
        print(f"📊 Total vulnerabilities found: {total_vulns}")
        print(f"📊 Average quality score: {avg_quality:.1f}/100")
        
        # Export results
        analyzer.export_results()
    
    else:
        print(f"❌ Error: {target} not found")


if __name__ == '__main__':
    main()
