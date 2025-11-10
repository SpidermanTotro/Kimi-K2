#!/usr/bin/env python3
"""
Example 1: Book Project Workflow

This example demonstrates how to use the Linux command system
to set up a book project and then use the Forge AI to populate it.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kimi_k2 import CommandSystem, ForgeAI


def main():
    print("=" * 70)
    print("Example 1: Book Project Workflow")
    print("=" * 70)
    print()
    
    # Initialize systems
    cmd_sys = CommandSystem()
    forge = ForgeAI()
    
    print("Step 1: Create project directory structure using Linux commands")
    print("-" * 70)
    
    # Create directory structure
    cmd_sys.execute("mkdir -p projects/fantasy_novel")
    cmd_sys.execute("cd projects/fantasy_novel")
    cmd_sys.execute("mkdir -p chapters outlines npcs quests")
    
    print(cmd_sys.execute("ls"))
    print()
    
    print("Step 2: Create book outline using Forge AI")
    print("-" * 70)
    
    # Create book outline
    outline = forge.book_writer.create_outline(
        title="The Dragon's Prophecy",
        author="Kimi AI",
        genre="Fantasy",
        num_chapters=5
    )
    
    print(f"Created outline for: {outline.title}")
    print(f"Author: {outline.author}")
    print(f"Genre: {outline.genre}")
    print(f"Chapters: {len(outline.chapters)}")
    print()
    
    print("Step 3: Customize chapter outlines")
    print("-" * 70)
    
    # Update chapter details
    chapters_info = [
        ("The Awakening", "A young mage discovers their hidden powers"),
        ("The Ancient Tome", "Finding a mysterious book in the forbidden library"),
        ("The Dragon's Warning", "A dragon appears with a dire prophecy"),
        ("Gathering Allies", "Assembling a team to face the coming darkness"),
        ("The Final Stand", "Confronting the ancient evil"),
    ]
    
    for i, (title, summary) in enumerate(chapters_info, 1):
        forge.book_writer.update_chapter_outline(i, title, summary)
        print(f"Chapter {i}: {title}")
    print()
    
    print("Step 4: Generate chapter content")
    print("-" * 70)
    
    # Generate content for first chapter
    content = forge.book_writer.generate_chapter_content(1, word_count=500)
    
    # Save to file using command system
    cmd_sys.execute("cd chapters")
    filepath = cmd_sys.vfs._resolve_path("chapter_01.md")
    filepath.write_text(content)
    print("Generated and saved Chapter 1")
    print()
    
    print("Step 5: Save outline to file")
    print("-" * 70)
    
    cmd_sys.execute("cd ../outlines")
    outline_path = str(cmd_sys.vfs._resolve_path("book_outline.json"))
    forge.book_writer.save_outline(outline_path)
    print("Saved outline to:", outline_path)
    print()
    
    print("Step 6: Create supporting NPCs")
    print("-" * 70)
    
    # Create NPCs for the story
    npcs = [
        ("Aldric", "wizard", "wise and patient", "Ancient guardian of magical knowledge"),
        ("Sera", "warrior", "brave and loyal", "Skilled fighter seeking redemption"),
        ("Thorne", "merchant", "cunning but helpful", "Knows secrets of the ancient world"),
    ]
    
    for name, role, personality, background in npcs:
        npc = forge.dialogue_generator.create_npc(name, role, personality, background)
        
        # Save NPC profile
        cmd_sys.execute("cd ../npcs")
        npc_path = str(cmd_sys.vfs._resolve_path(f"{name.lower()}.json"))
        forge.dialogue_generator.save_npc(name, npc_path)
        print(f"Created NPC: {name} ({role})")
    print()
    
    print("Step 7: Create quest chain for the story")
    print("-" * 70)
    
    # Generate quest chain
    quests = forge.quest_scripter.generate_quest_chain(
        chain_name="dragon_prophecy",
        num_quests=5,
        theme="Dragon"
    )
    
    # Save quests
    cmd_sys.execute("cd ../quests")
    quests_path = str(cmd_sys.vfs._resolve_path("quest_chain.json"))
    forge.quest_scripter.export_all_quests(quests_path)
    
    for quest in quests:
        print(f"  {quest.title}: {quest.description}")
    print()
    
    print("Step 8: View final project structure")
    print("-" * 70)
    
    cmd_sys.execute("cd ..")
    print(cmd_sys.execute("pwd"))
    print(cmd_sys.execute("ls"))
    print()
    
    print("=" * 70)
    print("Workflow Complete!")
    print("=" * 70)
    print()
    print("The project structure has been created with:")
    print("  - Book outline with 5 chapters")
    print("  - Generated content for Chapter 1")
    print("  - 3 NPC profiles for the story")
    print("  - Quest chain with 5 quests")
    print()
    print("All files are organized in the virtual file system")
    print("accessible through the command system.")


if __name__ == "__main__":
    main()
