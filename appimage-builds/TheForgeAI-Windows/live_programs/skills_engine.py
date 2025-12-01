#!/usr/bin/env python3
"""
THE FORGE - Live Skills Engine
Transforms ALL_SKILLS.md into executable capabilities
"""

import json
import re
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Skill:
    """Individual skill representation"""
    name: str
    category: str
    subcategory: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
            'capabilities': self.capabilities,
            'dependencies': self.dependencies,
            'examples': self.examples
        }


@dataclass
class SkillCategory:
    """Category of related skills"""
    name: str
    description: str
    skills: List[Skill] = field(default_factory=list)
    total_capabilities: int = 0
    
    def add_skill(self, skill: Skill):
        self.skills.append(skill)
        self.total_capabilities += len(skill.capabilities)
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'total_capabilities': self.total_capabilities,
            'skills': [s.to_dict() for s in self.skills]
        }


class SkillsEngine:
    """
    Live Skills Engine - Parses and executes skills from documentation
    """
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.categories: Dict[str, SkillCategory] = {}
        self.all_skills: List[Skill] = []
        self.skill_index: Dict[str, Skill] = {}
        
    def load_all_skills(self):
        """Load and parse ALL_SKILLS.md"""
        skills_file = self.docs_dir / "ALL_SKILLS.md"
        
        if not skills_file.exists():
            raise FileNotFoundError(f"Skills file not found: {skills_file}")
        
        print("🔥 Loading ALL SKILLS from documentation...")
        
        with open(skills_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse categories and skills
        self._parse_skills_document(content)
        
        print(f"✅ Loaded {len(self.categories)} categories")
        print(f"✅ Loaded {len(self.all_skills)} individual skills")
        print(f"✅ Total capabilities: {sum(c.total_capabilities for c in self.categories.values())}")
        
    def _parse_skills_document(self, content: str):
        """Parse the skills document structure"""
        
        # Define skill categories from the document
        categories = {
            "Programming & Code Skills": "programming",
            "Content & Book Writing": "content_writing",
            "Gaming Enhancement": "gaming",
            "Video & Image Processing": "video_image",
            "Multimedia & Productivity": "multimedia",
            "GitHub & Version Control": "github",
            "File Handling & Processing": "file_handling",
            "AI/ML & Advanced Tech": "ai_ml",
            "DevOps & Deployment": "devops",
            "Security & Compliance": "security",
            "Ecosystem & Character Skills": "ecosystem",
            "Unique Forge Features": "forge_features"
        }
        
        # Parse each category
        for category_name, category_id in categories.items():
            category = SkillCategory(
                name=category_name,
                description=f"Skills related to {category_name.lower()}"
            )
            self.categories[category_id] = category
        
        # Extract skills from content
        self._extract_skills_from_content(content)
    
    def _extract_skills_from_content(self, content: str):
        """Extract individual skills and capabilities"""
        
        # Pattern to find skill sections
        lines = content.split('\n')
        current_category = None
        current_subcategory = None
        current_skill = None
        
        for line in lines:
            # Detect category headers (## 1️⃣ PROGRAMMING & CODE SKILLS)
            if re.match(r'^##\s+\d+.*?[A-Z\s&]+$', line):
                category_text = re.sub(r'^##\s+\d+.*?\s+', '', line).strip()
                current_category = self._map_category(category_text)
                current_subcategory = None
                current_skill = None
            
            # Detect subcategory headers (### Code Generation)
            elif line.startswith('###'):
                current_subcategory = line.replace('###', '').strip()
                # Extract capability count if present
                match = re.search(r'\((\d+)\s+capabilities?\)', current_subcategory)
                if match:
                    current_subcategory = re.sub(r'\s*\(\d+\s+capabilities?\)', '', current_subcategory)
            
            # Detect skill items (✅ **Multi-Language Support:**)
            elif line.strip().startswith('✅'):
                skill_text = line.replace('✅', '').strip()
                skill_name = re.sub(r'\*\*|\:', '', skill_text).strip()
                
                if current_category and current_subcategory:
                    skill = Skill(
                        name=skill_name,
                        category=current_category,
                        subcategory=current_subcategory,
                        description=f"{skill_name} in {current_subcategory}"
                    )
                    current_skill = skill
                    self.all_skills.append(skill)
                    self.skill_index[skill_name.lower()] = skill
                    
                    if current_category in self.categories:
                        self.categories[current_category].add_skill(skill)
            
            # Detect capability items (- Python (advanced, all versions))
            elif current_skill and line.strip().startswith('-'):
                capability = line.strip()[1:].strip()
                if capability:
                    current_skill.capabilities.append(capability)
    
    def _map_category(self, category_text: str) -> Optional[str]:
        """Map category text to category ID"""
        mapping = {
            "PROGRAMMING & CODE SKILLS": "programming",
            "CONTENT & BOOK WRITING": "content_writing",
            "GAMING ENHANCEMENT": "gaming",
            "VIDEO & IMAGE PROCESSING": "video_image",
            "MULTIMEDIA & PRODUCTIVITY": "multimedia",
            "GITHUB & VERSION CONTROL": "github",
            "FILE HANDLING & PROCESSING": "file_handling",
            "AI/ML & ADVANCED TECH": "ai_ml",
            "DEVOPS & DEPLOYMENT": "devops",
            "SECURITY & COMPLIANCE": "security",
            "ECOSYSTEM & CHARACTER SKILLS": "ecosystem",
            "UNIQUE FORGE FEATURES": "forge_features"
        }
        return mapping.get(category_text.upper())
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category"""
        if category in self.categories:
            return self.categories[category].skills
        return []
    
    def search_skills(self, query: str) -> List[Skill]:
        """Search for skills by name or capability"""
        query_lower = query.lower()
        results = []
        
        for skill in self.all_skills:
            if query_lower in skill.name.lower():
                results.append(skill)
            elif any(query_lower in cap.lower() for cap in skill.capabilities):
                results.append(skill)
        
        return results
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        return self.skill_index.get(skill_name.lower())
    
    def export_to_json(self, output_file: str = "skills_database.json"):
        """Export all skills to JSON"""
        data = {
            'categories': {k: v.to_dict() for k, v in self.categories.items()},
            'total_skills': len(self.all_skills),
            'total_capabilities': sum(c.total_capabilities for c in self.categories.values())
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported skills database to {output_file}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about loaded skills"""
        return {
            'total_categories': len(self.categories),
            'total_skills': len(self.all_skills),
            'total_capabilities': sum(c.total_capabilities for c in self.categories.values()),
            'categories': {
                name: {
                    'skills': len(cat.skills),
                    'capabilities': cat.total_capabilities
                }
                for name, cat in self.categories.items()
            }
        }
    
    def execute_skill(self, skill_name: str, **kwargs) -> Dict:
        """
        Execute a skill (placeholder for actual implementation)
        This would be extended to actually perform the skill
        """
        skill = self.get_skill(skill_name)
        
        if not skill:
            return {
                'success': False,
                'error': f'Skill not found: {skill_name}'
            }
        
        return {
            'success': True,
            'skill': skill.name,
            'category': skill.category,
            'subcategory': skill.subcategory,
            'capabilities': skill.capabilities,
            'message': f'Skill {skill_name} ready to execute'
        }


def main():
    """Main execution"""
    print("🔥 THE FORGE - Live Skills Engine")
    print("=" * 70)
    print()
    
    # Initialize engine
    engine = SkillsEngine(docs_dir="../docs")
    
    # Load all skills
    engine.load_all_skills()
    
    # Show statistics
    print("\n📊 Skills Statistics:")
    print("-" * 70)
    stats = engine.get_statistics()
    print(f"Total Categories: {stats['total_categories']}")
    print(f"Total Skills: {stats['total_skills']}")
    print(f"Total Capabilities: {stats['total_capabilities']}")
    
    print("\n📋 Category Breakdown:")
    for cat_name, cat_stats in stats['categories'].items():
        print(f"  {cat_name}: {cat_stats['skills']} skills, {cat_stats['capabilities']} capabilities")
    
    # Export to JSON
    print()
    engine.export_to_json("skills_database.json")
    
    # Example: Search for skills
    print("\n🔍 Example: Searching for 'Python' skills...")
    python_skills = engine.search_skills("Python")
    print(f"Found {len(python_skills)} Python-related skills")
    
    print("\n✅ Skills Engine Ready!")


if __name__ == "__main__":
    main()