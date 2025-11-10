#!/usr/bin/env python3
"""
Kimi-K2 Interactive CLI

Combined interface for Linux-style command system and Forge AI extension.
"""

import sys
import cmd
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kimi_k2 import CommandSystem, ForgeAI
from kimi_k2.forge_ai import DialogueTone, QuestType


class KimiK2CLI(cmd.Cmd):
    """Interactive CLI for Kimi-K2 system"""
    
    intro = """
╔══════════════════════════════════════════════════════════════════╗
║                  Kimi-K2 Interactive System                      ║
║  Linux Command System + Forge AI Extension                       ║
╚══════════════════════════════════════════════════════════════════╝

Type 'help' or '?' to list commands.
Type 'help <command>' for detailed help on a command.
Type 'exit' or 'quit' to leave the CLI.
"""
    
    prompt = "kimi-k2> "
    
    def __init__(self):
        super().__init__()
        self.cmd_system = CommandSystem()
        self.forge_ai = ForgeAI()
        self.mode = "command"  # command or forge
    
    def do_mode(self, arg):
        """Switch between command and forge modes.
        
        Usage: mode [command|forge]
        """
        if not arg:
            print(f"Current mode: {self.mode}")
            return
        
        if arg in ["command", "forge"]:
            self.mode = arg
            print(f"Switched to {arg} mode")
            self.update_prompt()
        else:
            print("Invalid mode. Use 'command' or 'forge'")
    
    def update_prompt(self):
        """Update prompt based on current mode"""
        if self.mode == "command":
            current_dir = self.cmd_system.vfs.get_current_dir()
            self.prompt = f"kimi-k2:{current_dir}$ "
        else:
            self.prompt = "kimi-k2[forge]> "
    
    def default(self, line):
        """Handle commands not defined in CLI"""
        if self.mode == "command":
            # Execute as Linux command
            output = self.cmd_system.execute(line)
            if output:
                print(output)
            self.update_prompt()
        else:
            print(f"Unknown command: {line}")
    
    # Forge AI Commands
    
    def do_book_create(self, arg):
        """Create a new book outline.
        
        Usage: book_create <title> <author> <genre> <num_chapters>
        Example: book_create "My Novel" "John Doe" Fantasy 10
        """
        parts = arg.split()
        if len(parts) < 4:
            print("Usage: book_create <title> <author> <genre> <num_chapters>")
            return
        
        try:
            title = parts[0].strip('"')
            author = parts[1].strip('"')
            genre = parts[2]
            num_chapters = int(parts[3])
            
            outline = self.forge_ai.book_writer.create_outline(title, author, genre, num_chapters)
            print(f"Created outline for '{title}' with {num_chapters} chapters")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_book_chapter(self, arg):
        """Update or generate chapter content.
        
        Usage: book_chapter <chapter_num> [title] [summary]
        Example: book_chapter 1 "The Beginning" "Our hero starts their journey"
        """
        parts = arg.split(None, 2)
        if len(parts) < 1:
            print("Usage: book_chapter <chapter_num> [title] [summary]")
            return
        
        try:
            chapter_num = int(parts[0])
            
            if len(parts) == 1:
                # Generate content
                content = self.forge_ai.book_writer.generate_chapter_content(chapter_num)
                print(content)
            elif len(parts) == 3:
                # Update outline
                title = parts[1].strip('"')
                summary = parts[2].strip('"')
                success = self.forge_ai.book_writer.update_chapter_outline(chapter_num, title, summary)
                if success:
                    print(f"Updated chapter {chapter_num}")
                else:
                    print("Failed to update chapter")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_book_export(self, arg):
        """Export book to file.
        
        Usage: book_export <filepath>
        Example: book_export /path/to/book.md
        """
        if not arg:
            print("Usage: book_export <filepath>")
            return
        
        content = self.forge_ai.book_writer.export_book()
        
        # Save using command system
        filepath = arg.strip()
        target = self.cmd_system.vfs._resolve_path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        print(f"Book exported to {filepath}")
    
    def do_npc_create(self, arg):
        """Create a new NPC.
        
        Usage: npc_create <name> <role> <personality> <background>
        Example: npc_create "Aldric" "merchant" "greedy and cunning" "Former adventurer"
        """
        parts = arg.split(None, 3)
        if len(parts) < 4:
            print("Usage: npc_create <name> <role> <personality> <background>")
            return
        
        name = parts[0].strip('"')
        role = parts[1].strip('"')
        personality = parts[2].strip('"')
        background = parts[3].strip('"')
        
        npc = self.forge_ai.dialogue_generator.create_npc(name, role, personality, background)
        print(f"Created NPC: {npc.name} ({npc.role})")
    
    def do_npc_dialogue(self, arg):
        """Generate NPC dialogue.
        
        Usage: npc_dialogue <npc_name> <context> [tone]
        Example: npc_dialogue Aldric "player wants to buy sword" friendly
        """
        parts = arg.split(None, 2)
        if len(parts) < 2:
            print("Usage: npc_dialogue <npc_name> <context> [tone]")
            return
        
        npc_name = parts[0]
        context = parts[1].strip('"')
        tone = DialogueTone.NEUTRAL
        
        if len(parts) > 2:
            try:
                tone = DialogueTone(parts[2].lower())
            except ValueError:
                print(f"Invalid tone. Using neutral. Valid tones: {[t.value for t in DialogueTone]}")
        
        dialogue = self.forge_ai.dialogue_generator.generate_dialogue(npc_name, context, tone)
        print(dialogue)
    
    def do_quest_create(self, arg):
        """Create a new quest.
        
        Usage: quest_create <quest_id> <title> <type>
        Example: quest_create quest_001 "Retrieve Lost Sword" fetch
        """
        parts = arg.split(None, 2)
        if len(parts) < 3:
            print("Usage: quest_create <quest_id> <title> <type>")
            print(f"Available types: {[t.value for t in QuestType]}")
            return
        
        quest_id = parts[0]
        title = parts[1].strip('"')
        quest_type_str = parts[2]
        
        try:
            quest_type = QuestType(quest_type_str.lower())
            
            # Example parameters
            params = {"item": "Ancient Sword", "location": "Dark Cave"}
            if quest_type == QuestType.KILL:
                params = {"count": 5, "enemy_type": "Goblins", "location": "Forest"}
            elif quest_type == QuestType.ESCORT:
                params = {"npc": "Princess", "destination": "Castle"}
            elif quest_type == QuestType.INVESTIGATE:
                params = {"mystery": "Missing Villagers", "location": "Abandoned Mine"}
            
            quest = self.forge_ai.quest_scripter.create_quest(quest_id, title, quest_type, params)
            print(f"Created quest: {quest.title}")
            print(f"Description: {quest.description}")
            print(f"Objectives: {', '.join(quest.objectives)}")
        except ValueError:
            print(f"Invalid quest type. Available: {[t.value for t in QuestType]}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_quest_chain(self, arg):
        """Create a quest chain.
        
        Usage: quest_chain <chain_name> <num_quests> <theme>
        Example: quest_chain dragon_slayer 5 Dragon
        """
        parts = arg.split()
        if len(parts) < 3:
            print("Usage: quest_chain <chain_name> <num_quests> <theme>")
            return
        
        chain_name = parts[0]
        try:
            num_quests = int(parts[1])
            theme = parts[2]
            
            quests = self.forge_ai.quest_scripter.generate_quest_chain(chain_name, num_quests, theme)
            print(f"Created quest chain '{chain_name}' with {num_quests} quests:")
            for quest in quests:
                print(f"  - {quest.title}")
        except Exception as e:
            print(f"Error: {e}")
    
    # System commands
    
    def do_script(self, arg):
        """Execute a script file.
        
        Usage: script <filepath>
        """
        if not arg:
            print("Usage: script <filepath>")
            return
        
        outputs = self.cmd_system.execute_script(arg)
        for output in outputs:
            print(output)
    
    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the CLI"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Exit on EOF (Ctrl-D)"""
        print()
        return self.do_exit(arg)


def main():
    """Main entry point"""
    cli = KimiK2CLI()
    cli.cmdloop()


if __name__ == "__main__":
    main()
