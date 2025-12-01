#!/usr/bin/env python3
"""
THE FORGE AI - Backend Server
WebSocket and REST API for ChatGPT 2.0 style interface
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Import FORGE components
import sys
sys.path.append('..')
from forge_implementation import ForgeAI
from live_programs import SkillsEngine, IntelligentMonitor, MultimediaSuite, BookWritingSystem

app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'forge-ai-secret-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize FORGE AI
forge = ForgeAI()
forge.initialize()

# Initialize live programs
skills_engine = SkillsEngine(docs_dir="../docs")
skills_engine.load_all_skills()

monitor = IntelligentMonitor(project_root="..")
multimedia = MultimediaSuite()
books = BookWritingSystem()

# In-memory storage (replace with database in production)
conversations = {}
users = {}
sessions = {}


class ConversationManager:
    """Manage conversations and messages"""
    
    def __init__(self):
        self.conversations = {}
    
    def create_conversation(self, user_id: str, model: str = "kimi-k2") -> Dict:
        """Create new conversation"""
        conv_id = f"{user_id}_{datetime.now().timestamp()}"
        conversation = {
            'id': conv_id,
            'user_id': user_id,
            'title': 'New Chat',
            'messages': [],
            'model': model,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.conversations[conv_id] = conversation
        return conversation
    
    def add_message(self, conv_id: str, role: str, content: str, model: str = None) -> Dict:
        """Add message to conversation"""
        if conv_id not in self.conversations:
            raise ValueError(f"Conversation {conv_id} not found")
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'model': model
        }
        
        self.conversations[conv_id]['messages'].append(message)
        self.conversations[conv_id]['updated_at'] = datetime.now().isoformat()
        
        # Update title if first message
        if len(self.conversations[conv_id]['messages']) == 1:
            self.conversations[conv_id]['title'] = content[:50] + ('...' if len(content) > 50 else '')
        
        return message
    
    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """Get conversation by ID"""
        return self.conversations.get(conv_id)
    
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for user"""
        return [
            conv for conv in self.conversations.values()
            if conv['user_id'] == user_id
        ]
    
    def delete_conversation(self, conv_id: str) -> bool:
        """Delete conversation"""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            return True
        return False


conversation_manager = ConversationManager()


# REST API Endpoints

@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'THE FORGE AI',
        'version': '2.0.0',
        'forge_initialized': forge is not None,
        'skills_loaded': len(skills_engine.all_skills) if skills_engine else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    return jsonify({
        'models': [
            {
                'id': 'kimi-k2',
                'name': 'Kimi K2',
                'description': 'THE FORGE AI with 575+ capabilities',
                'available': True
            },
            {
                'id': 'gpt-4',
                'name': 'GPT-4',
                'description': 'OpenAI GPT-4',
                'available': bool(os.environ.get('OPENAI_API_KEY'))
            },
            {
                'id': 'claude-3',
                'name': 'Claude 3',
                'description': 'Anthropic Claude 3',
                'available': bool(os.environ.get('ANTHROPIC_API_KEY'))
            },
            {
                'id': 'local',
                'name': 'Local LLM',
                'description': 'Locally deployed model',
                'available': True
            }
        ]
    })

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get user conversations"""
    user_id = request.args.get('user_id', 'default')
    conversations = conversation_manager.get_user_conversations(user_id)
    return jsonify({'conversations': conversations})

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create new conversation"""
    data = request.json
    user_id = data.get('user_id', 'default')
    model = data.get('model', 'kimi-k2')
    
    conversation = conversation_manager.create_conversation(user_id, model)
    return jsonify(conversation)

@app.route('/api/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    """Get specific conversation"""
    conversation = conversation_manager.get_conversation(conv_id)
    if conversation:
        return jsonify(conversation)
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/api/conversations/<conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    """Delete conversation"""
    if conversation_manager.delete_conversation(conv_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Conversation not found'}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message and get response"""
    data = request.json
    conv_id = data.get('conversation_id')
    message = data.get('message')
    model = data.get('model', 'kimi-k2')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Create conversation if not exists
    if not conv_id:
        user_id = data.get('user_id', 'default')
        conversation = conversation_manager.create_conversation(user_id, model)
        conv_id = conversation['id']
    
    # Add user message
    conversation_manager.add_message(conv_id, 'user', message)
    
    # Get AI response
    try:
        response = get_ai_response(message, model, conv_id)
        
        # Add assistant message
        conversation_manager.add_message(conv_id, 'assistant', response, model)
        
        return jsonify({
            'conversation_id': conv_id,
            'response': response,
            'model': model
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get available skills"""
    stats = skills_engine.get_statistics()
    return jsonify(stats)

@app.route('/api/skills/search', methods=['GET'])
def search_skills():
    """Search skills"""
    query = request.args.get('q', '')
    results = skills_engine.search_skills(query)
    return jsonify({
        'query': query,
        'results': [s.to_dict() for s in results]
    })

@app.route('/api/monitor/scan', methods=['POST'])
def run_monitor_scan():
    """Run monitoring scan"""
    monitor.start_monitoring()
    stats = monitor.get_statistics()
    return jsonify(stats)

@app.route('/api/monitor/issues', methods=['GET'])
def get_issues():
    """Get detected issues"""
    issues = [i.to_dict() for i in monitor.issues]
    return jsonify({'issues': issues})


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to THE FORGE AI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join')
def handle_join(data):
    """Join conversation room"""
    conv_id = data.get('conversation_id')
    join_room(conv_id)
    emit('joined', {'conversation_id': conv_id})

@socketio.on('leave')
def handle_leave(data):
    """Leave conversation room"""
    conv_id = data.get('conversation_id')
    leave_room(conv_id)
    emit('left', {'conversation_id': conv_id})

@socketio.on('message')
def handle_message(data):
    """Handle incoming message"""
    conv_id = data.get('conversation_id')
    message = data.get('message')
    model = data.get('model', 'kimi-k2')
    
    if not message:
        emit('error', {'error': 'Message is required'})
        return
    
    # Create conversation if not exists
    if not conv_id:
        user_id = data.get('user_id', 'default')
        conversation = conversation_manager.create_conversation(user_id, model)
        conv_id = conversation['id']
        emit('conversation_created', {'conversation_id': conv_id})
    
    # Add user message
    user_msg = conversation_manager.add_message(conv_id, 'user', message)
    emit('message_added', user_msg, room=conv_id)
    
    # Emit typing indicator
    emit('typing', {'conversation_id': conv_id}, room=conv_id)
    
    # Get AI response (async)
    try:
        response = get_ai_response(message, model, conv_id)
        
        # Add assistant message
        assistant_msg = conversation_manager.add_message(conv_id, 'assistant', response, model)
        
        # Emit response
        emit('typing_stopped', {'conversation_id': conv_id}, room=conv_id)
        emit('response', assistant_msg, room=conv_id)
    
    except Exception as e:
        emit('error', {'error': str(e)}, room=conv_id)


def get_ai_response(message: str, model: str, conv_id: str) -> str:
    """Get AI response based on model"""
    
    # Get conversation context
    conversation = conversation_manager.get_conversation(conv_id)
    context = conversation['messages'] if conversation else []
    
    if model == 'kimi-k2':
        # Use FORGE AI
        response = f"""🔥 THE FORGE AI (Kimi K2) responding to: "{message}"

This is a demonstration response. In production, this would:
- Use the actual Kimi K2 model for generation
- Apply the complete system prompt from all documentation
- Utilize appropriate capabilities based on request
- Learn from interaction patterns
- Provide context-aware responses

Available capabilities:
- 575+ skills across 12 categories
- Programming in 20+ languages
- Content creation and book writing
- Multimedia editing and processing
- Code analysis and review
- Intelligent monitoring and scanning
- And much more!

The system is ready to handle your request with full context awareness."""
        
    elif model == 'gpt-4':
        # Would integrate with OpenAI API
        response = f"GPT-4 response to: {message}\n\n(OpenAI API integration would go here)"
        
    elif model == 'claude-3':
        # Would integrate with Anthropic API
        response = f"Claude 3 response to: {message}\n\n(Anthropic API integration would go here)"
        
    elif model == 'local':
        # Would use local LLM (Ollama, LM Studio, etc.)
        response = f"Local LLM response to: {message}\n\n(Local model integration would go here)"
        
    else:
        response = f"Unknown model: {model}"
    
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🔥 Starting THE FORGE AI Server on port {port}")
    print(f"📍 Access at: http://localhost:{port}")
    print(f"🚀 WebSocket enabled for real-time chat")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )