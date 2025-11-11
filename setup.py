"""
Kimi-K2 SDK Setup
Enhanced with Moon AI integration capabilities
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kimi-k2-sdk",
    version="1.0.0",
    author="Moonshot AI",
    author_email="support@moonshot.cn",
    description="Kimi K2 SDK with Moon AI integration capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moonshotai/Kimi-K2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "image": [
            "torch>=2.0.0",
            "diffusers>=0.21.0",
            "transformers>=4.30.0",
        ],
    },
)
