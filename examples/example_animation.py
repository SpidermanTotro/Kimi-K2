"""
Example: Using the Animation Assistant

This example demonstrates how to use the Animation Assistant to create
animation loops, skeletal rigs, and export to various formats.
"""

from kimi_k2.animation import AnimationAssistant


def main():
    """Run the animation assistant example."""
    print("=== Animation Assistant Example ===\n")
    
    # Create the assistant
    assistant = AnimationAssistant()
    
    # Create an animation loop
    print("1. Creating animation loop...")
    keyframes = [
        {"time": 0.0, "transform": {"x": 0, "y": 0, "rotation": 0}},
        {"time": 0.5, "transform": {"x": 5, "y": 3, "rotation": 90}},
        {"time": 1.0, "transform": {"x": 10, "y": 0, "rotation": 180}},
    ]
    
    success = assistant.create_animation_loop(
        "walk_cycle", keyframes, duration=2.0, loop_type="repeat"
    )
    if success:
        print("   Animation 'walk_cycle' created successfully")
        info = assistant.get_animation_info("walk_cycle")
        print(f"   Keyframes: {info['keyframe_count']}")
        print(f"   Duration: {info['duration']}s")
        print(f"   Loop type: {info['loop_type']}\n")
    
    # Create a skeleton
    print("2. Creating skeletal rig...")
    bones = [
        {"name": "root", "position": [0, 0, 0], "rotation": [0, 0, 0]},
        {"name": "spine", "position": [0, 1, 0], "rotation": [0, 0, 0]},
        {"name": "head", "position": [0, 2, 0], "rotation": [0, 0, 0]},
        {"name": "left_arm", "position": [-0.5, 1.5, 0], "rotation": [0, 0, 0]},
        {"name": "right_arm", "position": [0.5, 1.5, 0], "rotation": [0, 0, 0]},
    ]
    
    hierarchy = {
        "spine": "root",
        "head": "spine",
        "left_arm": "spine",
        "right_arm": "spine",
    }
    
    success = assistant.create_skeleton("humanoid", bones, hierarchy)
    if success:
        print("   Skeleton 'humanoid' created successfully")
        print(f"   Bones: {len(bones)}")
        print(f"   Hierarchy connections: {len(hierarchy)}\n")
    
    # Apply animation to skeleton
    print("3. Applying animation to skeleton...")
    result = assistant.apply_skeletal_animation("humanoid", "walk_cycle")
    if "skeleton" in result:
        print(f"   Applied '{result['animation']}' to '{result['skeleton']}'")
        print(f"   Duration: {result['duration']}s\n")
    
    # Test interpolation
    print("4. Testing keyframe interpolation...")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        interpolated = assistant.interpolate_keyframes(keyframes, t)
        if "transform" in interpolated:
            transform = interpolated["transform"]
            print(f"   t={t:.2f}: x={transform['x']:.2f}, y={transform['y']:.2f}, rotation={transform['rotation']:.1f}°")
    print()
    
    # Export to different formats
    print("5. Exporting animation to different formats...\n")
    
    # JSON export
    print("   a) Exporting to JSON...")
    json_output = assistant.export_to_json("walk_cycle", "humanoid")
    print(f"      JSON output length: {len(json_output)} characters")
    print(f"      Preview: {json_output[:100]}...\n")
    
    # FBX export
    print("   b) Exporting to FBX...")
    fbx_output = assistant.export_to_fbx("walk_cycle", "humanoid")
    print(f"      FBX output length: {len(fbx_output)} characters")
    print(f"      Preview: {fbx_output[:80]}...\n")
    
    # glTF export
    print("   c) Exporting to glTF...")
    gltf_output = assistant.export_to_gltf("walk_cycle", "humanoid")
    print(f"      glTF output length: {len(gltf_output)} characters")
    print(f"      Preview: {gltf_output[:100]}...\n")
    
    # List all animations and skeletons
    print("6. Listing all assets...")
    animations = assistant.list_animations()
    skeletons = assistant.list_skeletons()
    print(f"   Animations: {', '.join(animations)}")
    print(f"   Skeletons: {', '.join(skeletons)}\n")
    
    print("=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
