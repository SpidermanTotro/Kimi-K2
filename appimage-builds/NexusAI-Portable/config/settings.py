"""
NEXUS AI - Configuration Settings
Complete configuration management for the entire system
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv()

class NexusConfig(BaseSettings):
    """Complete configuration for Nexus AI"""
    
    # ========== API KEYS ==========
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    # ========== MODEL CONFIGURATIONS ==========
    
    # GPT Models
    GPT_4_TURBO: str = "gpt-4-turbo"
    GPT_4_VISION: str = "gpt-4-vision-preview"
    GPT_4: str = "gpt-4"
    GPT_35_TURBO: str = "gpt-3.5-turbo"
    
    # Reasoning Models (o1 series)
    O1_PREVIEW: str = "o1-preview"
    O1_MINI: str = "o1-mini"
    O1: str = "o1"
    
    # Claude Models
    CLAUDE_3_OPUS: str = "claude-3-opus-20240229"
    CLAUDE_3_SONNET: str = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU: str = "claude-3-haiku-20240307"
    
    # Default selections
    DEFAULT_CHAT_MODEL: str = Field(default="gpt-4-turbo", env="DEFAULT_CHAT_MODEL")
    DEFAULT_REASONING_MODEL: str = Field(default="o1-mini", env="DEFAULT_REASONING_MODEL")
    DEFAULT_CODE_MODEL: str = Field(default="gpt-4", env="DEFAULT_CODE_MODEL")
    DEFAULT_VISION_MODEL: str = Field(default="gpt-4-vision-preview", env="DEFAULT_VISION_MODEL")
    
    # ========== MODEL PARAMETERS ==========
    TEMPERATURE: float = Field(default=0.7, env="TEMPERATURE")
    MAX_TOKENS: int = Field(default=4096, env="MAX_TOKENS")
    
    # Reasoning efforts (for o1 models)
    REASONING_EFFORT: str = Field(default="medium", env="REASONING_EFFORT")
    REASONING_EFFORTS: Dict[str, str] = {
        "none": "none",
        "minimal": "minimal",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "extra_high": "extra_high"
    }
    
    # ========== MEMORY SETTINGS ==========
    MEMORY_COLLECTION: str = Field(default="nexus_memories", env="MEMORY_COLLECTION")
    MAX_MEMORY_RESULTS: int = Field(default=5, env="MAX_MEMORY_RESULTS")
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    CACHE_RETENTION: str = Field(default="24h", env="CACHE_RETENTION")
    
    # ========== AGENT SETTINGS ==========
    MAX_AGENT_ITERATIONS: int = Field(default=10, env="MAX_AGENT_ITERATIONS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")
    
    # ========== TOOL SETTINGS ==========
    ENABLE_CODE_EXECUTION: bool = Field(default=True, env="ENABLE_CODE_EXECUTION")
    CODE_EXECUTION_TIMEOUT: int = Field(default=30, env="CODE_EXECUTION_TIMEOUT")
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    ALLOWED_FILE_TYPES: List[str] = [".txt", ".py", ".json", ".csv", ".md", ".pdf", ".docx"]
    
    # ========== API SERVER SETTINGS ==========
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    LOG_LEVEL: str = Field(default="info", env="LOG_LEVEL")
    
    # ========== SECURITY ==========
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # ========== PERSONALITIES ==========
    PERSONALITIES: Dict[str, str] = {
        "default": "You are Nexus AI, a highly capable and balanced AI assistant.",
        "professional": "You are a formal, precise, and professional AI assistant.",
        "friendly": "You are a warm, conversational, and approachable AI assistant.",
        "technical": "You are a highly technical AI expert focused on precision and detail.",
        "creative": "You are a creative, imaginative, and innovative AI assistant.",
        "efficient": "You are a concise, direct, and efficiency-focused AI assistant.",
        "teacher": "You are a patient, educational AI that explains things clearly.",
        "researcher": "You are a thorough, analytical research-focused AI assistant.",
    }
    
    # ========== AGENT ROLES ==========
    AGENT_ROLES: Dict[str, str] = {
        "orchestrator": "Coordinates multiple agents to solve complex tasks",
        "coder": "Expert programmer who writes, debugs, and executes code",
        "researcher": "Web researcher who finds and analyzes information",
        "analyst": "Data analyst who processes and interprets data",
        "creative": "Creative writer and idea generator",
        "vision": "Image understanding and visual analysis expert",
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global config instance
config = NexusConfig()