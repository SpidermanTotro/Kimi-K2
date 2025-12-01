"""
THE FORGE - Live AI Programs
Executable implementations of all documentation capabilities
"""

from .skills_engine import SkillsEngine, Skill, SkillCategory
from .intelligent_monitor import IntelligentMonitor, Issue, UpdateCandidate, IssueSeverity, IssueType
from .multimedia_suite import MultimediaSuite, VideoProject, AudioProject, VideoFormat, VideoResolution, VideoCodec
from .book_writing_system import BookWritingSystem, BookProject, Character, Chapter, BookGenre, ChapterStatus

__version__ = "1.0.0"
__all__ = [
    # Skills Engine
    'SkillsEngine',
    'Skill',
    'SkillCategory',
    
    # Intelligent Monitor
    'IntelligentMonitor',
    'Issue',
    'UpdateCandidate',
    'IssueSeverity',
    'IssueType',
    
    # Multimedia Suite
    'MultimediaSuite',
    'VideoProject',
    'AudioProject',
    'VideoFormat',
    'VideoResolution',
    'VideoCodec',
    
    # Book Writing System
    'BookWritingSystem',
    'BookProject',
    'Character',
    'Chapter',
    'BookGenre',
    'ChapterStatus',
]