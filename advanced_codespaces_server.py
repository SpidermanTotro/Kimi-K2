#!/usr/bin/env python3
"""
Enhanced FREE Codespaces with Interactive AI Companions
========================================================
Features:
- Multiple skill levels (Beginner, Medium, Advanced, Expert)
- Interactive AI pet creatures with animations
- GitHub repository launcher with login
- Work/rest monitoring and reminders
- Creature care system (feeding, playing, resting)
- Mini home for AI companions
- Multiple creature personalities (friendly, playful, serious)
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import subprocess
import secrets
import sqlite3
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# AI Companion Creatures with personalities
AI_CREATURES = {
    'codie': {
        'name': 'Codie',
        'type': 'Code Helper',
        'gender': 'male',
        'emoji': '🦖',
        'avatar': '👨‍💻',
        'color': '#4CAF50',
        'personality': 'Friendly and enthusiastic',
        'specialty': 'Python & Backend',
        'animations': {
            'idle': '🦖 *sitting quietly*',
            'coding': '🦖 *typing rapidly*',
            'thinking': '🦖 *deep in thought*',
            'celebrating': '🦖 *dancing happily*',
            'sleeping': '🦖 💤 *snoring*',
            'eating': '🦖 🍕 *munching pizza*',
            'spaceship': '🚀 *flying around*',
            'resting': '🦖 😴 *taking a nap*'
        },
        'favorite_food': 'Pizza',
        'energy_level': 100,
        'happiness': 100,
        'hunger': 0
    },
    'luna': {
        'name': 'Luna',
        'type': 'AI Assistant',
        'gender': 'female',
        'emoji': '🦊',
        'avatar': '👩‍💻',
        'color': '#FF9800',
        'personality': 'Smart and caring',
        'specialty': 'Frontend & Design',
        'animations': {
            'idle': '🦊 *relaxing peacefully*',
            'coding': '🦊 *creating beautiful code*',
            'thinking': '🦊 *analyzing deeply*',
            'celebrating': '🦊 *jumping with joy*',
            'sleeping': '🦊 💤 *dreaming*',
            'eating': '🦊 🍰 *enjoying cake*',
            'spaceship': '✨ *zooming through space*',
            'resting': '🦊 😌 *meditating*'
        },
        'favorite_food': 'Cake',
        'energy_level': 100,
        'happiness': 100,
        'hunger': 0
    },
    'byte': {
        'name': 'Byte',
        'type': 'Debug Expert',
        'gender': 'male',
        'emoji': '🐛',
        'avatar': '🤖',
        'color': '#FF5722',
        'personality': 'Serious but helpful',
        'specialty': 'Debugging & Testing',
        'animations': {
            'idle': '🐛 *scanning code*',
            'coding': '🐛 *hunting bugs*',
            'thinking': '🐛 *deep analysis*',
            'celebrating': '🐛 *bug squashed!*',
            'sleeping': '🐛 💤 *hibernating*',
            'eating': '🐛 🍔 *eating burger*',
            'spaceship': '🛸 *patrolling*',
            'resting': '🐛 😴 *offline mode*'
        },
        'favorite_food': 'Burger',
        'energy_level': 100,
        'happiness': 100,
        'hunger': 0
    },
    'nova': {
        'name': 'Nova',
        'type': 'Advanced AI',
        'gender': 'female',
        'emoji': '⭐',
        'avatar': '👸',
        'color': '#9C27B0',
        'personality': 'Wise and elegant',
        'specialty': 'Architecture & Systems',
        'animations': {
            'idle': '⭐ *glowing softly*',
            'coding': '⭐ *architecting systems*',
            'thinking': '⭐ *consulting stars*',
            'celebrating': '⭐ *shining bright*',
            'sleeping': '⭐ 💤 *dimmed light*',
            'eating': '⭐ 🍱 *having sushi*',
            'spaceship': '🌟 *teleporting*',
            'resting': '⭐ 😊 *recharging*'
        },
        'favorite_food': 'Sushi',
        'energy_level': 100,
        'happiness': 100,
        'hunger': 0
    }
}

# Skill Levels Configuration
SKILL_LEVELS = {
    'beginner': {
        'name': 'Beginner',
        'icon': '🌱',
        'description': 'Just starting out? I\'ll guide you step by step!',
        'assistance_level': 'high',
        'features': [
            'Detailed code explanations',
            'Step-by-step tutorials',
            'Frequent helpful hints',
            'Auto-error detection',
            'Code templates',
            'Interactive lessons'
        ],
        'ai_behavior': 'very_helpful'
    },
    'medium': {
        'name': 'Intermediate',
        'icon': '🌿',
        'description': 'Know the basics? I\'ll help you level up!',
        'assistance_level': 'medium',
        'features': [
            'Code suggestions',
            'Best practices tips',
            'Optimization hints',
            'Moderate guidance',
            'Pattern recognition'
        ],
        'ai_behavior': 'balanced'
    },
    'advanced': {
        'name': 'Advanced',
        'icon': '🌳',
        'description': 'Experienced developer? I\'ll assist when needed!',
        'assistance_level': 'low',
        'features': [
            'Advanced patterns',
            'Performance optimization',
            'Architecture suggestions',
            'Minimal interruptions',
            'Expert-level tools'
        ],
        'ai_behavior': 'minimal'
    },
    'expert': {
        'name': 'Expert',
        'icon': '🚀',
        'description': 'Master coder? I\'m here for teamwork!',
        'assistance_level': 'minimal',
        'features': [
            'Pair programming mode',
            'Code review only',
            'Advanced debugging',
            'System architecture',
            'No hand-holding'
        ],
        'ai_behavior': 'collaborative'
    }
}

# Work/Rest Monitoring
class WorkMonitor:
    """Monitor work time and suggest breaks"""
    
    def __init__(self):
        self.work_sessions = []
        self.current_session_start = None
        self.break_reminder_interval = 3600  # 1 hour
    
    def start_session(self):
        """Start work session"""
        self.current_session_start = datetime.now()
        return {'status': 'started', 'time': self.current_session_start.isoformat()}
    
    def check_break_needed(self):
        """Check if user needs a break"""
        if not self.current_session_start:
            return {'needs_break': False}
        
        elapsed = (datetime.now() - self.current_session_start).total_seconds()
        
        if elapsed > self.break_reminder_interval:
            return {
                'needs_break': True,
                'message': 'You\'ve been coding for over an hour! Time for a break! 🌟',
                'duration': elapsed,
                'suggestion': 'Stand up, stretch, grab some water!'
            }
        
        return {
            'needs_break': False,
            'time_until_break': self.break_reminder_interval - elapsed
        }
    
    def take_break(self):
        """Log a break"""
        if self.current_session_start:
            duration = (datetime.now() - self.current_session_start).total_seconds()
            self.work_sessions.append({
                'start': self.current_session_start.isoformat(),
                'end': datetime.now().isoformat(),
                'duration': duration
            })
            self.current_session_start = None
            return {'status': 'break_started', 'session_duration': duration}
        return {'status': 'no_active_session'}

# GitHub Repository Manager
class GitHubRepoManager:
    """Manage GitHub repositories - list, clone, download"""
    
    def __init__(self):
        self.repos_cache = []
        self.authenticated = False
        self.username = None
    
    def authenticate(self, username, token):
        """Authenticate with GitHub"""
        # In production, verify token with GitHub API
        self.username = username
        self.authenticated = True
        return {
            'success': True,
            'username': username,
            'message': f'Welcome back, {username}! 🎉'
        }
    
    def list_user_repos(self, username=None):
        """List user's GitHub repositories"""
        # In production, use GitHub API
        # Simulated repos for demo
        if not username:
            username = self.username
        
        return [
            {
                'name': 'awesome-project',
                'full_name': f'{username}/awesome-project',
                'description': 'My awesome coding project',
                'language': 'Python',
                'stars': 42,
                'forks': 7,
                'url': f'https://github.com/{username}/awesome-project',
                'clone_url': f'https://github.com/{username}/awesome-project.git',
                'updated_at': '2024-11-12T10:30:00Z'
            },
            {
                'name': 'web-app',
                'full_name': f'{username}/web-app',
                'description': 'Full-stack web application',
                'language': 'JavaScript',
                'stars': 128,
                'forks': 23,
                'url': f'https://github.com/{username}/web-app',
                'clone_url': f'https://github.com/{username}/web-app.git',
                'updated_at': '2024-11-10T15:20:00Z'
            },
            {
                'name': 'ml-experiments',
                'full_name': f'{username}/ml-experiments',
                'description': 'Machine learning experiments',
                'language': 'Jupyter Notebook',
                'stars': 89,
                'forks': 15,
                'url': f'https://github.com/{username}/ml-experiments',
                'clone_url': f'https://github.com/{username}/ml-experiments.git',
                'updated_at': '2024-11-08T09:45:00Z'
            }
        ]
    
    def clone_repo(self, clone_url, workspace_path):
        """Clone repository"""
        try:
            result = subprocess.run(
                ['git', 'clone', clone_url, workspace_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Creature Care System
class CreatureCareSystem:
    """Manage creature feeding, happiness, and interactions"""
    
    def __init__(self):
        self.creatures = AI_CREATURES.copy()
        self.last_update = {}
    
    def get_creature_status(self, creature_id):
        """Get current creature status"""
        if creature_id not in self.creatures:
            return None
        
        creature = self.creatures[creature_id]
        
        # Decay stats over time
        if creature_id in self.last_update:
            elapsed = (datetime.now() - self.last_update[creature_id]).total_seconds() / 60
            creature['energy_level'] = max(0, creature['energy_level'] - elapsed * 0.5)
            creature['hunger'] = min(100, creature['hunger'] + elapsed * 0.3)
            creature['happiness'] = max(0, creature['happiness'] - elapsed * 0.2)
        
        self.last_update[creature_id] = datetime.now()
        
        return creature
    
    def feed_creature(self, creature_id, food_type):
        """Feed the creature"""
        if creature_id not in self.creatures:
            return {'success': False}
        
        creature = self.creatures[creature_id]
        
        # Calculate satisfaction based on favorite food
        satisfaction = 30
        if food_type == creature['favorite_food']:
            satisfaction = 50
        
        creature['hunger'] = max(0, creature['hunger'] - satisfaction)
        creature['happiness'] = min(100, creature['happiness'] + satisfaction / 2)
        
        return {
            'success': True,
            'message': f'{creature["name"]} loves {food_type}! {creature["animations"]["eating"]}',
            'hunger': creature['hunger'],
            'happiness': creature['happiness']
        }
    
    def play_with_creature(self, creature_id):
        """Play with creature"""
        if creature_id not in self.creatures:
            return {'success': False}
        
        creature = self.creatures[creature_id]
        
        creature['happiness'] = min(100, creature['happiness'] + 20)
        creature['energy_level'] = max(0, creature['energy_level'] - 10)
        
        return {
            'success': True,
            'message': f'{creature["name"]} is having fun! {creature["animations"]["celebrating"]}',
            'happiness': creature['happiness'],
            'energy': creature['energy_level']
        }
    
    def rest_creature(self, creature_id):
        """Let creature rest"""
        if creature_id not in self.creatures:
            return {'success': False}
        
        creature = self.creatures[creature_id]
        
        creature['energy_level'] = min(100, creature['energy_level'] + 40)
        
        return {
            'success': True,
            'message': f'{creature["name"]} is resting {creature["animations"]["sleeping"]}',
            'energy': creature['energy_level']
        }

# Initialize managers
work_monitor = WorkMonitor()
github_manager = GitHubRepoManager()
creature_care = CreatureCareSystem()

# Routes
@app.route('/')
def index():
    """Main interface with AI companions"""
    return render_template('advanced_codespaces.html')

@app.route('/api/creatures')
def get_creatures():
    """Get all AI creatures"""
    return jsonify(AI_CREATURES)

@app.route('/api/creatures/<creature_id>/status')
def creature_status(creature_id):
    """Get creature status"""
    status = creature_care.get_creature_status(creature_id)
    return jsonify(status) if status else ('Not found', 404)

@app.route('/api/creatures/<creature_id>/feed', methods=['POST'])
def feed_creature(creature_id):
    """Feed creature"""
    data = request.json
    result = creature_care.feed_creature(creature_id, data.get('food_type', 'snack'))
    return jsonify(result)

@app.route('/api/creatures/<creature_id>/play', methods=['POST'])
def play_creature(creature_id):
    """Play with creature"""
    result = creature_care.play_with_creature(creature_id)
    return jsonify(result)

@app.route('/api/creatures/<creature_id>/rest', methods=['POST'])
def rest_creature(creature_id):
    """Rest creature"""
    result = creature_care.rest_creature(creature_id)
    return jsonify(result)

@app.route('/api/skill-levels')
def get_skill_levels():
    """Get all skill levels"""
    return jsonify(SKILL_LEVELS)

@app.route('/api/work/start', methods=['POST'])
def start_work():
    """Start work session"""
    result = work_monitor.start_session()
    return jsonify(result)

@app.route('/api/work/check-break')
def check_break():
    """Check if break is needed"""
    result = work_monitor.check_break_needed()
    return jsonify(result)

@app.route('/api/work/break', methods=['POST'])
def take_break():
    """Take a break"""
    result = work_monitor.take_break()
    return jsonify(result)

@app.route('/api/github/auth', methods=['POST'])
def github_auth():
    """Authenticate with GitHub"""
    data = request.json
    result = github_manager.authenticate(
        data.get('username'),
        data.get('token')
    )
    return jsonify(result)

@app.route('/api/github/repos')
def list_repos():
    """List GitHub repositories"""
    username = request.args.get('username')
    repos = github_manager.list_user_repos(username)
    return jsonify(repos)

@app.route('/api/github/clone', methods=['POST'])
def clone_repo():
    """Clone repository"""
    data = request.json
    result = github_manager.clone_repo(
        data.get('clone_url'),
        data.get('workspace_path', '/tmp/repo')
    )
    return jsonify(result)

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║  🚀 ADVANCED FREE Codespaces - THE FORGE Edition 🚀                       ║
    ╠════════════════════════════════════════════════════════════════════════════╣
    ║  ✨ NEW FEATURES:                                                          ║
    ║     🎮 Interactive AI Companions (Codie, Luna, Byte, Nova)                ║
    ║     📊 4 Skill Levels (Beginner → Expert)                                 ║
    ║     ⏰ Work/Rest Monitoring & Break Reminders                             ║
    ║     🐾 Creature Care System (Feed, Play, Rest)                            ║
    ║     📁 GitHub Repository Launcher                                         ║
    ║     🔐 GitHub Login Integration                                           ║
    ║     🏠 Mini Home for AI Companions                                        ║
    ║     🚀 Multiple Creature Modes (Spaceship, Rest, Active)                  ║
    ║     💝 Family System for Creatures                                        ║
    ║                                                                            ║
    ║  💰 STILL 100% FREE - $0.00 FOREVER!                                      ║
    ║  📱 Access from anywhere: http://localhost:5000                           ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Start work monitor
    work_monitor.start_session()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
