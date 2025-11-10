"""
Example: Using the Claymation Assistant

This example demonstrates how to use the Claymation Assistant to analyze
stop-motion sequences and generate intermediate frames.
"""

import numpy as np
from kimi_k2.animation import ClayamationAssistant


def main():
    """Run the claymation assistant example."""
    print("=== Claymation Assistant Example ===\n")
    
    # Create the assistant
    assistant = ClayamationAssistant()
    
    # Create some sample frames (simulating stop-motion frames)
    print("1. Creating sample stop-motion frames...")
    frames = []
    for i in range(5):
        # Create frames with gradually changing values
        frame = np.ones((100, 100, 3)) * (i / 4)
        frames.append(frame)
    print(f"   Created {len(frames)} frames\n")
    
    # Analyze the sequence
    print("2. Analyzing the sequence...")
    analysis = assistant.analyze_sequence(frames)
    print(f"   Frame count: {analysis['frame_count']}")
    print(f"   Motion detected: {analysis['motion_detected']}")
    print(f"   Keyframe indices: {analysis['keyframe_indices']}")
    print(f"   Motion vectors: {len(analysis['motion_vectors'])} vectors\n")
    
    # Generate intermediate frames
    print("3. Generating intermediate frames...")
    start_frame = frames[0]
    end_frame = frames[-1]
    
    intermediate = assistant.generate_intermediate_frames(
        start_frame, end_frame, num_frames=10, style="smooth"
    )
    print(f"   Generated {len(intermediate)} intermediate frames\n")
    
    # Try different styles
    print("4. Testing different interpolation styles...")
    styles = assistant.get_available_styles()
    print(f"   Available styles: {', '.join(styles)}\n")
    
    for style in styles:
        intermediate = assistant.generate_intermediate_frames(
            start_frame, end_frame, num_frames=5, style=style
        )
        print(f"   Generated {len(intermediate)} frames with '{style}' style")
    
    print()
    
    # Add a custom style
    print("5. Adding a custom style...")
    success = assistant.add_custom_style("ultra_smooth", "cubic", 0.9)
    if success:
        print("   Custom style 'ultra_smooth' added successfully")
        intermediate = assistant.generate_intermediate_frames(
            start_frame, end_frame, num_frames=5, style="ultra_smooth"
        )
        print(f"   Generated {len(intermediate)} frames with custom style\n")
    
    # Process complete sequence
    print("6. Processing complete sequence...")
    result = assistant.process_sequence(frames, target_fps=24, style="smooth")
    print(f"   Original frames: {result['original_count']}")
    print(f"   Generated frames: {result['generated_count']}")
    print(f"   Total frames: {result['total_count']}")
    print(f"   Frame increase: {result['generated_count'] / result['original_count']:.1f}x\n")
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
