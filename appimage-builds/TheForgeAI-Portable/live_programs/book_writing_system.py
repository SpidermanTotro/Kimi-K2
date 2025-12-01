#!/usr/bin/env python3
"""
THE FORGE - Book Writing System
Transforms BOOK_WRITING_MASTERY.md into live book creation tools
"""

import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class BookGenre(Enum):
    """Book genres"""
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    ROMANCE = "romance"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    HORROR = "horror"
    BIOGRAPHY = "biography"
    SELF_HELP = "self_help"
    TECHNICAL = "technical"


class ChapterStatus(Enum):
    """Chapter writing status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DRAFT = "draft"
    REVISION = "revision"
    COMPLETE = "complete"


@dataclass
class Character:
    """Book character"""
    name: str
    role: str  # protagonist, antagonist, supporting
    description: str
    backstory: str = ""
    traits: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'role': self.role,
            'description': self.description,
            'backstory': self.backstory,
            'traits': self.traits,
            'relationships': self.relationships
        }


@dataclass
class Chapter:
    """Book chapter"""
    number: int
    title: str
    summary: str
    content: str = ""
    word_count: int = 0
    status: ChapterStatus = ChapterStatus.PLANNED
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'word_count': self.word_count,
            'status': self.status.value,
            'notes': self.notes
        }


@dataclass
class BookProject:
    """Complete book project"""
    title: str
    author: str
    genre: BookGenre
    target_words: int
    synopsis: str = ""
    outline: str = ""
    chapters: List[Chapter] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    settings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_words(self) -> int:
        return sum(c.word_count for c in self.chapters)
    
    def get_progress(self) -> float:
        return (self.get_total_words() / self.target_words) * 100 if self.target_words > 0 else 0
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'author': self.author,
            'genre': self.genre.value,
            'target_words': self.target_words,
            'current_words': self.get_total_words(),
            'progress': f"{self.get_progress():.1f}%",
            'synopsis': self.synopsis,
            'outline': self.outline,
            'chapters': [c.to_dict() for c in self.chapters],
            'characters': [c.to_dict() for c in self.characters],
            'themes': self.themes,
            'settings': self.settings,
            'created_at': self.created_at.isoformat()
        }


class BookWritingSystem:
    """
    Book Writing System
    - Project management
    - Character development
    - Plot structuring
    - Chapter organization
    - Writing assistance
    """
    
    def __init__(self, workspace: str = "books_workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
        self.projects: Dict[str, BookProject] = {}
        
    def create_project(self, title: str, author: str, genre: BookGenre,
                      target_words: int = 80000) -> BookProject:
        """Create a new book project"""
        project = BookProject(
            title=title,
            author=author,
            genre=genre,
            target_words=target_words
        )
        
        self.projects[title] = project
        
        # Create project directory
        project_dir = self.workspace / self._sanitize_filename(title)
        project_dir.mkdir(exist_ok=True)
        
        print(f"✅ Created book project: {title}")
        print(f"   Genre: {genre.value}")
        print(f"   Target: {target_words:,} words")
        
        return project
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename"""
        return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
    
    def add_character(self, project_title: str, name: str, role: str,
                     description: str, **kwargs) -> Character:
        """Add character to project"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        character = Character(
            name=name,
            role=role,
            description=description,
            **kwargs
        )
        
        self.projects[project_title].characters.append(character)
        print(f"✅ Added character: {name} ({role})")
        
        return character
    
    def add_chapter(self, project_title: str, number: int, title: str,
                   summary: str) -> Chapter:
        """Add chapter to project"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        chapter = Chapter(
            number=number,
            title=title,
            summary=summary
        )
        
        self.projects[project_title].chapters.append(chapter)
        print(f"✅ Added chapter {number}: {title}")
        
        return chapter
    
    def write_chapter_content(self, project_title: str, chapter_number: int,
                            content: str):
        """Write content for a chapter"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        chapter = next((c for c in project.chapters if c.number == chapter_number), None)
        
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found")
        
        chapter.content = content
        chapter.word_count = len(content.split())
        chapter.status = ChapterStatus.DRAFT
        
        print(f"✅ Chapter {chapter_number} written: {chapter.word_count:,} words")
    
    def update_chapter_status(self, project_title: str, chapter_number: int,
                            status: ChapterStatus):
        """Update chapter status"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        chapter = next((c for c in project.chapters if c.number == chapter_number), None)
        
        if not chapter:
            raise ValueError(f"Chapter {chapter_number} not found")
        
        chapter.status = status
        print(f"✅ Chapter {chapter_number} status: {status.value}")
    
    def generate_outline(self, project_title: str, num_chapters: int = 20) -> str:
        """Generate book outline structure"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        
        outline = f"# {project.title}\n\n"
        outline += f"## Author: {project.author}\n"
        outline += f"## Genre: {project.genre.value}\n"
        outline += f"## Target Words: {project.target_words:,}\n\n"
        
        outline += "## Three-Act Structure\n\n"
        
        # Act 1 (25%)
        act1_chapters = num_chapters // 4
        outline += f"### Act 1: Setup (Chapters 1-{act1_chapters})\n"
        outline += "- Introduce protagonist and world\n"
        outline += "- Establish normal life\n"
        outline += "- Inciting incident\n"
        outline += "- First plot point\n\n"
        
        # Act 2 (50%)
        act2_start = act1_chapters + 1
        act2_end = act1_chapters + (num_chapters // 2)
        outline += f"### Act 2: Confrontation (Chapters {act2_start}-{act2_end})\n"
        outline += "- Rising action\n"
        outline += "- Obstacles and conflicts\n"
        outline += "- Character development\n"
        outline += "- Midpoint twist\n"
        outline += "- Darkest moment\n\n"
        
        # Act 3 (25%)
        act3_start = act2_end + 1
        outline += f"### Act 3: Resolution (Chapters {act3_start}-{num_chapters})\n"
        outline += "- Final confrontation\n"
        outline += "- Climax\n"
        outline += "- Resolution\n"
        outline += "- Denouement\n\n"
        
        project.outline = outline
        print(f"✅ Generated outline for {num_chapters} chapters")
        
        return outline
    
    def analyze_pacing(self, project_title: str) -> Dict:
        """Analyze book pacing"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        
        if not project.chapters:
            return {'error': 'No chapters to analyze'}
        
        total_words = project.get_total_words()
        avg_chapter_words = total_words / len(project.chapters) if project.chapters else 0
        
        analysis = {
            'total_chapters': len(project.chapters),
            'total_words': total_words,
            'target_words': project.target_words,
            'progress': project.get_progress(),
            'avg_chapter_words': int(avg_chapter_words),
            'chapters_complete': len([c for c in project.chapters if c.status == ChapterStatus.COMPLETE]),
            'chapters_in_progress': len([c for c in project.chapters if c.status == ChapterStatus.IN_PROGRESS]),
            'chapters_planned': len([c for c in project.chapters if c.status == ChapterStatus.PLANNED])
        }
        
        return analysis
    
    def export_manuscript(self, project_title: str, output_file: Optional[str] = None):
        """Export complete manuscript"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        
        if not output_file:
            output_file = self.workspace / self._sanitize_filename(project.title) / "manuscript.txt"
        
        manuscript = f"{project.title}\n"
        manuscript += f"by {project.author}\n"
        manuscript += "=" * 70 + "\n\n"
        
        if project.synopsis:
            manuscript += f"Synopsis:\n{project.synopsis}\n\n"
            manuscript += "=" * 70 + "\n\n"
        
        # Sort chapters by number
        sorted_chapters = sorted(project.chapters, key=lambda c: c.number)
        
        for chapter in sorted_chapters:
            manuscript += f"\n\nChapter {chapter.number}: {chapter.title}\n"
            manuscript += "-" * 70 + "\n\n"
            manuscript += chapter.content + "\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(manuscript)
        
        print(f"✅ Manuscript exported: {output_file}")
        print(f"   Total words: {project.get_total_words():,}")
    
    def export_project(self, project_title: str, output_file: Optional[str] = None):
        """Export project as JSON"""
        if project_title not in self.projects:
            raise ValueError(f"Project not found: {project_title}")
        
        project = self.projects[project_title]
        
        if not output_file:
            output_file = self.workspace / self._sanitize_filename(project.title) / "project.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Project exported: {output_file}")
    
    def get_writing_prompts(self, genre: BookGenre) -> List[str]:
        """Get writing prompts for genre"""
        prompts = {
            BookGenre.MYSTERY: [
                "A detective receives an anonymous letter about a cold case",
                "A small town's secrets are revealed during a festival",
                "An amateur sleuth discovers a pattern in seemingly unrelated events"
            ],
            BookGenre.SCIENCE_FICTION: [
                "First contact with an alien civilization goes wrong",
                "A scientist discovers time travel has already been invented",
                "Humanity must evacuate Earth within 24 hours"
            ],
            BookGenre.FANTASY: [
                "A prophecy is misinterpreted for centuries",
                "Magic suddenly stops working in a magical world",
                "An ordinary person inherits an ancient power"
            ],
            BookGenre.ROMANCE: [
                "Two rivals must work together on a project",
                "A chance encounter leads to an unexpected connection",
                "Reuniting with a past love after many years"
            ]
        }
        
        return prompts.get(genre, ["Write what you know", "Start with a compelling character"])
    
    def get_capabilities(self) -> Dict:
        """Get system capabilities"""
        return {
            'project_management': [
                'Create book projects',
                'Set word count targets',
                'Track progress',
                'Organize chapters'
            ],
            'character_development': [
                'Create characters',
                'Define relationships',
                'Track character arcs',
                'Character profiles'
            ],
            'plot_structuring': [
                'Three-act structure',
                'Chapter outlines',
                'Plot points',
                'Story arcs'
            ],
            'writing_tools': [
                'Chapter writing',
                'Status tracking',
                'Word count tracking',
                'Manuscript export'
            ],
            'analysis': [
                'Pacing analysis',
                'Progress tracking',
                'Chapter statistics',
                'Writing prompts'
            ]
        }


def main():
    """Main execution"""
    print("🔥 THE FORGE - Book Writing System")
    print("=" * 70)
    print()
    
    # Initialize system
    system = BookWritingSystem()
    
    # Show capabilities
    print("📋 Available Capabilities:")
    print("-" * 70)
    caps = system.get_capabilities()
    
    for category, features in caps.items():
        print(f"\n📚 {category.replace('_', ' ').title()}:")
        for feature in features:
            print(f"  ✅ {feature}")
    
    print("\n✅ Book Writing System Ready!")
    print("\n💡 Example Usage:")
    print("  project = system.create_project('My Novel', 'Author Name', BookGenre.FICTION)")
    print("  system.add_character('My Novel', 'Hero', 'protagonist', 'Brave warrior')")
    print("  system.add_chapter('My Novel', 1, 'The Beginning', 'Hero starts journey')")
    print("  system.generate_outline('My Novel', num_chapters=20)")


if __name__ == "__main__":
    main()