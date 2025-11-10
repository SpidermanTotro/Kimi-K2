"""Example: Complete animation workflow."""

from kimi_k2 import Framework, Config
from kimi_k2.core.config import AnimationConfig


def main():
    """Demonstrate animation workflow."""
    # Configure for animation
    config = Config(
        animation=AnimationConfig(
            output_dir="examples/output",
            default_fps=30,
            quality_preset="tv"
        )
    )
    
    # Initialize framework
    framework = Framework(config)
    framework.initialize()
    
    try:
        # Get animation suite
        animation = framework.get_module('animation')
        
        # Create a project
        print("Creating animation project...")
        project = animation.create_project(
            name="demo_animation",
            fps=30,
            duration=15.0,
            quality="tv"
        )
        print(f"Created: {project.name} ({project.fps}fps, {project.duration}s)")
        
        # Add clips to timeline
        print("\nBuilding timeline...")
        timeline = animation.timeline_editor
        timeline.add_clip({'type': 'intro', 'duration': 3.0}, 0.0)
        timeline.add_clip({'type': 'main', 'duration': 10.0}, 3.0)
        timeline.add_clip({'type': 'outro', 'duration': 2.0}, 13.0)
        
        print(f"Timeline has {len(timeline.timeline)} clips")
        
        # Render the project
        print("\nRendering animation...")
        output_path = animation.render_project("demo_animation")
        print(f"Rendered to: {output_path}")
        
        # Show optimization stats
        print(f"\nOptimizations applied: {animation.optimizer.optimizations_applied}")
        
    finally:
        framework.shutdown()
        print("\nWorkflow complete!")


if __name__ == '__main__':
    main()
