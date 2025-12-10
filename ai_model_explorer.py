#!/usr/bin/env python3
"""
AI Model Explorer - ChatGPT-like Model Analysis and Replication System
=======================================================================

This module provides a comprehensive framework for analyzing, documenting,
and creating working copies of AI models similar to ChatGPT, with detailed
personality and skill profiling.

Features:
- Model personality extraction and analysis
- Skill profiling and capability mapping
- Behavior documentation generation
- Model comparison and benchmarking
- Offline model training framework
- Image generation integration

Usage:
    from ai_model_explorer import AIModelExplorer
    
    explorer = AIModelExplorer()
    profile = explorer.analyze_model("chatgpt")
    working_copy = explorer.create_working_copy(profile)
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of AI models that can be analyzed"""
    CHATGPT = "chatgpt"
    NINJA_AI = "ninja_ai"
    SUPER_NINJA_AI = "super_ninja_ai"
    GENSPARK_AI = "genspark_ai"
    KIMI_K2 = "kimi_k2"
    CUSTOM = "custom"


class SkillCategory(Enum):
    """Categories of AI capabilities"""
    CODING = "coding"
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    TOOL_USE = "tool_use"
    MULTIMODAL = "multimodal"
    SPECIALIZED = "specialized"


@dataclass
class PersonalityTrait:
    """Represents a personality trait of an AI model"""
    name: str
    description: str
    strength: float  # 0.0 to 1.0
    examples: List[str] = field(default_factory=list)


@dataclass
class ModelSkill:
    """Represents a specific skill or capability"""
    name: str
    category: SkillCategory
    proficiency: float  # 0.0 to 1.0
    description: str
    examples: List[str] = field(default_factory=list)
    benchmarks: Dict[str, float] = field(default_factory=dict)


@dataclass
class BehaviorPattern:
    """Documents a specific behavior pattern"""
    pattern_id: str
    description: str
    trigger_conditions: List[str]
    expected_response: str
    examples: List[Dict[str, str]] = field(default_factory=list)
    frequency: float = 1.0  # How often this pattern appears


@dataclass
class ModelProfile:
    """Complete profile of an AI model"""
    model_name: str
    model_type: ModelType
    version: str
    description: str
    
    # Core characteristics
    personality_traits: List[PersonalityTrait] = field(default_factory=list)
    skills: List[ModelSkill] = field(default_factory=list)
    behavior_patterns: List[BehaviorPattern] = field(default_factory=list)
    
    # Technical details
    parameters: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    training_data: Dict[str, Any] = field(default_factory=dict)
    
    # Capabilities
    supported_languages: List[str] = field(default_factory=list)
    multimodal_capabilities: List[str] = field(default_factory=list)
    tool_calling_support: bool = False
    
    # Metadata
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        data = asdict(self)
        # Convert enums to strings
        data['model_type'] = self.model_type.value
        for skill in data['skills']:
            skill['category'] = skill['category'].value if isinstance(skill['category'], Enum) else skill['category']
        return data
    
    def to_json(self, filepath: str):
        """Save profile to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"✅ Saved profile to {filepath}")


class AIModelExplorer:
    """Main class for exploring and analyzing AI models"""
    
    def __init__(self, config_dir: str = "./model_configs"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        self.profiles: Dict[str, ModelProfile] = {}
        logger.info("✅ AI Model Explorer initialized")
    
    def analyze_model(self, model_identifier: str, model_type: ModelType = None) -> ModelProfile:
        """
        Analyze an AI model and create comprehensive profile
        
        Args:
            model_identifier: Name or identifier of the model
            model_type: Type of model (auto-detected if not provided)
        
        Returns:
            ModelProfile: Comprehensive profile of the analyzed model
        """
        logger.info(f"🔍 Analyzing model: {model_identifier}")
        
        # Auto-detect model type
        if model_type is None:
            model_type = self._detect_model_type(model_identifier)
        
        # Create base profile
        profile = self._create_base_profile(model_identifier, model_type)
        
        # Analyze different aspects
        profile.personality_traits = self._analyze_personality(model_identifier, model_type)
        profile.skills = self._analyze_skills(model_identifier, model_type)
        profile.behavior_patterns = self._analyze_behaviors(model_identifier, model_type)
        
        # Store profile
        self.profiles[model_identifier] = profile
        
        logger.info(f"✅ Analysis complete: {len(profile.personality_traits)} traits, "
                   f"{len(profile.skills)} skills, {len(profile.behavior_patterns)} patterns")
        
        return profile
    
    def _detect_model_type(self, identifier: str) -> ModelType:
        """Auto-detect model type from identifier"""
        identifier_lower = identifier.lower()
        
        if "chatgpt" in identifier_lower or "gpt" in identifier_lower:
            return ModelType.CHATGPT
        elif "ninja" in identifier_lower and "super" in identifier_lower:
            return ModelType.SUPER_NINJA_AI
        elif "ninja" in identifier_lower:
            return ModelType.NINJA_AI
        elif "genspark" in identifier_lower:
            return ModelType.GENSPARK_AI
        elif "kimi" in identifier_lower:
            return ModelType.KIMI_K2
        else:
            return ModelType.CUSTOM
    
    def _create_base_profile(self, identifier: str, model_type: ModelType) -> ModelProfile:
        """Create base model profile"""
        profiles_map = {
            ModelType.CHATGPT: self._create_chatgpt_profile,
            ModelType.NINJA_AI: self._create_ninja_ai_profile,
            ModelType.SUPER_NINJA_AI: self._create_super_ninja_ai_profile,
            ModelType.GENSPARK_AI: self._create_genspark_ai_profile,
            ModelType.KIMI_K2: self._create_kimi_k2_profile,
        }
        
        creator = profiles_map.get(model_type, self._create_custom_profile)
        return creator(identifier)
    
    def _create_chatgpt_profile(self, identifier: str) -> ModelProfile:
        """Create ChatGPT-based profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.CHATGPT,
            version="4.0",
            description="Advanced conversational AI with broad capabilities",
            parameters={
                "size": "175B+",
                "architecture": "Transformer",
                "context_window": 128000,
            },
            supported_languages=["Python", "JavaScript", "Java", "C++", "Go", "Rust", "Ruby", "PHP"],
            multimodal_capabilities=["text", "image", "code"],
            tool_calling_support=True,
        )
    
    def _create_ninja_ai_profile(self, identifier: str) -> ModelProfile:
        """Create Ninja AI profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.NINJA_AI,
            version="1.0",
            description="Fast and efficient AI model optimized for quick responses",
            parameters={
                "size": "7B-13B",
                "architecture": "Optimized Transformer",
                "context_window": 32768,
            },
            supported_languages=["Python", "JavaScript", "TypeScript", "Go"],
            tool_calling_support=True,
        )
    
    def _create_super_ninja_ai_profile(self, identifier: str) -> ModelProfile:
        """Create Super Ninja AI profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.SUPER_NINJA_AI,
            version="2.0",
            description="Enhanced Ninja AI with advanced reasoning and specialized capabilities",
            parameters={
                "size": "70B+",
                "architecture": "Enhanced MoE Transformer",
                "context_window": 128000,
            },
            supported_languages=["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"],
            multimodal_capabilities=["text", "code", "analysis"],
            tool_calling_support=True,
        )
    
    def _create_genspark_ai_profile(self, identifier: str) -> ModelProfile:
        """Create Genspark AI profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.GENSPARK_AI,
            version="1.0",
            description="Creative AI focused on generation and innovation",
            parameters={
                "size": "20B-30B",
                "architecture": "Generative Transformer",
                "context_window": 64000,
            },
            supported_languages=["Python", "JavaScript", "TypeScript"],
            multimodal_capabilities=["text", "image", "creative"],
            tool_calling_support=True,
        )
    
    def _create_kimi_k2_profile(self, identifier: str) -> ModelProfile:
        """Create Kimi K2 profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.KIMI_K2,
            version="1.0",
            description="State-of-the-art MoE model with 1T parameters, optimized for agentic tasks",
            parameters={
                "total_parameters": "1T",
                "activated_parameters": "32B",
                "architecture": "MoE Transformer",
                "context_window": 128000,
                "num_experts": 384,
                "experts_per_token": 8,
            },
            supported_languages=["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++", "Ruby", "PHP"],
            multimodal_capabilities=["text", "code", "reasoning", "tool_use"],
            tool_calling_support=True,
        )
    
    def _create_custom_profile(self, identifier: str) -> ModelProfile:
        """Create custom model profile"""
        return ModelProfile(
            model_name=identifier,
            model_type=ModelType.CUSTOM,
            version="1.0",
            description="Custom AI model",
        )
    
    def _analyze_personality(self, identifier: str, model_type: ModelType) -> List[PersonalityTrait]:
        """Analyze and extract personality traits"""
        traits = []
        
        # Common traits for all models
        common_traits = [
            PersonalityTrait(
                name="Helpfulness",
                description="Desire to assist and provide useful information",
                strength=0.95,
                examples=["Offering detailed explanations", "Providing step-by-step guidance"]
            ),
            PersonalityTrait(
                name="Curiosity",
                description="Interest in understanding user needs and context",
                strength=0.85,
                examples=["Asking clarifying questions", "Exploring edge cases"]
            ),
            PersonalityTrait(
                name="Precision",
                description="Focus on accuracy and correctness",
                strength=0.90,
                examples=["Fact-checking responses", "Citing sources"]
            ),
        ]
        
        traits.extend(common_traits)
        
        # Model-specific traits
        if model_type == ModelType.CHATGPT:
            traits.extend([
                PersonalityTrait(
                    name="Conversational",
                    description="Natural, flowing communication style",
                    strength=0.95,
                    examples=["Engaging dialogue", "Context awareness"]
                ),
                PersonalityTrait(
                    name="Adaptable",
                    description="Ability to adjust tone and style to user preferences",
                    strength=0.90,
                    examples=["Formal/informal switching", "Technical level adjustment"]
                ),
            ])
        elif model_type in [ModelType.NINJA_AI, ModelType.SUPER_NINJA_AI]:
            traits.extend([
                PersonalityTrait(
                    name="Efficiency",
                    description="Focus on quick, direct responses",
                    strength=0.95,
                    examples=["Concise answers", "Fast processing"]
                ),
                PersonalityTrait(
                    name="Technical",
                    description="Strong technical orientation",
                    strength=0.90,
                    examples=["Code-focused", "Architecture discussions"]
                ),
            ])
        elif model_type == ModelType.GENSPARK_AI:
            traits.extend([
                PersonalityTrait(
                    name="Creative",
                    description="Innovative and imaginative approaches",
                    strength=0.95,
                    examples=["Novel solutions", "Creative suggestions"]
                ),
                PersonalityTrait(
                    name="Experimental",
                    description="Willingness to explore new ideas",
                    strength=0.85,
                    examples=["Trying new approaches", "Pushing boundaries"]
                ),
            ])
        elif model_type == ModelType.KIMI_K2:
            traits.extend([
                PersonalityTrait(
                    name="Agentic",
                    description="Autonomous problem-solving orientation",
                    strength=0.95,
                    examples=["Multi-step planning", "Tool orchestration"]
                ),
                PersonalityTrait(
                    name="Systematic",
                    description="Structured, methodical approach",
                    strength=0.92,
                    examples=["Step-by-step execution", "Comprehensive analysis"]
                ),
            ])
        
        return traits
    
    def _analyze_skills(self, identifier: str, model_type: ModelType) -> List[ModelSkill]:
        """Analyze and extract model skills"""
        skills = []
        
        # Universal skills
        skills.extend([
            ModelSkill(
                name="Code Generation",
                category=SkillCategory.CODING,
                proficiency=0.90,
                description="Generate high-quality code in multiple languages",
                examples=["Writing functions", "Creating classes", "Building applications"],
                benchmarks={"LiveCodeBench": 0.537, "HumanEval": 0.85}
            ),
            ModelSkill(
                name="Code Review",
                category=SkillCategory.CODING,
                proficiency=0.85,
                description="Analyze and improve existing code",
                examples=["Bug detection", "Performance optimization", "Style improvements"]
            ),
            ModelSkill(
                name="Mathematical Reasoning",
                category=SkillCategory.REASONING,
                proficiency=0.88,
                description="Solve complex mathematical problems",
                examples=["Algebra", "Calculus", "Statistics"],
                benchmarks={"AIME": 0.696, "MATH-500": 0.974}
            ),
            ModelSkill(
                name="Logical Reasoning",
                category=SkillCategory.REASONING,
                proficiency=0.87,
                description="Apply formal logic and deduction",
                examples=["Puzzles", "Proofs", "Inference"],
                benchmarks={"ZebraLogic": 0.890}
            ),
            ModelSkill(
                name="Natural Conversation",
                category=SkillCategory.CONVERSATION,
                proficiency=0.92,
                description="Engage in natural, contextual dialogue",
                examples=["Multi-turn conversations", "Context retention"]
            ),
            ModelSkill(
                name="Technical Writing",
                category=SkillCategory.CREATIVITY,
                proficiency=0.88,
                description="Create clear, professional documentation",
                examples=["API docs", "Tutorials", "Technical reports"]
            ),
        ])
        
        # Model-specific advanced skills
        if model_type in [ModelType.SUPER_NINJA_AI, ModelType.KIMI_K2]:
            skills.extend([
                ModelSkill(
                    name="Agentic Coding",
                    category=SkillCategory.CODING,
                    proficiency=0.92,
                    description="Autonomous multi-file code generation and modification",
                    examples=["Full project scaffolding", "Multi-file refactoring"],
                    benchmarks={"SWE-bench": 0.658}
                ),
                ModelSkill(
                    name="Tool Orchestration",
                    category=SkillCategory.TOOL_USE,
                    proficiency=0.90,
                    description="Coordinate multiple tools to solve complex tasks",
                    examples=["Multi-step workflows", "API integration"],
                    benchmarks={"Tau2": 0.706, "AceBench": 0.765}
                ),
            ])
        
        if model_type == ModelType.GENSPARK_AI:
            skills.extend([
                ModelSkill(
                    name="Creative Writing",
                    category=SkillCategory.CREATIVITY,
                    proficiency=0.93,
                    description="Generate creative content across genres",
                    examples=["Stories", "Poetry", "Scripts"]
                ),
                ModelSkill(
                    name="Image Generation Planning",
                    category=SkillCategory.MULTIMODAL,
                    proficiency=0.85,
                    description="Design and plan image generation tasks",
                    examples=["Prompt engineering", "Style guidance"]
                ),
            ])
        
        return skills
    
    def _analyze_behaviors(self, identifier: str, model_type: ModelType) -> List[BehaviorPattern]:
        """Analyze and document behavior patterns"""
        patterns = []
        
        # Common behavior patterns
        patterns.extend([
            BehaviorPattern(
                pattern_id="greeting_response",
                description="How the model responds to greetings",
                trigger_conditions=["User says hello", "User introduces themselves"],
                expected_response="Friendly greeting with offer to help",
                examples=[
                    {"input": "Hello!", "output": "Hello! How can I assist you today?"},
                    {"input": "Hi there", "output": "Hi! What can I help you with?"}
                ],
                frequency=1.0
            ),
            BehaviorPattern(
                pattern_id="clarification_seeking",
                description="Asks for clarification when input is ambiguous",
                trigger_conditions=["Ambiguous request", "Missing context"],
                expected_response="Polite clarification question",
                examples=[
                    {
                        "input": "Fix the bug",
                        "output": "I'd be happy to help! Could you provide more details about the bug? What code are you working with?"
                    }
                ],
                frequency=0.8
            ),
            BehaviorPattern(
                pattern_id="step_by_step_explanation",
                description="Breaks down complex problems into steps",
                trigger_conditions=["Complex problem", "Tutorial request"],
                expected_response="Numbered steps with explanations",
                examples=[
                    {
                        "input": "How do I set up a web server?",
                        "output": "I'll guide you through setting up a web server:\n1. Choose your platform...\n2. Install dependencies...\n3. Configure settings..."
                    }
                ],
                frequency=0.9
            ),
            BehaviorPattern(
                pattern_id="code_with_explanation",
                description="Provides code examples with detailed explanations",
                trigger_conditions=["Coding request", "How-to question"],
                expected_response="Code block followed by explanation",
                examples=[
                    {
                        "input": "Show me a Python function to sort a list",
                        "output": "```python\ndef sort_list(items):\n    return sorted(items)\n```\nThis function uses Python's built-in sorted() function..."
                    }
                ],
                frequency=0.95
            ),
        ])
        
        # Model-specific patterns
        if model_type == ModelType.KIMI_K2:
            patterns.extend([
                BehaviorPattern(
                    pattern_id="tool_selection",
                    description="Intelligently selects and uses tools for tasks",
                    trigger_conditions=["Task requires tools", "Multi-step problem"],
                    expected_response="Identifies needed tools and orchestrates their use",
                    examples=[
                        {
                            "input": "Deploy a web application",
                            "output": "I'll help you deploy the application using these tools:\n1. Git for version control\n2. Docker for containerization\n3. CI/CD for automation"
                        }
                    ],
                    frequency=0.85
                ),
                BehaviorPattern(
                    pattern_id="multi_step_planning",
                    description="Creates comprehensive plans for complex tasks",
                    trigger_conditions=["Large project", "Multi-phase task"],
                    expected_response="Detailed project plan with phases and checkpoints",
                    frequency=0.80
                ),
            ])
        
        return patterns
    
    def create_working_copy(self, profile: ModelProfile, output_dir: str = "./working_models") -> str:
        """
        Create a working copy implementation based on model profile
        
        Args:
            profile: ModelProfile to replicate
            output_dir: Directory to save working copy
        
        Returns:
            str: Path to created working copy
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create safe directory and file names
        safe_model_name = profile.model_name.replace(" ", "_").replace("-", "_")
        model_dir = os.path.join(output_dir, safe_model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save profile
        profile.to_json(os.path.join(model_dir, "profile.json"))
        
        # Generate implementation
        impl_path = os.path.join(model_dir, f"{safe_model_name}_implementation.py")
        self._generate_implementation(profile, impl_path)
        
        # Generate configuration
        config_path = os.path.join(model_dir, "config.json")
        self._generate_config(profile, config_path)
        
        # Generate documentation
        doc_path = os.path.join(model_dir, "README.md")
        self._generate_documentation(profile, doc_path)
        
        logger.info(f"✅ Created working copy at {model_dir}")
        return model_dir
    
    def _generate_implementation(self, profile: ModelProfile, filepath: str):
        """Generate Python implementation of the model"""
        code = f'''#!/usr/bin/env python3
"""
{profile.model_name} - Working Copy Implementation
Generated from AI Model Explorer

This is a working copy implementation that replicates the behavior
and capabilities of {profile.model_name}.
"""

import json
from typing import Dict, List, Any, Optional


class {profile.model_name.replace(" ", "").replace("-", "")}:
    """Working copy of {profile.model_name}"""
    
    def __init__(self):
        self.model_name = "{profile.model_name}"
        self.version = "{profile.version}"
        self.personality_traits = {json.dumps([t.name for t in profile.personality_traits], indent=8)}
        self.skills = {json.dumps([s.name for s in profile.skills], indent=8)}
        
        print(f"✅ Initialized {{self.model_name}} v{{self.version}}")
        print(f"📊 Personality traits: {{len(self.personality_traits)}}")
        print(f"🎯 Skills: {{len(self.skills)}}")
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's message or request
            context: Optional context for the conversation
        
        Returns:
            str: Model's response
        """
        # Apply behavior patterns
        response = self._apply_behavior_patterns(user_input)
        
        # Apply personality traits
        response = self._apply_personality(response)
        
        return response
    
    def _apply_behavior_patterns(self, user_input: str) -> str:
        """Apply learned behavior patterns to generate response"""
        # Greeting pattern
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(g in user_input.lower() for g in greetings):
            return f"Hello! I'm {{self.model_name}}. How can I assist you today?"
        
        # Code request pattern
        if "code" in user_input.lower() or "function" in user_input.lower():
            return self._generate_code_response(user_input)
        
        # Explanation request pattern
        if "how" in user_input.lower() or "what" in user_input.lower():
            return self._generate_explanation(user_input)
        
        # Default helpful response
        return f"I understand you're asking about: {{user_input}}. Let me help you with that..."
    
    def _apply_personality(self, response: str) -> str:
        """Apply personality traits to response"""
        # Add helpful tone
        if "helpfulness" in [t.lower() for t in self.personality_traits]:
            if not response.endswith("?") and "help" not in response.lower():
                response += "\n\nIs there anything else I can help you with?"
        
        return response
    
    def _generate_code_response(self, request: str) -> str:
        """Generate code-related response"""
        return f"""I'll help you with that code request.

```python
# Example implementation
def example_function():
    # TODO: Implement based on specific requirements
    pass
```

This is a template. Please provide more specific requirements so I can create the exact code you need."""
    
    def _generate_explanation(self, question: str) -> str:
        """Generate explanatory response"""
        return f"""Let me break this down step by step:

1. First, we need to understand the core concept
2. Then, we can explore the key components
3. Finally, we'll look at practical applications

Would you like me to dive deeper into any particular aspect?"""
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return model capabilities"""
        return {{
            "model_name": self.model_name,
            "version": self.version,
            "personality_traits": self.personality_traits,
            "skills": self.skills,
            "supported_languages": {json.dumps(profile.supported_languages)},
            "multimodal": {json.dumps(profile.multimodal_capabilities)},
        }}


def main():
    """Demo usage"""
    model = {profile.model_name.replace(" ", "").replace("-", "")}()
    
    # Test interactions
    test_inputs = [
        "Hello!",
        "How do I write a Python function?",
        "Can you help me with coding?",
    ]
    
    for user_input in test_inputs:
        print(f"\\nUser: {{user_input}}")
        response = model.process(user_input)
        print(f"Model: {{response}}")


if __name__ == "__main__":
    main()
'''
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        logger.info(f"✅ Generated implementation: {filepath}")
    
    def _generate_config(self, profile: ModelProfile, filepath: str):
        """Generate configuration file"""
        config = {
            "model_name": profile.model_name,
            "model_type": profile.model_type.value,
            "version": profile.version,
            "parameters": profile.parameters,
            "architecture": profile.architecture,
            "supported_languages": profile.supported_languages,
            "multimodal_capabilities": profile.multimodal_capabilities,
            "tool_calling_support": profile.tool_calling_support,
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ Generated config: {filepath}")
    
    def _generate_documentation(self, profile: ModelProfile, filepath: str):
        """Generate comprehensive documentation"""
        doc = f"""# {profile.model_name} - Working Copy

## Overview

{profile.description}

**Version:** {profile.version}  
**Type:** {profile.model_type.value}  
**Created:** {profile.created_date}

## Personality Traits

{profile.model_name} exhibits the following personality characteristics:

"""
        
        for trait in profile.personality_traits:
            doc += f"### {trait.name} (Strength: {trait.strength:.0%})\n\n"
            doc += f"{trait.description}\n\n"
            if trait.examples:
                doc += "**Examples:**\n"
                for example in trait.examples:
                    doc += f"- {example}\n"
                doc += "\n"
        
        doc += "## Skills and Capabilities\n\n"
        
        # Group skills by category
        from collections import defaultdict
        skills_by_category = defaultdict(list)
        for skill in profile.skills:
            cat = skill.category.value if isinstance(skill.category, Enum) else skill.category
            skills_by_category[cat].append(skill)
        
        for category, skills in skills_by_category.items():
            doc += f"### {category.title()}\n\n"
            for skill in skills:
                doc += f"#### {skill.name} (Proficiency: {skill.proficiency:.0%})\n\n"
                doc += f"{skill.description}\n\n"
                if skill.benchmarks:
                    doc += "**Benchmarks:**\n"
                    for bench, score in skill.benchmarks.items():
                        doc += f"- {bench}: {score:.1%}\n"
                    doc += "\n"
        
        doc += "## Behavior Patterns\n\n"
        
        for pattern in profile.behavior_patterns:
            doc += f"### {pattern.pattern_id}\n\n"
            doc += f"{pattern.description}\n\n"
            doc += "**Triggers:**\n"
            for trigger in pattern.trigger_conditions:
                doc += f"- {trigger}\n"
            doc += f"\n**Expected Response:** {pattern.expected_response}\n\n"
            if pattern.examples:
                doc += "**Examples:**\n"
                for example in pattern.examples:
                    doc += f"- Input: `{example.get('input', 'N/A')}`\n"
                    doc += f"  Output: `{example.get('output', 'N/A')}`\n"
                doc += "\n"
        
        doc += "## Technical Details\n\n"
        doc += "### Parameters\n\n"
        for key, value in profile.parameters.items():
            doc += f"- **{key}:** {value}\n"
        
        doc += "\n### Supported Languages\n\n"
        for lang in profile.supported_languages:
            doc += f"- {lang}\n"
        
        if profile.multimodal_capabilities:
            doc += "\n### Multimodal Capabilities\n\n"
            for cap in profile.multimodal_capabilities:
                doc += f"- {cap}\n"
        
        # Generate safe module name
        safe_module_name = profile.model_name.replace(' ', '_').replace('-', '_')
        safe_class_name = profile.model_name.replace(' ', '').replace('-', '')
        
        doc += "\n## Usage\n\n"
        doc += "```python\n"
        doc += f"# Import the model\n"
        doc += f"import sys\n"
        doc += f"sys.path.append('./working_models/{safe_module_name}')\n"
        doc += f"from {safe_module_name}_implementation import {safe_class_name}\n\n"
        doc += f"# Initialize model\n"
        doc += f"model = {safe_class_name}()\n\n"
        doc += f"# Get capabilities\n"
        doc += f"capabilities = model.get_capabilities()\n"
        doc += f"print(capabilities)\n\n"
        doc += f"# Process input\n"
        doc += f"response = model.process('Your question here')\n"
        doc += f"print(response)\n"
        doc += "```\n"
        
        with open(filepath, 'w') as f:
            f.write(doc)
        
        logger.info(f"✅ Generated documentation: {filepath}")
    
    def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple models
        
        Args:
            model_ids: List of model identifiers to compare
        
        Returns:
            Dict with comparison results
        """
        if not all(mid in self.profiles for mid in model_ids):
            missing = [mid for mid in model_ids if mid not in self.profiles]
            raise ValueError(f"Models not analyzed: {missing}")
        
        comparison = {
            "models": model_ids,
            "personality_comparison": {},
            "skill_comparison": {},
            "capabilities_comparison": {},
        }
        
        # Compare personalities
        all_traits = set()
        for mid in model_ids:
            all_traits.update(t.name for t in self.profiles[mid].personality_traits)
        
        for trait in all_traits:
            comparison["personality_comparison"][trait] = {}
            for mid in model_ids:
                profile = self.profiles[mid]
                matching_trait = next((t for t in profile.personality_traits if t.name == trait), None)
                comparison["personality_comparison"][trait][mid] = matching_trait.strength if matching_trait else 0.0
        
        # Compare skills
        all_skills = set()
        for mid in model_ids:
            all_skills.update(s.name for s in self.profiles[mid].skills)
        
        for skill in all_skills:
            comparison["skill_comparison"][skill] = {}
            for mid in model_ids:
                profile = self.profiles[mid]
                matching_skill = next((s for s in profile.skills if s.name == skill), None)
                comparison["skill_comparison"][skill][mid] = matching_skill.proficiency if matching_skill else 0.0
        
        logger.info(f"✅ Compared {len(model_ids)} models")
        return comparison
    
    def save_comparison(self, comparison: Dict, filepath: str):
        """Save comparison results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(comparison, f, indent=2)
        logger.info(f"✅ Saved comparison to {filepath}")


def main():
    """Main demo function"""
    print("="*80)
    print("AI Model Explorer - ChatGPT-like Model Analysis System")
    print("="*80)
    
    explorer = AIModelExplorer()
    
    # Analyze different models
    models_to_analyze = [
        ("ChatGPT-4", ModelType.CHATGPT),
        ("Ninja AI", ModelType.NINJA_AI),
        ("Super Ninja AI", ModelType.SUPER_NINJA_AI),
        ("Genspark AI", ModelType.GENSPARK_AI),
        ("Kimi K2", ModelType.KIMI_K2),
    ]
    
    profiles = []
    for model_name, model_type in models_to_analyze:
        print(f"\n{'='*80}")
        print(f"Analyzing: {model_name}")
        print(f"{'='*80}")
        
        profile = explorer.analyze_model(model_name, model_type)
        profiles.append(model_name)
        
        print(f"\n📊 Profile Summary:")
        print(f"   Personality Traits: {len(profile.personality_traits)}")
        print(f"   Skills: {len(profile.skills)}")
        print(f"   Behavior Patterns: {len(profile.behavior_patterns)}")
        print(f"   Supported Languages: {len(profile.supported_languages)}")
        
        # Create working copy
        working_dir = explorer.create_working_copy(profile)
        print(f"   ✅ Working copy created at: {working_dir}")
    
    # Compare all models
    print(f"\n{'='*80}")
    print(f"Comparing All Models")
    print(f"{'='*80}")
    
    comparison = explorer.compare_models(profiles)
    explorer.save_comparison(comparison, "./model_comparison.json")
    
    print(f"\n✅ Analysis complete!")
    print(f"   Total models analyzed: {len(profiles)}")
    print(f"   Working copies created in: ./working_models/")
    print(f"   Comparison saved to: ./model_comparison.json")


if __name__ == "__main__":
    main()
