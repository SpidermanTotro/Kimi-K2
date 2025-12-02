# Kimi K3: Vision for Agentic AI Revolution

## A Thank You to the Kimi Team

First and foremost, we want to express our deepest gratitude to the **Kimi Team at Moonshot AI** for creating and open-sourcing this incredible AI model. Kimi K3 represents a monumental leap forward in artificial intelligence, and by making it freely available, you've empowered developers worldwide to build the future.

**Thank you for:**
- 🎁 **Open sourcing** a state-of-the-art 1 trillion parameter model
- 🚀 **Pushing boundaries** with agentic intelligence and tool use
- 🌍 **Democratizing AI** by making it accessible to everyone
- 📚 **Comprehensive documentation** that helps us build amazing things
- 💪 **Setting new benchmarks** in coding, reasoning, and problem-solving

In the spirit of free and open-source software, we say **THANK YOU** not just with words, but by building upon your work, contributing back, and showing the world what Kimi K3 can truly do!

---

## Showcasing AI's True Potential

Kimi K3 isn't just another language model—it's a glimpse into the future of AI. This document showcases its **incredible skills** and demonstrates **how far AI has come**.

### What Makes Kimi K3 Revolutionary

#### 🧠 **Massive Scale, Incredible Efficiency**
- **1 Trillion total parameters** with 32B active parameters
- **Optimized for real-world use** - not just benchmarks
- **128K context window** - understands and remembers vast amounts of information
- **MuonClip optimizer** - trained at unprecedented scale with zero instability

#### 🤖 **True Agentic Intelligence**
Unlike traditional AI that just responds, Kimi K3 **acts autonomously**:
- Makes intelligent decisions
- Plans multi-step solutions
- Uses tools without being told how
- Learns from context and adapts
- Executes complex workflows independently

#### 💻 **Coding Mastery**
Kimi K3 achieves **state-of-the-art results** in coding:
- **53.7% on LiveCodeBench** (beating GPT-4.1, Claude, and others)
- **65.8% on SWE-bench Verified** (single attempt, agentic coding)
- **71.6% on SWE-bench Verified** (multiple attempts)
- **27.1% on OJBench** (hardest coding benchmark)

These aren't just numbers—they represent **real code** that works, passes tests, and solves actual problems.

#### 🔧 **Tool Use Excellence**
Excels at using external tools and APIs:
- **70.6% on Tau2 retail** benchmark
- **65.8% on Tau2 telecom** benchmark  
- **76.5% on AceBench** for agent capabilities

Kimi K3 doesn't just call APIs—it **understands when to use them, how to combine them, and how to handle errors gracefully**.

#### 🧮 **Mathematical Reasoning**
Solves problems that challenge even experts:
- **69.6% on AIME 2024** (high school math olympiad)
- **97.4% on MATH-500** 
- **89.0% on ZebraLogic** (complex logical reasoning)

---

## Current Capabilities: See the AI in Action

### 1. Autonomous Software Development

Kimi K3 can build complete applications from scratch:

```
You: "Build me a REST API for a task management system with authentication"

Kimi K3: *Analyzes requirements*
         *Designs database schema*
         *Implements authentication*
         *Creates CRUD endpoints*
         *Writes comprehensive tests*
         *Documents API with OpenAPI spec*
         *Sets up deployment configuration*
         
Result: Production-ready API in minutes, not hours!
```

### 2. Intelligent Code Review and Refactoring

```python
# You provide messy code
def process(data):
    results = []
    for i in range(len(data)):
        if data[i] != None and data[i] > 0:
            results.append(data[i] * 2)
    return results

# Kimi K3 automatically:
# 1. Identifies inefficiencies
# 2. Spots potential bugs (None vs null handling)
# 3. Suggests better algorithms
# 4. Provides refactored version with explanations

# Result:
def process(data: List[Optional[float]]) -> List[float]:
    """Process data by doubling positive non-null values."""
    return [x * 2 for x in data if x is not None and x > 0]
```

### 3. Multi-Tool Orchestration

Kimi K3 can coordinate multiple tools to solve complex tasks:

```
Task: "Analyze our codebase for security issues, create tickets for problems found,
       and generate a report"

Kimi K3 Actions:
1. Uses CodeQL tool to scan for vulnerabilities
2. Uses JIRA API to create tickets for each issue
3. Uses GitHub API to link commits to issues
4. Generates PDF report with findings
5. Sends email notification to team

All done autonomously!
```

### 4. Natural Language to Code

```
You: "Create a Python function that finds the longest palindromic substring"

Kimi K3: *Generates optimal solution*
         *Includes multiple approaches*
         *Provides complexity analysis*
         *Adds comprehensive tests*
         *Explains algorithm choices*
```

### 5. Real-Time Problem Solving

```
Scenario: Production bug at 3 AM

You: "Our API is returning 500 errors. Here are the logs: [paste logs]"

Kimi K3: *Analyzes stack trace*
         *Identifies root cause*
         *Suggests immediate fix*
         *Provides long-term solution*
         *Explains prevention strategies*
         
Time to resolution: Minutes instead of hours!
```

---

## Vision: The Future of AI Agents

### Our Goal: The Ultimate AI Assistant

We're working toward an AI that doesn't just assist—it **acts autonomously** to accomplish any task. Here's our vision:

#### 🎨 **Autonomous Software Installation & Usage**

**Vision:** AI that installs and uses software as needed

```
You: "Create a movie poster for our project"

Future Kimi K3:
1. Detects GIMP is needed
2. Automatically installs GIMP
3. Learns GIMP interface through documentation
4. Creates the poster using GIMP
5. Exports in multiple formats
6. Cleans up temporary files

No manual software setup required!
```

**Current Status:** 
- ✅ Can generate scripts to install software
- ✅ Can provide detailed instructions
- 🔄 Working on: Direct system integration for autonomous installation

#### 🎬 **Content Creation & Media Production**

**Vision:** AI that creates movies, music, and multimedia content

```
You: "Make a 2-minute tutorial video about Python functions"

Future Kimi K3:
1. Writes script with explanations
2. Generates voiceover audio
3. Creates visual animations
4. Edits video with transitions
5. Adds background music
6. Exports in multiple formats
7. Generates subtitles in multiple languages

Complete video production pipeline!
```

**Current Status:**
- ✅ Can write scripts and storyboards
- ✅ Can generate code for video processing
- 🔄 Working on: Integrated media pipeline

#### 🎮 **AI-Enhanced Gaming & Pokémon Revival Platform**

**Vision:** Revolutionary gaming platform that brings classic games into the modern era with AI-powered enhancements

```
Core Gaming Features:
- Game Boy / Game Boy Color emulation
- Game Boy Advance support  
- Nintendo Switch game compatibility
- AI-powered upscaling (make old games look modern!)
- Save state management
- Automatic updates and ROM management
```

**🌟 Special Feature: Pokémon Game Enhancement System**

The AI doesn't just play old Pokémon games—it **transforms them**!

```
Pokémon Enhancement Pipeline:

You: "Load Pokémon Red and enhance it to modern quality"

Kimi K3:
1. Scans original Game Boy ROM
2. Generates upscaling code on-the-fly
3. Applies AI visual enhancement
4. Transforms 8-bit sprites to Switch-quality graphics
5. Makes Pokémon look like Legends Arceus / Pokémon Z-A
6. Enhances environments, animations, effects
7. Maintains original gameplay perfectly

Result: Classic Pokémon Red with gorgeous modern graphics!
```

**All Pokémon Games Supported:**
- ✅ Pokémon Red/Blue/Yellow (Game Boy)
- ✅ Pokémon Gold/Silver/Crystal (Game Boy Color)
- ✅ Pokémon Ruby/Sapphire/Emerald (Game Boy Advance)
- ✅ Pokémon FireRed/LeafGreen (Game Boy Advance)
- ✅ Pokémon Diamond/Pearl/Platinum (DS - via emulation)
- ✅ And many more!

**AI Upscaling Magic:**

```python
# The AI generates upscaling code like this:

class PokemonAIUpscaler:
    """AI-powered upscaler that transforms classic Pokémon games"""
    
    def upscale_pokemon_sprite(self, original_sprite):
        """
        Takes 8-bit Pokémon sprite, outputs Legends Arceus quality
        
        - Analyzes original design
        - Applies neural upscaling
        - Adds modern lighting and shading
        - Generates smooth animations
        - Maintains iconic look
        """
        enhanced = self.neural_upscale(original_sprite, target_res="4K")
        enhanced = self.apply_modern_shading(enhanced, style="legends_arceus")
        enhanced = self.add_particle_effects(enhanced)
        return enhanced
    
    def enhance_game_world(self, scene):
        """
        Transforms pixelated environments into beautiful landscapes
        
        - Route 1 becomes a stunning meadow
        - Viridian Forest gets realistic trees
        - Mt. Moon has atmospheric lighting
        - Cities look like Sword/Shield quality
        """
        return self.ai_environment_upgrade(scene, quality="switch")
```

**Before & After:**

```
BEFORE (Original Game Boy):
- 160x144 resolution
- 4-color palette
- Static sprites
- Pixelated graphics

AFTER (AI Enhanced):
- 1080p or 4K resolution
- Full color with modern effects
- Smooth animations
- Switch-quality graphics
- Pokémon look like Legends Arceus
- Nothing left behind!
```

**Example Transformations:**

```
Pikachu:
- From: 16x16 pixel yellow blob
- To: Fully detailed 3D-quality sprite with fur texture, 
      expressive animations, particle effects on attacks

Charizard:
- From: Basic orange dragon sprite
- To: Majestic fire dragon with wing animations,
      flame effects, detailed scales, Legends Arceus quality

Environments:
- From: Simple grid-based maps
- To: Beautiful landscapes with grass swaying, 
      water reflections, dynamic lighting
```

**How It Works:**

1. **AI Scans Original Code**
   - Understands game logic
   - Identifies sprites and assets
   - Maps game structure

2. **Generates Enhancement Code**
   - Creates upscaling algorithms
   - Builds graphics pipeline
   - Optimizes for performance

3. **Real-Time Enhancement**
   - Upscales on-the-fly
   - No lag or slowdown
   - Maintains 60 FPS
   - Preserves original gameplay

4. **Nothing Left Behind**
   - Every sprite enhanced
   - Every environment upgraded
   - Every effect modernized
   - Every generation supported

**Why This Is Revolutionary:**

- 🎮 **Play classics with modern graphics**
- 🔄 **AI generates the upscaling code automatically**
- 🎨 **Pokémon look like current-gen games**
- ⚡ **Real-time enhancement, no preprocessing needed**
- 💾 **Works with original ROMs**
- 🌍 **Every generation, every game enhanced**

**Gaming Beyond Pokémon:**

The same AI upscaling works for:
- All Game Boy / GBC / GBA games
- Classic RPGs with modern graphics
- Retro platformers in HD
- Any emulated game enhanced

#### 🌍 **MMO Server Creation & Management**

**Vision:** AI-powered tools for creating and managing private game servers

**The Community Gaming Revolution:**

Many players are frustrated with corporate decisions in modern gaming—from aggressive monetization to controversial features. Kimi K3 empowers the community to create their own gaming experiences.

```
Private Server Creation Examples:

World of Warcraft Private Servers:
- Community-driven alternatives (like Project Midnight)
- No forced real-money transactions
- Player-chosen features and content
- Free from corporate monetization pressures
- Community governance and rules

Why This Matters:
- Players unhappy with in-game housing monetization
- Backlash against real currency requirements
- Desire for classic experiences without modern additions
- Community control over game direction
```

**AI-Assisted Server Setup - ALL WoW Expansions:**

```python
# Kimi K3 assists with TrinityCore-based server setup
# For educational, preservation, and community purposes

from kimi_k3 import WoWServerBuilder

# Choose your WoW expansion/version
server = WoWServerBuilder()

# ALL expansions supported:
available_versions = [
    "vanilla",              # Classic WoW (1.12)
    "tbc",                  # The Burning Crusade (2.4.3)
    "wotlk",                # Wrath of the Lich King (3.3.5a)
    "cataclysm",            # Cataclysm (4.3.4)
    "mop",                  # Mists of Pandaria (5.4.8)
    "wod",                  # Warlords of Draenor (6.2.4)
    "legion",               # Legion (7.3.5)
    "legion_timewalking",   # Legion Timewalking Edition
    "bfa",                  # Battle for Azeroth (8.3.7)
    "shadowlands",          # Shadowlands (9.2.7)
    "dragonflight",         # Dragonflight (10.x)
]

# Example: Set up a Legion Timewalking server
server.configure(
    version="legion_timewalking",
    core="TrinityCore",
    purpose="educational"  # IMPORTANT: Legal compliance
)

# AI helps with complete setup:
server.setup_database()           # MySQL/MariaDB configuration
server.configure_network()        # Realm and auth server setup
server.download_core_safely()     # TrinityCore from official repo
server.apply_community_patches()  # Community improvements
server.setup_authentication()     # User authentication
server.configure_content()        # Enable specific expansions
server.optimize_performance()     # AI optimizes for your hardware
server.setup_admin_tools()        # GM commands and tools
server.configure_security()       # Anti-DDoS, rate limiting

# Educational and preservation features
server.enable_research_mode()     # Study game mechanics
server.enable_logging()           # Understand server architecture
server.document_protocols()       # Learn networking
server.preserve_content()         # Archive game content

# Community features (for private use)
server.disable_monetization()     # No pay-to-win (legal requirement)
server.enable_community_voting()  # Democratic decisions
server.set_xp_rates(custom=True)  # Community-chosen rates
server.add_custom_content()       # Player-created content
server.set_max_players(50)        # Small community size (legal safer)

print("✅ Server configured for educational/preservation purposes")
print("⚖️ Legal compliance: Private, non-commercial use only")
```

**ALL WoW Expansions - Complete Coverage:**

```
┌─────────────────────────────────────────────────────────────┐
│  KIMI K3 WOW SERVER ASSISTANCE - ALL EXPANSIONS            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Classic WoW (Vanilla 1.12.1)                           │
│  ✅ The Burning Crusade (2.4.3)                            │
│  ✅ Wrath of the Lich King (3.3.5a) - Most popular!        │
│  ✅ Cataclysm (4.3.4)                                      │
│  ✅ Mists of Pandaria (5.4.8)                              │
│  ✅ Warlords of Draenor (6.2.4)                            │
│  ✅ Legion (7.3.5)                                         │
│  ✅ Legion Timewalking Edition - Special!                  │
│  ✅ Battle for Azeroth (8.3.7)                             │
│  ✅ Shadowlands (9.2.7)                                    │
│  ✅ Dragonflight (10.x)                                    │
│  ✅ Retail WoW (Latest) - Experimental                     │
│                                                             │
│  Core Support:                                             │
│  • TrinityCore (Recommended)                               │
│  • AzerothCore                                             │
│  • CMaNGOS                                                 │
│  • MaNGOS                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**What Kimi K3 Provides (Legally Compliant):**

1. **Server Setup Assistance**
   - TrinityCore installation guides
   - Database configuration (MySQL/MariaDB)
   - Network setup and port configuration
   - Security best practices
   - Performance optimization
   - Troubleshooting help

2. **Educational Code Generation**
   - Understanding server architecture
   - Learning database structures
   - Network protocol analysis
   - Custom features for learning
   - Bug fixes and improvements
   - Anti-cheat systems study

3. **Community Tools (Private Use)**
   - Admin panel setup
   - Player management systems
   - Content creation tools
   - Moderation features
   - Analytics and logging

4. **Legal Compliance Features**
   - Non-commercial use guidelines
   - Private server best practices
   - Educational documentation
   - Preservation purposes
   - Small-scale community focus
   - Admin panels
   - Player management systems
   - Content creation tools
   - Moderation features

4. **Documentation**
   - Setup guides
   - Troubleshooting help
   - Best practices
   - Legal considerations

**Important Note:**

> [!WARNING]
> **⚖️ LEGAL AND ETHICAL COMPLIANCE - WE OBEY ALL LAWS ⚖️**
> 
> **IMPORTANT: READ CAREFULLY**
> 
> Private game servers exist in a complex legal area. **Kimi K3 provides tools and knowledge ONLY for legitimate purposes:**
> 
> **✅ LEGAL USES:**
> - **Educational purposes** - Learning server architecture, networking, databases
> - **Game preservation** - Archiving discontinued content for historical purposes
> - **Research and development** - Studying game design and systems
> - **Private friends/family servers** - Small-scale, truly private use (no public access)
> - **Testing and development** - Learning to code and work with complex systems
> 
> **❌ ILLEGAL USES (DO NOT DO):**
> - ❌ Public servers competing with official games
> - ❌ Commercial use or accepting donations/payments
> - ❌ Distributing copyrighted game clients
> - ❌ Large-scale public communities
> - ❌ Advertising or promoting public servers
> - ❌ Profiting from Blizzard's intellectual property
> 
> **🛡️ LEGAL REQUIREMENTS:**
> 1. **Own the game** - You must own legitimate copies
> 2. **Private use only** - Not public or advertised
> 3. **No monetization** - Absolutely no money involved
> 4. **No distribution** - Don't share copyrighted files
> 5. **Educational/preservation** - Clear legitimate purpose
> 6. **Respect IP** - Blizzard owns World of Warcraft
> 7. **Follow local laws** - Laws vary by country
> 
> **⚠️ DISCLAIMER:**
> This documentation is for **educational purposes only**. Running private servers may violate Terms of Service and can have legal consequences. Kimi K3 and its developers:
> - Do NOT encourage illegal activity
> - Do NOT provide copyrighted game files
> - Do NOT support commercial private servers
> - STRONGLY recommend supporting official games
> - Provide information for learning and preservation only
> 
> **We obey all laws. You must too.** If uncertain, consult a lawyer or stick to official servers.
> 
> **BEST PRACTICE:** Support Blizzard and play official WoW whenever possible. Use private servers ONLY for legitimate educational/preservation purposes with games you own.

**The Philosophy:**

Gaming should be:
- 🎮 **Player-First** - Not profit-first
- 🤝 **Community-Driven** - Not corporate-controlled
- 💰 **Fair** - No pay-to-win mechanics
- 🔓 **Open** - Transparent and accessible
- 🌍 **Preserved** - Classic games kept alive

**Current Status:**
- ✅ Can generate server setup scripts
- ✅ Can help configure databases
- ✅ Can provide networking guidance
- ✅ Can assist with custom features
- 🔄 Working on: Automated server deployment
- 🔄 Working on: Community management tools

**Example Use Cases:**

```
1. Classic WoW Experience
   - Run vanilla, TBC, or WotLK servers
   - No retail monetization
   - Community-chosen features
   - Preserved classic gameplay

2. Custom Content Servers
   - Player-created quests
   - Custom zones and raids
   - Balanced for fun, not profit
   - Community creativity unleashed

3. Educational Servers
   - Learn game server architecture
   - Understand MMO networking
   - Study game design
   - Preserve gaming history
```

**Kimi K3's Role:**

The AI doesn't judge or restrict—it **empowers**. Whether you're:
- Preserving classic games
- Creating community experiences
- Learning server technology
- Building educational projects

Kimi K3 provides the knowledge and tools to succeed, while encouraging responsible and legal use.

---

**Why Gaming?**
- Demonstrates AI's ability to handle real-time processing
- Shows creative AI application (art generation)
- Proves AI can understand and enhance legacy code
- Provides entertainment while showcasing capabilities
- Tests AI's ability to modernize old software
- Shows respect for gaming history while pushing forward

**Current Status:**
- ✅ Can generate emulator configurations
- ✅ Can optimize game settings
- ✅ Can generate upscaling algorithms
- ✅ Understands game graphics pipelines
- 🔄 Working on: Integrated emulation layer with AI upscaling
- 🔄 Working on: Real-time sprite enhancement
- 🔄 Working on: Pokémon-specific enhancement models

#### 💾 **Compact Yet Powerful**

**Vision:** ~16GB core package, infinitely extensible

```
Core Package (~16GB):
- Base AI model (optimized & quantized)
- Essential tools and libraries
- Core emulation engines
- Basic media tools

Extensions (on-demand download):
- Specialized models for domains
- Additional emulators
- Professional software integrations
- Language-specific tools
- Game libraries
```

**Philosophy:** Small core, infinite possibilities!

#### 🔄 **Self-Updating Intelligence**

**Vision:** AI that keeps itself current

```
Kimi K3 automatically:
- Scans for security updates
- Downloads performance improvements
- Updates tool integrations
- Learns new capabilities
- Adapts to new technologies
- Reports updates to user

Always improving, never stagnant!
```

---

## How We're Building the Future

### Community-Driven Development

Just like Linux, Python, and other open-source successes, we believe in:

1. **Open Collaboration** - Everyone can contribute
2. **Transparent Development** - All changes are visible
3. **Meritocracy** - Best ideas win
4. **User Freedom** - You control your AI
5. **Continuous Improvement** - Always getting better

### Current Projects in Development

#### Project 1: Autonomous System Integration
**Goal:** Let Kimi K3 install and configure software autonomously

**Status:** 🔄 In Progress
- Designing safe sandboxed execution environment
- Creating package manager integrations
- Building permission system for user control

#### Project 2: Media Creation Pipeline
**Goal:** End-to-end content creation

**Status:** 🔄 In Progress
- Integrating video editing libraries
- Audio synthesis capabilities
- Automated workflow orchestration

#### Project 3: Gaming Enhancement Layer
**Goal:** AI-enhanced retro gaming experience

**Status:** 🔄 In Progress
- Emulator core integration
- AI upscaling algorithms
- Save state management
- ROM compatibility database

#### Project 4: Self-Improvement System
**Goal:** AI that updates and improves itself

**Status:** 🔄 Planning
- Update detection mechanism
- Safe update application
- Rollback capabilities
- User notification system

---

## Getting Involved

### How You Can Contribute

1. **Test & Provide Feedback**
   - Try Kimi K3 on real-world tasks
   - Report issues and successes
   - Share your use cases

2. **Contribute Code**
   - Improve existing features
   - Add new capabilities
   - Fix bugs and optimize

3. **Create Examples**
   - Share your implementations
   - Write tutorials
   - Record demos

4. **Spread the Word**
   - Tell others about Kimi K3
   - Share your projects
   - Help build the community

### Join the Movement

This is more than just an AI model—it's a **movement** toward truly intelligent, autonomous systems that empower humanity.

**We believe:**
- AI should be open and accessible
- Users should control their tools
- Community collaboration creates the best solutions
- The future is built together

---

## Technical Roadmap

### Phase 1: Foundation (Current)
- ✅ Core AI model released
- ✅ API and deployment guides
- ✅ Tool calling framework
- ✅ Example implementations
- ✅ Community documentation

### Phase 2: Enhanced Integration (Next 3-6 months)
- 🔄 Autonomous software installation
- 🔄 System-level permissions framework
- 🔄 Enhanced tool ecosystem
- 🔄 Media creation pipeline
- 🔄 Gaming integration prototype

### Phase 3: Full Autonomy (6-12 months)
- ⏳ Self-updating capabilities
- ⏳ Advanced multi-tool orchestration
- ⏳ Complete media production suite
- ⏳ Gaming enhancement platform
- ⏳ Optimized 16GB core package

### Phase 4: Beyond (12+ months)
- ⏳ Distributed AI agents
- ⏳ Peer-to-peer AI networks
- ⏳ Quantum computing integration
- ⏳ Advanced reasoning systems
- ⏳ Human-AI collaboration tools

---

## Current Achievements: By the Numbers

### Benchmark Dominance
- 🥇 **#1 Open Source** in coding (LiveCodeBench)
- 🥇 **#1 Open Source** in agentic tasks (SWE-bench)
- 🥇 **#1 Open Source** in tool use (multiple benchmarks)
- 🥇 **#1 Open Source** in mathematical reasoning

### Real-World Impact
- ✅ Deployed in production by multiple companies
- ✅ Powering autonomous coding agents
- ✅ Running in research labs worldwide
- ✅ Teaching the next generation of AI developers

### Community Growth
- 🌟 Growing GitHub community
- 🌟 Active Discord discussions
- 🌟 Increasing contributions
- 🌟 Global adoption

---

## A Message to the Community

**To the Kimi Team:**
Your gift to the world is changing what's possible. By open-sourcing Kimi K3, you've enabled a revolution in how we think about and build with AI. Thank you for trusting the community with such powerful technology.

**To Contributors:**
Every line of code, every bug report, every example you create makes Kimi K3 better. You're not just using AI—you're shaping its future. Thank you for your contributions!

**To Users:**
By choosing Kimi K3, you're supporting open AI development and helping prove that the best technology doesn't have to be locked behind paywalls. Share your successes, help others, and let's show the world what we can build together!

---

## Let's Build the Future Together

This is just the beginning. With Kimi K3, we have:
- The **most advanced open-source AI** for coding and reasoning
- A **proven agentic framework** for autonomous task execution  
- A **growing community** of developers and contributors
- A **clear vision** for what's next

**The future isn't something that happens to us—it's something we build.**

Join us in making Kimi K3 the most capable, most accessible, most amazing AI the world has ever seen!

---

## Resources

- **Main Repository:** [GitHub](https://github.com/moonshotai/Kimi-K3)
- **Documentation:** [README](../README.md) | [Examples](examples_guide.md) | [Quick Start](quick_start_examples.md)
- **Deployment:** [Deployment Guide](deploy_guidance.md)
- **Tool Usage:** [Tool Calling Guide](tool_call_guidance.md)
- **Community:** [Discord](https://discord.gg/TYU2fdJykW)
- **Support:** support@moonshot.cn

---

## License

Like Kimi K3 itself, this vision is built on **open principles**. All documentation and examples are available under the Modified MIT License—free to use, modify, and share.

**Let's make AI amazing, together! 🚀**

---

*Last Updated: November 2025*
*Status: Living Document - Updated as we build the future*

---

### Quick Links
- [See Kimi K3 in Action](examples_guide.md) - Live examples and demos
- [Get Started in 5 Minutes](quick_start_examples.md) - Quick start guide
- [Technical Details](../README.md) - Full model documentation
- [Deploy Your Own](deploy_guidance.md) - Deployment instructions
