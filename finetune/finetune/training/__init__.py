"""
Training and Evaluation Framework

This module provides comprehensive training capabilities for narrative-focused
language models, including parameter-efficient fine-tuning, evaluation metrics,
and specialized training procedures for coherent document generation.

Key Components:
- ModelTrainer: Main training orchestrator with PEFT support
- EvaluationManager: Comprehensive evaluation with narrative coherence metrics
- DatasetManager: Efficient dataset loading and preprocessing
- TrainingUtils: Utilities for model saving, logging, and optimization
"""

from .model_trainer import ModelTrainer, TrainingConfig
from .evaluation_manager import EvaluationManager, EvaluationMetrics
from .dataset_manager import DatasetManager
from .training_utils import TrainingUtils, ModelSaver, TrainingLogger

__all__ = [
    "ModelTrainer",
    "TrainingConfig",
    "EvaluationManager",
    "EvaluationMetrics",
    "DatasetManager",
    "TrainingUtils",
    "ModelSaver",
    "TrainingLogger",
]