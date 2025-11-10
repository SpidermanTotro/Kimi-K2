"""Tests for Forge AI Extension"""

import pytest
from kimi_k2.commands import ForgeAI


class TestForgeAI:
    """Test suite for ForgeAI class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.forge = ForgeAI()

    def test_initialization(self):
        """Test Forge AI initialization."""
        assert self.forge is not None
        assert len(self.forge.templates) > 0

    def test_generate_writing(self):
        """Test writing generation."""
        result = self.forge.generate_writing("A dark forest", style="narrative")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "dark forest" in result.lower()

    def test_generate_writing_styles(self):
        """Test different writing styles."""
        styles = ["narrative", "descriptive", "dialogue", "technical"]
        
        for style in styles:
            result = self.forge.generate_writing("test prompt", style=style)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_generate_writing_max_length(self):
        """Test writing generation with max length."""
        result = self.forge.generate_writing("test prompt", max_length=50)
        assert len(result) <= 50

    def test_generate_npc_dialogue_friendly(self):
        """Test friendly NPC dialogue generation."""
        result = self.forge.generate_npc_dialogue("Bob", personality="friendly")
        
        assert result["npc_name"] == "Bob"
        assert result["personality"] == "friendly"
        assert len(result["dialogue_options"]) > 0
        
        for option in result["dialogue_options"]:
            assert "id" in option
            assert "text" in option
            assert "personality" in option

    def test_generate_npc_dialogue_personalities(self):
        """Test different NPC personalities."""
        personalities = ["friendly", "hostile", "mysterious", "merchant"]
        
        for personality in personalities:
            result = self.forge.generate_npc_dialogue(
                "TestNPC", personality=personality
            )
            assert result["personality"] == personality
            assert len(result["dialogue_options"]) > 0

    def test_generate_npc_dialogue_with_context(self):
        """Test NPC dialogue with custom context."""
        context = {"player_title": "hero"}
        result = self.forge.generate_npc_dialogue(
            "NPC", personality="friendly", context=context
        )
        
        # Check that context was used
        dialogue_text = " ".join(
            opt["text"] for opt in result["dialogue_options"]
        )
        assert "hero" in dialogue_text

    def test_generate_quest_fetch(self):
        """Test fetch quest generation."""
        quest = self.forge.generate_quest(quest_type="fetch", difficulty="medium")
        
        assert quest["type"] == "fetch"
        assert quest["difficulty"] == "medium"
        assert "title" in quest
        assert "objective" in quest
        assert "rewards" in quest

    def test_generate_quest_types(self):
        """Test different quest types."""
        quest_types = ["fetch", "kill", "escort", "explore"]
        
        for quest_type in quest_types:
            quest = self.forge.generate_quest(quest_type=quest_type)
            assert quest["type"] == quest_type
            assert len(quest["title"]) > 0
            assert len(quest["objective"]) > 0

    def test_generate_quest_difficulties(self):
        """Test different quest difficulties."""
        difficulties = ["easy", "medium", "hard"]
        
        for difficulty in difficulties:
            quest = self.forge.generate_quest(
                quest_type="kill", difficulty=difficulty
            )
            assert quest["difficulty"] == difficulty
            assert "rewards" in quest

    def test_generate_quest_with_location(self):
        """Test quest generation with custom location."""
        quest = self.forge.generate_quest(
            quest_type="explore", location="Mystic Cave"
        )
        assert quest["location"] == "Mystic Cave"
        assert "Mystic Cave" in quest["objective"]

    def test_generate_quest_dialogue_intro(self):
        """Test quest introduction dialogue."""
        quest = self.forge.generate_quest(quest_type="fetch")
        dialogue = self.forge.generate_quest_dialogue(quest, stage="intro")
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0

    def test_generate_quest_dialogue_complete(self):
        """Test quest completion dialogue."""
        quest = self.forge.generate_quest(quest_type="fetch")
        dialogue = self.forge.generate_quest_dialogue(quest, stage="complete")
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0
        assert "reward" in dialogue.lower()

    def test_generate_quest_dialogue_progress(self):
        """Test quest progress dialogue."""
        quest = self.forge.generate_quest(quest_type="fetch")
        dialogue = self.forge.generate_quest_dialogue(quest, stage="progress")
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0

    def test_create_narrative_scene(self):
        """Test narrative scene creation."""
        scene = self.forge.create_narrative_scene(
            setting="Ancient Temple",
            characters=["Hero", "Wizard"],
            mood="mysterious"
        )
        
        assert scene["setting"] == "Ancient Temple"
        assert "Hero" in scene["characters"]
        assert "Wizard" in scene["characters"]
        assert scene["mood"] == "mysterious"
        assert "description" in scene

    def test_create_narrative_scene_moods(self):
        """Test different scene moods."""
        moods = ["tense", "peaceful", "mysterious", "chaotic", "somber"]
        
        for mood in moods:
            scene = self.forge.create_narrative_scene(
                setting="Test Location",
                characters=["Character1"],
                mood=mood
            )
            assert scene["mood"] == mood
            assert len(scene["description"]) > 0

    def test_add_template(self):
        """Test adding custom templates."""
        template = "Custom template with {placeholder}"
        result = self.forge.add_template("custom_type", template)
        
        assert result is True
        assert "custom_type" in self.forge.templates
        assert template in self.forge.templates["custom_type"]

    def test_set_get_context(self):
        """Test setting and getting context."""
        self.forge.set_context("key1", "value1")
        self.forge.set_context("key2", "value2")
        
        context = self.forge.get_context()
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"

    def test_quest_rewards(self):
        """Test that quests have appropriate rewards."""
        quest = self.forge.generate_quest(quest_type="kill", difficulty="hard")
        
        assert "rewards" in quest
        assert len(quest["rewards"]) > 0
        
        # Hard quests should have better rewards
        if "gold" in quest["rewards"]:
            assert quest["rewards"]["gold"] > 0
        if "experience" in quest["rewards"]:
            assert quest["rewards"]["experience"] > 0
