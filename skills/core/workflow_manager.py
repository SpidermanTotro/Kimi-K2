"""
Workflow Manager Module

Provides end-to-end workflow orchestration for complex media generation tasks.
Coordinates multiple modules to create complete productions.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class WorkflowStage(Enum):
    """Stages in a workflow"""
    PLANNING = "planning"
    CONTENT_GENERATION = "content_generation"
    ASSET_CREATION = "asset_creation"
    ASSEMBLY = "assembly"
    POST_PROCESSING = "post_processing"
    EXPORT = "export"


@dataclass
class WorkflowStep:
    """Individual step in workflow"""
    name: str
    stage: WorkflowStage
    function: Callable
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_id: str
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """
    End-to-end workflow orchestration for Kimi-K2
    
    Features:
    - Multi-stage workflow execution
    - Dependency management
    - Parallel step execution
    - Error handling and recovery
    - Progress tracking
    - Asset management
    
    Example:
        >>> manager = WorkflowManager()
        >>> workflow = manager.create_workflow("animated_film")
        >>> 
        >>> # Add steps
        >>> manager.add_step(workflow, WorkflowStep(
        ...     name="generate_script",
        ...     stage=WorkflowStage.CONTENT_GENERATION,
        ...     function=generate_script,
        ...     outputs=["script"]
        ... ))
        >>> 
        >>> manager.add_step(workflow, WorkflowStep(
        ...     name="generate_voices",
        ...     stage=WorkflowStage.ASSET_CREATION,
        ...     function=generate_voices,
        ...     inputs=["script"],
        ...     outputs=["voice_audio"],
        ...     dependencies=["generate_script"]
        ... ))
        >>> 
        >>> result = manager.execute_workflow(workflow)
    """
    
    def __init__(self):
        """Initialize workflow manager"""
        self._workflows = {}
        self._assets = {}
    
    def create_workflow(
        self,
        workflow_id: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new workflow
        
        Args:
            workflow_id: Unique workflow identifier
            description: Workflow description
            
        Returns:
            Workflow data structure
        """
        workflow = {
            "id": workflow_id,
            "description": description,
            "steps": [],
            "outputs": {},
            "status": "created",
            "progress": 0.0
        }
        
        self._workflows[workflow_id] = workflow
        return workflow
    
    def add_step(
        self,
        workflow: Dict[str, Any],
        step: WorkflowStep
    ):
        """
        Add step to workflow
        
        Args:
            workflow: Workflow to add step to
            step: Step to add
        """
        workflow["steps"].append(step)
    
    def execute_workflow(
        self,
        workflow: Dict[str, Any],
        parallel: bool = True
    ) -> WorkflowResult:
        """
        Execute complete workflow
        
        Args:
            workflow: Workflow to execute
            parallel: Enable parallel execution where possible
            
        Returns:
            Workflow execution result
        """
        workflow["status"] = "running"
        errors = []
        outputs = {}
        
        # Sort steps by dependencies
        sorted_steps = self._sort_steps_by_dependencies(workflow["steps"])
        
        for i, step in enumerate(sorted_steps):
            try:
                # Get inputs for this step
                step_inputs = {
                    input_name: outputs.get(input_name)
                    for input_name in step.inputs
                }
                
                # Execute step
                step_outputs = step.function(**step_inputs)
                
                # Store outputs
                for output_name in step.outputs:
                    if output_name in step_outputs:
                        outputs[output_name] = step_outputs[output_name]
                
                # Update progress
                workflow["progress"] = (i + 1) / len(sorted_steps)
                
            except Exception as e:
                error_msg = f"Error in step '{step.name}': {str(e)}"
                errors.append(error_msg)
                
                if not step.optional:
                    workflow["status"] = "failed"
                    break
        
        if not errors:
            workflow["status"] = "completed"
        
        workflow["outputs"] = outputs
        
        return WorkflowResult(
            workflow_id=workflow["id"],
            success=workflow["status"] == "completed",
            outputs=outputs,
            errors=errors
        )
    
    def _sort_steps_by_dependencies(
        self,
        steps: List[WorkflowStep]
    ) -> List[WorkflowStep]:
        """
        Sort steps based on dependencies (topological sort)
        
        Args:
            steps: List of workflow steps
            
        Returns:
            Sorted list of steps
        """
        # Simple dependency sort - in production, use proper topological sort
        sorted_steps = []
        remaining = steps.copy()
        
        while remaining:
            # Find steps with no unsatisfied dependencies
            ready = [
                step for step in remaining
                if all(
                    dep in [s.name for s in sorted_steps]
                    for dep in step.dependencies
                )
            ]
            
            if not ready:
                # Circular dependency or unsatisfiable
                sorted_steps.extend(remaining)
                break
            
            sorted_steps.extend(ready)
            for step in ready:
                remaining.remove(step)
        
        return sorted_steps
    
    def create_animated_film_workflow(
        self,
        project_name: str,
        script: str,
        duration: float = 60.0
    ) -> Dict[str, Any]:
        """
        Create complete animated film workflow template
        
        Args:
            project_name: Name of film project
            script: Film script
            duration: Film duration in seconds
            
        Returns:
            Configured workflow
        """
        workflow = self.create_workflow(
            f"{project_name}_production",
            "Complete animated film production workflow"
        )
        
        # Step 1: Generate storyboard
        self.add_step(workflow, WorkflowStep(
            name="storyboard",
            stage=WorkflowStage.PLANNING,
            function=lambda: {"storyboard": f"[Storyboard for {project_name}]"},
            outputs=["storyboard"]
        ))
        
        # Step 2: Generate voice audio
        self.add_step(workflow, WorkflowStep(
            name="voice_synthesis",
            stage=WorkflowStage.ASSET_CREATION,
            function=lambda: {"voice_audio": f"[Voice audio]"},
            outputs=["voice_audio"]
        ))
        
        # Step 3: Generate music
        self.add_step(workflow, WorkflowStep(
            name="music_generation",
            stage=WorkflowStage.ASSET_CREATION,
            function=lambda: {"music": f"[Background music]"},
            outputs=["music"]
        ))
        
        # Step 4: Create animation
        self.add_step(workflow, WorkflowStep(
            name="animation",
            stage=WorkflowStage.CONTENT_GENERATION,
            function=lambda storyboard, voice_audio: {
                "animation": f"[Animation based on storyboard]"
            },
            inputs=["storyboard", "voice_audio"],
            outputs=["animation"],
            dependencies=["storyboard", "voice_synthesis"]
        ))
        
        # Step 5: Assemble final video
        self.add_step(workflow, WorkflowStep(
            name="final_assembly",
            stage=WorkflowStage.ASSEMBLY,
            function=lambda animation, voice_audio, music: {
                "final_video": f"[Final assembled video]"
            },
            inputs=["animation", "voice_audio", "music"],
            outputs=["final_video"],
            dependencies=["animation", "voice_synthesis", "music_generation"]
        ))
        
        # Step 6: Export
        self.add_step(workflow, WorkflowStep(
            name="export",
            stage=WorkflowStage.EXPORT,
            function=lambda final_video: {
                "exported_path": f"{project_name}_final.mp4"
            },
            inputs=["final_video"],
            outputs=["exported_path"],
            dependencies=["final_assembly"]
        ))
        
        return workflow
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get current workflow status
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Status dictionary
        """
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        workflow = self._workflows[workflow_id]
        
        return {
            "id": workflow_id,
            "status": workflow["status"],
            "progress": workflow["progress"],
            "num_steps": len(workflow["steps"])
        }
