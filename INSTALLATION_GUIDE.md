# 🚀 THE FORGE Codespaces - Installation & Usage Guide

## Quick Start (3 Steps!)

### Step 1: Install Dependencies
```bash
pip install Flask Flask-CORS
```

### Step 2: Run Server
```bash
python3 advanced_codespaces_server.py
```

### Step 3: Open Browser
```
http://localhost:5000
```

**That's it! You're coding for FREE!** 🎉

---

## Detailed Installation

### Prerequisites
- Python 3.8+ installed
- pip package manager
- (Optional) Compilers: gcc, g++, rustc, node, java for code execution

### Linux Installation
```bash
# Update system
sudo apt-get update

# Install Python (if not installed)
sudo apt-get install python3 python3-pip

# Install dependencies
pip3 install Flask Flask-CORS

# Clone repository (or download from GitHub)
git clone https://github.com/YOUR_USERNAME/Kimi-K2.git
cd Kimi-K2

# Run server
python3 advanced_codespaces_server.py

# Open browser to http://localhost:5000
```

### Windows Installation
```powershell
# Install Python from python.org (if not installed)

# Install dependencies
pip install Flask Flask-CORS

# Download repository

# Run server
python advanced_codespaces_server.py

# Open browser to http://localhost:5000
```

### macOS Installation
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Install dependencies
pip3 install Flask Flask-CORS

# Run server
python3 advanced_codespaces_server.py

# Open browser to http://localhost:5000
```

---

## Optional: Install Compilers for Code Execution

### Linux (Ubuntu/Debian)
```bash
# C/C++
sudo apt-get install gcc g++ make cmake

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Go
sudo apt-get install golang

# Java
sudo apt-get install default-jdk

# Node.js
sudo apt-get install nodejs npm

# .NET
wget https://dot.net/v1/dotnet-install.sh
chmod +x dotnet-install.sh
./dotnet-install.sh

# TypeScript
sudo npm install -g typescript
```

### Windows
- Install Visual Studio Build Tools for C/C++
- Install Rust from https://rustup.rs
- Install Go from https://golang.org
- Install JDK from Oracle or OpenJDK
- Install Node.js from https://nodejs.org
- Install .NET SDK from Microsoft

### macOS
```bash
# Xcode Command Line Tools (includes gcc/g++)
xcode-select --install

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Go
brew install go

# Java
brew install openjdk

# Node.js
brew install node

# .NET
brew install --cask dotnet-sdk

# TypeScript
npm install -g typescript
```

---

## Usage

### 1. Start the Server
```bash
python3 advanced_codespaces_server.py
```

You should see:
```
🚀 THE FORGE Codespaces Starting...
✅ REAL Code Execution Engine Loaded!
   Supports: Python, JavaScript, C/C++, Rust, Java, TypeScript, C#
🧠 Self-Learning AI Initialized!
📚 Loaded 0 code patterns
🐛 Loaded 0 debugging solutions
```

### 2. Access the IDE

Open your browser and go to:
- **Launcher**: http://localhost:5000
- **Main IDE**: http://localhost:5000/vscode  
- **Download**: http://localhost:5000/download

### 3. Start Coding!

#### Create a New File
1. Click on file explorer
2. Right-click → New File
3. Name it (e.g., `hello.py`)
4. Start coding!

#### Run Code
1. Write your code
2. Press `Ctrl+Enter` or click Run button
3. See output in terminal

#### AI Assistance
1. Start typing
2. Press `Ctrl+Space` for suggestions
3. AI learns from your code!

#### GitHub Integration
1. Click Git icon in activity bar
2. Enter GitHub username
3. Browse repositories
4. Clone with one click
5. Make changes
6. Commit and push!

---

## Features Tour

### VS Code Interface
- **Activity Bar** (left): Explorer, Search, Git, Extensions, AI Companion
- **Sidebar**: File tree, search panel, git status, extensions list
- **Editor**: Multi-tab code editor with syntax highlighting
- **Terminal**: Integrated bash/shell
- **Status Bar**: Git branch, errors, language info

### AI Companions
- Click the robot icon in activity bar
- Choose your companion:
  - 🦖 Codie (Python/Backend)
  - 🦊 Luna (Frontend/Design)
  - 🐛 Byte (Debugging)
  - ⭐ Nova (Architecture)
- Feed, play, rest your companion
- They help you code!

### Code Execution
```python
# Write Python code
print("Hello from THE FORGE!")

# Press Ctrl+Enter
# Output appears in terminal!
```

```javascript
// Write JavaScript
console.log("Node.js works!");

// Run it!
```

```cpp
// Write C++
#include <iostream>
int main() {
    std::cout << "C++ compilation works!";
}

// Compile and run!
```

### Self-Learning AI
The AI learns from every file you edit:
- Import patterns
- Function styles
- Coding preferences
- Debugging solutions

It gets SMARTER over time!

---

## Troubleshooting

### Server won't start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Flask installation
pip3 list | grep Flask

# Reinstall if needed
pip3 install --upgrade Flask Flask-CORS
```

### Port already in use
```bash
# Change port in advanced_codespaces_server.py
# Line: app.run(host='0.0.0.0', port=5000, debug=True)
# Change 5000 to 5001 or any other port
```

### Code execution not working
```bash
# Check if compiler is installed
python3 --version
node --version
gcc --version
rustc --version

# Install missing compilers (see Optional section above)
```

### Browser can't connect
```bash
# Check firewall
# Allow port 5000

# Try localhost
http://localhost:5000

# Try IP address
http://127.0.0.1:5000
```

---

## Advanced Configuration

### Change Port
Edit `advanced_codespaces_server.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Changed to 8080
```

### Enable Remote Access
```python
# Already enabled by default with host='0.0.0.0'
# Access from other devices: http://YOUR_IP:5000
```

### Customize AI Brain Location
Edit `self_learning_ai.py`:
```python
ai_brain = SelfLearningAI(db_path='/custom/path/brain.db')
```

---

## Mobile Access

### iPhone/iPad
1. Find your computer's IP address
2. On iPhone, open Safari
3. Go to `http://YOUR_IP:5000`
4. Add to Home Screen for app-like experience

### Android
1. Find your computer's IP address
2. Open Chrome
3. Go to `http://YOUR_IP:5000`
4. Add to Home Screen

---

## Keyboard Shortcuts

- `Ctrl+S`: Save file
- `Ctrl+Space`: AI code completion
- `Ctrl+/`: Toggle comment
- `Ctrl+Enter`: Run code
- `Ctrl+Shift+E`: Toggle Explorer
- `Ctrl+Shift+F`: Toggle Search
- `Ctrl+Shift+G`: Toggle Git
- `Ctrl+Shift+X`: Toggle Extensions

---

## Tips & Tricks

1. **Let AI Learn**: The more you code, the smarter the AI gets
2. **Feed Your Companion**: Keep your AI buddy happy!
3. **Take Breaks**: The system monitors your work and suggests breaks
4. **Use Git**: Commit often, never lose work
5. **Try Different Languages**: All major languages supported
6. **Customize**: Edit templates to match your style

---

## Support

- **Issues**: GitHub Issues
- **Documentation**: See CODESPACES_README.md
- **Examples**: Check `/docs` folder

---

## Cost: $0.00 Forever!

Unlike GitHub Codespaces ($768/year), THE FORGE is 100% FREE!

**Happy Coding!** 🚀
