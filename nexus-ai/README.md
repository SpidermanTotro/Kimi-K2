# 🚀 NEXUS AI - Complete Intelligence System

**A powerful multi-agent AI system with advanced reasoning, code execution, and orchestration capabilities.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4%20%7C%20o1-green.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Features

### 🤖 Multi-Agent System
- **Orchestrator Agent** - Coordinates multiple agents for complex tasks
- **Code Agent** - Writes, debugs, and executes Python code safely
- **Research Agent** - Searches web and analyzes information
- **Analyst Agent** - Processes and analyzes data
- **Creative Agent** - Generates creative content
- **Vision Agent** - Understands and analyzes images

### 🧠 Advanced AI Models
- **GPT-4 & GPT-4 Turbo** - For general chat and complex tasks
- **o1, o1-preview, o1-mini** - For deep reasoning and problem-solving
- **GPT-4 Vision** - For image understanding
- **Smart Model Router** - Automatically selects best model for each task

### 🛠️ Powerful Tools
- **Safe Code Execution** - Sandboxed Python execution with timeout
- **Web Search** - Enhanced web research capabilities
- **File Management** - Read, write, and process files
- **Data Analysis** - Process and visualize data
- **Image Tools** - Generate and analyze images
- **Voice Tools** - Speech-to-text capabilities

### 🎯 Key Capabilities
- ✅ Deep reasoning for complex problems
- ✅ Safe code execution with security validation
- ✅ Multi-agent orchestration
- ✅ Memory and context management
- ✅ Streaming responses
- ✅ Function calling
- ✅ Vision understanding
- ✅ Cost estimation

---

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- OpenAI API key
- (Optional) Anthropic API key

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/nexus-ai.git
cd nexus-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the CLI**
```bash
python main.py
```

5. **Or start the API server**
```bash
python api.py
```

---

## 🚀 Quick Usage Examples

### Using the CLI

```python
from core.nexus import NexusAI

# Initialize Nexus AI
nexus = NexusAI()

# Simple chat
response = nexus.chat("What is the capital of France?")
print(response)

# Code generation and execution
response = nexus.chat("Write a Python function to calculate fibonacci numbers")
print(response)

# Deep reasoning
response = nexus.reason("Solve this logic puzzle: ...")
print(response)

# Image analysis
response = nexus.analyze_image("path/to/image.jpg", "What's in this image?")
print(response)
```

### Using Specific Agents

```python
from agents.code_agent import CodeAgent
from agents.research_agent import ResearchAgent

# Use Code Agent
code_agent = CodeAgent()
result = code_agent.process("Write a function to sort a list")
print(result['explanation'])
print(result['code_blocks'])

# Use Research Agent
research_agent = ResearchAgent()
result = research_agent.process("Research the latest AI developments")
print(result['findings'])
```

### Using the Model Router

```python
from models.model_router import ModelRouter

# Get model recommendation
recommendation = ModelRouter.recommend_model(
    "Solve this complex math problem",
    budget_conscious=False
)
print(f"Recommended model: {recommendation['model']}")
print(f"Reason: {recommendation['reason']}")
```

---

## 🏗️ Architecture

```
nexus-ai/
├── config/              # Configuration and prompts
│   ├── settings.py      # All system settings
│   └── prompts.py       # System prompts for agents
├── core/                # Core system components
│   ├── nexus.py         # Main Nexus AI class
│   ├── orchestrator.py  # Agent orchestration
│   └── memory.py        # Memory management
├── models/              # AI model handlers
│   ├── gpt_handler.py   # GPT-4 models
│   ├── reasoning_handler.py  # o1 models
│   └── model_router.py  # Smart model selection
├── agents/              # Specialized agents
│   ├── base_agent.py    # Base agent class
│   ├── code_agent.py    # Code generation/execution
│   ├── research_agent.py # Web research
│   ├── analyst_agent.py  # Data analysis
│   ├── creative_agent.py # Creative content
│   └── vision_agent.py   # Image understanding
├── tools/               # Utility tools
│   ├── code_executor.py  # Safe code execution
│   ├── web_search.py     # Web search
│   ├── file_manager.py   # File operations
│   └── ...
└── utils/               # Utilities
    ├── logger.py        # Logging system
    └── validators.py    # Input validation
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Settings
DEFAULT_CHAT_MODEL=gpt-4-turbo
DEFAULT_REASONING_MODEL=o1-mini
DEFAULT_CODE_MODEL=gpt-4
DEFAULT_VISION_MODEL=gpt-4-vision-preview

# System Settings
TEMPERATURE=0.7
MAX_TOKENS=4096
REASONING_EFFORT=medium

# Agent Settings
MAX_AGENT_ITERATIONS=10
AGENT_TIMEOUT=300

# Tool Settings
ENABLE_CODE_EXECUTION=true
CODE_EXECUTION_TIMEOUT=30
MAX_FILE_SIZE_MB=10
```

---

## 📚 Documentation

### Available Models

| Model | Use Case | Cost |
|-------|----------|------|
| `gpt-4-turbo` | General chat, complex tasks | Medium |
| `gpt-4` | Code generation, analysis | High |
| `gpt-4-vision` | Image understanding | Medium |
| `o1` | Deep reasoning, complex problems | High |
| `o1-preview` | Advanced reasoning | High |
| `o1-mini` | Fast reasoning | Low |
| `gpt-3.5-turbo` | Simple tasks, budget-friendly | Low |

### Agent Capabilities

| Agent | Capabilities |
|-------|-------------|
| **Orchestrator** | Coordinates multiple agents, breaks down complex tasks |
| **Code Agent** | Writes, debugs, executes, and reviews code |
| **Research Agent** | Web search, information gathering, fact-checking |
| **Analyst Agent** | Data analysis, visualization, statistical analysis |
| **Creative Agent** | Content creation, brainstorming, creative writing |
| **Vision Agent** | Image analysis, object detection, scene understanding |

---

## 🔒 Security

- **Code Execution Sandboxing** - Restricted Python execution environment
- **Module Whitelisting** - Only safe modules allowed
- **Timeout Protection** - Prevents infinite loops
- **Input Validation** - All inputs validated before processing
- **API Key Protection** - Keys stored securely in environment

---

## 🎯 Roadmap

- [x] Core agent system
- [x] GPT-4 and o1 model support
- [x] Safe code execution
- [x] Model router
- [ ] Web interface
- [ ] REST API
- [ ] Database persistence
- [ ] Authentication system
- [ ] Real-time collaboration
- [ ] Mobile apps
- [ ] Plugin system

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 and o1 models
- Anthropic for Claude models
- The open-source community

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: your-email@example.com

---

**Built with ❤️ by the Nexus AI Team**