"""Tests for AI model manager functionality."""

import pytest

from kimi_k2.models.manager import ModelManager, ModelType, ModelInfo
from kimi_k2.core.config import ModelsConfig


class TestModelManager:
    """Test model manager functionality."""
    
    @pytest.fixture
    def model_manager(self, tmp_path):
        """Create model manager for testing."""
        config = ModelsConfig(model_cache_dir=str(tmp_path / "cache"))
        return ModelManager(config)
        
    def test_manager_initialization(self, model_manager):
        """Test model manager initialization."""
        assert model_manager is not None
        assert model_manager.cache_dir.exists()
        
    def test_available_models(self, model_manager):
        """Test available models are registered."""
        models = model_manager.list_models()
        
        assert len(models) == 2
        model_names = [m.name for m in models]
        assert "lightweight" in model_names
        assert "heavy" in model_names
        
    def test_load_lightweight_model(self, model_manager):
        """Test loading lightweight model."""
        model_manager.load_model("lightweight")
        
        assert model_manager.current_model == "lightweight"
        assert model_manager.model_info["lightweight"].loaded is True
        
    def test_load_heavy_model(self, model_manager):
        """Test loading heavy model."""
        model_manager.load_model("heavy")
        
        assert model_manager.current_model == "heavy"
        assert model_manager.model_info["heavy"].loaded is True
        
    def test_load_unknown_model(self, model_manager):
        """Test loading unknown model raises error."""
        with pytest.raises(ValueError):
            model_manager.load_model("unknown")
            
    def test_unload_model(self, model_manager):
        """Test unloading a model."""
        model_manager.load_model("lightweight")
        model_manager.unload_model("lightweight")
        
        assert model_manager.current_model is None
        assert model_manager.model_info["lightweight"].loaded is False
        
    def test_switch_models(self, model_manager):
        """Test switching between models."""
        model_manager.load_model("lightweight")
        assert model_manager.current_model == "lightweight"
        
        model_manager.load_model("heavy")
        assert model_manager.current_model == "heavy"
        assert model_manager.model_info["lightweight"].loaded is False
        
    def test_generate_with_default_model(self, model_manager):
        """Test generation loads default model."""
        result = model_manager.generate("Test prompt")
        
        assert model_manager.current_model == model_manager.config.default_model
        assert result is not None
        
    def test_generate_with_loaded_model(self, model_manager):
        """Test generation with loaded model."""
        model_manager.load_model("lightweight")
        result = model_manager.generate("Test prompt")
        
        assert result is not None
        assert "Test prompt" in result


class TestLightweightModel:
    """Test lightweight model functionality."""
    
    @pytest.fixture
    def model_manager(self, tmp_path):
        """Create model manager for testing."""
        config = ModelsConfig(model_cache_dir=str(tmp_path / "cache"))
        return ModelManager(config)
    
    def test_model_load_unload(self, model_manager):
        """Test model load and unload."""
        model_manager.load_model("lightweight")
        model = model_manager.models["lightweight"]
        
        assert model.loaded is True
        
        model.unload()
        assert model.loaded is False
        
    def test_generate_without_load(self, model_manager):
        """Test generation without loading raises error."""
        from kimi_k2.models.manager import LightweightModel
        model = LightweightModel()
        
        with pytest.raises(RuntimeError):
            model.generate("test")
            
    def test_generate_with_max_tokens(self, model_manager):
        """Test generation with max tokens parameter."""
        model_manager.load_model("lightweight")
        result = model_manager.generate("Test", max_tokens=50)
        
        assert result is not None


class TestHeavyModel:
    """Test heavy model functionality."""
    
    @pytest.fixture
    def model_manager(self, tmp_path):
        """Create model manager for testing."""
        config = ModelsConfig(model_cache_dir=str(tmp_path / "cache"))
        return ModelManager(config)
    
    def test_model_with_optimization(self, tmp_path):
        """Test heavy model with optimization enabled."""
        config = ModelsConfig(
            model_cache_dir=str(tmp_path / "cache"),
            use_optimization=True
        )
        manager = ModelManager(config)
        manager.load_model("heavy")
        
        model = manager.models["heavy"]
        assert model.use_optimization is True
        
    def test_model_without_optimization(self, tmp_path):
        """Test heavy model without optimization."""
        config = ModelsConfig(
            model_cache_dir=str(tmp_path / "cache"),
            use_optimization=False
        )
        manager = ModelManager(config)
        manager.load_model("heavy")
        
        model = manager.models["heavy"]
        assert model.use_optimization is False
        
    def test_generate_with_temperature(self, model_manager):
        """Test generation with temperature parameter."""
        model_manager.load_model("heavy")
        result = model_manager.generate("Test", temperature=0.5)
        
        assert result is not None
        
    def test_memory_optimization(self, model_manager):
        """Test memory optimization."""
        model_manager.load_model("heavy")
        model = model_manager.models["heavy"]
        
        # Should not raise error
        model.optimize_memory()


class TestMemoryManagement:
    """Test memory management functionality."""
    
    @pytest.fixture
    def model_manager(self, tmp_path):
        """Create model manager for testing."""
        config = ModelsConfig(model_cache_dir=str(tmp_path / "cache"))
        return ModelManager(config)
    
    def test_memory_limit_enforced(self, tmp_path):
        """Test memory limit is enforced."""
        config = ModelsConfig(
            model_cache_dir=str(tmp_path / "cache"),
            max_memory_gb=2  # Lower than heavy model requirement
        )
        manager = ModelManager(config)
        
        # Lightweight should work (2GB requirement <= 2GB limit)
        manager.load_model("lightweight")
        
        # Heavy model should fail (16GB requirement > 2GB limit)
        with pytest.raises(RuntimeError):
            manager.load_model("heavy")
            
    def test_multiple_models_memory(self, model_manager):
        """Test loading multiple models respects memory."""
        # Load one model
        model_manager.load_model("lightweight")
        first_model = model_manager.current_model
        
        # Load another - should unload first
        model_manager.load_model("heavy")
        
        assert model_manager.model_info[first_model].loaded is False
        assert model_manager.model_info["heavy"].loaded is True


class TestModelInfo:
    """Test model information functionality."""
    
    @pytest.fixture
    def model_manager(self, tmp_path):
        """Create model manager for testing."""
        config = ModelsConfig(model_cache_dir=str(tmp_path / "cache"))
        return ModelManager(config)
    
    def test_model_info_structure(self, model_manager):
        """Test model info has correct structure."""
        models = model_manager.list_models()
        
        for model in models:
            assert hasattr(model, 'name')
            assert hasattr(model, 'type')
            assert hasattr(model, 'memory_gb')
            assert hasattr(model, 'parameters')
            assert hasattr(model, 'optimized')
            assert hasattr(model, 'loaded')
            
    def test_model_type_enum(self, model_manager):
        """Test model types are correct enum values."""
        models = model_manager.list_models()
        
        lightweight = next(m for m in models if m.name == "lightweight")
        heavy = next(m for m in models if m.name == "heavy")
        
        assert lightweight.type == ModelType.LIGHTWEIGHT
        assert heavy.type == ModelType.HEAVY
