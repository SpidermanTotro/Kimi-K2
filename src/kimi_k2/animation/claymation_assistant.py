"""Claymation Assistant - Analyze stop-motion sequences and generate intermediate frames"""

from typing import List, Dict, Any, Optional
import numpy as np


class ClayamationAssistant:
    """
    Claymation Assistant for analyzing stop-motion sequences,
    generating intermediate frames, and applying style presets.
    """

    def __init__(self):
        """Initialize the Claymation Assistant."""
        self.style_presets = {
            "classic": {"interpolation": "linear", "smoothing": 0.3},
            "smooth": {"interpolation": "cubic", "smoothing": 0.7},
            "artistic": {"interpolation": "bezier", "smoothing": 0.5},
        }
        self.current_style = "classic"

    def analyze_sequence(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """
        Analyze a stop-motion sequence to extract motion patterns and keyframes.

        Args:
            frames: List of frame arrays representing the stop-motion sequence

        Returns:
            Dictionary containing analysis results including:
            - frame_count: Number of frames
            - motion_detected: Whether motion was detected
            - keyframe_indices: Indices of detected keyframes
            - motion_vectors: Estimated motion between frames
        """
        if not frames or len(frames) < 2:
            return {
                "frame_count": len(frames) if frames else 0,
                "motion_detected": False,
                "keyframe_indices": [],
                "motion_vectors": [],
            }

        frame_count = len(frames)
        motion_vectors = []
        keyframe_indices = [0]  # First frame is always a keyframe

        # Analyze motion between consecutive frames
        for i in range(1, frame_count):
            # Calculate simple motion estimation (frame difference)
            motion = np.mean(np.abs(frames[i] - frames[i - 1]))
            motion_vectors.append(float(motion))

            # Detect keyframes based on motion threshold
            if motion > 0.1:  # Threshold for significant motion
                keyframe_indices.append(i)

        # Last frame is always a keyframe
        if keyframe_indices[-1] != frame_count - 1:
            keyframe_indices.append(frame_count - 1)

        return {
            "frame_count": frame_count,
            "motion_detected": len(motion_vectors) > 0 and max(motion_vectors) > 0.01,
            "keyframe_indices": keyframe_indices,
            "motion_vectors": motion_vectors,
        }

    def generate_intermediate_frames(
        self,
        start_frame: np.ndarray,
        end_frame: np.ndarray,
        num_frames: int = 5,
        style: Optional[str] = None,
    ) -> List[np.ndarray]:
        """
        Generate intermediate frames between two keyframes.

        Args:
            start_frame: Starting keyframe
            end_frame: Ending keyframe
            num_frames: Number of intermediate frames to generate
            style: Style preset to use (None uses current style)

        Returns:
            List of generated intermediate frames
        """
        if style and style in self.style_presets:
            self.current_style = style

        preset = self.style_presets[self.current_style]
        smoothing = preset["smoothing"]

        intermediate_frames = []

        for i in range(1, num_frames + 1):
            # Calculate interpolation weight
            t = i / (num_frames + 1)

            # Apply smoothing based on interpolation method
            if preset["interpolation"] == "linear":
                weight = t
            elif preset["interpolation"] == "cubic":
                weight = t * t * (3 - 2 * t)  # Smoothstep
            elif preset["interpolation"] == "bezier":
                weight = t * t * t * (t * (6 * t - 15) + 10)  # Smootherstep
            else:
                weight = t

            # Generate interpolated frame
            interpolated = (1 - weight) * start_frame + weight * end_frame

            # Apply smoothing
            if smoothing > 0:
                interpolated = interpolated * (1 - smoothing) + (
                    start_frame * 0.5 + end_frame * 0.5
                ) * smoothing

            intermediate_frames.append(interpolated.astype(start_frame.dtype))

        return intermediate_frames

    def apply_style_preset(self, style_name: str) -> bool:
        """
        Apply a style preset to the assistant.

        Args:
            style_name: Name of the style preset

        Returns:
            True if style was applied, False if style not found
        """
        if style_name in self.style_presets:
            self.current_style = style_name
            return True
        return False

    def get_available_styles(self) -> List[str]:
        """
        Get list of available style presets.

        Returns:
            List of style preset names
        """
        return list(self.style_presets.keys())

    def add_custom_style(
        self, name: str, interpolation: str, smoothing: float
    ) -> bool:
        """
        Add a custom style preset.

        Args:
            name: Name for the custom style
            interpolation: Interpolation method (linear, cubic, bezier)
            smoothing: Smoothing factor (0.0 to 1.0)

        Returns:
            True if style was added, False if invalid parameters
        """
        if interpolation not in ["linear", "cubic", "bezier"]:
            return False
        if not 0 <= smoothing <= 1:
            return False

        self.style_presets[name] = {
            "interpolation": interpolation,
            "smoothing": smoothing,
        }
        return True

    def process_sequence(
        self,
        frames: List[np.ndarray],
        target_fps: int = 24,
        style: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a complete stop-motion sequence, generating smooth animation.

        Args:
            frames: List of input frames
            target_fps: Target frames per second for output
            style: Style preset to use

        Returns:
            Dictionary containing:
            - processed_frames: List of all frames (original + interpolated)
            - original_count: Number of original frames
            - generated_count: Number of generated frames
            - total_count: Total number of frames
        """
        if not frames:
            return {
                "processed_frames": [],
                "original_count": 0,
                "generated_count": 0,
                "total_count": 0,
            }

        if style:
            self.apply_style_preset(style)

        # Analyze sequence to find keyframes
        analysis = self.analyze_sequence(frames)
        keyframe_indices = analysis["keyframe_indices"]

        processed_frames = []
        generated_count = 0

        # Generate intermediate frames between keyframes
        for i in range(len(keyframe_indices) - 1):
            start_idx = keyframe_indices[i]
            end_idx = keyframe_indices[i + 1]

            # Add the starting keyframe
            processed_frames.append(frames[start_idx])

            # Calculate number of intermediate frames based on target FPS
            num_intermediate = max(1, (end_idx - start_idx) * 2)

            # Generate intermediate frames
            intermediate = self.generate_intermediate_frames(
                frames[start_idx], frames[end_idx], num_intermediate
            )
            processed_frames.extend(intermediate)
            generated_count += len(intermediate)

        # Add the last keyframe
        processed_frames.append(frames[keyframe_indices[-1]])

        return {
            "processed_frames": processed_frames,
            "original_count": len(frames),
            "generated_count": generated_count,
            "total_count": len(processed_frames),
        }
