"""
Core components of the V2 Context Selection System.
"""

from .models import TextSegment, SelectionResult
from .selector import ContextSelector
from .embedding_manager import EmbeddingManager
from .evaluator import Evaluator

__all__ = [
    "TextSegment",
    "SelectionResult",
    "ContextSelector",
    "EmbeddingManager",
    "Evaluator"
]