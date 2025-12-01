"""
NEXUS AI - Logging System
Comprehensive logging with rich formatting
"""

import sys
from loguru import logger
from pathlib import Path
from config.settings import config

# Remove default handler
logger.remove()

# Add console handler with rich formatting
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL.upper(),
    colorize=True,
)

# Add file handler for persistent logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "nexus_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # Rotate at midnight
    retention="7 days",  # Keep logs for 7 days
    compression="zip",  # Compress old logs
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

# Add error-specific log file
logger.add(
    log_dir / "nexus_errors_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
)

def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logger.bind(name=name)

__all__ = ['logger', 'get_logger']