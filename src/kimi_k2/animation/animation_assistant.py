"""Animation Assistant - Create animation loops, skeletal rigging, and export capabilities"""

from typing import List, Dict, Any, Optional, Tuple
import json
import numpy as np


class AnimationAssistant:
    """
    Animation Assistant for creating animation loops, skeletal rigging,
    and exporting to various formats (JSON, FBX, glTF).
    """

    def __init__(self):
        """Initialize the Animation Assistant."""
        self.animations = {}
        self.skeletons = {}
        self.current_animation = None

    def create_animation_loop(
        self,
        name: str,
        keyframes: List[Dict[str, Any]],
        duration: float = 1.0,
        loop_type: str = "repeat",
    ) -> bool:
        """
        Create an animation loop from keyframes.

        Args:
            name: Name for the animation
            keyframes: List of keyframe dictionaries with 'time' and 'transform' data
            duration: Total duration of the animation in seconds
            loop_type: Type of loop ('repeat', 'pingpong', 'once')

        Returns:
            True if animation was created successfully
        """
        if not keyframes:
            return False

        if loop_type not in ["repeat", "pingpong", "once"]:
            return False

        # Normalize keyframe times
        normalized_keyframes = []
        for kf in keyframes:
            normalized_kf = kf.copy()
            if "time" in kf:
                normalized_kf["time"] = kf["time"] / duration
            else:
                # Auto-distribute keyframes if no time specified
                normalized_kf["time"] = len(normalized_keyframes) / len(keyframes)
            normalized_keyframes.append(normalized_kf)

        self.animations[name] = {
            "keyframes": normalized_keyframes,
            "duration": duration,
            "loop_type": loop_type,
        }
        self.current_animation = name
        return True

    def create_skeleton(
        self, name: str, bones: List[Dict[str, Any]], hierarchy: Dict[str, str]
    ) -> bool:
        """
        Create a skeletal rig structure.

        Args:
            name: Name for the skeleton
            bones: List of bone definitions with name, position, rotation
            hierarchy: Dictionary mapping child bone names to parent bone names

        Returns:
            True if skeleton was created successfully
        """
        if not bones:
            return False

        # Validate hierarchy
        bone_names = {bone["name"] for bone in bones}
        for child, parent in hierarchy.items():
            if child not in bone_names or (parent and parent not in bone_names):
                return False

        self.skeletons[name] = {"bones": bones, "hierarchy": hierarchy}
        return True

    def apply_skeletal_animation(
        self, skeleton_name: str, animation_name: str
    ) -> Dict[str, Any]:
        """
        Apply an animation to a skeleton.

        Args:
            skeleton_name: Name of the skeleton to animate
            animation_name: Name of the animation to apply

        Returns:
            Dictionary containing the animated skeleton data
        """
        if skeleton_name not in self.skeletons:
            return {"error": "Skeleton not found"}
        if animation_name not in self.animations:
            return {"error": "Animation not found"}

        skeleton = self.skeletons[skeleton_name]
        animation = self.animations[animation_name]

        return {
            "skeleton": skeleton_name,
            "animation": animation_name,
            "bones": skeleton["bones"],
            "keyframes": animation["keyframes"],
            "duration": animation["duration"],
        }

    def interpolate_keyframes(
        self, keyframes: List[Dict[str, Any]], time: float
    ) -> Dict[str, Any]:
        """
        Interpolate between keyframes at a given time.

        Args:
            keyframes: List of keyframes
            time: Time value to interpolate at (0.0 to 1.0)

        Returns:
            Interpolated transform data
        """
        if not keyframes:
            return {}

        # Normalize time to [0, 1]
        time = max(0.0, min(1.0, time))

        # Find surrounding keyframes
        prev_kf = keyframes[0]
        next_kf = keyframes[-1]

        for i in range(len(keyframes) - 1):
            if keyframes[i]["time"] <= time <= keyframes[i + 1]["time"]:
                prev_kf = keyframes[i]
                next_kf = keyframes[i + 1]
                break

        # Calculate interpolation factor
        if prev_kf["time"] == next_kf["time"]:
            t = 0.0
        else:
            t = (time - prev_kf["time"]) / (next_kf["time"] - prev_kf["time"])

        # Interpolate transform data
        result = {}
        if "transform" in prev_kf and "transform" in next_kf:
            result["transform"] = {}
            for key in prev_kf["transform"]:
                if key in next_kf["transform"]:
                    prev_val = prev_kf["transform"][key]
                    next_val = next_kf["transform"][key]

                    # Handle different data types
                    if isinstance(prev_val, (int, float)) and isinstance(
                        next_val, (int, float)
                    ):
                        result["transform"][key] = prev_val * (1 - t) + next_val * t
                    elif isinstance(prev_val, (list, tuple)) and isinstance(
                        next_val, (list, tuple)
                    ):
                        # Interpolate vectors
                        result["transform"][key] = [
                            pv * (1 - t) + nv * t
                            for pv, nv in zip(prev_val, next_val)
                        ]
                    else:
                        result["transform"][key] = (
                            prev_val if t < 0.5 else next_val
                        )

        return result

    def export_to_json(
        self, animation_name: str, skeleton_name: Optional[str] = None
    ) -> str:
        """
        Export animation to JSON format.

        Args:
            animation_name: Name of the animation to export
            skeleton_name: Optional skeleton name to include

        Returns:
            JSON string representation
        """
        if animation_name not in self.animations:
            return json.dumps({"error": "Animation not found"})

        export_data = {"animation": self.animations[animation_name]}

        if skeleton_name and skeleton_name in self.skeletons:
            export_data["skeleton"] = self.skeletons[skeleton_name]

        export_data["format"] = "kimi-k2-json"
        export_data["version"] = "1.0"

        return json.dumps(export_data, indent=2)

    def export_to_fbx(
        self, animation_name: str, skeleton_name: Optional[str] = None
    ) -> str:
        """
        Export animation to FBX format (simplified text representation).

        Args:
            animation_name: Name of the animation to export
            skeleton_name: Optional skeleton name to include

        Returns:
            FBX-like text representation
        """
        if animation_name not in self.animations:
            return "; FBX Export Error: Animation not found"

        animation = self.animations[animation_name]

        fbx_content = [
            "; FBX 7.4.0 project file",
            "; Created by Kimi-K2 Animation Assistant",
            "",
            "FBXHeaderExtension:  {",
            '    FBXVersion: 7400',
            '    Creator: "Kimi-K2 Animation Assistant"',
            "}",
            "",
            f"Animation: \"{animation_name}\" {{",
            f"    Duration: {animation['duration']}",
            f"    LoopType: \"{animation['loop_type']}\"",
            "    Keyframes: {",
        ]

        for i, kf in enumerate(animation["keyframes"]):
            fbx_content.append(f"        Keyframe {i}: {{")
            fbx_content.append(f"            Time: {kf.get('time', 0)}")
            if "transform" in kf:
                for key, value in kf["transform"].items():
                    fbx_content.append(f"            {key}: {value}")
            fbx_content.append("        }")

        fbx_content.append("    }")

        if skeleton_name and skeleton_name in self.skeletons:
            skeleton = self.skeletons[skeleton_name]
            fbx_content.append(f"    Skeleton: \"{skeleton_name}\" {{")
            for bone in skeleton["bones"]:
                fbx_content.append(f"        Bone: \"{bone['name']}\"")
            fbx_content.append("    }")

        fbx_content.append("}")

        return "\n".join(fbx_content)

    def export_to_gltf(
        self, animation_name: str, skeleton_name: Optional[str] = None
    ) -> str:
        """
        Export animation to glTF format.

        Args:
            animation_name: Name of the animation to export
            skeleton_name: Optional skeleton name to include

        Returns:
            glTF JSON string representation
        """
        if animation_name not in self.animations:
            return json.dumps({"error": "Animation not found"})

        animation = self.animations[animation_name]

        gltf_data = {
            "asset": {"version": "2.0", "generator": "Kimi-K2 Animation Assistant"},
            "animations": [
                {
                    "name": animation_name,
                    "channels": [],
                    "samplers": [],
                }
            ],
        }

        # Add animation samplers and channels
        for i, kf in enumerate(animation["keyframes"]):
            sampler = {
                "input": i,
                "interpolation": "LINEAR",
                "output": i,
            }
            gltf_data["animations"][0]["samplers"].append(sampler)

            if "transform" in kf:
                channel = {
                    "sampler": i,
                    "target": {"node": 0, "path": "translation"},
                }
                gltf_data["animations"][0]["channels"].append(channel)

        # Add skeleton if provided
        if skeleton_name and skeleton_name in self.skeletons:
            skeleton = self.skeletons[skeleton_name]
            gltf_data["nodes"] = []
            gltf_data["skins"] = [{"joints": [], "skeleton": 0}]

            for bone in skeleton["bones"]:
                node = {"name": bone["name"]}
                if "position" in bone:
                    node["translation"] = bone["position"]
                if "rotation" in bone:
                    node["rotation"] = bone["rotation"]
                gltf_data["nodes"].append(node)
                gltf_data["skins"][0]["joints"].append(len(gltf_data["nodes"]) - 1)

        return json.dumps(gltf_data, indent=2)

    def get_animation_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific animation.

        Args:
            name: Name of the animation

        Returns:
            Dictionary with animation information or None if not found
        """
        if name not in self.animations:
            return None

        anim = self.animations[name]
        return {
            "name": name,
            "keyframe_count": len(anim["keyframes"]),
            "duration": anim["duration"],
            "loop_type": anim["loop_type"],
        }

    def list_animations(self) -> List[str]:
        """Get list of all animation names."""
        return list(self.animations.keys())

    def list_skeletons(self) -> List[str]:
        """Get list of all skeleton names."""
        return list(self.skeletons.keys())
