"""Core framework configuration management."""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class AnimationConfig(BaseModel):
    """Animation suite configuration."""
    enabled: bool = Field(default=True, description="Enable animation features")
    output_dir: str = Field(default="output/animations", description="Animation output directory")
    default_fps: int = Field(default=30, description="Default frames per second")
    quality_preset: str = Field(default="tv", description="Quality preset: draft, tv, cinema")
    max_duration: int = Field(default=300, description="Maximum animation duration in seconds")


class CommandsConfig(BaseModel):
    """Generative interfaces configuration."""
    enabled: bool = Field(default=True, description="Enable command features")
    shell_mode: str = Field(default="bash", description="Shell mode: bash, zsh, fish")
    script_dir: str = Field(default="scripts", description="Scripts directory")
    allow_dangerous: bool = Field(default=False, description="Allow potentially dangerous commands")


class ModelsConfig(BaseModel):
    """GPT models configuration."""
    enabled: bool = Field(default=True, description="Enable AI models")
    default_model: str = Field(default="lightweight", description="Default model: lightweight, heavy")
    model_cache_dir: str = Field(default=".cache/models", description="Model cache directory")
    max_memory_gb: int = Field(default=16, description="Maximum memory allocation in GB")
    use_optimization: bool = Field(default=True, description="Enable model optimizations")


class UIConfig(BaseModel):
    """User interface configuration."""
    cli_enabled: bool = Field(default=True, description="Enable CLI interface")
    desktop_enabled: bool = Field(default=False, description="Enable desktop UI")
    theme: str = Field(default="dark", description="UI theme: dark, light")
    show_tutorials: bool = Field(default=True, description="Show tutorials for new users")


class CollaborationConfig(BaseModel):
    """Multi-user collaboration configuration."""
    enabled: bool = Field(default=False, description="Enable collaboration features")
    server_host: str = Field(default="localhost", description="Collaboration server host")
    server_port: int = Field(default=8080, description="Collaboration server port")
    max_users: int = Field(default=10, description="Maximum concurrent users")


class Config(BaseModel):
    """Main framework configuration."""
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    commands: CommandsConfig = Field(default_factory=CommandsConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    collaboration: CollaborationConfig = Field(default_factory=CollaborationConfig)
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
    
    @classmethod
    def default(cls) -> "Config":
        """Create default configuration."""
        return cls()
