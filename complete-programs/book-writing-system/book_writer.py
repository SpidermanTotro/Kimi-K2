#!/usr/bin/env python3
"""
THE FORGE AI - Complete Book Writing System
Professional Author-to-Publisher Platform
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

class BookWritingSystem:
    """Complete book writing and publishing system"""
    
    def __init__(self, workspace_dir: str = "books_workspace"):
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        self.projects_file = self.workspace / "projects.json"
        self.projects = self.load_projects()
    
    def load_projects(self) -> Dict:
        """Load existing projects"""
        if self.projects_file.exists():
            with open(self.projects_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_projects(self):
        """Save projects to disk"""
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def create_project(self, title: str, genre: str, target_words: int = 50000) -> str:
        """Create new book project"""
        project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir = self.workspace / project_id
        project_dir.mkdir(exist_ok=True)
        
        project = {
            'id': project_id,
            'title': title,
            'genre': genre,
            'target_words': target_words,
            'current_words': 0,
            'chapters': [],
            'created_at': datetime.now().isoformat(),
            'status': 'planning'
        }
        
        self.projects[project_id] = project
        self.save_projects()
        
        print(f"✓ Created project: {title}")
        print(f"  ID: {project_id}")
        print(f"  Genre: {genre}")
        print(f"  Target: {target_words:,} words")
        
        return project_id
    
    def add_chapter(self, project_id: str, chapter_title: str, content: str = ""):
        """Add chapter to project"""
        if project_id not in self.projects:
            print(f"✗ Project not found: {project_id}")
            return
        
        chapter_num = len(self.projects[project_id]['chapters']) + 1
        chapter = {
            'number': chapter_num,
            'title': chapter_title,
            'content': content,
            'word_count': len(content.split()),
            'created_at': datetime.now().isoformat()
        }
        
        self.projects[project_id]['chapters'].append(chapter)
        self.update_word_count(project_id)
        self.save_projects()
        
        # Save chapter to file
        project_dir = self.workspace / project_id
        chapter_file = project_dir / f"chapter_{chapter_num:02d}.txt"
        with open(chapter_file, 'w') as f:
            f.write(f"# Chapter {chapter_num}: {chapter_title}\n\n")
            f.write(content)
        
        print(f"✓ Added Chapter {chapter_num}: {chapter_title}")
        print(f"  Words: {chapter['word_count']:,}")
    
    def update_word_count(self, project_id: str):
        """Update total word count"""
        total = sum(ch['word_count'] for ch in self.projects[project_id]['chapters'])
        self.projects[project_id]['current_words'] = total
    
    def export_manuscript(self, project_id: str, format: str = 'txt'):
        """Export complete manuscript"""
        if project_id not in self.projects:
            print(f"✗ Project not found: {project_id}")
            return
        
        project = self.projects[project_id]
        project_dir = self.workspace / project_id
        
        # Compile all chapters
        manuscript = []
        manuscript.append(f"# {project['title']}\n")
        manuscript.append(f"Genre: {project['genre']}\n")
        manuscript.append(f"Total Words: {project['current_words']:,}\n")
        manuscript.append("\n" + "="*80 + "\n\n")
        
        for chapter in project['chapters']:
            manuscript.append(f"## Chapter {chapter['number']}: {chapter['title']}\n\n")
            manuscript.append(chapter['content'])
            manuscript.append("\n\n" + "-"*80 + "\n\n")
        
        # Save manuscript
        output_file = project_dir / f"manuscript.{format}"
        with open(output_file, 'w') as f:
            f.write('\n'.join(manuscript))
        
        print(f"✓ Exported manuscript: {output_file}")
        print(f"  Format: {format}")
        print(f"  Total words: {project['current_words']:,}")
        
        return str(output_file)
    
    def list_projects(self):
        """List all projects"""
        if not self.projects:
            print("No projects found. Create one with 'create' command.")
            return
        
        print("\n📚 BOOK PROJECTS\n")
        for pid, project in self.projects.items():
            progress = (project['current_words'] / project['target_words']) * 100
            print(f"  • {project['title']}")
            print(f"    ID: {pid}")
            print(f"    Genre: {project['genre']}")
            print(f"    Progress: {project['current_words']:,} / {project['target_words']:,} words ({progress:.1f}%)")
            print(f"    Chapters: {len(project['chapters'])}")
            print(f"    Status: {project['status']}")
            print()

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='THE FORGE AI - Book Writing System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create new book project')
    create_parser.add_argument('title', help='Book title')
    create_parser.add_argument('--genre', default='Fiction', help='Book genre')
    create_parser.add_argument('--words', type=int, default=50000, help='Target word count')
    
    # Add chapter
    chapter_parser = subparsers.add_parser('chapter', help='Add chapter')
    chapter_parser.add_argument('project_id', help='Project ID')
    chapter_parser.add_argument('title', help='Chapter title')
    chapter_parser.add_argument('--content', default='', help='Chapter content')
    
    # Export
    export_parser = subparsers.add_parser('export', help='Export manuscript')
    export_parser.add_argument('project_id', help='Project ID')
    export_parser.add_argument('--format', default='txt', choices=['txt', 'md'], help='Export format')
    
    # List
    subparsers.add_parser('list', help='List all projects')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    system = BookWritingSystem()
    
    if args.command == 'create':
        system.create_project(args.title, args.genre, args.words)
    elif args.command == 'chapter':
        system.add_chapter(args.project_id, args.title, args.content)
    elif args.command == 'export':
        system.export_manuscript(args.project_id, args.format)
    elif args.command == 'list':
        system.list_projects()

if __name__ == '__main__':
    main()
