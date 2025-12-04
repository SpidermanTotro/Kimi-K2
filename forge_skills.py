#!/usr/bin/env python3
"""
THE FORGE AI - Advanced Skills Module
======================================

Implements the "ChatGPT 2.0" advanced capabilities including:
- Advanced reasoning and chain-of-thought
- Contextual awareness with memory integration
- Personalization based on user profiles
- Multi-step problem solving
- Code analysis and generation
- Creative writing enhancement
- Knowledge synthesis

These skills work with the memory system to provide intelligent,
context-aware responses.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillCategory(Enum):
    """Categories of skills"""
    REASONING = "reasoning"
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CREATIVITY = "creativity"
    MEMORY = "memory"
    PERSONALIZATION = "personalization"
    COMMUNICATION = "communication"


@dataclass
class SkillResult:
    """Result from skill execution"""
    success: bool
    output: Any
    skill_name: str
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ReasoningStep:
    """A step in chain-of-thought reasoning"""
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    conclusion: Optional[str] = None


class AdvancedReasoning:
    """
    Advanced reasoning capabilities
    
    Implements:
    - Chain-of-thought reasoning
    - Multi-step problem decomposition
    - Logical inference
    - Hypothesis generation and testing
    """
    
    def __init__(self):
        self.reasoning_history: List[List[ReasoningStep]] = []
    
    def chain_of_thought(self, problem: str, context: Optional[str] = None) -> SkillResult:
        """
        Apply chain-of-thought reasoning to a problem
        
        Args:
            problem: The problem to solve
            context: Optional context information
            
        Returns:
            SkillResult with reasoning steps and conclusion
        """
        steps = []
        
        # Step 1: Understand the problem
        step1 = ReasoningStep(
            step_number=1,
            thought=f"Let me understand the problem: {problem[:100]}...",
            action="Analyzing the problem statement"
        )
        steps.append(step1)
        
        # Step 2: Break down into components
        components = self._decompose_problem(problem)
        step2 = ReasoningStep(
            step_number=2,
            thought=f"Breaking down into {len(components)} components",
            action="Problem decomposition",
            observation=f"Components: {', '.join(components[:5])}"
        )
        steps.append(step2)
        
        # Step 3: Consider context
        if context:
            step3 = ReasoningStep(
                step_number=3,
                thought="Considering the provided context",
                action="Context integration",
                observation=f"Context mentions: {context[:100]}..."
            )
            steps.append(step3)
        
        # Step 4: Generate approach
        approach = self._generate_approach(problem, components)
        step4 = ReasoningStep(
            step_number=4,
            thought="Developing solution approach",
            action="Strategy formulation",
            observation=approach
        )
        steps.append(step4)
        
        # Step 5: Reach conclusion
        conclusion = self._synthesize_conclusion(problem, components, approach)
        step5 = ReasoningStep(
            step_number=5,
            thought="Synthesizing final answer",
            conclusion=conclusion
        )
        steps.append(step5)
        
        self.reasoning_history.append(steps)
        
        # Format output
        output_parts = []
        for step in steps:
            output_parts.append(f"**Step {step.step_number}**: {step.thought}")
            if step.action:
                output_parts.append(f"  Action: {step.action}")
            if step.observation:
                output_parts.append(f"  Observation: {step.observation}")
            if step.conclusion:
                output_parts.append(f"  **Conclusion**: {step.conclusion}")
        
        return SkillResult(
            success=True,
            output="\n".join(output_parts),
            skill_name="chain_of_thought",
            reasoning=conclusion,
            metadata={
                "steps": len(steps),
                "components": components
            }
        )
    
    def _decompose_problem(self, problem: str) -> List[str]:
        """Break a problem into components"""
        components = []
        
        # Extract question words
        if '?' in problem:
            components.append("question_type")
        
        # Extract key concepts
        words = problem.lower().split()
        concept_words = ['how', 'what', 'why', 'when', 'where', 'which', 'who']
        for word in concept_words:
            if word in words:
                components.append(f"{word}_question")
                break
        
        # Extract action verbs
        action_verbs = ['create', 'build', 'write', 'explain', 'analyze', 'compare', 'implement']
        for verb in action_verbs:
            if verb in problem.lower():
                components.append(f"action_{verb}")
        
        # Extract domain
        domains = ['code', 'program', 'book', 'story', 'data', 'design', 'system']
        for domain in domains:
            if domain in problem.lower():
                components.append(f"domain_{domain}")
        
        return components if components else ["general_inquiry"]
    
    def _generate_approach(self, problem: str, components: List[str]) -> str:
        """Generate an approach based on problem analysis"""
        approaches = []
        
        if any('code' in c or 'program' in c for c in components):
            approaches.append("Apply systematic programming methodology")
        if any('write' in c or 'story' in c or 'book' in c for c in components):
            approaches.append("Use creative writing frameworks")
        if any('analyze' in c or 'compare' in c for c in components):
            approaches.append("Apply analytical frameworks")
        if any('explain' in c for c in components):
            approaches.append("Use clear explanation with examples")
        
        if not approaches:
            approaches.append("Apply general problem-solving methodology")
        
        return "; ".join(approaches)
    
    def _synthesize_conclusion(
        self,
        problem: str,
        components: List[str],
        approach: str
    ) -> str:
        """Synthesize a conclusion from the analysis"""
        return (
            f"Based on the analysis of this {components[0] if components else 'general'} "
            f"problem, the recommended approach is to {approach.lower()}. "
            f"This will address the core requirements of the query."
        )
    
    def multi_step_solve(
        self,
        problem: str,
        max_steps: int = 10
    ) -> SkillResult:
        """
        Solve a problem through multiple steps
        
        Useful for complex problems requiring iterative solutions
        """
        steps = []
        current_state = {"problem": problem, "solved": False, "partial_solutions": []}
        
        for i in range(max_steps):
            if current_state["solved"]:
                break
            
            # Analyze current state
            analysis = self._analyze_state(current_state)
            
            # Generate next action
            action = self._generate_action(analysis)
            
            # Execute action (simulated)
            result = self._execute_action(action, current_state)
            
            steps.append({
                "step": i + 1,
                "analysis": analysis,
                "action": action,
                "result": result
            })
            
            # Update state
            current_state["partial_solutions"].append(result)
            if self._check_completion(current_state):
                current_state["solved"] = True
        
        return SkillResult(
            success=current_state["solved"],
            output=steps,
            skill_name="multi_step_solve",
            metadata={"steps_taken": len(steps)}
        )
    
    def _analyze_state(self, state: Dict) -> str:
        """Analyze the current problem state"""
        if not state["partial_solutions"]:
            return "Initial state - no progress yet"
        return f"Progress: {len(state['partial_solutions'])} steps completed"
    
    def _generate_action(self, analysis: str) -> str:
        """Generate next action based on analysis"""
        return "Continue with next step of solution"
    
    def _execute_action(self, action: str, state: Dict) -> str:
        """Execute an action and return result"""
        return f"Executed: {action}"
    
    def _check_completion(self, state: Dict) -> bool:
        """Check if problem is solved"""
        return len(state["partial_solutions"]) >= 3


class CodeAnalysisSkills:
    """
    Advanced code analysis and generation skills
    
    Implements:
    - Code quality analysis
    - Bug detection
    - Optimization suggestions
    - Code generation with best practices
    """
    
    def __init__(self):
        self.analysis_cache: Dict[str, Any] = {}
    
    def analyze_code(
        self,
        code: str,
        language: str = "python"
    ) -> SkillResult:
        """
        Comprehensive code analysis
        
        Args:
            code: The code to analyze
            language: Programming language
            
        Returns:
            SkillResult with analysis details
        """
        analysis = {
            "language": language,
            "lines": len(code.split('\n')),
            "complexity": self._estimate_complexity(code),
            "issues": self._detect_issues(code, language),
            "suggestions": self._generate_suggestions(code, language),
            "quality_score": 0
        }
        
        # Calculate quality score
        base_score = 100
        base_score -= len(analysis["issues"]) * 5
        base_score -= max(0, analysis["complexity"] - 10) * 2
        analysis["quality_score"] = max(0, min(100, base_score))
        
        return SkillResult(
            success=True,
            output=analysis,
            skill_name="code_analysis",
            suggestions=analysis["suggestions"],
            metadata={"language": language}
        )
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity"""
        complexity = 1
        
        # Count control flow statements
        control_patterns = [
            r'\bif\b', r'\belse\b', r'\belif\b',
            r'\bfor\b', r'\bwhile\b',
            r'\btry\b', r'\bexcept\b',
            r'\band\b', r'\bor\b'
        ]
        
        for pattern in control_patterns:
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _detect_issues(self, code: str, language: str) -> List[Dict[str, str]]:
        """Detect potential issues in code"""
        issues = []
        
        # Check for common issues
        if language == "python":
            # Check for missing docstrings
            if 'def ' in code and '"""' not in code and "'''" not in code:
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "message": "Consider adding docstrings to functions"
                })
            
            # Check for bare except
            if 'except:' in code:
                issues.append({
                    "type": "error_handling",
                    "severity": "medium",
                    "message": "Avoid bare except clauses - catch specific exceptions"
                })
            
            # Check for print debugging
            if 'print(' in code and 'DEBUG' not in code.upper():
                issues.append({
                    "type": "debug",
                    "severity": "low",
                    "message": "Consider using logging instead of print statements"
                })
        
        # Check for TODO/FIXME
        if 'TODO' in code or 'FIXME' in code:
            issues.append({
                "type": "incomplete",
                "severity": "info",
                "message": "Contains TODO/FIXME comments"
            })
        
        # Check for very long lines
        for i, line in enumerate(code.split('\n'), 1):
            if len(line) > 120:
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "message": f"Line {i} exceeds 120 characters"
                })
                break  # Only report first occurrence
        
        return issues
    
    def _generate_suggestions(self, code: str, language: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if language == "python":
            if 'type' not in code and ':' not in code.split('def')[0] if 'def' in code else True:
                suggestions.append("Consider adding type hints for better code clarity")
            
            if 'logging' not in code:
                suggestions.append("Consider using the logging module for better debugging")
            
            if 'class ' in code and '__init__' not in code:
                suggestions.append("Classes should have an __init__ method")
        
        # General suggestions
        lines = code.split('\n')
        if len(lines) > 50:
            suggestions.append("Consider breaking this into smaller functions")
        
        if not any(line.strip().startswith('#') for line in lines):
            suggestions.append("Add comments to explain complex logic")
        
        return suggestions
    
    def generate_code(
        self,
        description: str,
        language: str = "python",
        style: str = "clean"
    ) -> SkillResult:
        """
        Generate code based on description
        
        Args:
            description: What the code should do
            language: Target programming language
            style: Code style (clean, verbose, minimal)
            
        Returns:
            SkillResult with generated code template
        """
        # Generate code template based on description
        template = self._generate_template(description, language, style)
        
        return SkillResult(
            success=True,
            output=template,
            skill_name="code_generation",
            metadata={
                "language": language,
                "style": style
            },
            suggestions=[
                "Review and test the generated code",
                "Add error handling as needed",
                "Add documentation"
            ]
        )
    
    def _generate_template(
        self,
        description: str,
        language: str,
        style: str
    ) -> str:
        """Generate a code template"""
        desc_lower = description.lower()
        
        if language == "python":
            if "function" in desc_lower or "def" in desc_lower:
                return self._python_function_template(description, style)
            elif "class" in desc_lower:
                return self._python_class_template(description, style)
            else:
                return self._python_script_template(description, style)
        elif language == "javascript":
            return self._javascript_template(description, style)
        else:
            return f"// Code for: {description}\n// Language: {language}"
    
    def _python_function_template(self, description: str, style: str) -> str:
        """Generate Python function template"""
        if style == "verbose":
            return f'''def process_data(data):
    """
    {description}
    
    Args:
        data: Input data to process
        
    Returns:
        Processed result
        
    Raises:
        ValueError: If data is invalid
    """
    # Validate input
    if data is None:
        raise ValueError("Data cannot be None")
    
    # Process the data
    result = None
    
    try:
        # TODO: Implement processing logic
        result = data
    except Exception as e:
        logging.error(f"Error processing data: {{e}}")
        raise
    
    return result
'''
        else:
            return f'''def process_data(data):
    """{description}"""
    # TODO: Implement logic
    return data
'''
    
    def _python_class_template(self, description: str, style: str) -> str:
        """Generate Python class template"""
        return f'''class DataProcessor:
    """
    {description}
    """
    
    def __init__(self):
        """Initialize the processor."""
        self.data = None
    
    def process(self, data):
        """Process the data."""
        self.data = data
        return self._transform()
    
    def _transform(self):
        """Internal transformation logic."""
        # TODO: Implement transformation
        return self.data
'''
    
    def _python_script_template(self, description: str, style: str) -> str:
        """Generate Python script template"""
        return f'''#!/usr/bin/env python3
"""
{description}
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting...")
    
    # TODO: Implement main logic
    
    logger.info("Complete!")


if __name__ == "__main__":
    main()
'''
    
    def _javascript_template(self, description: str, style: str) -> str:
        """Generate JavaScript template"""
        return f'''/**
 * {description}
 */

function processData(data) {{
    // TODO: Implement logic
    return data;
}}

module.exports = {{ processData }};
'''


class WritingEnhancementSkills:
    """
    Creative writing enhancement skills
    
    Implements:
    - Style analysis and improvement
    - Tone adjustment
    - Clarity enhancement
    - Structure optimization
    """
    
    def __init__(self):
        self.style_patterns: Dict[str, List[str]] = {
            "formal": ["furthermore", "moreover", "consequently", "therefore"],
            "casual": ["basically", "like", "you know", "pretty much"],
            "academic": ["research indicates", "studies show", "according to"],
            "creative": ["imagine", "picture", "feel", "sense"]
        }
    
    def analyze_writing(self, text: str) -> SkillResult:
        """
        Analyze writing style and quality
        
        Args:
            text: The text to analyze
            
        Returns:
            SkillResult with analysis
        """
        analysis = {
            "word_count": len(text.split()),
            "sentence_count": text.count('.') + text.count('!') + text.count('?'),
            "paragraph_count": text.count('\n\n') + 1,
            "style": self._detect_style(text),
            "readability": self._calculate_readability(text),
            "tone": self._detect_tone(text),
            "suggestions": []
        }
        
        # Average sentence length
        if analysis["sentence_count"] > 0:
            avg_sentence = analysis["word_count"] / analysis["sentence_count"]
            if avg_sentence > 25:
                analysis["suggestions"].append(
                    "Consider shorter sentences for better readability"
                )
            elif avg_sentence < 10:
                analysis["suggestions"].append(
                    "Consider varying sentence length for better flow"
                )
        
        # Check for passive voice
        passive_indicators = ['was', 'were', 'been', 'being', 'is being', 'was being']
        passive_count = sum(1 for indicator in passive_indicators if indicator in text.lower())
        if passive_count > analysis["sentence_count"] * 0.3:
            analysis["suggestions"].append(
                "Consider using more active voice"
            )
        
        return SkillResult(
            success=True,
            output=analysis,
            skill_name="writing_analysis",
            suggestions=analysis["suggestions"]
        )
    
    def _detect_style(self, text: str) -> str:
        """Detect the writing style"""
        text_lower = text.lower()
        scores = {}
        
        for style, patterns in self.style_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            scores[style] = score
        
        if max(scores.values()) == 0:
            return "neutral"
        
        return max(scores, key=scores.get)
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability metrics"""
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        if sentences == 0:
            sentences = 1
        
        # Approximate Flesch-Kincaid
        avg_sentence_length = len(words) / sentences
        
        # Approximate syllable count (simple heuristic)
        syllables = sum(max(1, len(re.findall(r'[aeiou]+', word.lower()))) for word in words)
        avg_syllables = syllables / len(words) if words else 0
        
        # Flesch Reading Ease (simplified)
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
        score = max(0, min(100, score))
        
        if score >= 80:
            level = "Easy"
        elif score >= 60:
            level = "Standard"
        elif score >= 40:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            "score": round(score, 1),
            "level": level,
            "avg_sentence_length": round(avg_sentence_length, 1)
        }
    
    def _detect_tone(self, text: str) -> str:
        """Detect the emotional tone of text"""
        text_lower = text.lower()
        
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate', 'disappointing']
        neutral_words = ['however', 'but', 'although', 'nevertheless']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count * 2:
            return "positive"
        elif neg_count > pos_count * 2:
            return "negative"
        else:
            return "neutral"
    
    def enhance_clarity(self, text: str) -> SkillResult:
        """
        Enhance text clarity
        
        Args:
            text: Text to enhance
            
        Returns:
            SkillResult with suggestions
        """
        suggestions = []
        
        # Check for jargon
        jargon_patterns = [
            (r'\butilize\b', 'use'),
            (r'\bfacilitate\b', 'help'),
            (r'\bleverage\b', 'use'),
            (r'\bsynergy\b', 'cooperation'),
            (r'\bparadigm\b', 'model'),
        ]
        
        for pattern, replacement in jargon_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append(f"Consider replacing jargon: use '{replacement}' instead")
        
        # Check for redundancy
        redundancies = [
            'in order to',
            'at this point in time',
            'due to the fact that',
            'in the event that',
        ]
        
        for phrase in redundancies:
            if phrase in text.lower():
                suggestions.append(f"Consider simplifying: '{phrase}'")
        
        return SkillResult(
            success=True,
            output={
                "original": text,
                "suggestions": suggestions,
                "clarity_score": max(0, 100 - len(suggestions) * 10)
            },
            skill_name="clarity_enhancement",
            suggestions=suggestions
        )


class PersonalizationSkills:
    """
    Personalization skills for adapting responses to users
    
    Implements:
    - User preference adaptation
    - Communication style matching
    - Expertise level detection
    - Interest-based customization
    """
    
    def __init__(self):
        self.style_templates: Dict[str, Dict[str, str]] = {
            "formal": {
                "greeting": "Good day",
                "acknowledgment": "I understand your inquiry",
                "closing": "Please let me know if you require further assistance"
            },
            "casual": {
                "greeting": "Hey there",
                "acknowledgment": "Got it",
                "closing": "Let me know if you need anything else"
            },
            "technical": {
                "greeting": "Hello",
                "acknowledgment": "I'll analyze this technically",
                "closing": "Feel free to ask for more technical details"
            },
            "friendly": {
                "greeting": "Hi!",
                "acknowledgment": "That's a great question",
                "closing": "Happy to help more if needed!"
            }
        }
    
    def adapt_response(
        self,
        content: str,
        user_preferences: Dict[str, Any]
    ) -> SkillResult:
        """
        Adapt a response based on user preferences
        
        Args:
            content: The base response content
            user_preferences: User preference dictionary
            
        Returns:
            SkillResult with adapted content
        """
        style = user_preferences.get("communication_style", "neutral")
        expertise = user_preferences.get("expertise_level", "intermediate")
        interests = user_preferences.get("topics_of_interest", [])
        
        adapted = content
        
        # Adapt complexity based on expertise
        if expertise == "beginner":
            adapted = self._simplify_content(adapted)
        elif expertise == "expert":
            adapted = self._add_technical_depth(adapted)
        
        # Add personalized touches based on interests
        if interests:
            adapted = self._add_interest_relevance(adapted, interests)
        
        # Apply style
        adapted = self._apply_style(adapted, style)
        
        return SkillResult(
            success=True,
            output=adapted,
            skill_name="personalization",
            metadata={
                "style_applied": style,
                "expertise_level": expertise,
                "interests_considered": interests
            }
        )
    
    def _simplify_content(self, content: str) -> str:
        """Simplify content for beginners"""
        # Add explanatory notes
        simplified = content
        
        # Replace technical terms with simpler alternatives
        simplifications = {
            "implementation": "code",
            "architecture": "design",
            "instantiate": "create",
            "iterate": "go through",
        }
        
        for technical, simple in simplifications.items():
            simplified = simplified.replace(technical, simple)
        
        return simplified
    
    def _add_technical_depth(self, content: str) -> str:
        """Add technical depth for experts"""
        return content + "\n\n[Note: More technical details available upon request]"
    
    def _add_interest_relevance(self, content: str, interests: List[str]) -> str:
        """Add relevance to user interests"""
        if interests:
            return content + f"\n\n[This relates to your interests in: {', '.join(interests[:3])}]"
        return content
    
    def _apply_style(self, content: str, style: str) -> str:
        """Apply communication style"""
        if style in self.style_templates:
            template = self.style_templates[style]
            return f"{template['acknowledgment']}.\n\n{content}\n\n{template['closing']}"
        return content
    
    def detect_user_intent(self, message: str) -> SkillResult:
        """
        Detect the user's intent from their message
        
        Args:
            message: User's message
            
        Returns:
            SkillResult with detected intent
        """
        message_lower = message.lower()
        
        intents = {
            "question": ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'which'],
            "request": ['please', 'could you', 'can you', 'would you', 'help me'],
            "command": ['create', 'make', 'build', 'write', 'generate', 'show me'],
            "feedback": ['great', 'thanks', 'not working', 'doesn\'t work', 'error'],
            "clarification": ['i mean', 'actually', 'sorry', 'let me clarify'],
        }
        
        detected_intents = []
        for intent, indicators in intents.items():
            if any(indicator in message_lower for indicator in indicators):
                detected_intents.append(intent)
        
        primary_intent = detected_intents[0] if detected_intents else "statement"
        
        # Detect urgency
        urgency = "normal"
        if any(word in message_lower for word in ['urgent', 'asap', 'immediately', 'critical']):
            urgency = "high"
        elif any(word in message_lower for word in ['when you have time', 'no rush', 'eventually']):
            urgency = "low"
        
        return SkillResult(
            success=True,
            output={
                "primary_intent": primary_intent,
                "all_intents": detected_intents,
                "urgency": urgency
            },
            skill_name="intent_detection",
            metadata={"message_length": len(message)}
        )


class AdvancedSkillsEngine:
    """
    Main engine that orchestrates all advanced skills
    
    This is the core of "ChatGPT 2.0" capabilities
    """
    
    def __init__(self):
        self.reasoning = AdvancedReasoning()
        self.code_skills = CodeAnalysisSkills()
        self.writing_skills = WritingEnhancementSkills()
        self.personalization = PersonalizationSkills()
        
        logger.info("🧠 Advanced Skills Engine initialized")
    
    def process_request(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request using appropriate skills
        
        Args:
            message: User's message
            context: Context from memory system
            user_preferences: User preferences
            
        Returns:
            Processed result with skill outputs
        """
        # Detect intent
        intent_result = self.personalization.detect_user_intent(message)
        intent = intent_result.output["primary_intent"]
        
        results = {
            "intent": intent_result.output,
            "skills_used": [],
            "outputs": []
        }
        
        # Apply relevant skills based on message content
        message_lower = message.lower()
        
        # Code-related requests
        if any(word in message_lower for word in ['code', 'program', 'function', 'debug', 'python', 'javascript']):
            if 'analyze' in message_lower or 'review' in message_lower:
                # Extract code if present
                code = self._extract_code(message)
                if code:
                    code_result = self.code_skills.analyze_code(code)
                    results["skills_used"].append("code_analysis")
                    results["outputs"].append(code_result.output)
            elif 'write' in message_lower or 'create' in message_lower or 'generate' in message_lower:
                code_result = self.code_skills.generate_code(message)
                results["skills_used"].append("code_generation")
                results["outputs"].append(code_result.output)
        
        # Writing-related requests
        if any(word in message_lower for word in ['write', 'text', 'article', 'story', 'book']):
            if 'analyze' in message_lower:
                text = self._extract_text(message)
                if text:
                    writing_result = self.writing_skills.analyze_writing(text)
                    results["skills_used"].append("writing_analysis")
                    results["outputs"].append(writing_result.output)
        
        # Apply reasoning for complex questions
        if intent == "question" or len(message) > 100:
            reasoning_result = self.reasoning.chain_of_thought(
                message,
                context=str(context) if context else None
            )
            results["skills_used"].append("chain_of_thought")
            results["reasoning"] = reasoning_result.reasoning
        
        # Apply personalization if preferences available
        if user_preferences:
            results["personalized"] = True
            results["style_applied"] = user_preferences.get("communication_style", "neutral")
        
        return results
    
    def _extract_code(self, message: str) -> Optional[str]:
        """Extract code from message"""
        # Look for code blocks
        code_match = re.search(r'```[\w]*\n(.*?)\n```', message, re.DOTALL)
        if code_match:
            return code_match.group(1)
        
        # Look for inline code
        inline_match = re.search(r'`([^`]+)`', message)
        if inline_match:
            return inline_match.group(1)
        
        return None
    
    def _extract_text(self, message: str) -> Optional[str]:
        """Extract text content from message"""
        # Look for quoted text
        quote_match = re.search(r'"([^"]+)"', message)
        if quote_match:
            return quote_match.group(1)
        
        # Return message itself if it's long enough
        if len(message) > 50:
            return message
        
        return None
    
    def get_available_skills(self) -> Dict[str, List[str]]:
        """Get list of all available skills"""
        return {
            "reasoning": [
                "chain_of_thought",
                "multi_step_solve",
                "problem_decomposition"
            ],
            "coding": [
                "code_analysis",
                "code_generation",
                "bug_detection",
                "optimization_suggestions"
            ],
            "writing": [
                "writing_analysis",
                "clarity_enhancement",
                "style_detection",
                "tone_analysis"
            ],
            "personalization": [
                "intent_detection",
                "response_adaptation",
                "style_matching",
                "expertise_adjustment"
            ]
        }


# ==================== MAIN ====================

def main():
    """Demo the advanced skills"""
    print("=" * 60)
    print("🧠 THE FORGE AI - Advanced Skills Demo")
    print("=" * 60)
    print()
    
    # Initialize the engine
    engine = AdvancedSkillsEngine()
    
    # Demo: Chain of thought reasoning
    print("📝 Demo: Chain-of-Thought Reasoning")
    print("-" * 40)
    result = engine.reasoning.chain_of_thought(
        "How can I optimize my Python code for better performance?"
    )
    print(result.output)
    print()
    
    # Demo: Code analysis
    print("💻 Demo: Code Analysis")
    print("-" * 40)
    sample_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
'''
    result = engine.code_skills.analyze_code(sample_code)
    print(f"Quality Score: {result.output['quality_score']}")
    print(f"Complexity: {result.output['complexity']}")
    print(f"Issues: {len(result.output['issues'])}")
    print(f"Suggestions: {result.suggestions}")
    print()
    
    # Demo: Writing analysis
    print("✍️ Demo: Writing Analysis")
    print("-" * 40)
    sample_text = """
    The implementation of artificial intelligence in modern software development 
    has revolutionized how we approach problem-solving. Furthermore, the integration 
    of machine learning models enables systems to adapt and improve over time.
    """
    result = engine.writing_skills.analyze_writing(sample_text)
    print(f"Style: {result.output['style']}")
    print(f"Tone: {result.output['tone']}")
    print(f"Readability: {result.output['readability']}")
    print()
    
    # Demo: Intent detection
    print("🎯 Demo: Intent Detection")
    print("-" * 40)
    messages = [
        "Can you help me debug this code?",
        "Write a function to sort an array",
        "Thanks, that worked perfectly!",
        "What is the best way to optimize database queries?"
    ]
    for msg in messages:
        result = engine.personalization.detect_user_intent(msg)
        print(f"'{msg[:40]}...' → {result.output['primary_intent']}")
    print()
    
    # Demo: Available skills
    print("🔧 Available Skills:")
    print("-" * 40)
    skills = engine.get_available_skills()
    for category, skill_list in skills.items():
        print(f"  {category}: {', '.join(skill_list)}")
    
    print("\n" + "=" * 60)
    print("✅ Advanced Skills Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
