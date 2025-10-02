"""
Synthetic Data Generation Pipeline

This module provides comprehensive synthetic data generation capabilities for
training narrative-focused language models. It combines multi-agent generation,
quality control, and consistency validation to create coherent training datasets.

Key Components:
- SyntheticGenerator: Main pipeline orchestrator
- QualityControl: Validation and filtering of generated content
- PromptTemplates: Structured prompts for different document types
- DataAugmentation: Techniques for expanding and diversifying datasets
"""

from .synthetic_generator import SyntheticDataGenerator
from .quality_control import QualityController, QualityMetrics
from .prompt_templates import PromptTemplateManager
from .data_augmentation import DataAugmentor

__all__ = [
    "SyntheticDataGenerator",
    "QualityController",
    "QualityMetrics",
    "PromptTemplateManager",
    "DataAugmentor",
]