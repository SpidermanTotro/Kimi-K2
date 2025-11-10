"""
Dialogue Generator Module

Provides natural dialogue generation for characters with support for:
- Multi-character conversations
- Emotional context and subtext
- Character voice consistency
- NPC dialogue for games
- Screenplay-style formatting
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DialogueStyle(Enum):
    """Dialogue formatting styles"""
    PROSE = "prose"  # Novel-style
    SCREENPLAY = "screenplay"  # Script format
    GAME = "game"  # Game dialogue tree
    CHAT = "chat"  # Chat/messaging format


@dataclass
class DialogueLine:
    """Single line of dialogue"""
    character: str
    text: str
    emotion: Optional[str] = None
    action: Optional[str] = None  # Character action while speaking
    subtext: Optional[str] = None  # What they're really thinking


@dataclass
class DialogueContext:
    """Context for dialogue generation"""
    scene_description: str
    characters_present: List[str]
    emotional_state: Dict[str, str] = field(default_factory=dict)
    goals: Dict[str, str] = field(default_factory=dict)  # What each character wants
    relationships: Dict[Tuple[str, str], str] = field(default_factory=dict)


class DialogueGenerator:
    """
    Natural dialogue generation engine for Kimi-K2
    
    Features:
    - Multi-character conversations with natural flow
    - Character-specific voices and speech patterns
    - Emotional subtext and character goals
    - NPC dialogue for games with branching
    - Multiple formatting styles
    
    Example:
        >>> generator = DialogueGenerator()
        >>> context = DialogueContext(
        ...     scene_description="A tense negotiation in a dimly lit room",
        ...     characters_present=["Detective", "Suspect"],
        ...     emotional_state={"Detective": "suspicious", "Suspect": "nervous"}
        ... )
        >>> dialogue = generator.generate_conversation(
        ...     context,
        ...     num_exchanges=5,
        ...     style=DialogueStyle.SCREENPLAY
        ... )
    """
    
    def __init__(self, kimi_client=None):
        """Initialize dialogue generator"""
        self.kimi_client = kimi_client
        self._character_voices = {}
    
    def define_character_voice(
        self,
        character_name: str,
        traits: List[str],
        speech_patterns: List[str],
        vocabulary: str = "standard"  # "simple", "standard", "formal", "technical"
    ):
        """
        Define character's unique voice and speech patterns
        
        Args:
            character_name: Character name
            traits: Personality traits affecting speech
            speech_patterns: Specific patterns (e.g., "uses metaphors", "speaks in short sentences")
            vocabulary: Vocabulary complexity level
        """
        self._character_voices[character_name] = {
            "traits": traits,
            "patterns": speech_patterns,
            "vocabulary": vocabulary
        }
    
    def generate_conversation(
        self,
        context: DialogueContext,
        num_exchanges: int = 10,
        style: DialogueStyle = DialogueStyle.PROSE,
        include_actions: bool = True
    ) -> List[DialogueLine]:
        """
        Generate natural conversation between characters
        
        Args:
            context: Dialogue context and setup
            num_exchanges: Number of back-and-forth exchanges
            style: Formatting style
            include_actions: Include character actions
            
        Returns:
            List of dialogue lines
        """
        dialogue = []
        
        # In production: use Kimi-K2 for generation
        for i in range(num_exchanges):
            char_idx = i % len(context.characters_present)
            character = context.characters_present[char_idx]
            
            line = DialogueLine(
                character=character,
                text=f"[Generated dialogue for {character}]",
                emotion=context.emotional_state.get(character),
                action="[action]" if include_actions and i % 3 == 0 else None
            )
            dialogue.append(line)
        
        return dialogue
    
    def generate_npc_dialogue(
        self,
        npc_name: str,
        player_action: str,
        context: str,
        branching: bool = True
    ) -> Dict[str, any]:
        """
        Generate NPC dialogue for games with optional branching
        
        Args:
            npc_name: NPC character name
            player_action: What the player did/said
            context: Current game context
            branching: Generate dialogue tree with choices
            
        Returns:
            Dialogue data with optional branches
        """
        response = {
            "npc": npc_name,
            "response": f"[NPC response to: {player_action}]",
            "emotion": "neutral",
            "context": context
        }
        
        if branching:
            response["player_choices"] = [
                {"text": "[Choice 1]", "leads_to": "branch_1"},
                {"text": "[Choice 2]", "leads_to": "branch_2"},
                {"text": "[Choice 3]", "leads_to": "branch_3"},
            ]
        
        return response
    
    def format_dialogue(
        self,
        dialogue: List[DialogueLine],
        style: DialogueStyle
    ) -> str:
        """
        Format dialogue in specified style
        
        Args:
            dialogue: List of dialogue lines
            style: Formatting style
            
        Returns:
            Formatted dialogue text
        """
        formatted = []
        
        if style == DialogueStyle.PROSE:
            for line in dialogue:
                text = f'"{line.text}"'
                if line.action:
                    text = f'{line.character} {line.action}. {text}'
                else:
                    text = f'{line.character} said, {text}'
                formatted.append(text)
        
        elif style == DialogueStyle.SCREENPLAY:
            for line in dialogue:
                formatted.append(f"\n{line.character.upper()}")
                if line.action:
                    formatted.append(f"({line.action})")
                formatted.append(line.text)
        
        elif style == DialogueStyle.GAME:
            for line in dialogue:
                formatted.append(f"[{line.character}]: {line.text}")
        
        return "\n".join(formatted)
    
    def add_subtext(
        self,
        dialogue: List[DialogueLine],
        analyze: bool = True
    ) -> List[DialogueLine]:
        """
        Add or analyze emotional subtext in dialogue
        
        Args:
            dialogue: Dialogue lines
            analyze: Analyze existing dialogue for subtext
            
        Returns:
            Dialogue with subtext added
        """
        # In production: use Kimi-K2 to analyze subtext
        for line in dialogue:
            if analyze and not line.subtext:
                line.subtext = "[Analyzed subtext]"
        
        return dialogue
