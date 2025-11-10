#!/usr/bin/env python3
"""
Example 2: Game Development Workflow

This example shows how to create NPCs, dialogues, and quests
for a game using both the command system and Forge AI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kimi_k2 import CommandSystem, ForgeAI
from kimi_k2.forge_ai import DialogueTone, QuestType


def main():
    print("=" * 70)
    print("Example 2: Game Development Workflow")
    print("=" * 70)
    print()
    
    # Initialize systems
    cmd_sys = CommandSystem()
    forge = ForgeAI()
    
    print("Step 1: Set up game project structure")
    print("-" * 70)
    
    # Create game project directories
    commands = [
        "mkdir -p game_project/npcs",
        "mkdir -p game_project/quests",
        "mkdir -p game_project/dialogues",
        "mkdir -p game_project/locations",
        "cd game_project"
    ]
    
    for cmd in commands:
        cmd_sys.execute(cmd)
    
    print(cmd_sys.execute("ls"))
    print()
    
    print("Step 2: Create village NPCs")
    print("-" * 70)
    
    # Create NPCs for a village
    village_npcs = [
        {
            "name": "Elder Mara",
            "role": "village_elder",
            "personality": "wise, caring, and protective of the village",
            "background": "Led the village for 40 years, knows ancient secrets"
        },
        {
            "name": "Blacksmith Gorn",
            "role": "blacksmith",
            "personality": "gruff but kind-hearted, perfectionist",
            "background": "Master craftsman, trained in the capital city"
        },
        {
            "name": "Trader Lyssa",
            "role": "merchant",
            "personality": "cheerful, talkative, loves gossip",
            "background": "Travels between villages, knows all the news"
        },
        {
            "name": "Guard Captain Rex",
            "role": "guard_captain",
            "personality": "serious, disciplined, protective",
            "background": "Former soldier, now protects the village"
        }
    ]
    
    for npc_data in village_npcs:
        npc = forge.dialogue_generator.create_npc(
            name=npc_data["name"],
            role=npc_data["role"],
            personality=npc_data["personality"],
            background=npc_data["background"],
            relationships={}
        )
        
        # Save NPC profile
        npc_file = f"npcs/{npc_data['name'].lower().replace(' ', '_')}.json"
        npc_path = str(cmd_sys.vfs._resolve_path(npc_file))
        forge.dialogue_generator.save_npc(npc_data["name"], npc_path)
        
        print(f"Created: {npc.name} ({npc.role})")
    print()
    
    print("Step 3: Generate NPC dialogues")
    print("-" * 70)
    
    # Generate dialogues for different scenarios
    dialogue_scenarios = [
        ("Elder Mara", "Player arrives in village for first time", DialogueTone.FRIENDLY),
        ("Blacksmith Gorn", "Player asks about crafting a weapon", DialogueTone.NEUTRAL),
        ("Trader Lyssa", "Player inquires about recent events", DialogueTone.EXCITED),
        ("Guard Captain Rex", "Suspicious stranger spotted near village", DialogueTone.HOSTILE)
    ]
    
    cmd_sys.execute("cd dialogues")
    
    for npc_name, context, tone in dialogue_scenarios:
        dialogue = forge.dialogue_generator.generate_dialogue(npc_name, context, tone)
        
        # Save dialogue
        filename = f"{npc_name.lower().replace(' ', '_')}_{tone.value}.txt"
        filepath = cmd_sys.vfs._resolve_path(filename)
        filepath.write_text(dialogue)
        
        print(f"Generated dialogue for {npc_name} ({tone.value})")
    
    cmd_sys.execute("cd ..")
    print()
    
    print("Step 4: Create main quest chain")
    print("-" * 70)
    
    # Create a series of quests
    quest_data = [
        {
            "id": "village_intro",
            "title": "Welcome to Riverside",
            "type": QuestType.INVESTIGATE,
            "params": {"mystery": "the recent bandit attacks", "location": "the village"},
        },
        {
            "id": "gather_supplies",
            "title": "Helping Hand",
            "type": QuestType.FETCH,
            "params": {"item": "healing herbs", "location": "the nearby forest"},
        },
        {
            "id": "bandit_problem",
            "title": "Bandit Trouble",
            "type": QuestType.KILL,
            "params": {"count": 10, "enemy_type": "bandits", "location": "the mountain pass"},
        },
        {
            "id": "escort_merchant",
            "title": "Safe Passage",
            "type": QuestType.ESCORT,
            "params": {"npc": "Trader Lyssa", "destination": "the capital city"},
        }
    ]
    
    cmd_sys.execute("cd quests")
    created_quests = []
    
    for i, qdata in enumerate(quest_data):
        prereqs = [quest_data[i-1]["id"]] if i > 0 else []
        
        quest = forge.quest_scripter.create_quest(
            quest_id=qdata["id"],
            title=qdata["title"],
            quest_type=qdata["type"],
            params=qdata["params"],
            rewards={"gold": 100 * (i+1), "xp": 250 * (i+1)},
            prerequisites=prereqs
        )
        
        # Save individual quest
        quest_file = f"{qdata['id']}.json"
        quest_path = str(cmd_sys.vfs._resolve_path(quest_file))
        forge.quest_scripter.save_quest(qdata["id"], quest_path)
        
        created_quests.append(quest)
        print(f"Quest: {quest.title}")
        print(f"  Description: {quest.description}")
        print(f"  Rewards: {quest.rewards}")
        print()
    
    # Export all quests
    all_quests_path = str(cmd_sys.vfs._resolve_path("all_quests.json"))
    forge.quest_scripter.export_all_quests(all_quests_path)
    
    cmd_sys.execute("cd ..")
    print()
    
    print("Step 5: Create side quest chain")
    print("-" * 70)
    
    # Generate a thematic quest chain
    side_quests = forge.quest_scripter.generate_quest_chain(
        chain_name="ancient_ruins",
        num_quests=3,
        theme="Ancient"
    )
    
    for quest in side_quests:
        print(f"Side Quest: {quest.title}")
        print(f"  {quest.description}")
    print()
    
    print("Step 6: Create location descriptions")
    print("-" * 70)
    
    # Create location files
    locations = {
        "village_square.txt": """VILLAGE SQUARE
The heart of Riverside village, bustling with activity. The Elder's house
stands prominently on the north side, while the blacksmith's forge sends
sparks into the air on the east. The marketplace fills the center.""",
        
        "blacksmith.txt": """GORN'S FORGE
Heat radiates from the forge. Weapons and armor line the walls, each piece
showing masterful craftsmanship. The rhythmic sound of hammer on anvil
echoes throughout.""",
        
        "market.txt": """MARKET DISTRICT
Colorful stalls display various wares. Trader Lyssa's wagon sits in the
center, laden with exotic goods from distant lands. The air is filled with
the chatter of merchants and customers."""
    }
    
    cmd_sys.execute("cd locations")
    
    for filename, content in locations.items():
        filepath = cmd_sys.vfs._resolve_path(filename)
        filepath.write_text(content)
        print(f"Created location: {filename}")
    
    cmd_sys.execute("cd ..")
    print()
    
    print("Step 7: Create project README")
    print("-" * 70)
    
    readme = """# Riverside Village Game Project

## NPCs
- Elder Mara: Village leader
- Blacksmith Gorn: Master craftsman
- Trader Lyssa: Traveling merchant
- Guard Captain Rex: Village protector

## Main Quest Line
1. Welcome to Riverside
2. Helping Hand
3. Bandit Trouble
4. Safe Passage

## Side Quests
- Ancient Ruins quest chain (3 quests)

## Locations
- Village Square
- Gorn's Forge
- Market District

All game assets are organized in their respective folders.
"""
    
    readme_path = cmd_sys.vfs._resolve_path("README.md")
    readme_path.write_text(readme)
    print("Created project README")
    print()
    
    print("Step 8: View final project structure")
    print("-" * 70)
    
    print(cmd_sys.execute("pwd"))
    print()
    print("Project contents:")
    print(cmd_sys.execute("ls"))
    print()
    
    # Show details of each directory
    for directory in ["npcs", "quests", "dialogues", "locations"]:
        print(f"\n{directory}/:")
        cmd_sys.execute(f"cd {directory}")
        print(cmd_sys.execute("ls"))
        cmd_sys.execute("cd ..")
    
    print()
    print("=" * 70)
    print("Game Development Workflow Complete!")
    print("=" * 70)
    print()
    print("Created:")
    print(f"  - {len(village_npcs)} NPCs with profiles and dialogues")
    print(f"  - {len(quest_data)} main quests")
    print(f"  - {len(side_quests)} side quests")
    print(f"  - {len(locations)} location descriptions")
    print()


if __name__ == "__main__":
    main()
