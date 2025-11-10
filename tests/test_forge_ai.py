"""
Unit tests for Forge AI Extension
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kimi_k2.forge_ai import (
    ForgeAI, BookWriter, DialogueGenerator, QuestScripter,
    BookOutline, NPCProfile, Quest, DialogueTone, QuestType
)


class TestBookWriter:
    """Test BookWriter functionality"""
    
    @pytest.fixture
    def writer(self):
        """Create a book writer instance"""
        return BookWriter()
    
    def test_create_outline(self, writer):
        """Test creating a book outline"""
        outline = writer.create_outline(
            title="Test Book",
            author="Test Author",
            genre="Fantasy",
            num_chapters=5
        )
        
        assert outline.title == "Test Book"
        assert outline.author == "Test Author"
        assert outline.genre == "Fantasy"
        assert len(outline.chapters) == 5
    
    def test_update_chapter_outline(self, writer):
        """Test updating chapter outline"""
        writer.create_outline("Test", "Author", "Genre", 3)
        
        success = writer.update_chapter_outline(
            1, "New Title", "New Summary"
        )
        
        assert success is True
        assert writer.current_outline.chapters[0]["title"] == "New Title"
        assert writer.current_outline.chapters[0]["summary"] == "New Summary"
    
    def test_update_chapter_invalid(self, writer):
        """Test updating invalid chapter"""
        writer.create_outline("Test", "Author", "Genre", 3)
        
        success = writer.update_chapter_outline(10, "Title", "Summary")
        assert success is False
    
    def test_generate_chapter_content(self, writer):
        """Test generating chapter content"""
        writer.create_outline("Test", "Author", "Fantasy", 2)
        
        content = writer.generate_chapter_content(1, word_count=500)
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Chapter" in content
    
    def test_generate_chapter_no_outline(self, writer):
        """Test generating chapter without outline"""
        content = writer.generate_chapter_content(1)
        assert "Error" in content
    
    def test_export_book(self, writer):
        """Test exporting book"""
        writer.create_outline("Test", "Author", "Genre", 2)
        writer.generate_chapter_content(1)
        
        export = writer.export_book("markdown")
        
        assert "Test" in export
        assert "Author" in export
        assert "Genre" in export
    
    def test_save_and_load_outline(self, writer, tmp_path):
        """Test saving and loading outline"""
        writer.create_outline("Test", "Author", "Genre", 3)
        
        filepath = tmp_path / "outline.json"
        success = writer.save_outline(str(filepath))
        assert success is True
        assert filepath.exists()
        
        # Load into new writer
        new_writer = BookWriter()
        success = new_writer.load_outline(str(filepath))
        assert success is True
        assert new_writer.current_outline.title == "Test"
        assert len(new_writer.current_outline.chapters) == 3


class TestDialogueGenerator:
    """Test DialogueGenerator functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create a dialogue generator instance"""
        return DialogueGenerator()
    
    def test_create_npc(self, generator):
        """Test creating an NPC"""
        npc = generator.create_npc(
            name="TestNPC",
            role="merchant",
            personality="friendly",
            background="A helpful trader",
            relationships={"player": "friendly"}
        )
        
        assert npc.name == "TestNPC"
        assert npc.role == "merchant"
        assert npc.personality == "friendly"
        assert "player" in npc.relationships
    
    def test_generate_dialogue(self, generator):
        """Test generating NPC dialogue"""
        generator.create_npc(
            name="TestNPC",
            role="merchant",
            personality="friendly",
            background="Trader"
        )
        
        dialogue = generator.generate_dialogue(
            "TestNPC",
            "greeting",
            DialogueTone.FRIENDLY
        )
        
        assert isinstance(dialogue, str)
        assert "TestNPC" in dialogue
        assert len(dialogue) > 0
    
    def test_generate_dialogue_unknown_npc(self, generator):
        """Test generating dialogue for unknown NPC"""
        dialogue = generator.generate_dialogue(
            "Unknown",
            "context",
            DialogueTone.NEUTRAL
        )
        
        assert "Error" in dialogue
    
    def test_generate_conversation(self, generator):
        """Test generating a conversation"""
        generator.create_npc(
            "TestNPC", "guide", "helpful", "Village guide"
        )
        
        conversation = generator.generate_conversation(
            "TestNPC",
            ["Hello", "Can you help me?"]
        )
        
        assert len(conversation) == 4  # 2 player + 2 NPC responses
        assert conversation[0]["speaker"] == "Player"
        assert conversation[1]["speaker"] == "TestNPC"
    
    def test_dialogue_tones(self, generator):
        """Test different dialogue tones"""
        generator.create_npc("NPC", "guard", "serious", "Guard")
        
        for tone in DialogueTone:
            dialogue = generator.generate_dialogue("NPC", "test", tone)
            assert tone.value in dialogue.lower()
    
    def test_save_and_load_npc(self, generator, tmp_path):
        """Test saving and loading NPC"""
        generator.create_npc("TestNPC", "merchant", "friendly", "Trader")
        
        filepath = tmp_path / "npc.json"
        success = generator.save_npc("TestNPC", str(filepath))
        assert success is True
        assert filepath.exists()
        
        # Load into new generator
        new_generator = DialogueGenerator()
        npc = new_generator.load_npc(str(filepath))
        assert npc is not None
        assert npc.name == "TestNPC"


class TestQuestScripter:
    """Test QuestScripter functionality"""
    
    @pytest.fixture
    def scripter(self):
        """Create a quest scripter instance"""
        return QuestScripter()
    
    def test_create_fetch_quest(self, scripter):
        """Test creating a fetch quest"""
        quest = scripter.create_quest(
            quest_id="test_fetch",
            title="Get the Sword",
            quest_type=QuestType.FETCH,
            params={"item": "Magic Sword", "location": "Dark Cave"}
        )
        
        assert quest.id == "test_fetch"
        assert quest.title == "Get the Sword"
        assert "Magic Sword" in quest.description
        assert len(quest.objectives) > 0
    
    def test_create_kill_quest(self, scripter):
        """Test creating a kill quest"""
        quest = scripter.create_quest(
            quest_id="test_kill",
            title="Clear the Forest",
            quest_type=QuestType.KILL,
            params={"count": 10, "enemy_type": "wolves", "location": "Dark Forest"}
        )
        
        assert "10" in quest.description
        assert "wolves" in quest.description
    
    def test_create_custom_quest(self, scripter):
        """Test creating a custom quest"""
        quest = scripter.create_custom_quest(
            quest_id="custom",
            title="Custom Quest",
            quest_type="special",
            description="A unique quest",
            objectives=["Do thing 1", "Do thing 2"],
            rewards={"gold": 500}
        )
        
        assert quest.id == "custom"
        assert quest.quest_type == "special"
        assert len(quest.objectives) == 2
    
    def test_generate_quest_chain(self, scripter):
        """Test generating a quest chain"""
        quests = scripter.generate_quest_chain(
            chain_name="dragon_quest",
            num_quests=3,
            theme="Dragon"
        )
        
        assert len(quests) == 3
        assert quests[0].prerequisites == []
        assert quests[1].prerequisites == ["dragon_quest_quest_1"]
    
    def test_quest_with_prerequisites(self, scripter):
        """Test quest with prerequisites"""
        quest = scripter.create_quest(
            quest_id="advanced",
            title="Advanced Quest",
            quest_type=QuestType.INVESTIGATE,
            params={"mystery": "the curse", "location": "ruins"},
            prerequisites=["basic_quest"]
        )
        
        assert "basic_quest" in quest.prerequisites
    
    def test_save_and_load_quest(self, scripter, tmp_path):
        """Test saving and loading quest"""
        scripter.create_quest(
            "test", "Test Quest", QuestType.FETCH,
            {"item": "item", "location": "place"}
        )
        
        filepath = tmp_path / "quest.json"
        success = scripter.save_quest("test", str(filepath))
        assert success is True
        
        # Load into new scripter
        new_scripter = QuestScripter()
        quest = new_scripter.load_quest(str(filepath))
        assert quest is not None
        assert quest.id == "test"
    
    def test_export_all_quests(self, scripter, tmp_path):
        """Test exporting all quests"""
        scripter.create_quest(
            "q1", "Quest 1", QuestType.FETCH,
            {"item": "a", "location": "b"}
        )
        scripter.create_quest(
            "q2", "Quest 2", QuestType.KILL,
            {"count": 5, "enemy_type": "c", "location": "d"}
        )
        
        filepath = tmp_path / "all_quests.json"
        success = scripter.export_all_quests(str(filepath))
        assert success is True
        
        # Verify file contents
        with open(filepath) as f:
            data = json.load(f)
        assert "q1" in data
        assert "q2" in data


class TestForgeAI:
    """Test ForgeAI main interface"""
    
    def test_forge_ai_initialization(self):
        """Test ForgeAI initializes all components"""
        forge = ForgeAI()
        
        assert forge.book_writer is not None
        assert forge.dialogue_generator is not None
        assert forge.quest_scripter is not None
    
    def test_get_components(self):
        """Test getting individual components"""
        forge = ForgeAI()
        
        writer = forge.get_book_writer()
        assert isinstance(writer, BookWriter)
        
        generator = forge.get_dialogue_generator()
        assert isinstance(generator, DialogueGenerator)
        
        scripter = forge.get_quest_scripter()
        assert isinstance(scripter, QuestScripter)


class TestDataClasses:
    """Test data classes"""
    
    def test_book_outline_serialization(self):
        """Test BookOutline serialization"""
        outline = BookOutline(
            title="Test",
            author="Author",
            genre="Genre",
            chapters=[{"number": 1, "title": "Ch1", "summary": "Sum1"}]
        )
        
        data = outline.to_dict()
        assert data["title"] == "Test"
        
        loaded = BookOutline.from_dict(data)
        assert loaded.title == "Test"
        assert len(loaded.chapters) == 1
    
    def test_npc_profile_serialization(self):
        """Test NPCProfile serialization"""
        npc = NPCProfile(
            name="Test",
            role="role",
            personality="friendly",
            background="bg",
            relationships={"a": "b"}
        )
        
        data = npc.to_dict()
        assert data["name"] == "Test"
        
        loaded = NPCProfile.from_dict(data)
        assert loaded.name == "Test"
    
    def test_quest_serialization(self):
        """Test Quest serialization"""
        quest = Quest(
            id="q1",
            title="Quest",
            quest_type="fetch",
            description="desc",
            objectives=["obj1"],
            rewards={"gold": 100},
            prerequisites=[]
        )
        
        data = quest.to_dict()
        assert data["id"] == "q1"
        
        loaded = Quest.from_dict(data)
        assert loaded.id == "q1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
