"""
Moon AI Integration
Interoperability layer for Moon AI systems
"""

from typing import Dict, List, Optional, Any
from ..client import KimiClient


class MoonAIIntegration:
    """
    Integration layer for Moon AI and other AI systems.
    
    Provides:
    - Configuration management
    - Cross-AI communication
    - Feature sharing
    - Unified interface
    """
    
    def __init__(
        self,
        kimi_client: Optional[KimiClient] = None,
        moon_ai_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Moon AI integration.
        
        Args:
            kimi_client: Kimi K2 client instance
            moon_ai_config: Configuration for Moon AI systems
        """
        self.kimi_client = kimi_client or KimiClient()
        self.config = moon_ai_config or {}
        self.active_integrations: Dict[str, bool] = {}
    
    def register_integration(
        self,
        integration_name: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Register a new AI system integration.
        
        Args:
            integration_name: Name of the AI system
            config: Configuration for the integration
            
        Returns:
            Registration result
        """
        self.config[integration_name] = config
        self.active_integrations[integration_name] = True
        
        return {
            "status": "success",
            "integration": integration_name,
            "active": True
        }
    
    def get_integration_status(
        self,
        integration_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get status of integrations.
        
        Args:
            integration_name: Optional specific integration to check
            
        Returns:
            Integration status
        """
        if integration_name:
            if integration_name not in self.config:
                return {
                    "status": "error",
                    "message": f"Integration {integration_name} not found"
                }
            
            return {
                "status": "success",
                "integration": integration_name,
                "active": self.active_integrations.get(integration_name, False),
                "config": self.config[integration_name]
            }
        
        return {
            "status": "success",
            "integrations": list(self.config.keys()),
            "active": self.active_integrations,
            "total": len(self.config)
        }
    
    def unified_query(
        self,
        query: str,
        target_systems: Optional[List[str]] = None,
        combine_results: bool = True,
    ) -> Dict[str, Any]:
        """
        Query multiple AI systems with a unified interface.
        
        Args:
            query: Query to send
            target_systems: Optional list of systems to query
            combine_results: Whether to combine results
            
        Returns:
            Query results from all systems
        """
        systems = target_systems or list(self.config.keys())
        results = {}
        
        # Always query Kimi K2
        kimi_result = self.kimi_client.simple_chat(query)
        results["kimi_k2"] = {
            "response": kimi_result,
            "source": "kimi_k2"
        }
        
        # Query other systems (placeholder for actual implementations)
        for system in systems:
            if system in self.active_integrations and self.active_integrations[system]:
                results[system] = {
                    "response": f"[{system} response would be here]",
                    "source": system,
                    "note": "Placeholder - actual integration requires system-specific API"
                }
        
        if combine_results and len(results) > 1:
            # Combine results using Kimi K2
            combined_prompt = f"""I received responses from multiple AI systems for this query: "{query}"

Responses:
"""
            for system, result in results.items():
                combined_prompt += f"\n{system}: {result['response']}\n"
            
            combined_prompt += "\nPlease provide a synthesized answer that combines the best insights from all responses."
            
            combined = self.kimi_client.simple_chat(combined_prompt)
            
            return {
                "status": "success",
                "query": query,
                "individual_results": results,
                "combined_result": combined,
                "systems_queried": list(results.keys())
            }
        
        return {
            "status": "success",
            "query": query,
            "results": results,
            "systems_queried": list(results.keys())
        }
    
    def share_context(
        self,
        context: Dict[str, Any],
        target_system: str,
    ) -> Dict[str, Any]:
        """
        Share context with another AI system.
        
        Args:
            context: Context to share
            target_system: Target AI system
            
        Returns:
            Sharing result
        """
        if target_system not in self.config:
            return {
                "status": "error",
                "message": f"System {target_system} not configured"
            }
        
        # Placeholder for actual context sharing
        return {
            "status": "success",
            "target_system": target_system,
            "context_shared": True,
            "note": "Actual implementation requires system-specific API"
        }
    
    def create_ai_pipeline(
        self,
        pipeline_steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a pipeline across multiple AI systems.
        
        Args:
            pipeline_steps: List of steps, each specifying system and task
            
        Returns:
            Pipeline execution results
        """
        results = []
        current_output = None
        
        for i, step in enumerate(pipeline_steps):
            system = step.get("system", "kimi_k2")
            task = step.get("task", "")
            
            # Use output from previous step if available
            if current_output and step.get("use_previous_output", True):
                task = f"{task}\n\nContext from previous step: {current_output}"
            
            if system == "kimi_k2":
                response = self.kimi_client.simple_chat(task)
            else:
                response = f"[{system} would process: {task}]"
            
            results.append({
                "step": i,
                "system": system,
                "task": task,
                "response": response
            })
            
            current_output = response
        
        return {
            "status": "success",
            "pipeline_steps": len(pipeline_steps),
            "results": results,
            "final_output": current_output
        }
    
    def enable_integration(self, integration_name: str) -> Dict[str, Any]:
        """
        Enable an integration.
        
        Args:
            integration_name: Name of integration to enable
            
        Returns:
            Operation result
        """
        if integration_name not in self.config:
            return {
                "status": "error",
                "message": f"Integration {integration_name} not found"
            }
        
        self.active_integrations[integration_name] = True
        
        return {
            "status": "success",
            "integration": integration_name,
            "active": True
        }
    
    def disable_integration(self, integration_name: str) -> Dict[str, Any]:
        """
        Disable an integration.
        
        Args:
            integration_name: Name of integration to disable
            
        Returns:
            Operation result
        """
        if integration_name not in self.config:
            return {
                "status": "error",
                "message": f"Integration {integration_name} not found"
            }
        
        self.active_integrations[integration_name] = False
        
        return {
            "status": "success",
            "integration": integration_name,
            "active": False
        }
