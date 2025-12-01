#!/usr/bin/env python3
"""
THE FORGE - Intelligent Monitoring System
Transforms INTELLIGENT_SYSTEMS.md into live monitoring and auto-update system
"""

import os
import json
import time
import hashlib
import subprocess
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    MINOR = "minor"
    INFORMATIONAL = "informational"


class IssueType(Enum):
    """Types of issues that can be detected"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    DEPRECATED = "deprecated"
    CODE_SMELL = "code_smell"
    BREAKING_CHANGE = "breaking_change"
    ACCESSIBILITY = "accessibility"
    DESIGN = "design"


@dataclass
class Issue:
    """Detected issue"""
    issue_id: str
    issue_type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'issue_id': self.issue_id,
            'type': self.issue_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'suggestion': self.suggestion,
            'detected_at': self.detected_at.isoformat(),
            'resolved': self.resolved
        }


@dataclass
class UpdateCandidate:
    """Package or dependency that can be updated"""
    name: str
    current_version: str
    latest_version: str
    update_type: str  # major, minor, patch
    breaking_changes: bool
    security_fix: bool
    changelog_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'update_type': self.update_type,
            'breaking_changes': self.breaking_changes,
            'security_fix': self.security_fix,
            'changelog_url': self.changelog_url
        }


class IntelligentMonitor:
    """
    Intelligent Monitoring System
    - Issue detection and scanning
    - Auto-update management
    - Performance monitoring
    - Security scanning
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[Issue] = []
        self.update_candidates: List[UpdateCandidate] = []
        self.scan_history: List[Dict] = []
        self.monitoring_active = False
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        print("🔥 Starting Intelligent Monitoring System...")
        self.monitoring_active = True
        
        # Initial scans
        self.scan_dependencies()
        self.scan_security_vulnerabilities()
        self.scan_code_quality()
        self.scan_performance_issues()
        
        print("✅ Monitoring system active")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        print("⏹️  Monitoring system stopped")
    
    def scan_dependencies(self) -> List[UpdateCandidate]:
        """Scan for outdated dependencies"""
        print("\n📦 Scanning dependencies...")
        
        candidates = []
        
        # Check Python dependencies
        if (self.project_root / "requirements.txt").exists():
            candidates.extend(self._scan_python_deps())
        
        # Check Node.js dependencies
        if (self.project_root / "package.json").exists():
            candidates.extend(self._scan_node_deps())
        
        self.update_candidates = candidates
        print(f"✅ Found {len(candidates)} update candidates")
        
        return candidates
    
    def _scan_python_deps(self) -> List[UpdateCandidate]:
        """Scan Python dependencies"""
        candidates = []
        
        try:
            # Read requirements.txt
            req_file = self.project_root / "requirements.txt"
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name and version
                        if '>=' in line or '==' in line:
                            parts = line.replace('>=', '==').split('==')
                            if len(parts) == 2:
                                pkg_name = parts[0].strip()
                                current_ver = parts[1].strip()
                                
                                # Check for updates (simplified)
                                candidate = UpdateCandidate(
                                    name=pkg_name,
                                    current_version=current_ver,
                                    latest_version=current_ver,  # Would check PyPI
                                    update_type="unknown",
                                    breaking_changes=False,
                                    security_fix=False
                                )
                                candidates.append(candidate)
        except Exception as e:
            print(f"⚠️  Error scanning Python deps: {e}")
        
        return candidates
    
    def _scan_node_deps(self) -> List[UpdateCandidate]:
        """Scan Node.js dependencies"""
        candidates = []
        
        try:
            pkg_file = self.project_root / "package.json"
            with open(pkg_file, 'r') as f:
                pkg_data = json.load(f)
            
            deps = pkg_data.get('dependencies', {})
            dev_deps = pkg_data.get('devDependencies', {})
            
            all_deps = {**deps, **dev_deps}
            
            for pkg_name, version in all_deps.items():
                candidate = UpdateCandidate(
                    name=pkg_name,
                    current_version=version,
                    latest_version=version,  # Would check npm
                    update_type="unknown",
                    breaking_changes=False,
                    security_fix=False
                )
                candidates.append(candidate)
        except Exception as e:
            print(f"⚠️  Error scanning Node deps: {e}")
        
        return candidates
    
    def scan_security_vulnerabilities(self) -> List[Issue]:
        """Scan for security vulnerabilities"""
        print("\n🔒 Scanning for security vulnerabilities...")
        
        security_issues = []
        
        # Check for common security issues
        security_issues.extend(self._check_exposed_secrets())
        security_issues.extend(self._check_weak_patterns())
        
        # Add to issues list
        for issue in security_issues:
            if issue not in self.issues:
                self.issues.append(issue)
        
        print(f"✅ Found {len(security_issues)} security issues")
        return security_issues
    
    def _check_exposed_secrets(self) -> List[Issue]:
        """Check for exposed secrets in code"""
        issues = []
        
        # Patterns to detect
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret key'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
        ]
        
        # Scan Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in secret_patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        issue = Issue(
                            issue_id=hashlib.md5(f"{py_file}{description}".encode()).hexdigest()[:8],
                            issue_type=IssueType.SECURITY,
                            severity=IssueSeverity.CRITICAL,
                            title=f"Exposed secret: {description}",
                            description=f"Found {description.lower()} in {py_file.name}",
                            file_path=str(py_file.relative_to(self.project_root)),
                            suggestion="Move secrets to environment variables or secure vault"
                        )
                        issues.append(issue)
            except Exception:
                pass
        
        return issues
    
    def _check_weak_patterns(self) -> List[Issue]:
        """Check for weak security patterns"""
        issues = []
        
        # Check for eval() usage
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'eval(' in content:
                    issue = Issue(
                        issue_id=hashlib.md5(f"{py_file}eval".encode()).hexdigest()[:8],
                        issue_type=IssueType.SECURITY,
                        severity=IssueSeverity.IMPORTANT,
                        title="Unsafe eval() usage",
                        description=f"Found eval() in {py_file.name}",
                        file_path=str(py_file.relative_to(self.project_root)),
                        suggestion="Replace eval() with safer alternatives like ast.literal_eval()"
                    )
                    issues.append(issue)
            except Exception:
                pass
        
        return issues
    
    def scan_code_quality(self) -> List[Issue]:
        """Scan for code quality issues"""
        print("\n🔍 Scanning code quality...")
        
        quality_issues = []
        
        # Check for code smells
        quality_issues.extend(self._check_code_smells())
        quality_issues.extend(self._check_complexity())
        
        # Add to issues list
        for issue in quality_issues:
            if issue not in self.issues:
                self.issues.append(issue)
        
        print(f"✅ Found {len(quality_issues)} code quality issues")
        return quality_issues
    
    def _check_code_smells(self) -> List[Issue]:
        """Check for code smells"""
        issues = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check for long functions (>50 lines)
                in_function = False
                function_start = 0
                function_name = ""
                
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('def '):
                        if in_function and (i - function_start) > 50:
                            issue = Issue(
                                issue_id=hashlib.md5(f"{py_file}{function_name}".encode()).hexdigest()[:8],
                                issue_type=IssueType.CODE_SMELL,
                                severity=IssueSeverity.MINOR,
                                title=f"Long function: {function_name}",
                                description=f"Function has {i - function_start} lines",
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=function_start,
                                suggestion="Consider breaking into smaller functions"
                            )
                            issues.append(issue)
                        
                        in_function = True
                        function_start = i
                        function_name = line.split('def ')[1].split('(')[0].strip()
            except Exception:
                pass
        
        return issues
    
    def _check_complexity(self) -> List[Issue]:
        """Check for high complexity"""
        issues = []
        # Placeholder for complexity analysis
        return issues
    
    def scan_performance_issues(self) -> List[Issue]:
        """Scan for performance issues"""
        print("\n⚡ Scanning for performance issues...")
        
        perf_issues = []
        
        # Check for common performance issues
        perf_issues.extend(self._check_inefficient_loops())
        
        # Add to issues list
        for issue in perf_issues:
            if issue not in self.issues:
                self.issues.append(issue)
        
        print(f"✅ Found {len(perf_issues)} performance issues")
        return perf_issues
    
    def _check_inefficient_loops(self) -> List[Issue]:
        """Check for inefficient loops"""
        issues = []
        # Placeholder for loop analysis
        return issues
    
    def get_critical_issues(self) -> List[Issue]:
        """Get all critical issues"""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]
    
    def get_issues_by_type(self, issue_type: IssueType) -> List[Issue]:
        """Get issues by type"""
        return [i for i in self.issues if i.issue_type == issue_type]
    
    def export_report(self, output_file: str = "monitoring_report.json"):
        """Export monitoring report"""
        report = {
            'scan_time': datetime.now().isoformat(),
            'total_issues': len(self.issues),
            'critical_issues': len(self.get_critical_issues()),
            'update_candidates': len(self.update_candidates),
            'issues': [i.to_dict() for i in self.issues],
            'updates': [u.to_dict() for u in self.update_candidates]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report exported to {output_file}")
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        return {
            'total_issues': len(self.issues),
            'critical': len([i for i in self.issues if i.severity == IssueSeverity.CRITICAL]),
            'important': len([i for i in self.issues if i.severity == IssueSeverity.IMPORTANT]),
            'minor': len([i for i in self.issues if i.severity == IssueSeverity.MINOR]),
            'by_type': {
                issue_type.value: len(self.get_issues_by_type(issue_type))
                for issue_type in IssueType
            },
            'update_candidates': len(self.update_candidates)
        }


def main():
    """Main execution"""
    print("🔥 THE FORGE - Intelligent Monitoring System")
    print("=" * 70)
    print()
    
    # Initialize monitor
    monitor = IntelligentMonitor(project_root="..")
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Show statistics
    print("\n📊 Monitoring Statistics:")
    print("-" * 70)
    stats = monitor.get_statistics()
    print(f"Total Issues: {stats['total_issues']}")
    print(f"  Critical: {stats['critical']}")
    print(f"  Important: {stats['important']}")
    print(f"  Minor: {stats['minor']}")
    print(f"\nUpdate Candidates: {stats['update_candidates']}")
    
    print("\n📋 Issues by Type:")
    for issue_type, count in stats['by_type'].items():
        if count > 0:
            print(f"  {issue_type}: {count}")
    
    # Export report
    monitor.export_report("monitoring_report.json")
    
    print("\n✅ Monitoring System Ready!")


if __name__ == "__main__":
    main()