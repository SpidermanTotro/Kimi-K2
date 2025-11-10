"""Pytest configuration and fixtures."""

import pytest
import logging


# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration for each test."""
    yield
    logging.getLogger().handlers.clear()
