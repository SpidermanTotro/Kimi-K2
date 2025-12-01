"""
THE FORGE AI - Advanced Book Writing System
Enhanced book creation with advanced publishing and collaboration tools
"""

import os
import json
import datetime
from typing import Dict, List, Any
import re

class AdvancedBookWritingSystem:
    """Complete advanced book writing and publishing platform"""
    
    def __init__(self):
        self.books = {}
        self.genres = self.load_genres()
        self.templates = self.load_advanced_templates()
        self.characters = {}
        self.plots = {}
        self.publishing_tools = PublishingTools()
    
    def load_genres(self) -> Dict[str, Dict]:
        """Load genre-specific configurations"""
        return {
            "fantasy": {
                "themes": ["magic", "adventure", "mythical creatures", "quests"],
                "structure": "three_act",
                "pacing": "epic",
                "word_count_target": 80000,
                "chapter_count": 20,
                "character_archetypes": ["hero", "mentor", "villain", "sidekick"]
            },
            "romance": {
                "themes": ["love", "relationships", "emotional journey", "conflict"],
                "structure": "meet_cute_to_resolution",
                "pacing": "emotional",
                "word_count_target": 60000,
                "chapter_count": 15,
                "character_archetypes": ["protagonist", "love_interest", "obstacle", "support"]
            },
            "thriller": {
                "themes": ["suspense", "danger", "mystery", "psychological tension"],
                "structure": "rising_tension",
                "pacing": "fast",
                "word_count_target": 70000,
                "chapter_count": 18,
                "character_archetypes": ["detective", "victim", "suspect", "witness"]
            },
            "scifi": {
                "themes": ["technology", "future", "space", "artificial intelligence"],
                "structure": "discovery_to_resolution",
                "pacing": "thoughtful",
                "word_count_target": 75000,
                "chapter_count": 16,
                "character_archetypes": ["scientist", "explorer", "ai", "alien"]
            },
            "mystery": {
                "themes": ["crime", "investigation", "clues", "revelation"],
                "structure": "crime_to_solution",
                "pacing": "investigative",
                "word_count_target": 65000,
                "chapter_count": 17,
                "character_archetypes": ["detective", "suspects", "victim", "witness"]
            }
        }
    
    def load_advanced_templates(self) -> Dict[str, str]:
        """Load advanced writing templates"""
        return {
            "fantasy_epic": '''# [BOOK_TITLE]
*An Epic Fantasy Adventure*

## Prologue: The Ancient Prophecy

In the realm of [REALM_NAME], where magic flows like rivers and dragons soar across azure skies, an ancient prophecy stirs. The chosen one, [PROTAGONIST_NAME], must embark on a perilous quest to [MAIN_GOAL].

## Chapter 1: The Call to Adventure

[PROTAGONIST_NAME] lived a simple life in [VILLAGE_NAME] until the fateful day when [INCITING_INCIDENT]. The wise mentor, [MENTOR_NAME], revealed the truth about their destiny...

## Chapter Structure Template
- Introduction: Setting the scene and character
- Rising Action: Challenge or obstacle appears
- Climax: Major confrontation or revelation
- Resolution: Chapter conclusion and setup for next

Each chapter should be approximately 3,000-4,000 words for optimal pacing.
''',
            "psychological_thriller": '''# [BOOK_TITLE]
*A Psychological Thriller*

## Chapter 1: The Incident

The rain fell in sheets against the window as [PROTAGONIST_NAME] made the discovery that would change everything. What seemed like a routine investigation into [CASE_TYPE] quickly spiraled into something far more sinister.

## Psychological Elements
- Build tension through internal monologue
- Use unreliable narration techniques
- Plant subtle clues throughout
- Create moral ambiguity
- Employ twist endings

## Pacing Guide
- Chapters 1-5: Setup and initial mystery
- Chapters 6-10: Rising stakes and complications
- Chapters 11-15: Climax and resolution
''',
            "romance_contemporary": '''# [BOOK_TITLE]
*A Contemporary Romance*

## Chapter 1: Unexpected Meeting

[PROTAGONIST_1] never expected to meet someone like [PROTAGONIST_2] at [LOCATION]. The moment their eyes met across [SCENE_DESCRIPTION], sparks flew that neither could deny.

## Romance Structure
- Meet Cute: Initial encounter with chemistry
- Development: Growing connection and vulnerability
- Conflict: External or internal obstacles
- Resolution: Overcoming obstacles and commitment

## Character Development
- Show, don't tell emotional growth
- Create believable internal conflicts
- Develop supporting cast relationships
- Use dialogue to reveal character depth
'''
        }
    
    def create_advanced_book(self, title: str, author: str, genre: str, 
                           word_count_target: int = None, themes: List[str] = None) -> Dict[str, Any]:
        """Create advanced book with genre-specific configuration"""
        try:
            if genre not in self.genres:
                return {"success": False, "error": f"Genre '{genre}' not supported"}
            
            genre_config = self.genres[genre]
            book_id = f"book_{len(self.books) + 1}"
            
            # Set word count target
            if word_count_target is None:
                word_count_target = genre_config["word_count_target"]
            
            # Set themes
            if themes is None:
                themes = genre_config["themes"]
            
            # Create book structure
            book_structure = {
                "title": title,
                "author": author,
                "genre": genre,
                "book_id": book_id,
                "created_at": datetime.datetime.now().isoformat(),
                "word_count_target": word_count_target,
                "current_word_count": 0,
                "themes": themes,
                "structure": genre_config["structure"],
                "pacing": genre_config["pacing"],
                "chapter_count_target": genre_config["chapter_count"],
                "chapters": [],
                "characters": [],
                "plot_outline": [],
                "status": "outline",
                "progress_percentage": 0
            }
            
            # Generate chapter outlines
            book_structure["chapters"] = self.generate_chapter_outlines(
                genre_config["chapter_count"], genre, themes
            )
            
            self.books[book_id] = book_structure
            
            return {
                "success": True,
                "book_id": book_id,
                "title": title,
                "genre": genre,
                "chapter_count": len(book_structure["chapters"]),
                "word_count_target": word_count_target,
                "structure_generated": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_chapter_outlines(self, chapter_count: int, genre: str, themes: List[str]) -> List[Dict]:
        """Generate chapter outlines based on genre and themes"""
        outlines = []
        
        for i in range(1, chapter_count + 1):
            chapter = {
                "chapter_number": i,
                "title": f"Chapter {i}",
                "word_count_target": 3000,
                "current_word_count": 0,
                "content": "",
                "summary": "",
                "key_events": [],
                "characters_present": [],
                "settings": [],
                "themes_developed": [],
                "status": "outline"
            }
            
            # Add genre-specific chapter guidance
            if genre == "fantasy":
                if i == 1:
                    chapter["summary"] = "Introduction to protagonist and ordinary world"
                    chapter["key_events"] = ["Meet main character", "Establish setting", "Foreshadowing of adventure"]
                elif i == chapter_count // 3:
                    chapter["summary"] = "Call to adventure and journey begins"
                    chapter["key_events"] = ["Inciting incident", "Mentor appears", "Quest accepted"]
                elif i == 2 * chapter_count // 3:
                    chapter["summary"] = "Major confrontation or revelation"
                    chapter["key_events"] = ["Dark moment", "Truth revealed", "Allies tested"]
                elif i == chapter_count:
                    chapter["summary"] = "Final confrontation and resolution"
                    chapter["key_events"] = ["Final battle", "Victory achieved", "New beginning"]
            
            elif genre == "romance":
                if i == 1:
                    chapter["summary"] = "First meeting of main characters"
                    chapter["key_events"] = ["Meet cute", "Initial attraction", "Obstacle introduced"]
                elif i == chapter_count // 2:
                    chapter["summary"] = "Relationship development and complications"
                    chapter["key_events"] = ["Deeper connection", "Vulnerability shared", "Conflict arises"]
                elif i == chapter_count:
                    chapter["summary"] = "Resolution and commitment"
                    chapter["key_events"] = ["Obstacle overcome", "Love confirmed", "Future together"]
            
            outlines.append(chapter)
        
        return outlines
    
    def create_character(self, book_id: str, name: str, role: str, 
                        archetype: str = None, background: str = "") -> Dict[str, Any]:
        """Create detailed character with development arc"""
        try:
            if book_id not in self.books:
                return {"success": False, "error": "Book not found"}
            
            book = self.books[book_id]
            genre = book["genre"]
            
            character_id = f"char_{len(self.characters) + 1}"
            
            # Default archetype based on role
            if archetype is None:
                if role == "protagonist":
                    archetype = "hero"
                elif role == "antagonist":
                    archetype = "villain"
                elif role == "mentor":
                    archetype = "mentor"
                else:
                    archetype = "support"
            
            character = {
                "character_id": character_id,
                "name": name,
                "role": role,
                "archetype": archetype,
                "background": background,
                "physical_description": "",
                "personality_traits": [],
                "motivations": [],
                "fears": [],
                "goals": [],
                "character_arc": "transformation",
                "development_points": [],
                "relationships": {},
                "book_id": book_id
            }
            
            # Add archetype-specific traits
            if archetype == "hero":
                character["personality_traits"] = ["brave", "determined", "compassionate"]
                character["goals"] = ["save the world", "protect loved ones", "find truth"]
                character["development_points"] = [
                    "Reluctant hero accepting destiny",
                    "Learning to use powers/responsibility",
                    "Sacrifice for greater good"
                ]
            
            elif archetype == "villain":
                character["personality_traits"] = ["ambitious", "cunning", "ruthless"]
                character["motivations"] = ["power", "revenge", "control"]
                character["development_points"] = [
                    "Rise to power",
                    "Major confrontation with hero",
                    "Potential redemption or final defeat"
                ]
            
            elif archetype == "mentor":
                character["personality_traits"] = ["wise", "patient", "mysterious"]
                character["goals"] = ["guide protagonist", "maintain balance", "hidden agenda"]
                character["development_points"] = [
                    "Introduce protagonist to new world",
                    "Provide crucial knowledge/training",
                    "Sacrifice or transcendence"
                ]
            
            self.characters[character_id] = character
            book["characters"].append(character_id)
            
            return {
                "success": True,
                "character_id": character_id,
                "name": name,
                "role": role,
                "archetype": archetype,
                "development_points": len(character["development_points"])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_plot_outline(self, book_id: str, plot_type: str = "three_act") -> Dict[str, Any]:
        """Generate comprehensive plot outline"""
        try:
            if book_id not in self.books:
                return {"success": False, "error": "Book not found"}
            
            book = self.books[book_id]
            genre = book["genre"]
            chapter_count = book["chapter_count_target"]
            
            plot_outline = {
                "plot_type": plot_type,
                "acts": [],
                "key_plot_points": [],
                "subplots": [],
                "climax_position": int(chapter_count * 0.75),
                "resolution_position": chapter_count - 2
            }
            
            if plot_type == "three_act":
                # Act 1: Setup (25% of book)
                act1_end = int(chapter_count * 0.25)
                plot_outline["acts"].append({
                    "act": 1,
                    "title": "Setup",
                    "chapters": list(range(1, act1_end + 1)),
                    "purpose": "Introduce characters, establish normal world, inciting incident",
                    "key_events": ["Normal life", "Call to adventure", "Crossing threshold"]
                })
                
                # Act 2: Confrontation (50% of book)
                act2_start = act1_end + 1
                act2_end = int(chapter_count * 0.75)
                plot_outline["acts"].append({
                    "act": 2,
                    "title": "Confrontation",
                    "chapters": list(range(act2_start, act2_end + 1)),
                    "purpose": "Rising stakes, tests, allies/enemies, dark moment",
                    "key_events": ["Training/preparation", "First major test", "Allies gained", "Dark moment/revelation"]
                })
                
                # Act 3: Resolution (25% of book)
                act3_start = act2_end + 1
                plot_outline["acts"].append({
                    "act": 3,
                    "title": "Resolution",
                    "chapters": list(range(act3_start, chapter_count + 1)),
                    "purpose": "Final confrontation, climax, resolution, new normal",
                    "key_events": ["Final push", "Climax", "Falling action", "Resolution"]
                })
            
            book["plot_outline"] = plot_outline
            
            return {
                "success": True,
                "plot_type": plot_type,
                "acts": len(plot_outline["acts"]),
                "climax_chapter": plot_outline["climax_position"],
                "structure_generated": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_chapter_content(self, book_id: str, chapter_number: int, 
                            content: str, summary: str = "") -> Dict[str, Any]:
        """Write and analyze chapter content"""
        try:
            if book_id not in self.books:
                return {"success": False, "error": "Book not found"}
            
            book = self.books[book_id]
            chapters = book["chapters"]
            
            # Find the chapter
            chapter = None
            for ch in chapters:
                if ch["chapter_number"] == chapter_number:
                    chapter = ch
                    break
            
            if not chapter:
                return {"success": False, "error": f"Chapter {chapter_number} not found"}
            
            # Update chapter
            chapter["content"] = content
            chapter["current_word_count"] = len(content.split())
            chapter["status"] = "written"
            
            if summary:
                chapter["summary"] = summary
            
            # Analyze content
            analysis = self.analyze_chapter_content(content, book["genre"])
            chapter.update(analysis)
            
            # Update book progress
            self.update_book_progress(book_id)
            
            return {
                "success": True,
                "chapter_number": chapter_number,
                "word_count": chapter["current_word_count"],
                "analysis": analysis,
                "book_progress": book["progress_percentage"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_chapter_content(self, content: str, genre: str) -> Dict[str, Any]:
        """Analyze chapter content for quality and genre compliance"""
        word_count = len(content.split())
        sentences = len(re.split(r'[.!?]+', content))
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        
        analysis = {
            "word_count": word_count,
            "sentence_count": sentences,
            "paragraph_count": paragraphs,
            "avg_sentence_length": word_count / sentences if sentences > 0 else 0,
            "avg_paragraph_length": word_count / paragraphs if paragraphs > 0 else 0,
            "dialogue_percentage": self.calculate_dialogue_percentage(content),
            "pacing_score": self.calculate_pacing_score(content),
            "genre_compliance": self.check_genre_compliance(content, genre),
            "suggestions": self.generate_writing_suggestions(content, genre)
        }
        
        return analysis
    
    def calculate_dialogue_percentage(self, content: str) -> float:
        """Calculate percentage of content that is dialogue"""
        dialogue_matches = re.findall(r'"[^"]*"', content)
        dialogue_words = sum(len(match.split()) for match in dialogue_matches)
        total_words = len(content.split())
        return (dialogue_words / total_words * 100) if total_words > 0 else 0
    
    def calculate_pacing_score(self, content: str) -> float:
        """Calculate pacing score based on sentence length variation"""
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) < 2:
            return 50.0
        
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if not lengths:
            return 50.0
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        
        # Good pacing has moderate variation (not too uniform, not too chaotic)
        if variance < 4:
            return 60.0  # Too uniform
        elif variance > 25:
            return 70.0  # Too chaotic
        else:
            return 85.0  # Good variation
    
    def check_genre_compliance(self, content: str, genre: str) -> Dict[str, Any]:
        """Check if content follows genre conventions"""
        compliance = {"score": 75.0, "issues": [], "strengths": []}
        
        genre_keywords = {
            "fantasy": ["magic", "sword", "dragon", "kingdom", "quest", "ancient"],
            "romance": ["love", "heart", "kiss", "relationship", "feelings", "emotion"],
            "thriller": ["danger", "suspense", "mystery", "fear", "dark", "shadow"],
            "scifi": ["technology", "future", "space", "computer", "data", "system"],
            "mystery": ["clue", "detective", "evidence", "case", "suspect", "investigation"]
        }
        
        if genre in genre_keywords:
            keywords = genre_keywords[genre]
            content_lower = content.lower()
            found_keywords = [kw for kw in keywords if kw in content_lower]
            
            if len(found_keywords) >= 3:
                compliance["strengths"].append(f"Good use of genre-specific keywords: {found_keywords}")
                compliance["score"] += 10
            elif len(found_keywords) == 0:
                compliance["issues"].append("No genre-specific keywords detected")
                compliance["score"] -= 15
        
        return compliance
    
    def generate_writing_suggestions(self, content: str, genre: str) -> List[str]:
        """Generate writing improvement suggestions"""
        suggestions = []
        
        word_count = len(content.split())
        
        if word_count < 500:
            suggestions.append("Consider adding more detail to reach target chapter length")
        elif word_count > 5000:
            suggestions.append("Chapter is quite long - consider splitting or tightening")
        
        dialogue_pct = self.calculate_dialogue_percentage(content)
        if dialogue_pct < 20:
            suggestions.append("Add more dialogue to improve character engagement")
        elif dialogue_pct > 60:
            suggestions.append("Balance dialogue with narrative description")
        
        # Genre-specific suggestions
        if genre == "fantasy" and "magic" not in content.lower():
            suggestions.append("Consider incorporating magical elements")
        
        if genre == "romance" and "love" not in content.lower():
            suggestions.append("Emphasize emotional connection between characters")
        
        if genre == "thriller" and len(re.findall(r'[.!?]+', content)) / len(content.split()) < 0.1:
            suggestions.append("Use shorter sentences to increase tension")
        
        return suggestions
    
    def update_book_progress(self, book_id: str):
        """Update overall book progress"""
        try:
            if book_id not in self.books:
                return
            
            book = self.books[book_id]
            chapters = book["chapters"]
            
            total_words = sum(ch["current_word_count"] for ch in chapters)
            target_words = book["word_count_target"]
            
            book["current_word_count"] = total_words
            book["progress_percentage"] = (total_words / target_words * 100) if target_words > 0 else 0
            
            # Update status
            if book["progress_percentage"] >= 100:
                book["status"] = "completed"
            elif book["progress_percentage"] >= 75:
                book["status"] = "editing"
            elif book["progress_percentage"] >= 25:
                book["status"] = "writing"
            elif book["progress_percentage"] > 0:
                book["status"] = "in_progress"
            
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def get_publishing_readiness(self, book_id: str) -> Dict[str, Any]:
        """Assess book readiness for publishing"""
        try:
            if book_id not in self.books:
                return {"success": False, "error": "Book not found"}
            
            book = self.books[book_id]
            
            readiness_score = 0
            max_score = 100
            issues = []
            strengths = []
            
            # Word count check
            if book["current_word_count"] >= book["word_count_target"] * 0.9:
                readiness_score += 25
                strengths.append("Word count target met")
            else:
                issues.append(f"Word count: {book['current_word_count']}/{book['word_count_target']}")
            
            # Chapter completion
            completed_chapters = sum(1 for ch in book["chapters"] if ch["status"] == "written")
            if completed_chapters >= len(book["chapters"]) * 0.9:
                readiness_score += 25
                strengths.append("Most chapters completed")
            else:
                issues.append(f"Chapters completed: {completed_chapters}/{len(book['chapters'])}")
            
            # Character development
            if len(book["characters"]) >= 3:
                readiness_score += 15
                strengths.append("Good character development")
            else:
                issues.append("Need more character development")
            
            # Plot structure
            if book["plot_outline"]:
                readiness_score += 15
                strengths.append("Plot structure defined")
            else:
                issues.append("Plot outline missing")
            
            # Content quality
            avg_word_count = sum(ch["current_word_count"] for ch in book["chapters"]) / len(book["chapters"])
            if avg_word_count >= 2000:
                readiness_score += 10
                strengths.append("Adequate chapter length")
            else:
                issues.append("Chapters need more content")
            
            # Publishing recommendations
            recommendations = []
            if readiness_score >= 80:
                recommendations.append("Ready for beta readers")
            if readiness_score >= 90:
                recommendations.append("Ready for professional editing")
            if readiness_score >= 95:
                recommendations.append("Ready for publishing")
            
            return {
                "success": True,
                "readiness_score": readiness_score,
                "max_score": max_score,
                "issues": issues,
                "strengths": strengths,
                "recommendations": recommendations,
                "next_steps": self.get_next_publishing_steps(readiness_score)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_next_publishing_steps(self, readiness_score: int) -> List[str]:
        """Get recommended next steps based on readiness score"""
        if readiness_score < 50:
            return [
                "Complete missing chapters",
                "Develop main characters",
                "Create plot outline",
                "Increase word count"
            ]
        elif readiness_score < 70:
            return [
                "Finish remaining chapters",
                "Enhance character arcs",
                "Review pacing",
                "Add descriptive details"
            ]
        elif readiness_score < 85:
            return [
                "Complete all chapters",
                "Review plot consistency",
                "Beta reader feedback",
                "Professional editing"
            ]
        else:
            return [
                "Final polish and proofreading",
                "Cover design",
                "Formatting for publication",
                "Marketing strategy"
            ]


class PublishingTools:
    """Tools for book publishing and marketing"""
    
    def __init__(self):
        self.publishers = self.load_publishers()
        self.marketing_strategies = self.load_marketing_strategies()
    
    def load_publishers(self) -> Dict[str, Dict]:
        """Load publisher information"""
        return {
            "traditional": {
                "top_publishers": [
                    "Penguin Random House", "HarperCollins", "Simon & Schuster",
                    "Macmillan", "Hachette Book Group"
                ],
                "submission_requirements": [
                    "Query letter", "Synopsis", "Sample chapters",
                    "Author bio", "Marketing plan"
                ],
                "timeline": "6-18 months",
                "royalty_rate": "10-15%"
            },
            "self_publishing": {
                "platforms": [
                    "Amazon KDP", "Apple Books", "Google Play",
                    "Kobo Writing Life", "Barnes & Noble Press"
                ],
                "requirements": [
                    "Formatted manuscript", "Cover design",
                    "Book description", "Author platform"
                ],
                "timeline": "1-4 weeks",
                "royalty_rate": "35-70%"
            }
        }
    
    def load_marketing_strategies(self) -> Dict[str, List[str]]:
        """Load marketing strategies"""
        return {
            "pre_launch": [
                "Build author website",
                "Create social media presence",
                "Start email newsletter",
                "Cover reveal campaign",
                "ARC reader recruitment"
            ],
            "launch": [
                "Book launch event",
                "Social media blitz",
                "Email announcement",
                "Promotional pricing",
                "Blog tour"
            ],
            "post_launch": [
                "Reader engagement",
                "Review solicitation",
                "Continue content creation",
                "Paid advertising",
                "Cross-promotion"
            ]
        }
    
    def generate_marketing_plan(self, genre: str, target_audience: str) -> Dict[str, Any]:
        """Generate customized marketing plan"""
        plan = {
            "genre": genre,
            "target_audience": target_audience,
            "timeline": {},
            "budget_categories": {},
            "key_metrics": []
        }
        
        # Genre-specific strategies
        if genre == "fantasy":
            plan["timeline"] = {
                "3_months_pre": "World-building teasers on social media",
                "1_month_pre": "Character reveals and map releases",
                "launch_week": "Fantasy blog tour and giveaway",
                "post_launch": "Reader Q&A and fan art contests"
            }
        elif genre == "romance":
            plan["timeline"] = {
                "3_months_pre": "Behind-the-scenes writing process",
                "1_month_pre": "Meet the characters campaign",
                "launch_week": "Romance reader outreach",
                "post_launch": "Book club discussions"
            }
        
        plan["budget_categories"] = {
            "cover_design": "200-1000",
            "editing": "500-3000",
            "marketing": "100-500",
            "advertising": "200-1000",
            "website": "100-500"
        }
        
        plan["key_metrics"] = [
            "Sales numbers", "Review count", "Social media engagement",
            "Email list growth", "Website traffic", "Amazon ranking"
        ]
        
        return plan

# Initialize the advanced book writing system
advanced_book_system = AdvancedBookWritingSystem()