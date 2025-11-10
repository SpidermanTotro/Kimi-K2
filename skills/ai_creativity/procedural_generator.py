"""
Procedural Generator Module

Provides procedural content generation capabilities with support for:
- Dynamic script generation
- Branching storylines and narratives
- Quest and mission generation
- World and level generation
- Random but coherent content
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random


class GenerationType(Enum):
    """Types of procedural generation"""
    NARRATIVE = "narrative"  # Story branches
    QUEST = "quest"  # Game quests/missions
    WORLD = "world"  # World/environment
    CHARACTER = "character"  # Character generation
    DIALOGUE = "dialogue"  # Dynamic dialogue
    EVENT = "event"  # Random events


@dataclass
class Node:
    """Node in a branching structure"""
    id: str
    type: str
    content: str
    choices: List[Dict[str, str]] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    consequences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BranchingNarrative:
    """Branching narrative structure"""
    title: str
    start_node: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)


class ProceduralGenerator:
    """
    Procedural content generation engine for Kimi-K2
    
    Features:
    - Branching narrative and storyline generation
    - Dynamic quest and mission creation
    - Procedural world and character generation
    - Context-aware random content
    - Rule-based and AI-guided generation
    
    Example:
        >>> generator = ProceduralGenerator()
        >>> narrative = generator.create_branching_narrative(
        ...     "Mystery Investigation",
        ...     num_branches=3,
        ...     depth=4
        ... )
        >>> quest = generator.generate_quest(
        ...     quest_type="fetch",
        ...     difficulty="medium"
        ... )
    """
    
    def __init__(self, kimi_client=None, seed: Optional[int] = None):
        """
        Initialize procedural generator
        
        Args:
            kimi_client: Kimi-K2 client for AI generation
            seed: Random seed for reproducibility
        """
        self.kimi_client = kimi_client
        if seed is not None:
            random.seed(seed)
        self._templates = {}
        self._rules = {}
    
    def create_branching_narrative(
        self,
        title: str,
        num_branches: int = 3,
        depth: int = 3,
        theme: Optional[str] = None
    ) -> BranchingNarrative:
        """
        Create branching narrative structure
        
        Args:
            title: Narrative title
            num_branches: Branches per node
            depth: Maximum depth of tree
            theme: Optional theme/genre
            
        Returns:
            Branching narrative structure
        """
        narrative = BranchingNarrative(
            title=title,
            start_node="start"
        )
        
        # Generate start node
        start = Node(
            id="start",
            type="intro",
            content=f"[Opening of '{title}']",
            choices=[]
        )
        
        # Generate branches recursively
        self._generate_branches(narrative, start, num_branches, depth, 0)
        
        narrative.nodes[start.id] = start
        narrative.start_node = start.id
        
        return narrative
    
    def _generate_branches(
        self,
        narrative: BranchingNarrative,
        parent: Node,
        num_branches: int,
        max_depth: int,
        current_depth: int
    ):
        """Recursively generate narrative branches"""
        if current_depth >= max_depth:
            return
        
        for i in range(num_branches):
            node_id = f"{parent.id}_branch_{i}"
            
            node = Node(
                id=node_id,
                type="choice" if current_depth < max_depth - 1 else "ending",
                content=f"[Content for {node_id}]",
                choices=[]
            )
            
            narrative.nodes[node_id] = node
            
            parent.choices.append({
                "text": f"Choice {i + 1}",
                "leads_to": node_id,
                "condition": None
            })
            
            if current_depth < max_depth - 1:
                self._generate_branches(
                    narrative, node, num_branches, max_depth, current_depth + 1
                )
    
    def generate_quest(
        self,
        quest_type: str = "fetch",  # "fetch", "kill", "escort", "investigate", "puzzle"
        difficulty: str = "medium",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate game quest/mission
        
        Args:
            quest_type: Type of quest
            difficulty: Difficulty level
            context: World context for quest
            
        Returns:
            Quest data
        """
        quest = {
            "id": f"quest_{random.randint(1000, 9999)}",
            "type": quest_type,
            "difficulty": difficulty,
            "title": f"[Generated {quest_type} quest]",
            "description": f"[Quest description]",
            "objectives": [],
            "rewards": [],
            "npc_giver": f"[NPC name]",
            "location": f"[Location]"
        }
        
        # Generate objectives based on type
        if quest_type == "fetch":
            quest["objectives"] = [
                {"type": "collect", "item": "[item]", "quantity": random.randint(1, 10)},
                {"type": "return", "npc": "[npc]"}
            ]
        elif quest_type == "investigate":
            quest["objectives"] = [
                {"type": "visit", "location": "[location 1]"},
                {"type": "examine", "object": "[clue]"},
                {"type": "report", "npc": "[npc]"}
            ]
        
        return quest
    
    def generate_character(
        self,
        role: str = "npc",
        archetype: Optional[str] = None,
        include_backstory: bool = True
    ) -> Dict[str, Any]:
        """
        Procedurally generate character
        
        Args:
            role: Character role
            archetype: Character archetype (optional)
            include_backstory: Generate backstory
            
        Returns:
            Character data
        """
        character = {
            "name": self._generate_name(),
            "role": role,
            "archetype": archetype or random.choice([
                "warrior", "mage", "rogue", "cleric", "merchant"
            ]),
            "attributes": {
                "strength": random.randint(3, 18),
                "intelligence": random.randint(3, 18),
                "charisma": random.randint(3, 18)
            },
            "personality": random.sample([
                "brave", "cautious", "greedy", "kind", "cynical",
                "optimistic", "mysterious", "cheerful"
            ], 3)
        }
        
        if include_backstory:
            character["backstory"] = f"[Generated backstory for {character['name']}]"
        
        return character
    
    def _generate_name(self) -> str:
        """Generate random character name"""
        prefixes = ["Ar", "El", "Th", "Za", "Kr", "Val", "Mor"]
        middles = ["en", "or", "an", "il", "ad", "ex"]
        suffixes = ["dor", "wen", "ian", "is", "eth", "us"]
        
        return (
            random.choice(prefixes) +
            random.choice(middles) +
            random.choice(suffixes)
        )
    
    def generate_world_element(
        self,
        element_type: str,  # "location", "faction", "artifact", "event"
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate world-building element
        
        Args:
            element_type: Type of element to generate
            theme: Optional theme/setting
            
        Returns:
            World element data
        """
        element = {
            "type": element_type,
            "name": f"[Generated {element_type} name]",
            "description": f"[Description]"
        }
        
        if element_type == "location":
            element.update({
                "terrain": random.choice(["forest", "mountain", "desert", "plains"]),
                "climate": random.choice(["temperate", "cold", "hot", "tropical"]),
                "population": random.randint(100, 100000),
                "notable_features": []
            })
        elif element_type == "faction":
            element.update({
                "alignment": random.choice(["good", "neutral", "evil"]),
                "size": random.choice(["small", "medium", "large"]),
                "influence": random.randint(1, 10)
            })
        
        return element
    
    def add_generation_rule(
        self,
        name: str,
        rule_function: Callable,
        category: str = "general"
    ):
        """
        Add custom generation rule
        
        Args:
            name: Rule name
            rule_function: Function that generates content
            category: Rule category
        """
        if category not in self._rules:
            self._rules[category] = {}
        
        self._rules[category][name] = rule_function
    
    def generate_event(
        self,
        event_type: str = "random",
        context: Optional[Dict] = None,
        impact: str = "medium"  # "minor", "medium", "major"
    ) -> Dict[str, Any]:
        """
        Generate random event
        
        Args:
            event_type: Type of event
            context: Current context
            impact: Event impact level
            
        Returns:
            Event data
        """
        event = {
            "type": event_type,
            "title": f"[Event title]",
            "description": f"[Event description]",
            "impact": impact,
            "consequences": [],
            "duration": random.choice(["instant", "short", "long", "permanent"])
        }
        
        return event
    
    def generate_dialogue_tree(
        self,
        topic: str,
        depth: int = 3,
        personality: Optional[str] = None
    ) -> Dict[str, Node]:
        """
        Generate branching dialogue tree
        
        Args:
            topic: Dialogue topic
            depth: Tree depth
            personality: Speaker personality
            
        Returns:
            Dialogue tree as node dictionary
        """
        tree = {}
        
        start = Node(
            id="dialogue_start",
            type="greeting",
            content=f"[Greeting about {topic}]",
            choices=[]
        )
        
        tree[start.id] = start
        
        # Generate dialogue branches
        self._generate_dialogue_branches(tree, start, depth, 0)
        
        return tree
    
    def _generate_dialogue_branches(
        self,
        tree: Dict[str, Node],
        parent: Node,
        max_depth: int,
        current_depth: int
    ):
        """Generate dialogue tree branches"""
        if current_depth >= max_depth:
            return
        
        num_choices = random.randint(2, 4)
        
        for i in range(num_choices):
            node_id = f"{parent.id}_response_{i}"
            
            node = Node(
                id=node_id,
                type="response",
                content=f"[Response option {i + 1}]",
                choices=[]
            )
            
            tree[node_id] = node
            
            parent.choices.append({
                "text": f"[Player choice {i + 1}]",
                "leads_to": node_id
            })
            
            if current_depth < max_depth - 1:
                self._generate_dialogue_branches(tree, node, max_depth, current_depth + 1)
