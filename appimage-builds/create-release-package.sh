#!/bin/bash
# Create Complete Release Package
# Bundles all versions together

set -e

echo "📦 Creating Complete Release Package"
echo "====================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Create release directory
RELEASE_DIR="Kimi-K2-Complete-Release-v2.0"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

print_info "Creating release structure..."

# Copy all builds
cp TheForgeAI-Portable.tar.gz "$RELEASE_DIR/"
cp NexusAI-Portable.tar.gz "$RELEASE_DIR/"
cp TheForgeAI-Windows.zip "$RELEASE_DIR/"
cp NexusAI-Windows.zip "$RELEASE_DIR/"

# Create main README
cat > "$RELEASE_DIR/README.md" << 'EOF'
# 🚀 Kimi K2 - Complete Release Package v2.0

**Two Powerful AI Systems in One Package!**

---

## 📦 What's Included

### 1. THE FORGE AI 🔥
**ChatGPT 2.0 Style Interface with 575+ Capabilities**

- Modern web interface
- Multiple LLM support (Kimi K2, GPT-4, Claude, Local)
- Programming in 20+ languages
- Content creation and book writing
- Multimedia editing
- Code analysis and review
- Offline mode with local models

### 2. NEXUS AI 🚀
**Multi-Agent AI System with Advanced Reasoning**

- Multi-agent orchestration
- GPT-4 and o1 reasoning models
- Safe code execution
- Code Agent (write, debug, optimize)
- Research capabilities
- Data analysis
- Creative content generation
- Vision understanding (coming soon)

---

## 🖥️ Platform Support

### Linux (Portable)
- `TheForgeAI-Portable.tar.gz` - THE FORGE AI for Linux
- `NexusAI-Portable.tar.gz` - NEXUS AI for Linux

### Windows
- `TheForgeAI-Windows.zip` - THE FORGE AI for Windows
- `NexusAI-Windows.zip` - NEXUS AI for Windows

---

## 🚀 Quick Start

### THE FORGE AI

**Linux:**
```bash
tar -xzf TheForgeAI-Portable.tar.gz
cd TheForgeAI-Portable
./run-forge.sh
```

**Windows:**
1. Extract `TheForgeAI-Windows.zip`
2. Double-click `run-forge.bat`
3. Browser opens automatically

**Access:** http://localhost:9001

### NEXUS AI

**Linux:**
```bash
tar -xzf NexusAI-Portable.tar.gz
cd NexusAI-Portable
# Edit .env and add your OpenAI API key
./run-nexus.sh
```

**Windows:**
1. Extract `NexusAI-Windows.zip`
2. Edit `.env` and add your OpenAI API key
3. Double-click `run-nexus.bat`

---

## 📋 Requirements

### THE FORGE AI
- Python 3.7+
- Internet connection (first run only)
- Modern web browser

### NEXUS AI
- Python 3.11+
- OpenAI API key (get from platform.openai.com)
- Internet connection

---

## 🎯 Features Comparison

| Feature | THE FORGE AI | NEXUS AI |
|---------|--------------|----------|
| Web Interface | ✅ Modern UI | 🔄 Coming Soon |
| CLI Interface | ✅ Available | ✅ Rich Terminal |
| Code Execution | ✅ Basic | ✅ Advanced + Safe |
| Multiple LLMs | ✅ 4+ Models | ✅ GPT-4 + o1 |
| Reasoning | ❌ | ✅ o1 Models |
| Multi-Agent | ❌ | ✅ 6 Agents |
| Offline Mode | ✅ Local Models | ❌ |
| Book Writing | ✅ Specialized | 🔄 Coming Soon |
| Multimedia | ✅ Full Suite | 🔄 Coming Soon |

---

## 📚 Documentation

### THE FORGE AI
- See `TheForgeAI-*/README.txt` for detailed instructions
- Web interface is self-explanatory
- Access documentation at http://localhost:9001/docs

### NEXUS AI
- See `NexusAI-*/README.txt` for setup
- Use `help` command in CLI for guidance
- Check `BUILD_PROGRESS.md` for features

---

## 🔧 Troubleshooting

### Python Not Found
- **Linux:** `sudo apt install python3 python3-pip python3-venv`
- **Windows:** Download from https://www.python.org/
  - ⚠️ Check "Add Python to PATH" during installation

### Port Already in Use
- **THE FORGE AI:** Edit `server.py` and change port 9001
- **NEXUS AI:** No port conflicts (CLI only)

### Dependencies Installation Fails
- Ensure internet connection
- Try: `pip install --upgrade pip`
- Use Python 3.11+ for NEXUS AI

### OpenAI API Key Issues
- Get key from https://platform.openai.com/api-keys
- Add to `.env` file: `OPENAI_API_KEY=sk-...`
- Or export: `export OPENAI_API_KEY=sk-...`

---

## 🎓 Usage Examples

### THE FORGE AI Examples

**1. Code Generation:**
```
User: Write a Python function to calculate fibonacci numbers
AI: [Generates code with explanation]
```

**2. Book Writing:**
```
User: Help me write a chapter about AI
AI: [Provides structured content with sections]
```

**3. Multimedia Editing:**
```
User: Convert this video to MP4
AI: [Provides conversion commands and options]
```

### NEXUS AI Examples

**1. Code Mode:**
```
Coding Task: Create a web scraper for news articles
[Generates code, executes it, shows results]
```

**2. Reasoning Mode:**
```
Problem: Solve this logic puzzle: [puzzle description]
[Shows step-by-step reasoning and solution]
```

**3. Chat Mode:**
```
You: Explain quantum computing
AI: [Detailed explanation with examples]
```

---

## 🔒 Security & Privacy

- **Code Execution:** Sandboxed environment with whitelisted modules
- **API Keys:** Stored locally, never transmitted
- **Data:** All processing happens locally or via your API keys
- **No Telemetry:** No usage data collected

---

## 📊 System Requirements

### Minimum
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB
- **Storage:** 500 MB free space
- **OS:** Linux (Ubuntu 20.04+) or Windows 10+

### Recommended
- **CPU:** Quad-core 2.5 GHz+
- **RAM:** 8 GB+
- **Storage:** 2 GB free space
- **Internet:** Broadband connection

---

## 🤝 Support & Community

- **GitHub:** https://github.com/SpidermanTotro/Kimi-K2
- **Issues:** Report bugs on GitHub Issues
- **Discussions:** Join GitHub Discussions

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

- **Kimi K2:** Moonshot AI
- **OpenAI:** GPT-4 and o1 models
- **Community:** Open-source contributors

---

## 🔄 Updates

**Version 2.0.0** (2024-12-01)
- ✅ THE FORGE AI with ChatGPT 2.0 interface
- ✅ NEXUS AI multi-agent system
- ✅ Portable Linux builds
- ✅ Windows builds
- ✅ Safe code execution
- ✅ o1 reasoning models
- ✅ Comprehensive documentation

---

**Built with ❤️ by the Kimi K2 Team**

🚀 **Ready to explore AI? Start with THE FORGE AI for ease of use, or NEXUS AI for advanced capabilities!**
EOF

# Create installation guide
cat > "$RELEASE_DIR/INSTALLATION_GUIDE.txt" << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          KIMI K2 - INSTALLATION GUIDE v2.0                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

QUICK START - 3 STEPS
=====================

STEP 1: Choose Your Platform
-----------------------------
Linux Users:   Use *-Portable.tar.gz files
Windows Users: Use *-Windows.zip files

STEP 2: Extract
---------------
Linux:   tar -xzf <filename>.tar.gz
Windows: Right-click → Extract All

STEP 3: Run
-----------
Linux:   ./run-*.sh
Windows: Double-click run-*.bat


DETAILED INSTRUCTIONS
=====================

THE FORGE AI (Web Interface)
-----------------------------

Linux:
1. Extract: tar -xzf TheForgeAI-Portable.tar.gz
2. Enter: cd TheForgeAI-Portable
3. Run: ./run-forge.sh
4. Browser opens automatically to http://localhost:9001

Windows:
1. Extract TheForgeAI-Windows.zip
2. Open the extracted folder
3. Double-click run-forge.bat
4. Browser opens automatically

First Run:
- Dependencies install automatically (requires internet)
- Takes 1-2 minutes on first launch
- Subsequent launches are instant


NEXUS AI (Terminal Interface)
------------------------------

Linux:
1. Extract: tar -xzf NexusAI-Portable.tar.gz
2. Enter: cd NexusAI-Portable
3. Setup: cp .env .env.local
4. Edit .env.local and add: OPENAI_API_KEY=sk-your-key-here
5. Run: ./run-nexus.sh

Windows:
1. Extract NexusAI-Windows.zip
2. Open the extracted folder
3. Copy .env to .env.local
4. Edit .env.local and add your OpenAI API key
5. Double-click run-nexus.bat

Getting OpenAI API Key:
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with sk-)
5. Paste into .env.local file


TROUBLESHOOTING
===============

Problem: "Python not found"
Solution (Linux): sudo apt install python3 python3-pip python3-venv
Solution (Windows): Install from https://www.python.org/
                    ⚠️ Check "Add Python to PATH"!

Problem: "Port already in use"
Solution: Another app is using the port
         - Close other web servers
         - Or edit server.py to change port

Problem: "Permission denied"
Solution (Linux): chmod +x run-*.sh

Problem: Dependencies fail to install
Solution: - Check internet connection
         - Update pip: pip install --upgrade pip
         - Try manual install: pip install -r requirements.txt

Problem: OpenAI API errors
Solution: - Verify API key is correct
         - Check you have credits at platform.openai.com
         - Ensure key has proper permissions


SYSTEM REQUIREMENTS
===================

Minimum:
- Python 3.7+ (THE FORGE AI)
- Python 3.11+ (NEXUS AI)
- 4 GB RAM
- 500 MB free space
- Internet connection

Recommended:
- Python 3.11+
- 8 GB RAM
- 2 GB free space
- Broadband internet


WHAT TO TRY FIRST
==================

THE FORGE AI:
1. Open http://localhost:9001
2. Try: "Write a Python function to sort a list"
3. Try: "Help me write a blog post about AI"
4. Explore the 575+ capabilities!

NEXUS AI:
1. Select "chat" mode
2. Try: "Explain quantum computing"
3. Select "code" mode
4. Try: "Create a web scraper"
5. Select "reason" mode
6. Try: "Solve this math problem: [your problem]"


GETTING HELP
============

Documentation: See README.md
GitHub: https://github.com/SpidermanTotro/Kimi-K2
Issues: Report on GitHub Issues


Enjoy exploring AI! 🚀
EOF

# Create checksums
print_info "Generating checksums..."
cd "$RELEASE_DIR"
sha256sum *.tar.gz *.zip > CHECKSUMS.txt
cd ..

print_status "Checksums generated"

# Create final archive
print_info "Creating final release archive..."
tar -czf "${RELEASE_DIR}.tar.gz" "$RELEASE_DIR"
zip -q -r "${RELEASE_DIR}.zip" "$RELEASE_DIR"

print_status "Release package created!"

echo ""
echo "====================================="
echo -e "${GREEN}✓ Complete!${NC}"
echo "====================================="
echo ""
echo "Created:"
echo "  • ${RELEASE_DIR}.tar.gz (for Linux)"
echo "  • ${RELEASE_DIR}.zip (for Windows)"
echo ""
echo "Contents:"
ls -lh "$RELEASE_DIR"
echo ""
echo "Package sizes:"
du -h "${RELEASE_DIR}.tar.gz"
du -h "${RELEASE_DIR}.zip"
echo ""