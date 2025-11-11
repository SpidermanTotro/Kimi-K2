"""
Specialized Pipelines
Domain-specific AI pipelines for healthcare, education, etc.
"""

from typing import Dict, List, Optional, Any
from ..client import KimiClient


class SpecializedPipeline:
    """
    Specialized pipelines for domain-specific tasks.
    
    Supports:
    - Healthcare: Medical information, symptom analysis
    - Education: Tutoring, curriculum planning
    - Legal: Document analysis, research
    - Finance: Analysis, reporting
    """
    
    def __init__(self, domain: str, client: Optional[KimiClient] = None):
        """
        Initialize a specialized pipeline.
        
        Args:
            domain: Domain name ('healthcare', 'education', 'legal', 'finance')
            client: Kimi K2 client instance
        """
        self.domain = domain.lower()
        self.client = client or KimiClient()
        self.domain_prompts = self._load_domain_prompts()
    
    def _load_domain_prompts(self) -> Dict[str, str]:
        """Load domain-specific system prompts."""
        return {
            "healthcare": (
                "You are a knowledgeable healthcare AI assistant. "
                "Provide accurate medical information while being clear that you're not "
                "a replacement for professional medical advice. Always recommend consulting "
                "healthcare professionals for serious concerns."
            ),
            "education": (
                "You are an educational AI tutor. Adapt your teaching style to the student's "
                "level, use examples and analogies, encourage critical thinking, and provide "
                "constructive feedback. Make learning engaging and accessible."
            ),
            "legal": (
                "You are a legal research assistant. Provide accurate information about laws "
                "and legal concepts while being clear that you're not providing legal advice. "
                "Always recommend consulting qualified attorneys for specific legal matters."
            ),
            "finance": (
                "You are a financial analysis assistant. Provide insights on financial data, "
                "market trends, and economic concepts. Emphasize that you don't provide "
                "personalized investment advice and recommend consulting financial advisors."
            ),
        }
    
    def process(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a task using the specialized pipeline.
        
        Args:
            task: The task to process
            context: Optional domain-specific context
            
        Returns:
            Processing results
        """
        system_prompt = self.domain_prompts.get(
            self.domain,
            "You are Kimi, an AI assistant created by Moonshot AI."
        )
        
        if context:
            context_str = "\n\nAdditional context:\n" + "\n".join([
                f"- {k}: {v}" for k, v in context.items()
            ])
            system_prompt += context_str
        
        response = self.client.simple_chat(task, system_prompt=system_prompt)
        
        return {
            "domain": self.domain,
            "task": task,
            "response": response,
            "context_provided": context is not None,
        }
    
    def healthcare_analysis(
        self,
        symptoms: List[str],
        patient_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze symptoms (for educational purposes only).
        
        Args:
            symptoms: List of symptoms
            patient_info: Optional patient information
            
        Returns:
            Analysis results with disclaimers
        """
        if self.domain != "healthcare":
            return {"error": "This method requires healthcare domain"}
        
        symptoms_str = ", ".join(symptoms)
        patient_str = ""
        if patient_info:
            patient_str = f"\nPatient info: {patient_info}"
        
        task = f"""For educational purposes, analyze these symptoms: {symptoms_str}{patient_str}

Provide:
1. Possible conditions (educational overview)
2. General recommendations
3. When to seek professional medical help
4. Important disclaimer

Remember: This is for educational purposes only, not medical advice."""
        
        return self.process(task)
    
    def education_tutor(
        self,
        subject: str,
        topic: str,
        student_level: str,
        question: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Provide educational tutoring.
        
        Args:
            subject: Subject area (math, science, history, etc.)
            topic: Specific topic
            student_level: Student level (elementary, middle, high, college)
            question: Optional specific question
            
        Returns:
            Tutoring response
        """
        if self.domain != "education":
            return {"error": "This method requires education domain"}
        
        task = f"""I'm helping a {student_level} student with {subject}, specifically {topic}."""
        if question:
            task += f"\n\nStudent's question: {question}"
        else:
            task += f"\n\nPlease provide an introduction to this topic suitable for their level."
        
        task += """

Please provide:
1. Clear explanation with examples
2. Visual analogies if helpful
3. Practice questions or exercises
4. Additional resources for learning"""
        
        return self.process(task)
    
    def legal_research(
        self,
        legal_question: str,
        jurisdiction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Assist with legal research.
        
        Args:
            legal_question: Legal question or topic
            jurisdiction: Optional jurisdiction
            
        Returns:
            Research results with disclaimers
        """
        if self.domain != "legal":
            return {"error": "This method requires legal domain"}
        
        task = f"""Legal research question: {legal_question}"""
        if jurisdiction:
            task += f"\nJurisdiction: {jurisdiction}"
        
        task += """

Please provide:
1. Overview of relevant legal concepts
2. Common interpretations and precedents
3. Important considerations
4. Disclaimer about seeking professional legal advice"""
        
        return self.process(task)
    
    def financial_analysis(
        self,
        data_description: str,
        analysis_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Perform financial analysis.
        
        Args:
            data_description: Description of financial data
            analysis_type: Type of analysis (trend, comparison, forecast)
            
        Returns:
            Analysis results
        """
        if self.domain != "finance":
            return {"error": "This method requires finance domain"}
        
        task = f"""Financial analysis request ({analysis_type}):
{data_description}

Please provide:
1. Key insights from the data
2. Trends and patterns
3. Potential implications
4. Considerations and caveats
5. Disclaimer about personalized financial advice"""
        
        return self.process(task)
