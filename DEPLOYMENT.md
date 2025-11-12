# Deploying Kimi K2 to Free Hosting Platforms

This guide shows you how to deploy the Kimi K2 web interface to free hosting platforms without needing local hardware.

## ✨ What You Get

- **Web-based AI interface** - Access from any browser
- **No hardware required** - Runs on free cloud hosting
- **Full API access** - REST endpoints for chat, code review, book writing, etc.
- **Professional UI** - Complete with splash screen and interactive interface

## 🚀 Quick Deploy Options

### Option 1: Render.com (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repository to your GitHub account
2. Sign up at [render.com](https://render.com) (free tier available)
3. Click "New Web Service"
4. Connect your GitHub repository
5. Render will auto-detect the `render.yaml` configuration
6. Click "Create Web Service"
7. Wait 5-10 minutes for deployment
8. Access your app at `https://your-app-name.onrender.com`

**Render.com Free Tier:**
- ✅ 750 hours/month free
- ✅ Automatic SSL certificate
- ✅ Auto-deploy on git push
- ⚠️ Spins down after 15 minutes of inactivity (cold starts ~30 seconds)

### Option 2: Railway.app

1. Fork this repository
2. Sign up at [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Railway auto-detects the `Procfile` and deploys
6. Your app will be live at `https://your-app.up.railway.app`

**Railway Free Tier:**
- ✅ $5 free credit/month
- ✅ ~500 hours of runtime
- ✅ Fast deployments
- ✅ No cold starts

### Option 3: Fly.io

1. Install the Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Clone this repository
3. Run `fly launch` in the project directory
4. Follow the prompts (choose a name and region)
5. Deploy with `fly deploy`
6. Access at `https://your-app.fly.dev`

**Fly.io Free Tier:**
- ✅ 3 shared-cpu VMs
- ✅ 160GB traffic/month
- ✅ No cold starts
- ✅ Global edge network

### Option 4: PythonAnywhere

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code via their web interface or git
3. Create a new web app (choose Flask)
4. Configure WSGI file to point to `forge_server:app`
5. Set working directory to your project
6. Click "Reload" and your app is live

**PythonAnywhere Free Tier:**
- ✅ Always-on hosting (no cold starts)
- ✅ Simple interface
- ⚠️ Limited CPU (good for light usage)
- ⚠️ HTTP only (no HTTPS on free tier)

## 🔧 Manual Setup (Any Platform)

If your platform isn't listed above, you can deploy manually:

1. **Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   # Development
   python3 forge_server.py
   
   # Production (with Gunicorn)
   gunicorn forge_server:app --bind 0.0.0.0:5000 --workers 2
   ```

3. **Environment Variables:**
   ```
   PORT=5000  # Port to run on (auto-set by most platforms)
   ```

## 📋 What's Included

The web deployment includes:

- **REST API Server** (`forge_server.py`)
  - `/health` - Health check
  - `/api/chat` - Chat endpoint
  - `/api/capabilities` - List all capabilities
  - `/api/system-prompt` - Get system prompt
  - `/api/documentation` - Get all docs
  - `/api/code-review` - Code review endpoint
  - `/api/book-writing/analyze` - Book analysis
  - `/api/stats` - System statistics

- **Web GUI** (`forge_gui.py`)
  - Full interactive interface
  - Professional splash screen
  - Chat interface
  - Tools and capabilities browser

- **Documentation** (automatically loaded)
  - All markdown files from `/docs`
  - README.md
  - Complete knowledge base

## 🎯 Using Your Deployed App

Once deployed, you can:

1. **Access the Web Interface:**
   - Open `https://your-app-url.com` in your browser
   - Interactive chat interface loads automatically

2. **Use the REST API:**
   ```bash
   # Chat
   curl -X POST https://your-app-url.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "session_id": "test"}'
   
   # Get capabilities
   curl https://your-app-url.com/api/capabilities
   
   # Health check
   curl https://your-app-url.com/health
   ```

3. **Integrate with Your Apps:**
   ```python
   import requests
   
   API_URL = "https://your-app-url.com"
   
   # Send a message
   response = requests.post(
       f"{API_URL}/api/chat",
       json={"message": "Write a Python function", "session_id": "user123"}
   )
   print(response.json())
   ```

## 🛠️ Configuration Files

- `Procfile` - Heroku/Railway configuration
- `render.yaml` - Render.com configuration
- `runtime.txt` - Python version specification
- `requirements.txt` - Python dependencies

## 💡 Tips for Free Hosting

1. **Cold Starts:** Free tier apps on Render.com spin down after 15 min of inactivity
   - First request after idle takes ~30 seconds to wake up
   - Use a service like UptimeRobot to ping your app every 14 minutes

2. **Resource Limits:** Free tiers have CPU/memory limits
   - The app is optimized for minimal resource usage
   - No model inference happens on free hosting (documentation/API only)

3. **For Actual AI Inference:**
   - Free hosting is great for the web interface and API structure
   - For real AI responses, you'd need to:
     - Deploy Kimi K2 model separately (requires GPU)
     - Use API keys from Moonshot AI platform
     - Connect to external inference services

## 🔍 Troubleshooting

**App won't start:**
- Check logs in your hosting platform dashboard
- Verify `requirements.txt` dependencies installed
- Ensure Python 3.11+ is being used

**404 errors:**
- Check that static files are being served
- Verify templates directory exists
- Check application routes in `forge_server.py`

**Slow response:**
- Free tiers have limited resources
- Cold starts on Render take ~30 seconds
- Consider upgrading to paid tier for better performance

## 📚 Next Steps

1. **Customize the Interface:**
   - Edit `templates/index.html` for UI changes
   - Modify `static/css/style.css` for styling
   - Update `static/js/app.js` for functionality

2. **Add Authentication:**
   - Use Flask-Login for user management
   - Add API key authentication
   - Implement rate limiting

3. **Connect to Real AI:**
   - Get API keys from [platform.moonshot.ai](https://platform.moonshot.ai)
   - Update `forge_server.py` to make real API calls
   - Implement streaming responses

4. **Scale Up:**
   - Move to paid tier for better performance
   - Use Redis for session management
   - Add CDN for static assets

## 🎉 Success!

You now have a live, web-based AI interface accessible from anywhere! Share your URL with others or integrate it into your own applications.

For questions and support, open an issue on GitHub.
