"""
Setup script for V2 Context Selection System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="v2-context-selector",
    version="2.0.0",
    author="V2 Context Selection Team",
    author_email="team@v2context.com",
    description="A high-performance hybrid semantic-keyword retrieval system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/v2-context-selector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "performance": [
            "memory-profiler>=0.60.0",
            "line-profiler>=4.0.0",
        ],
        "web": [
            "fastapi>=0.95.0",
            "uvicorn>=0.20.0",
            "streamlit>=1.25.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "matplotlib>=3.5.0",
        ],
        "cache": [
            "redis>=4.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "v2-context-selector=v2_context_selector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)