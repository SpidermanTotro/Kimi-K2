"""
Example: Using the Forge AI Extension

This example demonstrates generative AI capabilities for writing,
NPC dialogues, and quest scripting.
"""

from kimi_k2.commands import ForgeAI


def main():
    """Run the Forge AI example."""
    print("=== Forge AI Extension Example ===\n")
    
    # Create the Forge AI
    forge = ForgeAI()
    
    # Writing generation
    print("1. Generating creative writing...\n")
    
    styles = ["narrative", "descriptive", "dialogue"]
    prompt = "A mysterious artifact discovered in an ancient temple"
    
    for style in styles:
        text = forge.generate_writing(prompt, style=style, max_length=150)
        print(f"   {style.capitalize()} style:")
        print(f"   {text}\n")
    
    # NPC dialogue generation
    print("2. Generating NPC dialogues...\n")
    
    personalities = ["friendly", "mysterious", "merchant"]
    
    for personality in personalities:
        npc_dialogue = forge.generate_npc_dialogue(
            f"{personality.capitalize()} NPC",
            personality=personality,
            context={"player_title": "brave adventurer"}
        )
        
        print(f"   {npc_dialogue['npc_name']} ({personality}):")
        for option in npc_dialogue['dialogue_options'][:2]:
            print(f"   - {option['text']}")
        print()
    
    # Quest generation
    print("3. Generating quests...\n")
    
    quest_types = ["fetch", "kill", "escort", "explore"]
    
    for quest_type in quest_types:
        quest = forge.generate_quest(
            quest_type=quest_type,
            difficulty="medium",
            location="Darkwood Forest"
        )
        
        print(f"   {quest['title']}")
        print(f"   Type: {quest['type']} | Difficulty: {quest['difficulty']}")
        print(f"   Objective: {quest['objective']}")
        print(f"   Rewards: {', '.join(f'{v} {k}' for k, v in quest['rewards'].items())}")
        print()
    
    # Quest dialogue stages
    print("4. Generating quest dialogues...\n")
    
    quest = forge.generate_quest(quest_type="fetch", difficulty="hard")
    
    print(f"   Quest: {quest['title']}\n")
    
    stages = ["intro", "progress", "complete"]
    for stage in stages:
        dialogue = forge.generate_quest_dialogue(quest, stage=stage)
        print(f"   {stage.capitalize()}: {dialogue}")
    print()
    
    # Narrative scene creation
    print("5. Creating narrative scenes...\n")
    
    moods = ["mysterious", "tense", "peaceful"]
    
    for mood in moods:
        scene = forge.create_narrative_scene(
            setting="The Grand Library",
            characters=["Scholar", "Apprentice", "Guardian"],
            mood=mood
        )
        
        print(f"   {mood.capitalize()} scene:")
        print(f"   {scene['description']}")
        print(f"   Characters: {', '.join(scene['characters'])}\n")
    
    # Custom templates
    print("6. Adding custom templates...\n")
    
    custom_template = "Greetings, {player_title}! I have heard tales of your {achievement}."
    forge.add_template("custom_greeting", custom_template)
    
    print("   Custom template added: 'custom_greeting'")
    print(f"   Template: {custom_template}\n")
    
    # Context management
    print("7. Using context variables...\n")
    
    forge.set_context("player_title", "Dragon Slayer")
    forge.set_context("achievement", "legendary deeds")
    forge.set_context("location", "Crystal Caverns")
    
    context = forge.get_context()
    print("   Context variables:")
    for key, value in context.items():
        print(f"   - {key}: {value}")
    
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
