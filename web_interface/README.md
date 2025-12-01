# 🔥 THE FORGE AI - ChatGPT 2.0 Style Web Interface

A modern, ChatGPT-style web interface with 575+ capabilities, multiple LLM support, and offline functionality.

## ✨ Features

### 🎨 Modern UI
- **ChatGPT-style interface** - Familiar and intuitive design
- **Dark/Light themes** - Automatic or manual theme switching
- **Responsive design** - Works on desktop, tablet, and mobile
- **Real-time chat** - WebSocket-powered instant messaging
- **Typing indicators** - See when AI is thinking
- **Message history** - Persistent conversation storage

### 🤖 Multiple LLM Support
- **Kimi K2** - THE FORGE AI with 575+ capabilities
- **GPT-4** - OpenAI's most capable model
- **Claude 3** - Anthropic's advanced AI
- **Local LLMs** - Ollama, LM Studio, and more
- **Switch on-the-fly** - Change models mid-conversation

### 🌐 Offline Mode
- **Progressive Web App (PWA)** - Install as desktop app
- **Service Worker** - Works without internet
- **Local storage** - Conversations saved locally
- **Local LLM support** - Run models offline

### 🛠️ Advanced Features
- **Code syntax highlighting** - Beautiful code display
- **Markdown rendering** - Rich text formatting
- **File upload** - Attach and analyze files
- **Conversation branching** - Edit and regenerate responses
- **Export/Import** - Save and restore conversations
- **Settings panel** - Customize your experience

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Install dependencies
pip install flask flask-cors flask-socketio python-socketio pyjwt

# Start server
cd web_interface
python3 server.py

# Open browser
# Navigate to http://localhost:5000
```

### Option 2: Docker

```bash
# Build image
docker build -t forge-ai .

# Run container
docker run -p 5000:5000 forge-ai

# Access at http://localhost:5000
```

### Option 3: Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet server:app
```

## 📁 Project Structure

```
web_interface/
├── index.html          # Main HTML file
├── styles.css          # Styling
├── app.js             # Frontend JavaScript
├── server.py          # Backend server
├── manifest.json      # PWA manifest
├── sw.js             # Service worker
└── README.md         # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Server port (default: 5000)
export PORT=5000

# Secret key for sessions
export SECRET_KEY=your-secret-key

# OpenAI API key (optional)
export OPENAI_API_KEY=sk-...

# Anthropic API key (optional)
export ANTHROPIC_API_KEY=sk-ant-...
```

### Settings Panel

Access settings by clicking the gear icon:
- **Theme**: Dark, Light, or Auto
- **Default Model**: Choose your preferred LLM
- **Temperature**: Control response randomness (0-2)
- **Code Highlighting**: Enable/disable syntax highlighting
- **Auto-save**: Automatically save conversations
- **Sound Effects**: Enable notification sounds

## 🌐 API Endpoints

### REST API

```
GET  /api/health              - Health check
GET  /api/models              - List available models
GET  /api/conversations       - Get user conversations
POST /api/conversations       - Create new conversation
GET  /api/conversations/:id   - Get specific conversation
DELETE /api/conversations/:id - Delete conversation
POST /api/chat                - Send message and get response
GET  /api/skills              - Get available skills
GET  /api/skills/search       - Search skills
POST /api/monitor/scan        - Run monitoring scan
GET  /api/monitor/issues      - Get detected issues
```

### WebSocket Events

```javascript
// Client -> Server
socket.emit('connect')                    // Connect to server
socket.emit('join', {conversation_id})    // Join conversation
socket.emit('message', {message, model})  // Send message
socket.emit('leave', {conversation_id})   // Leave conversation

// Server -> Client
socket.on('connected')                    // Connection confirmed
socket.on('joined', {conversation_id})    // Joined conversation
socket.on('typing')                       // AI is typing
socket.on('typing_stopped')               // AI stopped typing
socket.on('response', {message})          // AI response
socket.on('error', {error})              // Error occurred
```

## 🎯 Usage Examples

### Basic Chat

```javascript
// Send a message
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: 'Hello, how are you?',
    model: 'kimi-k2'
  })
});

const data = await response.json();
console.log(data.response);
```

### WebSocket Chat

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Send message
socket.emit('message', {
  message: 'Hello!',
  model: 'kimi-k2',
  conversation_id: 'conv_123'
});

// Receive response
socket.on('response', (data) => {
  console.log('AI:', data.content);
});
```

### Search Skills

```javascript
// Search for Python skills
const response = await fetch('/api/skills/search?q=Python');
const data = await response.json();
console.log(data.results);
```

## 🔌 Integration

### With FORGE AI

```python
from forge_implementation import ForgeAI
from live_programs import SkillsEngine

# Initialize FORGE
forge = ForgeAI()
forge.initialize()

# Load skills
skills = SkillsEngine()
skills.load_all_skills()

# Use in your application
response = forge.process_message("Your message here")
```

### With Local LLMs

```python
# Ollama integration
import ollama

response = ollama.chat(model='llama2', messages=[
  {'role': 'user', 'content': 'Hello!'}
])
```

## 📱 Progressive Web App (PWA)

### Install as Desktop App

1. Open in Chrome/Edge
2. Click the install icon in address bar
3. Click "Install"
4. Launch from desktop/start menu

### Features
- Works offline
- Desktop icon
- Native notifications
- Background sync
- File handling

## 🎨 Customization

### Themes

Edit `styles.css` to customize colors:

```css
:root {
    --primary-color: #10a37f;
    --bg-primary: #343541;
    --text-primary: #ececf1;
}
```

### Models

Add new models in `server.py`:

```python
@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({
        'models': [
            {
                'id': 'your-model',
                'name': 'Your Model',
                'description': 'Description',
                'available': True
            }
        ]
    })
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Change port
PORT=8080 python3 server.py
```

### WebSocket Connection Failed

```bash
# Check firewall
sudo ufw allow 5000

# Check if server is running
curl http://localhost:5000/api/health
```

### Offline Mode Not Working

```bash
# Clear cache
# In browser: DevTools > Application > Clear Storage

# Re-register service worker
# In browser: DevTools > Application > Service Workers > Unregister
```

## 📊 Performance

- **Initial Load**: < 2s
- **Message Response**: < 1s (local) / 2-5s (API)
- **Memory Usage**: ~100MB
- **Storage**: ~10MB per 1000 messages

## 🔒 Security

- **HTTPS**: Use SSL/TLS in production
- **Authentication**: JWT tokens for API
- **CORS**: Configured for security
- **Input Validation**: All inputs sanitized
- **Rate Limiting**: Prevent abuse

## 📄 License

Same as parent project - see LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

- **Issues**: GitHub Issues
- **Docs**: See parent README
- **Community**: Join discussions

## 🎉 Credits

Built with:
- Flask & Flask-SocketIO
- Vanilla JavaScript
- CSS3 with custom properties
- Service Workers for PWA

---

**Built with 🔥 by THE FORGE AI Team**

*Making AI accessible, powerful, and beautiful*