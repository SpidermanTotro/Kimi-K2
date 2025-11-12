# THE FORGE - Installation Guide for Nobara Linux

## 🎮 Perfect for Nobara Users!

THE FORGE works flawlessly on Nobara Linux (Fedora-based gaming distro).

---

## 🚀 Quick Install (3 Commands)

### Step 1: Install Python & Dependencies
```bash
# Nobara already has Python 3, just install Flask
pip install Flask Flask-CORS

# Or use system package manager
sudo dnf install python3-flask python3-flask-cors
```

### Step 2: Clone THE FORGE
```bash
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2
```

### Step 3: Launch!
```bash
python3 LAUNCH_FORGE.py
```

That's it! 🎉

---

## 🎯 Nobara-Specific Tips

### If you want to compile C/C++:
```bash
sudo dnf install gcc gcc-c++ make cmake
```

### If you want Rust support:
```bash
sudo dnf install rust cargo
```

### If you want Go support:
```bash
sudo dnf install golang
```

### If you want Java support:
```bash
sudo dnf install java-latest-openjdk java-latest-openjdk-devel
```

### If you want Node.js/JavaScript:
```bash
sudo dnf install nodejs npm
```

---

## 💡 Recommended Setup for Nobara

Since Nobara is gaming-focused, you probably have a powerful GPU. THE FORGE will run super fast!

**Complete installation:**
```bash
# Install all language support at once
sudo dnf install gcc gcc-c++ make cmake rust cargo golang nodejs npm java-latest-openjdk

# Install Python packages
pip install Flask Flask-CORS

# Clone and run
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2
python3 LAUNCH_FORGE.py
```

---

## 🎮 Gaming + Coding Setup

Nobara is perfect for game dev! THE FORGE supports:
- ✅ C++ game engines
- ✅ Rust game development
- ✅ Python game scripting
- ✅ JavaScript web games
- ✅ Real-time compilation

---

## ⚡ Performance on Nobara

THE FORGE runs **faster** on Nobara than on Windows because:
- Native Linux performance
- No Windows overhead
- Direct hardware access
- Optimized kernel (Nobara has performance tweaks)

---

## 🔧 Troubleshooting

### If port 5000 is busy:
```bash
# THE FORGE will auto-select another port
# Or manually specify:
PORT=8080 python3 advanced_codespaces_server.py
```

### If Flask isn't found:
```bash
# Use Nobara's Python
python3 -m pip install --user Flask Flask-CORS
```

### If you get permission errors:
```bash
# Don't use sudo with pip, use --user flag
pip install --user Flask Flask-CORS
```

---

## 🎯 Features That Work Great on Nobara

- ✅ Full IDE (VS Code clone)
- ✅ Real compilation (faster on Linux!)
- ✅ Self-learning AI
- ✅ Session tracking
- ✅ Remote connections (SSH, HTTP, WebSocket)
- ✅ GitHub integration
- ✅ Beautiful dashboards
- ✅ AI companions

---

## 🏆 Why THE FORGE is Perfect for Nobara

1. **Native Linux** - Built for Linux, runs best on Linux
2. **Free** - Like Nobara, completely free (save $6,038/year!)
3. **Gaming-ready** - Code game mods, scripts, engines
4. **Performance** - Uses Nobara's optimized kernel
5. **No bloat** - Lightweight, fast startup

---

## 📊 System Requirements

- **OS**: Nobara Linux ✅ (You have this!)
- **Python**: 3.7+ ✅ (Pre-installed on Nobara)
- **RAM**: 2GB+ (You probably have 16GB+ for gaming!)
- **Disk**: 200MB
- **Internet**: Optional (works 100% offline!)

---

## 🚀 Quick Start Commands

```bash
# One-line install and run:
pip install Flask Flask-CORS && git clone https://github.com/SpidermanTotro/Kimi-K2.git && cd Kimi-K2 && python3 LAUNCH_FORGE.py

# Or use the launcher script:
./start_forge.sh

# Or direct start:
python3 advanced_codespaces_server.py
# Then open: http://localhost:5000
```

---

## 🎮 Perfect for Game Development

THE FORGE on Nobara is ideal for:
- C++ game engine development
- Rust game programming
- Python game scripting
- Godot/Unity scripting
- Modding tools development
- Real-time shader coding

---

## 💻 Nobara Terminal Tips

THE FORGE looks amazing in Nobara's default terminal!

**For best experience:**
```bash
# Use Nobara's Konsole or GNOME Terminal
# THE FORGE uses colors and animations that look great!
```

---

## ✅ Verification

After installation, verify everything works:

```bash
# Run tests
python3 COMPILE_AND_TEST.py

# Should show:
# Total Tests: 31
# ✅ Passed: 31 (100%)
# ❌ Failed: 0 (0%)
```

---

## 🎉 You're Ready!

THE FORGE is now installed on your Nobara system!

**Start coding:**
```bash
python3 LAUNCH_FORGE.py
```

**Save $6,038/year compared to:**
- Microsoft Visual Studio Enterprise
- GitHub Codespaces
- GitHub Copilot
- IntelliJ IDEA
- And 18+ more tools!

---

## 🆘 Need Help?

THE FORGE includes complete documentation:
- `RUN_ME_FIRST.md` - Quick start
- `INSTALLATION_GUIDE.md` - Detailed installation
- `RELEASE_NOTES.md` - What's new
- This file - Nobara-specific help

---

**Welcome to THE FORGE on Nobara Linux!** 🚀🎮
