"""
Finetune: Synthetic Narrative Generation System

A comprehensive framework for training language models to generate coherent
fictional documents that form unified narrative worlds.
"""

# Core configuration
from .config import SUPPORTED_MODELS, TrainingConfig

# Training components
from .training import ModelTrainer, EvaluationManager, DatasetManager

# Data generation
from .data_generation import SyntheticDataGenerator, QualityController

# Document generation
from .generation import DocumentGenerator, GenerationConfig

# Knowledge graph
from .knowledge_graph import KnowledgeGraphManager

# Agents
from .agents import AgentCoordinator

__version__ = "0.1.0"
__author__ = "Finetune Research Team"

__all__ = [
    "SUPPORTED_MODELS",
    "TrainingConfig",
    "ModelTrainer",
    "EvaluationManager",
    "DatasetManager",
    "SyntheticDataGenerator",
    "QualityController",
    "DocumentGenerator",
    "GenerationConfig",
    "KnowledgeGraphManager",
    "AgentCoordinator",
]