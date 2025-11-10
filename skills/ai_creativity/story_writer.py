"""
Story Writer Module

Provides comprehensive story and book writing capabilities with support for:
- Long-form narrative generation
- Character development and tracking
- Plot structure and progression
- Multiple genres and styles
- Chapter and scene organization
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Genre(Enum):
    """Story genre categories"""
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    HORROR = "horror"
    ADVENTURE = "adventure"
    HISTORICAL = "historical"
    CONTEMPORARY = "contemporary"
    LITERARY = "literary"


class NarrativePOV(Enum):
    """Narrative point of view"""
    FIRST_PERSON = "first_person"
    SECOND_PERSON = "second_person"
    THIRD_PERSON_LIMITED = "third_person_limited"
    THIRD_PERSON_OMNISCIENT = "third_person_omniscient"


@dataclass
class Character:
    """Story character definition"""
    name: str
    role: str  # "protagonist", "antagonist", "supporting", "minor"
    description: str
    personality: List[str] = field(default_factory=list)
    background: str = ""
    goals: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    arc: Optional[str] = None


@dataclass
class PlotPoint:
    """Key plot point in story structure"""
    name: str
    description: str
    chapter: int
    timing: float  # Position in story (0.0 to 1.0)
    type: str  # "setup", "inciting_incident", "climax", "resolution", etc.


@dataclass
class Chapter:
    """Chapter structure"""
    number: int
    title: str
    summary: str
    word_count_target: int = 3000
    scenes: List[str] = field(default_factory=list)
    pov_character: Optional[str] = None
    content: str = ""


@dataclass
class StoryConfig:
    """Story generation configuration"""
    title: str = "Untitled"
    genre: Genre = Genre.FANTASY
    target_word_count: int = 80000
    num_chapters: int = 20
    pov: NarrativePOV = NarrativePOV.THIRD_PERSON_LIMITED
    writing_style: str = "descriptive"  # "descriptive", "minimalist", "literary"
    tone: str = "serious"  # "serious", "humorous", "dark", "light"
    target_audience: str = "adult"  # "children", "young_adult", "adult"


class StoryWriter:
    """
    Advanced story and book writing engine for Kimi-K2
    
    Features:
    - Long-form narrative generation (books, novels, screenplays)
    - Character development and tracking
    - Plot structure and story arcs
    - Multiple genre support
    - Consistent world-building
    - Chapter and scene organization
    
    Example:
        >>> writer = StoryWriter()
        >>> config = StoryConfig(
        ...     title="The Crystal Chronicles",
        ...     genre=Genre.FANTASY,
        ...     num_chapters=25,
        ...     target_word_count=100000
        ... )
        >>> story = writer.create_story(config)
        >>> writer.add_character(story, Character(
        ...     name="Aria",
        ...     role="protagonist",
        ...     description="A young mage discovering her powers"
        ... ))
        >>> writer.generate_outline(story)
        >>> writer.write_chapter(story, 1)
    """
    
    def __init__(self, kimi_client=None):
        """
        Initialize story writer
        
        Args:
            kimi_client: Kimi-K2 client for text generation
        """
        self.kimi_client = kimi_client
        self._stories = {}
    
    def create_story(
        self,
        config: StoryConfig,
        premise: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Create new story project
        
        Args:
            config: Story configuration
            premise: Optional story premise/pitch
            
        Returns:
            Story data structure
        """
        story = {
            "id": f"story_{len(self._stories)}",
            "config": config,
            "premise": premise,
            "characters": [],
            "plot_points": [],
            "chapters": [],
            "world_building": {},
            "outline": None,
            "metadata": {
                "created": datetime.now().isoformat(),
                "word_count": 0,
                "progress": 0.0
            }
        }
        
        self._stories[story["id"]] = story
        return story
    
    def add_character(
        self,
        story: Dict[str, any],
        character: Character
    ) -> Dict[str, any]:
        """
        Add character to story
        
        Args:
            story: Story data
            character: Character to add
            
        Returns:
            Updated story
        """
        story["characters"].append(character.__dict__)
        return story
    
    def generate_outline(
        self,
        story: Dict[str, any],
        use_structure: str = "three_act"  # "three_act", "hero_journey", "five_act"
    ) -> Dict[str, any]:
        """
        Generate story outline with plot structure
        
        Args:
            story: Story data
            use_structure: Story structure to use
            
        Returns:
            Story with generated outline
        """
        config = story["config"]
        num_chapters = config.num_chapters
        
        # Generate plot points based on structure
        if use_structure == "three_act":
            plot_points = [
                PlotPoint("Opening", "Introduction to world and characters", 1, 0.0, "setup"),
                PlotPoint("Inciting Incident", "Event that starts the journey", 2, 0.1, "inciting_incident"),
                PlotPoint("First Plot Point", "Point of no return", 5, 0.25, "plot_point"),
                PlotPoint("Midpoint", "Major revelation or reversal", 10, 0.5, "midpoint"),
                PlotPoint("Crisis", "Darkest moment", 15, 0.75, "crisis"),
                PlotPoint("Climax", "Final confrontation", 18, 0.9, "climax"),
                PlotPoint("Resolution", "Aftermath and new normal", 20, 1.0, "resolution"),
            ]
        else:
            # Other structures can be implemented
            plot_points = []
        
        story["plot_points"] = [p.__dict__ for p in plot_points]
        
        # Generate chapter outlines
        chapters = []
        words_per_chapter = config.target_word_count // num_chapters
        
        for i in range(num_chapters):
            chapter = Chapter(
                number=i + 1,
                title=f"Chapter {i + 1}",
                summary=f"Chapter {i + 1} summary to be generated",
                word_count_target=words_per_chapter
            )
            chapters.append(chapter.__dict__)
        
        story["chapters"] = chapters
        story["outline"] = {
            "structure": use_structure,
            "generated": True
        }
        
        return story
    
    def write_chapter(
        self,
        story: Dict[str, any],
        chapter_number: int,
        style_guidance: Optional[str] = None
    ) -> str:
        """
        Write/generate a specific chapter
        
        Args:
            story: Story data
            chapter_number: Chapter to write (1-indexed)
            style_guidance: Optional style guidance
            
        Returns:
            Generated chapter text
        """
        if chapter_number < 1 or chapter_number > len(story["chapters"]):
            raise ValueError(f"Invalid chapter number: {chapter_number}")
        
        chapter = story["chapters"][chapter_number - 1]
        config = story["config"]
        
        # In production: use Kimi-K2 for actual generation
        prompt = self._build_chapter_prompt(story, chapter, style_guidance)
        
        # Placeholder generation
        chapter_text = f"# {chapter['title']}\n\n"
        chapter_text += f"[Chapter {chapter_number} content would be generated here]\n"
        chapter_text += f"Target word count: {chapter['word_count_target']}\n"
        chapter_text += f"Summary: {chapter['summary']}\n"
        
        # Update chapter content
        chapter["content"] = chapter_text
        chapter["word_count"] = len(chapter_text.split())
        
        # Update story progress
        self._update_progress(story)
        
        return chapter_text
    
    def _build_chapter_prompt(
        self,
        story: Dict[str, any],
        chapter: Dict[str, any],
        style_guidance: Optional[str]
    ) -> str:
        """Build prompt for chapter generation using Kimi-K2"""
        config = story["config"]
        
        prompt = f"Write Chapter {chapter['number']} of '{config.title}'\n"
        prompt += f"Genre: {config.genre.value}\n"
        prompt += f"POV: {config.pov.value}\n"
        prompt += f"Summary: {chapter['summary']}\n"
        
        if story.get("characters"):
            prompt += f"\nCharacters: {', '.join(c['name'] for c in story['characters'])}\n"
        
        if style_guidance:
            prompt += f"\nStyle guidance: {style_guidance}\n"
        
        return prompt
    
    def develop_character_arc(
        self,
        story: Dict[str, any],
        character_name: str,
        arc_description: str
    ) -> Dict[str, any]:
        """
        Develop character arc throughout story
        
        Args:
            story: Story data
            character_name: Character to develop
            arc_description: Description of character's journey
            
        Returns:
            Updated story with character arc
        """
        for character in story["characters"]:
            if character["name"] == character_name:
                character["arc"] = arc_description
                break
        
        return story
    
    def add_world_building(
        self,
        story: Dict[str, any],
        category: str,  # "location", "magic_system", "culture", "technology"
        name: str,
        description: str,
        details: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Add world-building elements
        
        Args:
            story: Story data
            category: Type of world element
            name: Name of element
            description: Description
            details: Additional details
            
        Returns:
            Updated story
        """
        if category not in story["world_building"]:
            story["world_building"][category] = []
        
        story["world_building"][category].append({
            "name": name,
            "description": description,
            "details": details or {}
        })
        
        return story
    
    def generate_scene(
        self,
        story: Dict[str, any],
        scene_description: str,
        characters: List[str],
        location: str,
        word_count: int = 1000
    ) -> str:
        """
        Generate individual scene
        
        Args:
            story: Story data
            scene_description: What happens in the scene
            characters: Characters in the scene
            location: Where the scene takes place
            word_count: Target word count
            
        Returns:
            Generated scene text
        """
        # In production: use Kimi-K2 for generation
        scene = f"Scene: {scene_description}\n"
        scene += f"Location: {location}\n"
        scene += f"Characters: {', '.join(characters)}\n\n"
        scene += f"[Scene content would be generated here, ~{word_count} words]\n"
        
        return scene
    
    def _update_progress(self, story: Dict[str, any]):
        """Update story writing progress"""
        total_words = sum(
            ch.get("word_count", 0)
            for ch in story["chapters"]
            if ch.get("content")
        )
        
        story["metadata"]["word_count"] = total_words
        story["metadata"]["progress"] = total_words / story["config"].target_word_count
    
    def export_manuscript(
        self,
        story: Dict[str, any],
        format: str = "markdown"  # "markdown", "docx", "pdf", "html"
    ) -> str:
        """
        Export completed story as manuscript
        
        Args:
            story: Story data
            format: Export format
            
        Returns:
            Path to exported manuscript
        """
        config = story["config"]
        output_path = f"{config.title.replace(' ', '_')}.{format}"
        
        print(f"Exporting manuscript to {output_path}")
        print(f"Title: {config.title}")
        print(f"Genre: {config.genre.value}")
        print(f"Chapters: {len(story['chapters'])}")
        print(f"Word count: {story['metadata']['word_count']}")
        
        return output_path
