"""
Document Generation System

High-level document generation interface that combines trained models
with narrative coherence validation and multi-document coordination.

Key Components:
- DocumentGenerator: Main generation orchestrator
- CoherenceValidator: Real-time coherence checking
- GenerationConfig: Configuration for generation parameters
- OutputFormatter: Structured output formatting
"""

from .document_generator import DocumentGenerator, GenerationConfig
from .coherence_validator import CoherenceValidator
from .output_formatter import OutputFormatter, DocumentFormat

__all__ = [
    "DocumentGenerator",
    "GenerationConfig",
    "CoherenceValidator",
    "OutputFormatter",
    "DocumentFormat",
]