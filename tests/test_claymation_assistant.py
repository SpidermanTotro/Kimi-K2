"""Tests for Claymation Assistant"""

import numpy as np
import pytest
from kimi_k2.animation import ClayamationAssistant


class TestClayamationAssistant:
    """Test suite for ClayamationAssistant class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.assistant = ClayamationAssistant()

    def test_initialization(self):
        """Test assistant initialization."""
        assert self.assistant is not None
        assert self.assistant.current_style == "classic"
        assert "classic" in self.assistant.style_presets
        assert "smooth" in self.assistant.style_presets
        assert "artistic" in self.assistant.style_presets

    def test_analyze_sequence_empty(self):
        """Test sequence analysis with empty input."""
        result = self.assistant.analyze_sequence([])
        assert result["frame_count"] == 0
        assert result["motion_detected"] is False
        assert result["keyframe_indices"] == []

    def test_analyze_sequence_single_frame(self):
        """Test sequence analysis with single frame."""
        frame = np.random.rand(10, 10, 3)
        result = self.assistant.analyze_sequence([frame])
        assert result["frame_count"] == 1
        assert result["motion_detected"] is False

    def test_analyze_sequence_multiple_frames(self):
        """Test sequence analysis with multiple frames."""
        frames = [np.random.rand(10, 10, 3) for _ in range(5)]
        result = self.assistant.analyze_sequence(frames)
        assert result["frame_count"] == 5
        assert isinstance(result["motion_detected"], bool)
        assert len(result["keyframe_indices"]) >= 2  # At least first and last
        assert result["keyframe_indices"][0] == 0
        assert result["keyframe_indices"][-1] == 4

    def test_generate_intermediate_frames(self):
        """Test intermediate frame generation."""
        start_frame = np.zeros((10, 10, 3))
        end_frame = np.ones((10, 10, 3))
        
        intermediate = self.assistant.generate_intermediate_frames(
            start_frame, end_frame, num_frames=3
        )
        
        assert len(intermediate) == 3
        assert intermediate[0].shape == start_frame.shape
        
        # Check interpolation is working (values between 0 and 1)
        for frame in intermediate:
            assert np.all(frame >= 0) and np.all(frame <= 1)

    def test_generate_intermediate_frames_with_style(self):
        """Test intermediate frame generation with different styles."""
        start_frame = np.zeros((10, 10, 3))
        end_frame = np.ones((10, 10, 3))
        
        for style in ["classic", "smooth", "artistic"]:
            intermediate = self.assistant.generate_intermediate_frames(
                start_frame, end_frame, num_frames=3, style=style
            )
            assert len(intermediate) == 3

    def test_apply_style_preset(self):
        """Test applying style presets."""
        assert self.assistant.apply_style_preset("smooth")
        assert self.assistant.current_style == "smooth"
        
        assert not self.assistant.apply_style_preset("nonexistent")

    def test_get_available_styles(self):
        """Test getting available styles."""
        styles = self.assistant.get_available_styles()
        assert "classic" in styles
        assert "smooth" in styles
        assert "artistic" in styles

    def test_add_custom_style(self):
        """Test adding custom style."""
        assert self.assistant.add_custom_style("custom", "cubic", 0.5)
        assert "custom" in self.assistant.get_available_styles()
        
        # Test invalid parameters
        assert not self.assistant.add_custom_style("invalid1", "invalid", 0.5)
        assert not self.assistant.add_custom_style("invalid2", "linear", 1.5)

    def test_process_sequence(self):
        """Test processing complete sequence."""
        frames = [np.random.rand(10, 10, 3) for _ in range(3)]
        result = self.assistant.process_sequence(frames, target_fps=24)
        
        assert "processed_frames" in result
        assert "original_count" in result
        assert "generated_count" in result
        assert "total_count" in result
        
        assert result["original_count"] == 3
        assert result["generated_count"] > 0
        assert result["total_count"] > result["original_count"]

    def test_process_sequence_empty(self):
        """Test processing empty sequence."""
        result = self.assistant.process_sequence([])
        assert result["original_count"] == 0
        assert result["generated_count"] == 0
        assert result["total_count"] == 0
