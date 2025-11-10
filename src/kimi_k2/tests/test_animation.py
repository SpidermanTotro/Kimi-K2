"""Tests for animation suite functionality."""

import pytest
from pathlib import Path

from kimi_k2.animation.suite import AnimationSuite, QualityPreset, AnimationProject
from kimi_k2.core.config import AnimationConfig


class TestAnimationSuite:
    """Test animation suite functionality."""
    
    @pytest.fixture
    def animation_suite(self, tmp_path):
        """Create animation suite for testing."""
        config = AnimationConfig(output_dir=str(tmp_path / "animations"))
        return AnimationSuite(config)
        
    def test_suite_initialization(self, animation_suite):
        """Test animation suite initialization."""
        assert animation_suite is not None
        assert animation_suite.output_dir.exists()
        
    def test_create_project(self, animation_suite):
        """Test creating an animation project."""
        project = animation_suite.create_project(
            name="test_project",
            fps=30,
            duration=10.0,
            quality="tv"
        )
        
        assert project.name == "test_project"
        assert project.fps == 30
        assert project.duration == 10.0
        assert project.quality == QualityPreset.TV
        
    def test_create_project_with_defaults(self, animation_suite):
        """Test creating project with default values."""
        project = animation_suite.create_project(name="test_default")
        
        assert project.fps == animation_suite.config.default_fps
        assert project.quality == QualityPreset.TV
        
    def test_render_project(self, animation_suite):
        """Test rendering a project."""
        project = animation_suite.create_project(name="render_test")
        output_path = animation_suite.render_project("render_test")
        
        assert output_path.exists()
        assert output_path.name == "render_test.mp4"
        
    def test_render_nonexistent_project(self, animation_suite):
        """Test rendering non-existent project raises error."""
        with pytest.raises(ValueError):
            animation_suite.render_project("nonexistent")
            
    def test_multiple_projects(self, animation_suite):
        """Test managing multiple projects."""
        project1 = animation_suite.create_project(name="project1")
        project2 = animation_suite.create_project(name="project2")
        
        assert "project1" in animation_suite.projects
        assert "project2" in animation_suite.projects
        assert len(animation_suite.projects) == 2


class TestTimelineEditor:
    """Test timeline editor functionality."""
    
    @pytest.fixture
    def animation_suite(self, tmp_path):
        """Create animation suite for testing."""
        config = AnimationConfig(output_dir=str(tmp_path / "animations"))
        return AnimationSuite(config)
    
    def test_timeline_initialization(self, animation_suite):
        """Test timeline editor initialization."""
        editor = animation_suite.timeline_editor
        assert len(editor.timeline) == 0
        
    def test_add_clip(self, animation_suite):
        """Test adding clips to timeline."""
        editor = animation_suite.timeline_editor
        clip = {'type': 'video', 'data': 'test'}
        
        editor.add_clip(clip, 0.0)
        assert len(editor.timeline) == 1
        
    def test_add_multiple_clips_sorted(self, animation_suite):
        """Test clips are sorted by position."""
        editor = animation_suite.timeline_editor
        
        editor.add_clip({'data': 'clip2'}, 2.0)
        editor.add_clip({'data': 'clip1'}, 1.0)
        editor.add_clip({'data': 'clip3'}, 3.0)
        
        positions = [clip['position'] for clip in editor.timeline]
        assert positions == [1.0, 2.0, 3.0]
        
    def test_remove_clip(self, animation_suite):
        """Test removing clips from timeline."""
        editor = animation_suite.timeline_editor
        
        editor.add_clip({'data': 'clip1'}, 1.0)
        editor.add_clip({'data': 'clip2'}, 2.0)
        
        editor.remove_clip(0)
        assert len(editor.timeline) == 1


class TestAnimationOptimizer:
    """Test animation optimizer functionality."""
    
    @pytest.fixture
    def animation_suite(self, tmp_path):
        """Create animation suite for testing."""
        config = AnimationConfig(output_dir=str(tmp_path / "animations"))
        return AnimationSuite(config)
    
    def test_optimizer_initialization(self, animation_suite):
        """Test optimizer initialization."""
        optimizer = animation_suite.optimizer
        assert optimizer.optimizations_applied == 0
        
    def test_optimize_frames(self, animation_suite):
        """Test frame optimization."""
        optimizer = animation_suite.optimizer
        frames = [1, 2, 3, 4, 5]
        
        optimized = optimizer.optimize_frames(frames)
        assert len(optimized) == len(frames)
        assert optimizer.optimizations_applied == 1
        
    def test_interpolate_frames(self, animation_suite):
        """Test frame interpolation."""
        optimizer = animation_suite.optimizer
        
        start = {'frame': 1}
        end = {'frame': 10}
        
        interpolated = optimizer.interpolate_frames(start, end, 5)
        assert len(interpolated) == 5
