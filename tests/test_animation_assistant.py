"""Tests for Animation Assistant"""

import json
import pytest
from kimi_k2.animation import AnimationAssistant


class TestAnimationAssistant:
    """Test suite for AnimationAssistant class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.assistant = AnimationAssistant()

    def test_initialization(self):
        """Test assistant initialization."""
        assert self.assistant is not None
        assert len(self.assistant.animations) == 0
        assert len(self.assistant.skeletons) == 0

    def test_create_animation_loop(self):
        """Test creating animation loop."""
        keyframes = [
            {"time": 0.0, "transform": {"x": 0, "y": 0}},
            {"time": 0.5, "transform": {"x": 5, "y": 5}},
            {"time": 1.0, "transform": {"x": 10, "y": 0}},
        ]
        
        assert self.assistant.create_animation_loop(
            "test_anim", keyframes, duration=2.0, loop_type="repeat"
        )
        assert "test_anim" in self.assistant.animations
        assert self.assistant.current_animation == "test_anim"

    def test_create_animation_loop_invalid(self):
        """Test creating animation with invalid parameters."""
        assert not self.assistant.create_animation_loop("invalid", [], duration=1.0)
        assert not self.assistant.create_animation_loop(
            "invalid", [{"time": 0}], duration=1.0, loop_type="invalid"
        )

    def test_create_skeleton(self):
        """Test creating skeleton."""
        bones = [
            {"name": "root", "position": [0, 0, 0]},
            {"name": "spine", "position": [0, 1, 0]},
            {"name": "head", "position": [0, 2, 0]},
        ]
        hierarchy = {"spine": "root", "head": "spine"}
        
        assert self.assistant.create_skeleton("test_skel", bones, hierarchy)
        assert "test_skel" in self.assistant.skeletons

    def test_create_skeleton_invalid_hierarchy(self):
        """Test creating skeleton with invalid hierarchy."""
        bones = [{"name": "root", "position": [0, 0, 0]}]
        hierarchy = {"nonexistent": "root"}
        
        assert not self.assistant.create_skeleton("invalid", bones, hierarchy)

    def test_apply_skeletal_animation(self):
        """Test applying animation to skeleton."""
        # Create skeleton
        bones = [{"name": "root", "position": [0, 0, 0]}]
        self.assistant.create_skeleton("skel", bones, {})
        
        # Create animation
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("anim", keyframes)
        
        result = self.assistant.apply_skeletal_animation("skel", "anim")
        assert "skeleton" in result
        assert result["skeleton"] == "skel"
        assert result["animation"] == "anim"

    def test_interpolate_keyframes(self):
        """Test keyframe interpolation."""
        keyframes = [
            {"time": 0.0, "transform": {"x": 0, "y": 0}},
            {"time": 1.0, "transform": {"x": 10, "y": 10}},
        ]
        
        result = self.assistant.interpolate_keyframes(keyframes, 0.5)
        assert "transform" in result
        assert result["transform"]["x"] == 5.0
        assert result["transform"]["y"] == 5.0

    def test_interpolate_keyframes_vector(self):
        """Test keyframe interpolation with vectors."""
        keyframes = [
            {"time": 0.0, "transform": {"pos": [0, 0, 0]}},
            {"time": 1.0, "transform": {"pos": [10, 10, 10]}},
        ]
        
        result = self.assistant.interpolate_keyframes(keyframes, 0.5)
        assert result["transform"]["pos"] == [5.0, 5.0, 5.0]

    def test_export_to_json(self):
        """Test exporting to JSON."""
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("test", keyframes)
        
        json_str = self.assistant.export_to_json("test")
        data = json.loads(json_str)
        
        assert "animation" in data
        assert "format" in data
        assert data["format"] == "kimi-k2-json"

    def test_export_to_json_with_skeleton(self):
        """Test exporting to JSON with skeleton."""
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("test", keyframes)
        
        bones = [{"name": "root", "position": [0, 0, 0]}]
        self.assistant.create_skeleton("skel", bones, {})
        
        json_str = self.assistant.export_to_json("test", "skel")
        data = json.loads(json_str)
        
        assert "animation" in data
        assert "skeleton" in data

    def test_export_to_fbx(self):
        """Test exporting to FBX format."""
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("test", keyframes)
        
        fbx_str = self.assistant.export_to_fbx("test")
        assert "FBX" in fbx_str
        assert "test" in fbx_str

    def test_export_to_gltf(self):
        """Test exporting to glTF format."""
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("test", keyframes)
        
        gltf_str = self.assistant.export_to_gltf("test")
        data = json.loads(gltf_str)
        
        assert "asset" in data
        assert "animations" in data

    def test_get_animation_info(self):
        """Test getting animation info."""
        keyframes = [
            {"time": 0.0, "transform": {"x": 0}},
            {"time": 1.0, "transform": {"x": 10}},
        ]
        self.assistant.create_animation_loop("test", keyframes, duration=2.0)
        
        info = self.assistant.get_animation_info("test")
        assert info is not None
        assert info["name"] == "test"
        assert info["keyframe_count"] == 2
        assert info["duration"] == 2.0

    def test_list_animations(self):
        """Test listing animations."""
        keyframes = [{"time": 0.0, "transform": {"x": 0}}]
        self.assistant.create_animation_loop("anim1", keyframes)
        self.assistant.create_animation_loop("anim2", keyframes)
        
        animations = self.assistant.list_animations()
        assert "anim1" in animations
        assert "anim2" in animations

    def test_list_skeletons(self):
        """Test listing skeletons."""
        bones = [{"name": "root", "position": [0, 0, 0]}]
        self.assistant.create_skeleton("skel1", bones, {})
        self.assistant.create_skeleton("skel2", bones, {})
        
        skeletons = self.assistant.list_skeletons()
        assert "skel1" in skeletons
        assert "skel2" in skeletons
