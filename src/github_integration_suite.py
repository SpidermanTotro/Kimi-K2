"""
THE FORGE AI - GitHub Integration Suite
Complete GitHub repository management, version control, and collaboration tools
"""

import os
import json
import subprocess
import datetime
from typing import Dict, List, Any
import tempfile

class GitHubIntegrationSuite:
    """Comprehensive GitHub integration and collaboration platform"""
    
    def __init__(self):
        self.repositories = {}
        self.branches = {}
        self.issues = {}
        self.pull_requests = {}
        self.workflows = {}
        self.collaboration_tools = CollaborationTools()
        self.code_review_tools = CodeReviewTools()
        self.automation_tools = AutomationTools()
    
    def clone_repository(self, repo_url: str, destination: str = None) -> Dict[str, Any]:
        """Clone GitHub repository"""
        try:
            if destination is None:
                # Extract repo name from URL
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                destination = f"/workspace/repos/{repo_name}"
            
            # Clone repository using GitHub CLI
            result = subprocess.run(
                ['gh', 'repo', 'clone', repo_url, destination],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                repo_info = {
                    "repo_url": repo_url,
                    "destination": destination,
                    "cloned_at": datetime.datetime.now().isoformat(),
                    "status": "cloned"
                }
                
                self.repositories[destination] = repo_info
                
                return {
                    "success": True,
                    "repo_url": repo_url,
                    "destination": destination,
                    "cloned_successfully": True,
                    "next_steps": [
                        "Navigate to repository directory",
                        "Create new branch for changes",
                        "Make modifications",
                        "Commit and push changes",
                        "Create pull request"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to clone repository: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_repository(self, name: str, description: str = "", 
                          is_private: bool = False, template: str = None) -> Dict[str, Any]:
        """Create new GitHub repository"""
        try:
            # Create repository using GitHub CLI
            privacy_flag = "--private" if is_private else "--public"
            
            cmd = ['gh', 'repo', 'create', name, privacy_flag, '--description', description]
            
            if template:
                cmd.extend(['--template', template])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                
                repo_info = {
                    "name": name,
                    "description": description,
                    "url": repo_url,
                    "is_private": is_private,
                    "created_at": datetime.datetime.now().isoformat(),
                    "status": "created",
                    "template_used": template
                }
                
                self.repositories[name] = repo_info
                
                return {
                    "success": True,
                    "repository_name": name,
                    "url": repo_url,
                    "is_private": is_private,
                    "created_successfully": True,
                    "setup_instructions": [
                        "Clone the repository locally",
                        "Add initial files and README",
                        "Set up development branches",
                        "Configure CI/CD workflows",
                        "Add collaborators"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create repository: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_branch(self, repo_path: str, branch_name: str, 
                     base_branch: str = "main") -> Dict[str, Any]:
        """Create new branch"""
        try:
            # Change to repository directory
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create and checkout new branch
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name, f'origin/{base_branch}'],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                branch_info = {
                    "repo_path": repo_path,
                    "branch_name": branch_name,
                    "base_branch": base_branch,
                    "created_at": datetime.datetime.now().isoformat(),
                    "status": "created"
                }
                
                self.branches[branch_name] = branch_info
                
                return {
                    "success": True,
                    "branch_name": branch_name,
                    "base_branch": base_branch,
                    "created_successfully": True,
                    "ready_for_development": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create branch: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def commit_changes(self, repo_path: str, message: str, 
                      files: List[str] = None) -> Dict[str, Any]:
        """Commit changes to repository"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Add files
            if files:
                for file in files:
                    subprocess.run(['git', 'add', file], capture_output=True)
            else:
                subprocess.run(['git', 'add', '.'], capture_output=True)
            
            # Commit changes
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "commit_message": message,
                    "files_committed": files or "all changes",
                    "committed_successfully": True,
                    "ready_to_push": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to commit changes: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def push_changes(self, repo_path: str, branch_name: str = None) -> Dict[str, Any]:
        """Push changes to remote repository"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Get current branch if not specified
            if branch_name is None:
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True
                )
                branch_name = result.stdout.strip()
            
            # Push changes
            result = subprocess.run(
                ['git', 'push', 'origin', branch_name],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "branch_name": branch_name,
                    "pushed_successfully": True,
                    "ready_for_pr": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to push changes: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_pull_request(self, repo_path: str, title: str, description: str,
                           head_branch: str, base_branch: str = "main") -> Dict[str, Any]:
        """Create pull request"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create pull request using GitHub CLI
            result = subprocess.run(
                ['gh', 'pr', 'create', '--title', title, '--body', description,
                 '--head', head_branch, '--base', base_branch],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                
                pr_info = {
                    "repo_path": repo_path,
                    "title": title,
                    "description": description,
                    "head_branch": head_branch,
                    "base_branch": base_branch,
                    "url": pr_url,
                    "created_at": datetime.datetime.now().isoformat(),
                    "status": "open"
                }
                
                pr_id = f"pr_{len(self.pull_requests) + 1}"
                self.pull_requests[pr_id] = pr_info
                
                return {
                    "success": True,
                    "pr_url": pr_url,
                    "title": title,
                    "created_successfully": True,
                    "next_steps": [
                        "Wait for code review",
                        "Address feedback",
                        "Update PR if needed",
                        "Request approval",
                        "Merge when ready"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create pull request: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_issue(self, repo_path: str, title: str, description: str,
                    labels: List[str] = None) -> Dict[str, Any]:
        """Create GitHub issue"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create issue using GitHub CLI
            cmd = ['gh', 'issue', 'create', '--title', title, '--body', description]
            
            if labels:
                cmd.extend(['--label', ','.join(labels)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                
                issue_info = {
                    "repo_path": repo_path,
                    "title": title,
                    "description": description,
                    "labels": labels or [],
                    "url": issue_url,
                    "created_at": datetime.datetime.now().isoformat(),
                    "status": "open"
                }
                
                issue_id = f"issue_{len(self.issues) + 1}"
                self.issues[issue_id] = issue_info
                
                return {
                    "success": True,
                    "issue_url": issue_url,
                    "title": title,
                    "labels": labels,
                    "created_successfully": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create issue: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_workflows(self, repo_path: str, workflow_configs: List[Dict]) -> Dict[str, Any]:
        """Set up GitHub workflows"""
        return self.automation_tools.setup_workflows(repo_path, workflow_configs)
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository and provide insights"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Get repository statistics
            stats = {}
            
            # Get commit count
            commit_result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True
            )
            stats["total_commits"] = int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0
            
            # Get branch count
            branch_result = subprocess.run(
                ['git', 'branch', '-a'],
                capture_output=True,
                text=True
            )
            stats["total_branches"] = len(branch_result.stdout.strip().split('\n')) if branch_result.returncode == 0 else 0
            
            # Get contributor count
            contributor_result = subprocess.run(
                ['git', 'shortlog', '-sn'],
                capture_output=True,
                text=True
            )
            stats["total_contributors"] = len(contributor_result.stdout.strip().split('\n')) if contributor_result.returncode == 0 else 0
            
            # Get file statistics
            file_result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True,
                text=True
            )
            if file_result.returncode == 0:
                files = file_result.stdout.strip().split('\n')
                stats["total_files"] = len(files)
                
                # File type breakdown
                file_types = {}
                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext:
                        file_types[ext] = file_types.get(ext, 0) + 1
                
                stats["file_types"] = dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10])
            
            os.chdir(original_cwd)
            
            analysis = {
                "repository_path": repo_path,
                "statistics": stats,
                "health_score": self.calculate_health_score(stats),
                "recommendations": self.generate_repo_recommendations(stats),
                "analyzed_at": datetime.datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_health_score(self, stats: Dict) -> int:
        """Calculate repository health score"""
        score = 100
        
        # Deduct points for low activity
        if stats["total_commits"] < 10:
            score -= 20
        elif stats["total_commits"] < 50:
            score -= 10
        
        # Deduct points for single contributor
        if stats["total_contributors"] == 1:
            score -= 15
        elif stats["total_contributors"] < 3:
            score -= 5
        
        # Deduct points for too many branches without structure
        if stats["total_branches"] > 20:
            score -= 10
        
        return max(0, score)
    
    def generate_repo_recommendations(self, stats: Dict) -> List[str]:
        """Generate repository improvement recommendations"""
        recommendations = []
        
        if stats["total_commits"] < 10:
            recommendations.append("Increase development activity with regular commits")
        
        if stats["total_contributors"] == 1:
            recommendations.append("Encourage more contributors to improve code diversity")
        
        if stats["total_branches"] > 20:
            recommendations.append("Implement branch naming conventions and cleanup")
        
        if stats["total_files"] > 1000:
            recommendations.append("Consider modularizing large codebase")
        
        # Check for missing files
        recommendations.extend([
            "Add comprehensive README.md documentation",
            "Set up CI/CD workflows for automated testing",
            "Implement code review processes",
            "Add contribution guidelines (CONTRIBUTING.md)",
            "Set up issue templates for better bug tracking"
        ])
        
        return recommendations
    
    def create_release(self, repo_path: str, tag: str, title: str, 
                      description: str, is_draft: bool = False) -> Dict[str, Any]:
        """Create GitHub release"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create release using GitHub CLI
            cmd = ['gh', 'release', 'create', tag, '--title', title, '--notes', description]
            
            if is_draft:
                cmd.append('--draft')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                release_url = result.stdout.strip()
                
                return {
                    "success": True,
                    "release_url": release_url,
                    "tag": tag,
                    "title": title,
                    "created_successfully": True,
                    "is_draft": is_draft
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create release: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class CollaborationTools:
    """Collaboration and team management tools"""
    
    def __init__(self):
        self.team_members = {}
        self.permissions = {"read", "write", "admin", "maintain"}
    
    def add_collaborator(self, repo_path: str, username: str, 
                        permission: str = "write") -> Dict[str, Any]:
        """Add collaborator to repository"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            if permission not in self.permissions:
                return {"success": False, "error": f"Invalid permission: {permission}"}
            
            # Add collaborator using GitHub CLI
            result = subprocess.run(
                ['gh', 'repo', 'edit', '--add-collaborator', username, '--permission', permission],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "username": username,
                    "permission": permission,
                    "added_successfully": True,
                    "notified": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to add collaborator: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_team(self, org_name: str, team_name: str, description: str,
                   privacy: str = "closed") -> Dict[str, Any]:
        """Create GitHub team"""
        try:
            # Create team using GitHub CLI
            result = subprocess.run(
                ['gh', 'api', '--method', 'POST', f'/orgs/{org_name}/teams',
                 '--field', f'name={team_name}',
                 '--field', f'description={description}',
                 '--field', f'privacy={privacy}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                team_data = json.loads(result.stdout)
                
                return {
                    "success": True,
                    "team_name": team_name,
                    "team_id": team_data.get("id"),
                    "description": description,
                    "created_successfully": True,
                    "privacy": privacy
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create team: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class CodeReviewTools:
    """Code review and quality analysis tools"""
    
    def __init__(self):
        self.review_criteria = [
            "code_quality", "performance", "security", "documentation", "testing"
        ]
    
    def review_pull_request(self, repo_path: str, pr_number: int) -> Dict[str, Any]:
        """Review pull request and provide feedback"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Get PR details using GitHub CLI
            result = subprocess.run(
                ['gh', 'pr', 'view', str(pr_number), '--json', 'title,body,files,author'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pr_data = json.loads(result.stdout)
                
                # Analyze changes
                review_analysis = self.analyze_pr_changes(pr_data)
                
                # Generate review comments
                review_comments = self.generate_review_comments(review_analysis)
                
                review_result = {
                    "pr_number": pr_number,
                    "title": pr_data.get("title"),
                    "author": pr_data.get("author", {}).get("login"),
                    "files_changed": len(pr_data.get("files", [])),
                    "analysis": review_analysis,
                    "recommendations": review_comments,
                    "overall_score": self.calculate_review_score(review_analysis)
                }
                
                os.chdir(original_cwd)
                
                return {
                    "success": True,
                    "review": review_result
                }
            else:
                os.chdir(original_cwd)
                return {
                    "success": False,
                    "error": f"Failed to review PR: {result.stderr}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_pr_changes(self, pr_data: Dict) -> Dict[str, Any]:
        """Analyze pull request changes"""
        analysis = {
            "additions": 0,
            "deletions": 0,
            "files_count": len(pr_data.get("files", [])),
            "complexity_score": 0,
            "risk_level": "low",
            "suggested_reviewers": 2
        }
        
        files = pr_data.get("files", [])
        
        for file in files:
            analysis["additions"] += file.get("additions", 0)
            analysis["deletions"] += file.get("deletions", 0)
            
            # Calculate complexity based on file types and changes
            filename = file.get("filename", "")
            if filename.endswith('.py'):
                analysis["complexity_score"] += 3
            elif filename.endswith(('.js', '.ts')):
                analysis["complexity_score"] += 2
            elif filename.endswith(('.yml', '.yaml')):
                analysis["complexity_score"] += 1
        
        # Determine risk level
        if analysis["additions"] > 500:
            analysis["risk_level"] = "high"
            analysis["suggested_reviewers"] = 3
        elif analysis["additions"] > 200:
            analysis["risk_level"] = "medium"
            analysis["suggested_reviewers"] = 2
        
        return analysis
    
    def generate_review_comments(self, analysis: Dict) -> List[str]:
        """Generate review comments based on analysis"""
        comments = []
        
        if analysis["additions"] > 500:
            comments.append("Large PR detected - consider splitting into smaller changes")
        
        if analysis["complexity_score"] > 10:
            comments.append("Complex changes detected - ensure thorough testing")
        
        if analysis["risk_level"] == "high":
            comments.append("High risk changes - consider additional security review")
        
        comments.extend([
            "Check for adequate test coverage",
            "Verify documentation updates are included",
            "Ensure backward compatibility is maintained",
            "Review performance implications"
        ])
        
        return comments
    
    def calculate_review_score(self, analysis: Dict) -> int:
        """Calculate overall review score"""
        score = 100
        
        # Deduct points for large changes
        if analysis["additions"] > 500:
            score -= 20
        elif analysis["additions"] > 200:
            score -= 10
        
        # Deduct points for complexity
        if analysis["complexity_score"] > 10:
            score -= 15
        elif analysis["complexity_score"] > 5:
            score -= 5
        
        # Deduct points for risk
        if analysis["risk_level"] == "high":
            score -= 10
        elif analysis["risk_level"] == "medium":
            score -= 5
        
        return max(0, score)


class AutomationTools:
    """GitHub automation and workflow tools"""
    
    def __init__(self):
        self.workflow_templates = self.load_workflow_templates()
    
    def load_workflow_templates(self) -> Dict[str, Dict]:
        """Load workflow templates"""
        return {
            "ci": {
                "name": "Continuous Integration",
                "triggers": ["push", "pull_request"],
                "jobs": ["lint", "test", "build"],
                "languages": ["python", "javascript", "go"]
            },
            "cd": {
                "name": "Continuous Deployment",
                "triggers": ["push"],
                "jobs": ["test", "build", "deploy"],
                "environments": ["staging", "production"]
            },
            "security": {
                "name": "Security Scanning",
                "triggers": ["push", "schedule"],
                "jobs": ["vulnerability_scan", "code_analysis", "dependency_check"],
                "tools": ["codeql", "dependabot", "security_scan"]
            },
            "release": {
                "name": "Release Automation",
                "triggers": ["push", "workflow_dispatch"],
                "jobs": ["test", "build", "package", "release"],
                "versioning": "semantic"
            }
        }
    
    def setup_workflows(self, repo_path: str, workflow_configs: List[Dict]) -> Dict[str, Any]:
        """Set up GitHub workflows"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create .github/workflows directory
            workflow_dir = ".github/workflows"
            os.makedirs(workflow_dir, exist_ok=True)
            
            created_workflows = []
            
            for config in workflow_configs:
                workflow_type = config.get("type", "ci")
                workflow_name = config.get("name", f"{workflow_type}.yml")
                
                if workflow_type in self.workflow_templates:
                    template = self.workflow_templates[workflow_type]
                    workflow_content = self.generate_workflow_content(template, config)
                    
                    workflow_file = f"{workflow_dir}/{workflow_name}"
                    with open(workflow_file, 'w') as f:
                        f.write(workflow_content)
                    
                    created_workflows.append({
                        "name": workflow_name,
                        "type": workflow_type,
                        "file": workflow_file
                    })
            
            os.chdir(original_cwd)
            
            return {
                "success": True,
                "workflows_created": len(created_workflows),
                "workflows": created_workflows,
                "workflow_directory": workflow_dir,
                "ready_for_commit": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_workflow_content(self, template: Dict, config: Dict) -> str:
        """Generate GitHub workflow content"""
        workflow = f'''name: {template['name']}

on:
'''
        
        # Add triggers
        for trigger in template["triggers"]:
            workflow += f'''  {trigger}:
    branches: [ main, develop ]
'''
        
        workflow += '''
jobs:
'''
        
        # Add jobs
        for i, job in enumerate(template["jobs"]):
            job_name = job.capitalize()
            workflow += f'''  {job}:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Environment
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: {job_name}
      run: |
        echo "Running {job}..."
        # Add {job} commands here
'''
        
        return workflow
    
    def enable_dependabot(self, repo_path: str) -> Dict[str, Any]:
        """Enable Dependabot for dependency updates"""
        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Create .github directory
            os.makedirs(".github", exist_ok=True)
            
            # Create dependabot configuration
            dependabot_config = '''version: 2
updates:
  # Enable version updates for npm
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5

  # Enable version updates for pip
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5

  # Enable version updates for Docker
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
'''
            
            with open(".github/dependabot.yml", 'w') as f:
                f.write(dependabot_config)
            
            os.chdir(original_cwd)
            
            return {
                "success": True,
                "dependabot_enabled": True,
                "config_file": ".github/dependabot.yml",
                "update_schedule": "weekly",
                "ecosystems": ["npm", "pip", "docker"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Initialize the GitHub integration suite
github_suite = GitHubIntegrationSuite()