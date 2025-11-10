from setuptools import setup, find_packages

setup(
    name="kimi-k2",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    python_requires=">=3.8",
)
