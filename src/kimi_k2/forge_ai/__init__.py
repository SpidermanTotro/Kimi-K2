"""
Forge-like AI Extension for Creative Tasks

Provides AI-driven capabilities for:
- Interactive book writing with structured outlines
- NPC dialogue generation with context-aware interactions
- Quest and event scripting
"""

import json
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DialogueTone(Enum):
    """Tone options for NPC dialogue"""
    FRIENDLY = "friendly"
    HOSTILE = "hostile"
    NEUTRAL = "neutral"
    MYSTERIOUS = "mysterious"
    FEARFUL = "fearful"
    EXCITED = "excited"


class QuestType(Enum):
    """Types of quests"""
    FETCH = "fetch"
    KILL = "kill"
    ESCORT = "escort"
    INVESTIGATE = "investigate"
    DELIVERY = "delivery"
    PUZZLE = "puzzle"


@dataclass
class BookOutline:
    """Structure for book outline"""
    title: str
    author: str
    genre: str
    chapters: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookOutline':
        return cls(**data)


@dataclass
class NPCProfile:
    """NPC character profile"""
    name: str
    role: str
    personality: str
    background: str
    relationships: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCProfile':
        return cls(**data)


@dataclass
class Quest:
    """Quest structure"""
    id: str
    title: str
    quest_type: str
    description: str
    objectives: List[str]
    rewards: Dict[str, Any]
    prerequisites: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quest':
        return cls(**data)


class BookWriter:
    """AI-driven book writing assistant"""
    
    def __init__(self):
        self.current_outline: Optional[BookOutline] = None
        self.chapters_content: Dict[int, str] = {}
    
    def create_outline(self, title: str, author: str, genre: str, num_chapters: int) -> BookOutline:
        """Create a structured book outline
        
        Args:
            title: Book title
            author: Author name
            genre: Book genre
            num_chapters: Number of chapters
            
        Returns:
            BookOutline object
        """
        chapters = []
        for i in range(1, num_chapters + 1):
            chapters.append({
                "number": i,
                "title": f"Chapter {i}",
                "summary": f"Summary for chapter {i}"
            })
        
        self.current_outline = BookOutline(
            title=title,
            author=author,
            genre=genre,
            chapters=chapters
        )
        
        return self.current_outline
    
    def update_chapter_outline(self, chapter_num: int, title: str, summary: str) -> bool:
        """Update a chapter's outline
        
        Args:
            chapter_num: Chapter number
            title: Chapter title
            summary: Chapter summary
            
        Returns:
            Success status
        """
        if not self.current_outline:
            return False
        
        if chapter_num < 1 or chapter_num > len(self.current_outline.chapters):
            return False
        
        self.current_outline.chapters[chapter_num - 1]["title"] = title
        self.current_outline.chapters[chapter_num - 1]["summary"] = summary
        return True
    
    def generate_chapter_content(self, chapter_num: int, word_count: int = 1000) -> str:
        """Generate content for a chapter
        
        Args:
            chapter_num: Chapter number
            word_count: Target word count
            
        Returns:
            Generated chapter content
        """
        if not self.current_outline:
            return "Error: No outline created. Please create an outline first."
        
        if chapter_num < 1 or chapter_num > len(self.current_outline.chapters):
            return f"Error: Invalid chapter number. Must be between 1 and {len(self.current_outline.chapters)}"
        
        chapter = self.current_outline.chapters[chapter_num - 1]
        
        # Simulated content generation
        content = f"""# {chapter['title']}

{chapter['summary']}

[This is a simulated chapter content for '{self.current_outline.title}']
[Genre: {self.current_outline.genre}]
[Target word count: {word_count}]

In a real implementation, this would be connected to an AI model like Kimi-K2
to generate creative, contextual content based on the outline and genre.

The chapter would expand on: {chapter['summary']}

This is placeholder text to demonstrate the structure. In production, this would
be replaced with actual AI-generated narrative content."""
        
        self.chapters_content[chapter_num] = content
        return content
    
    def export_book(self, format: str = "markdown") -> str:
        """Export complete book
        
        Args:
            format: Export format (markdown, text)
            
        Returns:
            Formatted book content
        """
        if not self.current_outline:
            return "Error: No book to export"
        
        if format == "markdown":
            output = f"# {self.current_outline.title}\n\n"
            output += f"**Author:** {self.current_outline.author}\n\n"
            output += f"**Genre:** {self.current_outline.genre}\n\n"
            output += "---\n\n"
            
            for chapter_num in sorted(self.chapters_content.keys()):
                output += self.chapters_content[chapter_num]
                output += "\n\n---\n\n"
            
            return output
        
        return "Error: Unsupported format"
    
    def save_outline(self, filepath: str) -> bool:
        """Save outline to JSON file
        
        Args:
            filepath: Path to save file
            
        Returns:
            Success status
        """
        if not self.current_outline:
            return False
        
        with open(filepath, 'w') as f:
            json.dump(self.current_outline.to_dict(), f, indent=2)
        
        return True
    
    def load_outline(self, filepath: str) -> bool:
        """Load outline from JSON file
        
        Args:
            filepath: Path to load file
            
        Returns:
            Success status
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.current_outline = BookOutline.from_dict(data)
            return True
        except Exception:
            return False


class DialogueGenerator:
    """NPC dialogue generation with context awareness"""
    
    def __init__(self):
        self.npcs: Dict[str, NPCProfile] = {}
        self.dialogue_history: List[Dict[str, Any]] = []
    
    def create_npc(self, name: str, role: str, personality: str, background: str,
                   relationships: Optional[Dict[str, str]] = None) -> NPCProfile:
        """Create an NPC profile
        
        Args:
            name: NPC name
            role: NPC role (e.g., merchant, guard, quest giver)
            personality: Personality description
            background: Background story
            relationships: Relationships with other NPCs
            
        Returns:
            NPCProfile object
        """
        npc = NPCProfile(
            name=name,
            role=role,
            personality=personality,
            background=background,
            relationships=relationships or {}
        )
        
        self.npcs[name] = npc
        return npc
    
    def generate_dialogue(self, npc_name: str, context: str, tone: DialogueTone = DialogueTone.NEUTRAL) -> str:
        """Generate NPC dialogue based on context
        
        Args:
            npc_name: Name of the NPC
            context: Conversation context
            tone: Desired tone for the dialogue
            
        Returns:
            Generated dialogue
        """
        if npc_name not in self.npcs:
            return f"Error: NPC '{npc_name}' not found"
        
        npc = self.npcs[npc_name]
        
        # Simulated context-aware dialogue generation
        dialogue = f"[{npc.name} - {npc.role}]\n"
        dialogue += f"[Tone: {tone.value}]\n\n"
        
        # In production, this would use AI to generate contextual dialogue
        dialogue += f'"Hello, traveler. I am {npc.name}, {npc.role} of these lands. '
        
        if tone == DialogueTone.FRIENDLY:
            dialogue += "It's always a pleasure to meet new faces!"
        elif tone == DialogueTone.HOSTILE:
            dialogue += "State your business quickly, or be on your way."
        elif tone == DialogueTone.MYSTERIOUS:
            dialogue += "I sense something... unusual about you."
        
        dialogue += '"\n\n'
        dialogue += f"Context: {context}\n"
        dialogue += f"Personality: {npc.personality}\n"
        
        # Store in history
        self.dialogue_history.append({
            "npc": npc_name,
            "context": context,
            "tone": tone.value,
            "dialogue": dialogue
        })
        
        return dialogue
    
    def generate_conversation(self, npc_name: str, player_lines: List[str]) -> List[Dict[str, str]]:
        """Generate a full conversation
        
        Args:
            npc_name: Name of the NPC
            player_lines: List of player dialogue options
            
        Returns:
            List of conversation exchanges
        """
        if npc_name not in self.npcs:
            return [{"error": f"NPC '{npc_name}' not found"}]
        
        npc = self.npcs[npc_name]
        conversation = []
        
        for i, player_line in enumerate(player_lines):
            conversation.append({
                "speaker": "Player",
                "text": player_line
            })
            
            # Generate NPC response
            response = f"[{npc.name} responds based on their {npc.personality} personality]"
            conversation.append({
                "speaker": npc.name,
                "text": response
            })
        
        return conversation
    
    def save_npc(self, npc_name: str, filepath: str) -> bool:
        """Save NPC profile to file
        
        Args:
            npc_name: Name of NPC to save
            filepath: Path to save file
            
        Returns:
            Success status
        """
        if npc_name not in self.npcs:
            return False
        
        with open(filepath, 'w') as f:
            json.dump(self.npcs[npc_name].to_dict(), f, indent=2)
        
        return True
    
    def load_npc(self, filepath: str) -> Optional[NPCProfile]:
        """Load NPC profile from file
        
        Args:
            filepath: Path to load file
            
        Returns:
            NPCProfile object or None
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            npc = NPCProfile.from_dict(data)
            self.npcs[npc.name] = npc
            return npc
        except Exception:
            return None


class QuestScripter:
    """Dynamic quest and event scripting"""
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.quest_templates: Dict[QuestType, Dict[str, Any]] = self._init_templates()
    
    def _init_templates(self) -> Dict[QuestType, Dict[str, Any]]:
        """Initialize quest templates"""
        return {
            QuestType.FETCH: {
                "description_template": "Retrieve {item} from {location}",
                "objectives_template": ["Find {item}", "Return to quest giver"]
            },
            QuestType.KILL: {
                "description_template": "Defeat {count} {enemy_type} in {location}",
                "objectives_template": ["Defeat {count} {enemy_type}", "Report back"]
            },
            QuestType.ESCORT: {
                "description_template": "Escort {npc} safely to {destination}",
                "objectives_template": ["Meet {npc}", "Escort to {destination}"]
            },
            QuestType.INVESTIGATE: {
                "description_template": "Investigate {mystery} at {location}",
                "objectives_template": ["Travel to {location}", "Gather clues", "Report findings"]
            },
            QuestType.DELIVERY: {
                "description_template": "Deliver {item} to {recipient} at {location}",
                "objectives_template": ["Obtain {item}", "Travel to {location}", "Deliver to {recipient}"]
            },
            QuestType.PUZZLE: {
                "description_template": "Solve the {puzzle_name} puzzle at {location}",
                "objectives_template": ["Find the puzzle at {location}", "Solve {puzzle_name}", "Claim reward"]
            }
        }
    
    def create_quest(self, quest_id: str, title: str, quest_type: QuestType,
                    params: Dict[str, Any], rewards: Optional[Dict[str, Any]] = None,
                    prerequisites: Optional[List[str]] = None) -> Quest:
        """Create a new quest
        
        Args:
            quest_id: Unique quest identifier
            title: Quest title
            quest_type: Type of quest
            params: Parameters for quest template
            rewards: Quest rewards
            prerequisites: Required quests/conditions
            
        Returns:
            Quest object
        """
        template = self.quest_templates.get(quest_type)
        
        if not template:
            raise ValueError(f"Unknown quest type: {quest_type}")
        
        # Generate description from template
        description = template["description_template"].format(**params)
        
        # Generate objectives from template
        objectives = [obj.format(**params) for obj in template["objectives_template"]]
        
        quest = Quest(
            id=quest_id,
            title=title,
            quest_type=quest_type.value,
            description=description,
            objectives=objectives,
            rewards=rewards or {"gold": 100, "xp": 50},
            prerequisites=prerequisites or []
        )
        
        self.quests[quest_id] = quest
        return quest
    
    def create_custom_quest(self, quest_id: str, title: str, quest_type: str,
                           description: str, objectives: List[str],
                           rewards: Dict[str, Any], prerequisites: Optional[List[str]] = None) -> Quest:
        """Create a custom quest without template
        
        Args:
            quest_id: Unique quest identifier
            title: Quest title
            quest_type: Type of quest
            description: Quest description
            objectives: List of objectives
            rewards: Quest rewards
            prerequisites: Required quests/conditions
            
        Returns:
            Quest object
        """
        quest = Quest(
            id=quest_id,
            title=title,
            quest_type=quest_type,
            description=description,
            objectives=objectives,
            rewards=rewards,
            prerequisites=prerequisites or []
        )
        
        self.quests[quest_id] = quest
        return quest
    
    def generate_quest_chain(self, chain_name: str, num_quests: int, theme: str) -> List[Quest]:
        """Generate a chain of related quests
        
        Args:
            chain_name: Name for the quest chain
            num_quests: Number of quests in chain
            theme: Theme for the quest chain
            
        Returns:
            List of Quest objects
        """
        quests = []
        quest_types = list(QuestType)
        
        for i in range(num_quests):
            quest_id = f"{chain_name}_quest_{i+1}"
            quest_type = quest_types[i % len(quest_types)]
            
            # Create quest with appropriate parameters
            if quest_type == QuestType.FETCH:
                params = {"item": f"{theme} Artifact {i+1}", "location": f"{theme} Ruins"}
            elif quest_type == QuestType.KILL:
                params = {"count": (i+1)*5, "enemy_type": f"{theme} Creatures", "location": f"{theme} Territory"}
            elif quest_type == QuestType.ESCORT:
                params = {"npc": f"{theme} Scholar", "destination": f"{theme} Sanctuary"}
            elif quest_type == QuestType.INVESTIGATE:
                params = {"mystery": f"{theme} Mystery", "location": f"{theme} Site"}
            elif quest_type == QuestType.DELIVERY:
                params = {"item": f"{theme} Package", "recipient": f"{theme} Elder", "location": f"{theme} Village"}
            elif quest_type == QuestType.PUZZLE:
                params = {"puzzle_name": f"{theme} Enigma", "location": f"{theme} Temple"}
            else:
                params = {"mystery": f"{theme} Secret", "location": f"{theme} Location"}
            
            prereqs = [f"{chain_name}_quest_{i}"] if i > 0 else []
            
            quest = self.create_quest(
                quest_id=quest_id,
                title=f"{theme} Quest Part {i+1}",
                quest_type=quest_type,
                params=params,
                rewards={"gold": 100 * (i+1), "xp": 50 * (i+1)},
                prerequisites=prereqs
            )
            
            quests.append(quest)
        
        return quests
    
    def save_quest(self, quest_id: str, filepath: str) -> bool:
        """Save quest to file
        
        Args:
            quest_id: Quest ID to save
            filepath: Path to save file
            
        Returns:
            Success status
        """
        if quest_id not in self.quests:
            return False
        
        with open(filepath, 'w') as f:
            json.dump(self.quests[quest_id].to_dict(), f, indent=2)
        
        return True
    
    def load_quest(self, filepath: str) -> Optional[Quest]:
        """Load quest from file
        
        Args:
            filepath: Path to load file
            
        Returns:
            Quest object or None
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            quest = Quest.from_dict(data)
            self.quests[quest.id] = quest
            return quest
        except Exception:
            return None
    
    def export_all_quests(self, filepath: str) -> bool:
        """Export all quests to a single file
        
        Args:
            filepath: Path to save file
            
        Returns:
            Success status
        """
        try:
            quests_data = {qid: q.to_dict() for qid, q in self.quests.items()}
            with open(filepath, 'w') as f:
                json.dump(quests_data, f, indent=2)
            return True
        except Exception:
            return False


class ForgeAI:
    """Main Forge AI interface combining all creative tools"""
    
    def __init__(self):
        self.book_writer = BookWriter()
        self.dialogue_generator = DialogueGenerator()
        self.quest_scripter = QuestScripter()
    
    def get_book_writer(self) -> BookWriter:
        """Get book writing assistant"""
        return self.book_writer
    
    def get_dialogue_generator(self) -> DialogueGenerator:
        """Get dialogue generator"""
        return self.dialogue_generator
    
    def get_quest_scripter(self) -> QuestScripter:
        """Get quest scripter"""
        return self.quest_scripter


__all__ = [
    "ForgeAI",
    "BookWriter",
    "DialogueGenerator", 
    "QuestScripter",
    "BookOutline",
    "NPCProfile",
    "Quest",
    "DialogueTone",
    "QuestType"
]
