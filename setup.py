"""Setup script for Kimi-K2 utilities and examples."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kimi-k2-utils",
    version="1.0.0",
    author="Moonshot AI",
    description="Utilities, examples, and tools for Kimi-K2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moonshotai/Kimi-K2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.25.0",
        "transformers>=4.30.0",
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "examples": [
            "tiktoken>=0.4.0",
            "numpy>=1.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kimi-cli=kimi_k2.cli.main:cli",
            "kimi-benchmark=kimi_k2.benchmark.runner:main",
        ],
    },
)
