# Kimi-K2 Extensions Usage Guide

This guide covers the Linux-style Command System and Forge AI Extension added to Kimi-K2.

## Table of Contents
1. [Installation](#installation)
2. [Linux Command System](#linux-command-system)
3. [Forge AI Extension](#forge-ai-extension)
4. [Integration Examples](#integration-examples)
5. [CLI Interface](#cli-interface)
6. [API Reference](#api-reference)

## Installation

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Install dependencies (optional, for testing)
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_linux_commands.py -v

# Run with coverage
pytest tests/ --cov=src/kimi_k2 --cov-report=html
```

## Linux Command System

The Linux Command System provides a virtual file system with familiar Linux commands.

### Basic Usage

```python
from kimi_k2 import CommandSystem

# Create command system instance
cmd = CommandSystem()

# Execute commands
cmd.execute("mkdir projects")
cmd.execute("cd projects")
cmd.execute("touch README.md")
cmd.execute("ls")
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ls [path]` | List directory contents | `ls`, `ls /path` |
| `cd [path]` | Change directory | `cd projects` |
| `pwd` | Print working directory | `pwd` |
| `mkdir <path>` | Create directory | `mkdir new_dir` |
| `rm [-rf] <path>` | Remove files/directories | `rm file.txt`, `rm -rf dir/` |
| `cat <file>` | Display file contents | `cat file.txt` |
| `echo <text>` | Echo text (supports redirect) | `echo "text" > file.txt` |
| `touch <file>` | Create empty file | `touch new_file.txt` |
| `cp [-r] <src> <dest>` | Copy files/directories | `cp file.txt backup.txt` |
| `mv <src> <dest>` | Move/rename files | `mv old.txt new.txt` |
| `alias <name>=<cmd>` | Create command alias | `alias ll='ls -la'` |
| `help` | Show help | `help` |

### Aliasing

Create shortcuts for frequently used commands:

```python
# Create alias
cmd.execute("alias ll='ls -la'")

# Use alias
cmd.execute("ll")

# List all aliases
cmd.execute("alias")
```

### Scripting

Execute multiple commands from a script file:

```python
# Create a script
cmd.execute("echo 'mkdir project' > setup.sh")
cmd.execute("echo 'cd project' >> setup.sh")
cmd.execute("echo 'touch README.md' >> setup.sh")

# Execute the script
outputs = cmd.execute_script("setup.sh")
```

## Forge AI Extension

The Forge AI Extension provides creative tools for book writing, NPC dialogue, and quest scripting.

### Book Writing

#### Creating a Book Outline

```python
from kimi_k2 import ForgeAI

forge = ForgeAI()
writer = forge.get_book_writer()

# Create outline
outline = writer.create_outline(
    title="The Dragon's Tale",
    author="AI Writer",
    genre="Fantasy",
    num_chapters=10
)

# Update chapter details
writer.update_chapter_outline(
    chapter_num=1,
    title="The Awakening",
    summary="The hero discovers their magical powers"
)

# Generate chapter content
content = writer.generate_chapter_content(
    chapter_num=1,
    word_count=1000
)

# Export complete book
book_text = writer.export_book(format="markdown")
```

#### Saving and Loading

```python
# Save outline
writer.save_outline("book_outline.json")

# Load outline
writer.load_outline("book_outline.json")
```

### NPC Dialogue Generation

#### Creating NPCs

```python
from kimi_k2.forge_ai import DialogueTone

dialogue_gen = forge.get_dialogue_generator()

# Create an NPC
npc = dialogue_gen.create_npc(
    name="Aldric the Wise",
    role="wizard",
    personality="wise, patient, mysterious",
    background="Ancient guardian of magical knowledge",
    relationships={"player": "mentor"}
)
```

#### Generating Dialogue

```python
# Generate context-aware dialogue
dialogue = dialogue_gen.generate_dialogue(
    npc_name="Aldric the Wise",
    context="player asks about ancient prophecy",
    tone=DialogueTone.MYSTERIOUS
)

# Generate full conversation
conversation = dialogue_gen.generate_conversation(
    npc_name="Aldric the Wise",
    player_lines=[
        "I seek knowledge of the ancient ways",
        "Can you teach me magic?",
        "What dangers lie ahead?"
    ]
)
```

#### Available Dialogue Tones

- `FRIENDLY` - Warm and welcoming
- `HOSTILE` - Aggressive or unfriendly
- `NEUTRAL` - Professional and balanced
- `MYSTERIOUS` - Cryptic and enigmatic
- `FEARFUL` - Scared or worried
- `EXCITED` - Enthusiastic and energetic

### Quest Scripting

#### Creating Quests

```python
from kimi_k2.forge_ai import QuestType

quest_scripter = forge.get_quest_scripter()

# Create a fetch quest
quest = quest_scripter.create_quest(
    quest_id="ancient_sword",
    title="Retrieve the Ancient Sword",
    quest_type=QuestType.FETCH,
    params={
        "item": "Ancient Sword of Light",
        "location": "Temple of Shadows"
    },
    rewards={"gold": 500, "xp": 1000},
    prerequisites=[]
)
```

#### Quest Types

- `FETCH` - Retrieve items
- `KILL` - Defeat enemies
- `ESCORT` - Protect and guide NPCs
- `INVESTIGATE` - Gather information
- `DELIVERY` - Transport items
- `PUZZLE` - Solve mysteries

#### Creating Quest Chains

```python
# Generate related quest sequence
quest_chain = quest_scripter.generate_quest_chain(
    chain_name="dragon_slayer",
    num_quests=5,
    theme="Dragon"
)

# Each quest automatically links to the previous one
for quest in quest_chain:
    print(f"{quest.title}: {quest.description}")
```

#### Custom Quests

```python
# Create quest without template
custom_quest = quest_scripter.create_custom_quest(
    quest_id="unique_quest",
    title="The Cursed Artifact",
    quest_type="mystery",
    description="Investigate the source of the village curse",
    objectives=[
        "Interview the village elder",
        "Search the old cemetery",
        "Confront the dark mage"
    ],
    rewards={"gold": 1000, "reputation": 50}
)
```

## Integration Examples

### Example 1: Book Project Setup

Combine command system and AI to create a complete book project:

```python
from kimi_k2 import CommandSystem, ForgeAI

cmd = CommandSystem()
forge = ForgeAI()

# Set up project structure
cmd.execute("mkdir -p book_project/chapters")
cmd.execute("mkdir -p book_project/outlines")
cmd.execute("cd book_project")

# Create book outline
outline = forge.book_writer.create_outline(
    "My Novel", "Author Name", "Fantasy", 10
)

# Save outline using command system
outline_path = cmd.vfs._resolve_path("outlines/outline.json")
forge.book_writer.save_outline(str(outline_path))

# Generate and save chapters
for i in range(1, 6):
    content = forge.book_writer.generate_chapter_content(i)
    chapter_path = cmd.vfs._resolve_path(f"chapters/chapter_{i:02d}.md")
    chapter_path.write_text(content)

# List created files
print(cmd.execute("ls -R"))
```

### Example 2: Game Development Workflow

Create NPCs, dialogues, and quests for a game:

```python
# Set up game project
cmd.execute("mkdir -p game/npcs game/quests game/dialogues")
cmd.execute("cd game")

# Create NPCs
npcs = [
    ("Merchant Bob", "merchant", "friendly", "Sells rare items"),
    ("Guard Captain", "guard", "serious", "Protects the city"),
]

for name, role, personality, background in npcs:
    npc = forge.dialogue_generator.create_npc(
        name, role, personality, background
    )
    
    # Generate dialogue
    dialogue = forge.dialogue_generator.generate_dialogue(
        name, "greeting", DialogueTone.FRIENDLY
    )
    
    # Save files
    npc_file = cmd.vfs._resolve_path(f"npcs/{name.replace(' ', '_')}.json")
    forge.dialogue_generator.save_npc(name, str(npc_file))

# Create quest chain
quests = forge.quest_scripter.generate_quest_chain(
    "main_story", 5, "Kingdom"
)

quest_file = cmd.vfs._resolve_path("quests/main_chain.json")
forge.quest_scripter.export_all_quests(str(quest_file))
```

## CLI Interface

### Starting the CLI

```bash
python src/kimi_k2/cli.py
```

### CLI Commands

The CLI supports both modes:

#### Command Mode
In command mode, all Linux commands work directly:
```
kimi-k2:/$ mkdir test
kimi-k2:/$ cd test
kimi-k2:/test$ ls
```

#### Forge Mode
Switch to forge mode for AI features:
```
kimi-k2> mode forge
kimi-k2[forge]> book_create "My Book" "Author" Fantasy 5
kimi-k2[forge]> npc_create "Wizard" "mage" "wise" "Ancient wizard"
kimi-k2[forge]> quest_create q1 "First Quest" fetch
```

### CLI-Specific Commands

| Command | Description |
|---------|-------------|
| `mode [command\|forge]` | Switch between modes |
| `book_create <title> <author> <genre> <chapters>` | Create book outline |
| `book_chapter <num> [title] [summary]` | Update/generate chapter |
| `book_export <path>` | Export book to file |
| `npc_create <name> <role> <personality> <bg>` | Create NPC |
| `npc_dialogue <name> <context> [tone]` | Generate dialogue |
| `quest_create <id> <title> <type>` | Create quest |
| `quest_chain <name> <num> <theme>` | Create quest chain |
| `script <file>` | Execute command script |
| `exit` or `quit` | Exit CLI |

## API Reference

### CommandSystem

```python
class CommandSystem:
    def __init__(self, vfs: Optional[VirtualFileSystem] = None)
    def execute(self, command_line: str) -> str
    def execute_script(self, script_path: str) -> List[str]
```

### ForgeAI

```python
class ForgeAI:
    def get_book_writer() -> BookWriter
    def get_dialogue_generator() -> DialogueGenerator
    def get_quest_scripter() -> QuestScripter
```

### BookWriter

```python
class BookWriter:
    def create_outline(title, author, genre, num_chapters) -> BookOutline
    def update_chapter_outline(chapter_num, title, summary) -> bool
    def generate_chapter_content(chapter_num, word_count) -> str
    def export_book(format: str) -> str
    def save_outline(filepath: str) -> bool
    def load_outline(filepath: str) -> bool
```

### DialogueGenerator

```python
class DialogueGenerator:
    def create_npc(name, role, personality, background, relationships) -> NPCProfile
    def generate_dialogue(npc_name, context, tone) -> str
    def generate_conversation(npc_name, player_lines) -> List[Dict]
    def save_npc(npc_name, filepath) -> bool
    def load_npc(filepath) -> Optional[NPCProfile]
```

### QuestScripter

```python
class QuestScripter:
    def create_quest(quest_id, title, quest_type, params, rewards, prerequisites) -> Quest
    def create_custom_quest(quest_id, title, quest_type, description, objectives, rewards) -> Quest
    def generate_quest_chain(chain_name, num_quests, theme) -> List[Quest]
    def save_quest(quest_id, filepath) -> bool
    def load_quest(filepath) -> Optional[Quest]
    def export_all_quests(filepath) -> bool
```

## Tips and Best Practices

1. **Organize Projects**: Use the command system to create clear directory structures
2. **Save Frequently**: Save outlines, NPCs, and quests to JSON files for persistence
3. **Use Templates**: Quest templates provide consistency across similar quests
4. **Leverage Integration**: Combine both systems for powerful workflows
5. **Test Iteratively**: Use the CLI for quick testing and prototyping

## Troubleshooting

### Common Issues

**Q: Files not persisting between sessions**
A: The virtual file system is temporary by default. Save important content to actual files using the save methods.

**Q: Commands not found**
A: Ensure you're in the correct mode (command vs forge) in the CLI.

**Q: Path not found errors**
A: Remember paths in the VFS are isolated. Use absolute paths from root (/) or relative to current directory.

## Further Development

This implementation provides a foundation for creative AI-driven development. Future enhancements could include:

- Integration with actual Kimi-K2 AI model for content generation
- Advanced dialogue trees with branching conversations
- Quest validation and dependency checking
- Export to game engine formats
- Collaborative editing features

For more information, see the example scripts in the `examples/` directory.
