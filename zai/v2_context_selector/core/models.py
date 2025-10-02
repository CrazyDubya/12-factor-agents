"""
Data models for the V2 Context Selection System.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TextSegment:
    """A text segment with metadata for context selection.

    Attributes:
        id: Unique identifier for the segment
        text: The actual text content
        document_id: Source document identifier
        position: Position within the document (0-based)
        timestamp: Optional timestamp for temporal relevance
        metadata: Additional metadata dictionary
        temporal_relevance: Computed time-based relevance score
        topic_cluster: Optional topic cluster assignment
    """
    id: str
    text: str
    document_id: str
    position: int
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    temporal_relevance: float = 0.0
    topic_cluster: Optional[str] = None

    def __post_init__(self):
        """Validate the segment after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Segment ID cannot be empty")
        if not self.text or not self.text.strip():
            raise ValueError("Segment text cannot be empty")
        if self.position < 0:
            raise ValueError("Position must be non-negative")

    @property
    def word_count(self) -> int:
        """Return the number of words in this segment."""
        return len(self.text.split())

    @property
    def character_count(self) -> int:
        """Return the number of characters in this segment."""
        return len(self.text)

    def get_tokens(self) -> List[str]:
        """Get tokens for this segment."""
        return self.text.split()

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "document_id": self.document_id,
            "position": self.position,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "temporal_relevance": self.temporal_relevance,
            "topic_cluster": self.topic_cluster,
            "word_count": self.word_count,
            "character_count": self.character_count
        }


@dataclass
class SelectionResult:
    """Result of context selection operation.

    Attributes:
        selected_segments: List of selected text segments
        method: Method used for selection
        execution_time_ms: Execution time in milliseconds
        query: Original query string
        total_segments_available: Total number of segments considered
        budget_used: Number of tokens/budget units used
        confidence_score: Overall confidence in the selection
        debug_info: Additional debugging information
    """
    selected_segments: List[TextSegment]
    method: str
    execution_time_ms: float
    query: str
    total_segments_available: int
    budget_used: int = 0
    confidence_score: float = 0.0
    debug_info: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the result after initialization."""
        if self.execution_time_ms < 0:
            raise ValueError("Execution time cannot be negative")
        if self.budget_used < 0:
            raise ValueError("Budget used cannot be negative")
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")

    @property
    def selection_count(self) -> int:
        """Number of selected segments."""
        return len(self.selected_segments)

    @property
    def total_words_selected(self) -> int:
        """Total number of words in selected segments."""
        return sum(seg.word_count for seg in self.selected_segments)

    @property
    def selected_segment_ids(self) -> List[str]:
        """IDs of selected segments."""
        return [seg.id for seg in self.selected_segments]

    def get_segment_texts(self) -> List[str]:
        """Get text content of selected segments."""
        return [seg.text for seg in self.selected_segments]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            "selected_segments": [seg.to_dict() for seg in self.selected_segments],
            "method": self.method,
            "execution_time_ms": self.execution_time_ms,
            "query": self.query,
            "total_segments_available": self.total_segments_available,
            "budget_used": self.budget_used,
            "confidence_score": self.confidence_score,
            "selection_count": self.selection_count,
            "total_words_selected": self.total_words_selected,
            "selected_segment_ids": self.selected_segment_ids,
            "debug_info": self.debug_info
        }


@dataclass
class QueryAnalysis:
    """Analysis of a query for feature selection.

    Attributes:
        original_query: The original query string
        clean_query: Cleaned and processed query
        is_time_sensitive: Whether query requires temporal ranking
        requires_expansion: Whether query would benefit from expansion
        complexity_score: Complexity score (0-1)
        keywords: Extracted keywords
        query_type: Type of query (what, how, why, etc.)
    """
    original_query: str
    clean_query: str
    is_time_sensitive: bool
    requires_expansion: bool
    complexity_score: float
    keywords: List[str]
    query_type: Optional[str] = None

    def __post_init__(self):
        """Validate analysis after initialization."""
        if not 0 <= self.complexity_score <= 1:
            raise ValueError("Complexity score must be between 0 and 1")
        if not self.original_query.strip():
            raise ValueError("Original query cannot be empty")