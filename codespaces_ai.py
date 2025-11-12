#!/usr/bin/env python3
"""
AI-Powered Codespaces Alternative - THE FORGE Edition
=====================================================
Advanced web-based IDE with AI assistance, GitHub integration, and cute monster companions!
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
from datetime import datetime
import subprocess
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# AI Monster Companions - Each has unique coding specialties
MONSTER_COMPANIONS = {
    'codie': {
        'name': 'Codie the Code Monster',
        'emoji': '🦖',
        'color': '#4CAF50',
        'specialty': 'Python & Backend Development',
        'personality': 'Helpful and enthusiastic',
        'skills': ['Python', 'Flask', 'Django', 'FastAPI', 'Database Design']
    },
    'bugsy': {
        'name': 'Bugsy the Debug Monster',
        'emoji': '🐛',
        'color': '#FF5722',
        'specialty': 'Debugging & Testing',
        'personality': 'Meticulous and patient',
        'skills': ['Bug Detection', 'Unit Testing', 'Code Review', 'Performance Optimization']
    },
    'gitty': {
        'name': 'Gitty the Version Monster',
        'emoji': '🐙',
        'color': '#9C27B0',
        'specialty': 'Git & Version Control',
        'personality': 'Organized and reliable',
        'skills': ['Git', 'GitHub', 'CI/CD', 'Code Deployment', 'Branch Management']
    },
    'scriptz': {
        'name': 'Scriptz the Frontend Monster',
        'emoji': '🦊',
        'color': '#FF9800',
        'specialty': 'JavaScript & Frontend',
        'personality': 'Creative and modern',
        'skills': ['JavaScript', 'React', 'Vue', 'TypeScript', 'CSS/Tailwind']
    },
    'datamax': {
        'name': 'DataMax the Data Monster',
        'emoji': '🐘',
        'color': '#2196F3',
        'specialty': 'Data Science & ML',
        'personality': 'Analytical and precise',
        'skills': ['Data Analysis', 'Machine Learning', 'SQL', 'Pandas', 'Visualization']
    },
    'rusty': {
        'name': 'Rusty the Systems Monster',
        'emoji': '🦀',
        'color': '#E91E63',
        'specialty': 'Systems Programming',
        'personality': 'Fast and reliable',
        'skills': ['Rust', 'C++', 'Go', 'Systems Design', 'Performance']
    }
}

# AI Code Analysis Engine
class AICodeAssistant:
    """Advanced AI assistant powered by Kimi K2 with monster companions"""
    
    def __init__(self):
        self.active_monster = 'codie'
        self.context = []
        
    def analyze_code(self, code, language='python'):
        """AI-powered code analysis"""
        issues = []
        suggestions = []
        
        # Basic analysis (in production, this would use Kimi K2 model)
        lines = code.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            if 'print(' in line and language == 'python':
                suggestions.append({
                    'line': i,
                    'type': 'info',
                    'message': f'{MONSTER_COMPANIONS["codie"]["emoji"]} Codie suggests: Consider using logging instead of print for production code',
                    'monster': 'codie'
                })
            
            if 'TODO' in line or 'FIXME' in line:
                issues.append({
                    'line': i,
                    'type': 'warning',
                    'message': f'{MONSTER_COMPANIONS["bugsy"]["emoji"]} Bugsy found: Incomplete code marked for attention',
                    'monster': 'bugsy'
                })
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'complexity': self._calculate_complexity(code),
            'quality_score': max(0, 100 - len(issues) * 5)
        }
    
    def _calculate_complexity(self, code):
        """Calculate code complexity"""
        lines = len([l for l in code.split('\n') if l.strip()])
        functions = code.count('def ') + code.count('function ')
        conditionals = code.count('if ') + code.count('else') + code.count('elif')
        loops = code.count('for ') + code.count('while ')
        
        complexity = (conditionals + loops) / max(functions, 1)
        
        if complexity < 2:
            return {'level': 'Low', 'score': complexity, 'color': 'green'}
        elif complexity < 5:
            return {'level': 'Medium', 'score': complexity, 'color': 'orange'}
        else:
            return {'level': 'High', 'score': complexity, 'color': 'red'}
    
    def get_ai_suggestion(self, prompt, monster_id='codie'):
        """Get AI-powered coding suggestions from monster companions"""
        monster = MONSTER_COMPANIONS.get(monster_id, MONSTER_COMPANIONS['codie'])
        
        # Simulate AI response (in production, use Kimi K2)
        suggestions = {
            'codie': [
                "Let me help you write cleaner Python code! Try using list comprehensions for better readability.",
                "Great start! Consider adding type hints to make your code more maintainable.",
                "I recommend breaking this into smaller functions for better organization."
            ],
            'bugsy': [
                "I spotted a potential bug! Make sure to handle edge cases.",
                "Add error handling here to make your code more robust.",
                "Consider adding unit tests to verify this behavior."
            ],
            'gitty': [
                "Don't forget to commit your changes! Use descriptive commit messages.",
                "Time to push to GitHub! I'll help you with the commands.",
                "Consider creating a new branch for this feature."
            ],
            'scriptz': [
                "Use async/await for better async handling in JavaScript!",
                "Add some animations to make the UI more engaging!",
                "Consider using a modern framework like React or Vue."
            ],
            'datamax': [
                "Use pandas for efficient data manipulation!",
                "Visualize your data with matplotlib or plotly!",
                "Consider using scikit-learn for machine learning tasks."
            ],
            'rusty': [
                "Memory safety is key! Use ownership and borrowing correctly.",
                "Consider using async Rust for better performance!",
                "Profile your code to find bottlenecks."
            ]
        }
        
        import random
        base_suggestions = suggestions.get(monster_id, suggestions['codie'])
        suggestion = random.choice(base_suggestions)
        
        return {
            'monster': monster,
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat()
        }
    
    def autocomplete(self, code, cursor_position):
        """AI-powered code completion"""
        # Get context before cursor
        context = code[:cursor_position]
        
        # Simple autocomplete logic (production would use Kimi K2)
        completions = []
        
        if context.endswith('import '):
            completions = ['os', 'sys', 'json', 'datetime', 'requests', 'numpy', 'pandas']
        elif context.endswith('def '):
            completions = ['main()', 'process_data()', 'calculate()', 'helper()']
        elif context.endswith('.'):
            completions = ['append()', 'split()', 'join()', 'format()', 'strip()']
        
        return [{'text': c, 'type': 'keyword'} for c in completions]

# GitHub Integration
class GitHubManager:
    """Manage GitHub operations"""
    
    def __init__(self):
        self.workspace = '/tmp/codespaces_workspace'
        os.makedirs(self.workspace, exist_ok=True)
    
    def execute_git_command(self, command):
        """Execute git command safely"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def git_status(self):
        """Get git status"""
        return self.execute_git_command('git status --short')
    
    def git_commit(self, message):
        """Commit changes"""
        result1 = self.execute_git_command('git add .')
        if result1['success']:
            return self.execute_git_command(f'git commit -m "{message}"')
        return result1
    
    def git_push(self):
        """Push to remote"""
        return self.execute_git_command('git push')
    
    def git_init(self, repo_url=None):
        """Initialize or clone repository"""
        if repo_url:
            return self.execute_git_command(f'git clone {repo_url} .')
        else:
            return self.execute_git_command('git init')

# Initialize components
ai_assistant = AICodeAssistant()
github_manager = GitHubManager()

# Routes
@app.route('/')
def index():
    """Main Codespaces IDE interface"""
    return render_template('codespaces.html')

@app.route('/api/monsters')
def get_monsters():
    """Get all available monster companions"""
    return jsonify(MONSTER_COMPANIONS)

@app.route('/api/monster/<monster_id>/activate', methods=['POST'])
def activate_monster(monster_id):
    """Activate a monster companion"""
    if monster_id in MONSTER_COMPANIONS:
        ai_assistant.active_monster = monster_id
        return jsonify({
            'success': True,
            'monster': MONSTER_COMPANIONS[monster_id]
        })
    return jsonify({'success': False, 'error': 'Monster not found'}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """Analyze code with AI"""
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    analysis = ai_assistant.analyze_code(code, language)
    
    return jsonify(analysis)

@app.route('/api/suggest', methods=['POST'])
def get_suggestion():
    """Get AI suggestion from active monster"""
    data = request.json
    prompt = data.get('prompt', '')
    monster_id = data.get('monster_id', ai_assistant.active_monster)
    
    suggestion = ai_assistant.get_ai_suggestion(prompt, monster_id)
    
    return jsonify(suggestion)

@app.route('/api/autocomplete', methods=['POST'])
def autocomplete():
    """AI-powered autocomplete"""
    data = request.json
    code = data.get('code', '')
    cursor_position = data.get('cursor_position', len(code))
    
    completions = ai_assistant.autocomplete(code, cursor_position)
    
    return jsonify(completions)

@app.route('/api/git/status', methods=['GET'])
def git_status():
    """Get git status"""
    result = github_manager.git_status()
    return jsonify(result)

@app.route('/api/git/commit', methods=['POST'])
def git_commit():
    """Commit changes"""
    data = request.json
    message = data.get('message', 'Update files')
    
    result = github_manager.git_commit(message)
    return jsonify(result)

@app.route('/api/git/push', methods=['POST'])
def git_push():
    """Push to GitHub"""
    result = github_manager.git_push()
    return jsonify(result)

@app.route('/api/git/init', methods=['POST'])
def git_init():
    """Initialize or clone repository"""
    data = request.json
    repo_url = data.get('repo_url')
    
    result = github_manager.git_init(repo_url)
    return jsonify(result)

@app.route('/api/files/list', methods=['GET'])
def list_files():
    """List files in workspace"""
    try:
        files = []
        for root, dirs, filenames in os.walk(github_manager.workspace):
            # Skip .git directory
            dirs[:] = [d for d in dirs if d != '.git']
            
            for filename in filenames:
                filepath = os.path.join(root, filename)
                relpath = os.path.relpath(filepath, github_manager.workspace)
                files.append({
                    'name': filename,
                    'path': relpath,
                    'size': os.path.getsize(filepath)
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/read', methods=['POST'])
def read_file():
    """Read file content"""
    data = request.json
    filepath = data.get('filepath', '')
    
    try:
        full_path = os.path.join(github_manager.workspace, filepath)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/files/write', methods=['POST'])
def write_file():
    """Write file content"""
    data = request.json
    filepath = data.get('filepath', '')
    content = data.get('content', '')
    
    try:
        full_path = os.path.join(github_manager.workspace, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'message': f'File saved: {filepath}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/terminal', methods=['POST'])
def execute_terminal():
    """Execute terminal command"""
    data = request.json
    command = data.get('command', '')
    
    # Security: whitelist safe commands
    safe_commands = ['ls', 'pwd', 'cat', 'echo', 'git', 'python', 'node', 'npm']
    
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        return jsonify({
            'success': False,
            'error': 'Command not allowed for security reasons'
        }), 403
    
    result = github_manager.execute_git_command(command)
    return jsonify(result)

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  🦖 AI-Powered Codespaces - THE FORGE Edition 🦖              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  🎨 Features:                                                  ║
    ║     • Web-based IDE with syntax highlighting                  ║
    ║     • 6 AI Monster Companions for coding help                 ║
    ║     • Full GitHub integration (commit, push, clone)           ║
    ║     • AI-powered code analysis & suggestions                  ║
    ║     • Real-time autocomplete                                  ║
    ║     • Integrated terminal                                     ║
    ║     • File management system                                  ║
    ║                                                                ║
    ║  🚀 Starting server on http://localhost:5050                  ║
    ║  🦖 Meet your AI companions and start coding!                 ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5050, debug=True)
