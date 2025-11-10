"""Setup configuration for Kimi-K2 Unified Framework."""

from setuptools import setup, find_packages

setup(
    name="kimi-k2-framework",
    version="1.0.0",
    description="Unified AI Framework consolidating animation, commands, and GPT optimizations",
    author="Kimi Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "pillow>=9.0.0",
        "numpy>=1.21.0",
        "pyyaml>=6.0",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "ui": [
            "tkinter>=8.6",
            "customtkinter>=5.0.0",
        ],
        "animation": [
            "opencv-python>=4.5.0",
            "moviepy>=1.0.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "kimi-k2=kimi_k2.cli.main:cli",
        ],
    },
)
