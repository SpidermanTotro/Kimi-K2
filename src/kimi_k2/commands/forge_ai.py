"""Forge AI Extension for generative tasks"""

from typing import List, Dict, Any, Optional
import random


class ForgeAI:
    """
    Forge-like AI extension for generative tasks such as writing,
    NPC dialogues, and quest scripting.
    """

    def __init__(self):
        """Initialize the Forge AI extension."""
        self.templates = {
            "npc_dialogue": [
                "Greetings, traveler! {greeting}",
                "Well met! {greeting}",
                "Ah, {player_title}, {greeting}",
            ],
            "quest_intro": [
                "I have a task for you, {player_title}. {task}",
                "Listen well, {player_title}. {task}",
                "There's trouble afoot. {task}",
            ],
            "quest_complete": [
                "Well done, {player_title}! {reward}",
                "Excellent work! {reward}",
                "You've succeeded! {reward}",
            ],
        }
        self.context = {}

    def generate_writing(
        self, prompt: str, style: str = "narrative", max_length: int = 200
    ) -> str:
        """
        Generate creative writing based on a prompt.

        Args:
            prompt: Writing prompt or topic
            style: Writing style (narrative, descriptive, dialogue, etc.)
            max_length: Maximum length of generated text

        Returns:
            Generated text
        """
        # Placeholder implementation - in a real system this would use an LLM
        style_prefixes = {
            "narrative": "Once upon a time, ",
            "descriptive": "The scene unfolds before you: ",
            "dialogue": 'The character speaks: "',
            "technical": "From a technical perspective, ",
        }

        prefix = style_prefixes.get(style, "")
        generated = f"{prefix}{prompt}"

        # Truncate to max_length
        if len(generated) > max_length:
            generated = generated[:max_length] + "..."

        return generated

    def generate_npc_dialogue(
        self,
        npc_name: str,
        personality: str = "friendly",
        context: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate NPC dialogue based on personality and context.

        Args:
            npc_name: Name of the NPC
            personality: Personality type (friendly, hostile, mysterious, etc.)
            context: Additional context for dialogue generation

        Returns:
            Dictionary containing dialogue options and metadata
        """
        ctx = context or {}
        ctx.setdefault("player_title", "adventurer")

        personality_greetings = {
            "friendly": [
                "It's wonderful to see you!",
                "How can I help you today?",
                "What brings you to these parts?",
            ],
            "hostile": [
                "What do you want?",
                "State your business quickly.",
                "You're not welcome here.",
            ],
            "mysterious": [
                "The winds of fate have brought you here...",
                "I've been expecting someone like you.",
                "Interesting... very interesting.",
            ],
            "merchant": [
                "Looking to buy or sell?",
                "I have the finest wares!",
                "Everything has a price, friend.",
            ],
        }

        greetings = personality_greetings.get(
            personality, personality_greetings["friendly"]
        )

        dialogue_options = []
        for i, greeting_template in enumerate(self.templates["npc_dialogue"][:3]):
            greeting_text = random.choice(greetings)
            dialogue = greeting_template.format(greeting=greeting_text, **ctx)
            dialogue_options.append(
                {"id": i, "text": dialogue, "personality": personality}
            )

        return {
            "npc_name": npc_name,
            "personality": personality,
            "dialogue_options": dialogue_options,
            "context": ctx,
        }

    def generate_quest(
        self,
        quest_type: str = "fetch",
        difficulty: str = "medium",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a quest with objectives and rewards.

        Args:
            quest_type: Type of quest (fetch, kill, escort, explore, etc.)
            difficulty: Difficulty level (easy, medium, hard)
            location: Quest location

        Returns:
            Dictionary containing quest details
        """
        quest_templates = {
            "fetch": {
                "title": "Retrieve the {item}",
                "objective": "Find and bring back the {item} from {location}",
                "reward_type": "item",
            },
            "kill": {
                "title": "Defeat the {enemy}",
                "objective": "Eliminate {count} {enemy} in {location}",
                "reward_type": "experience",
            },
            "escort": {
                "title": "Escort {npc}",
                "objective": "Safely guide {npc} to {location}",
                "reward_type": "gold",
            },
            "explore": {
                "title": "Explore {location}",
                "objective": "Discover the secrets of {location}",
                "reward_type": "item",
            },
        }

        template = quest_templates.get(quest_type, quest_templates["fetch"])

        # Generate quest parameters based on difficulty
        difficulty_params = {
            "easy": {"count": 3, "gold": 50, "experience": 100},
            "medium": {"count": 7, "gold": 150, "experience": 300},
            "hard": {"count": 15, "gold": 500, "experience": 1000},
        }

        params = difficulty_params.get(difficulty, difficulty_params["medium"])

        # Fill in quest details
        quest_details = {
            "item": random.choice(
                ["Ancient Relic", "Magic Scroll", "Rare Herb", "Lost Artifact"]
            ),
            "enemy": random.choice(["Goblin", "Skeleton", "Bandit", "Wolf"]),
            "npc": random.choice(["Merchant", "Pilgrim", "Scholar", "Child"]),
            "location": location
            or random.choice(["Dark Forest", "Ancient Ruins", "Mountain Pass", "Cave"]),
            "count": params["count"],
        }

        quest = {
            "title": template["title"].format(**quest_details),
            "type": quest_type,
            "difficulty": difficulty,
            "objective": template["objective"].format(**quest_details),
            "location": quest_details["location"],
            "rewards": {},
        }

        # Add rewards based on type and difficulty
        if template["reward_type"] == "gold":
            quest["rewards"]["gold"] = params["gold"]
        elif template["reward_type"] == "experience":
            quest["rewards"]["experience"] = params["experience"]
        elif template["reward_type"] == "item":
            quest["rewards"]["item"] = quest_details["item"]
            quest["rewards"]["gold"] = params["gold"] // 2

        return quest

    def generate_quest_dialogue(
        self, quest: Dict[str, Any], stage: str = "intro"
    ) -> str:
        """
        Generate dialogue for different quest stages.

        Args:
            quest: Quest dictionary from generate_quest
            stage: Quest stage (intro, progress, complete)

        Returns:
            Generated dialogue text
        """
        ctx = {"player_title": "adventurer", "task": quest.get("objective", "")}

        if stage == "intro":
            template = random.choice(self.templates["quest_intro"])
            return template.format(**ctx)
        elif stage == "complete":
            reward_text = ", ".join(
                f"{v} {k}" for k, v in quest.get("rewards", {}).items()
            )
            ctx["reward"] = f"Here is your reward: {reward_text}"
            template = random.choice(self.templates["quest_complete"])
            return template.format(**ctx)
        elif stage == "progress":
            return f"How goes your task, {ctx['player_title']}?"
        else:
            return "..."

    def create_narrative_scene(
        self, setting: str, characters: List[str], mood: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Create a narrative scene with setting, characters, and atmosphere.

        Args:
            setting: Scene setting/location
            characters: List of character names present
            mood: Scene mood (tense, peaceful, mysterious, etc.)

        Returns:
            Dictionary containing scene details
        """
        mood_descriptions = {
            "tense": "The air is thick with tension as",
            "peaceful": "A sense of calm pervades the scene as",
            "mysterious": "An aura of mystery surrounds the area as",
            "chaotic": "Chaos reigns as",
            "somber": "A somber atmosphere fills the space as",
        }

        mood_desc = mood_descriptions.get(mood, "The scene unfolds as")

        scene = {
            "setting": setting,
            "characters": characters,
            "mood": mood,
            "description": f"{mood_desc} {', '.join(characters)} gather at {setting}.",
            "atmosphere": mood,
        }

        return scene

    def add_template(
        self, template_type: str, template: str
    ) -> bool:
        """
        Add a custom template for dialogue or quest generation.

        Args:
            template_type: Type of template (npc_dialogue, quest_intro, etc.)
            template: Template string with placeholders

        Returns:
            True if template was added successfully
        """
        if template_type not in self.templates:
            self.templates[template_type] = []

        self.templates[template_type].append(template)
        return True

    def set_context(self, key: str, value: str) -> None:
        """
        Set a context variable for template generation.

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value

    def get_context(self) -> Dict[str, str]:
        """Get current context variables."""
        return self.context.copy()
