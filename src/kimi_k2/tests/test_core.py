"""Tests for core framework functionality."""

import pytest
from pathlib import Path
import tempfile

from kimi_k2.core.framework import Framework
from kimi_k2.core.config import Config, AnimationConfig, CommandsConfig, ModelsConfig


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config.default()
        assert config.animation.enabled is True
        assert config.commands.enabled is True
        assert config.models.enabled is True
        
    def test_config_serialization(self):
        """Test config save and load."""
        config = Config.default()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
            
        try:
            config.save_to_file(temp_path)
            loaded_config = Config.load_from_file(temp_path)
            
            assert loaded_config.animation.enabled == config.animation.enabled
            assert loaded_config.models.default_model == config.models.default_model
        finally:
            temp_path.unlink()
            
    def test_custom_config(self):
        """Test custom configuration values."""
        config = Config(
            animation=AnimationConfig(enabled=False),
            models=ModelsConfig(default_model="heavy")
        )
        
        assert config.animation.enabled is False
        assert config.models.default_model == "heavy"


class TestFramework:
    """Test framework initialization and management."""
    
    def test_framework_creation(self):
        """Test framework can be created."""
        framework = Framework()
        assert framework is not None
        assert not framework._initialized
        
    def test_framework_initialization(self):
        """Test framework initialization."""
        config = Config.default()
        framework = Framework(config)
        framework.initialize()
        
        assert framework._initialized
        assert 'animation' in framework._modules
        assert 'commands' in framework._modules
        assert 'models' in framework._modules
        
        framework.shutdown()
        
    def test_framework_shutdown(self):
        """Test framework shutdown."""
        framework = Framework()
        framework.initialize()
        framework.shutdown()
        
        assert not framework._initialized
        assert len(framework._modules) == 0
        
    def test_get_module(self):
        """Test getting modules."""
        framework = Framework()
        framework.initialize()
        
        animation = framework.get_module('animation')
        assert animation is not None
        
        framework.shutdown()
        
    def test_get_module_not_initialized(self):
        """Test getting module before initialization raises error."""
        framework = Framework()
        
        with pytest.raises(RuntimeError):
            framework.get_module('animation')
            
    def test_get_nonexistent_module(self):
        """Test getting non-existent module raises error."""
        framework = Framework()
        framework.initialize()
        
        with pytest.raises(KeyError):
            framework.get_module('nonexistent')
            
        framework.shutdown()
        
    def test_disabled_module_not_loaded(self):
        """Test disabled modules are not loaded."""
        config = Config(
            animation=AnimationConfig(enabled=False)
        )
        framework = Framework(config)
        framework.initialize()
        
        assert 'animation' not in framework._modules
        
        framework.shutdown()
