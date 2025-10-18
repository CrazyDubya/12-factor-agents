"""Setup script for Conductor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md")
long_description = readme.read_text() if readme.exists() else ""

setup(
    name="wave-flow-conductor",
    version="0.1.0",
    description="AI orchestration system with privacy/budget/deadline awareness",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wave Flow",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "llm": ["openai>=1.0.0", "anthropic>=0.25.0"],
        "validation": ["jsonschema>=4.20.0", "pytest>=8.0.0"],
        "web": ["fastapi>=0.110.0", "uvicorn>=0.27.0", "websockets>=12.0"],
        "dev": ["black>=24.0.0", "mypy>=1.8.0", "pytest-asyncio>=0.23.0"],
    },
    entry_points={
        "console_scripts": [
            "conductor=conductor.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
