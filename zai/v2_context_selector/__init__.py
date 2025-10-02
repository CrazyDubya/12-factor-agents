"""
V2 Context Selection System

A hybrid semantic-keyword retrieval system for selecting relevant text segments
from large document collections. Optimized for real-time performance with
configurable features and multiple scoring strategies.

Basic Usage:
    from v2_context_selector import ContextSelector

    selector = ContextSelector()
    results = selector.select("What is artificial intelligence?", documents, budget=1000)

Advanced Usage:
    selector = ContextSelector(
        enable_temporal_ranking=True,
        enable_query_expansion=True,
        embedding_model="all-MiniLM-L6-v2"
    )
"""

from .core.selector import ContextSelector
from .core.models import TextSegment, SelectionResult
from .config.settings import Config

__version__ = "2.0.0"
__author__ = "V2 Context Selection Team"

__all__ = [
    "ContextSelector",
    "TextSegment",
    "SelectionResult",
    "Config"
]