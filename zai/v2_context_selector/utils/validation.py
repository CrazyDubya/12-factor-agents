"""
Validation utilities for the V2 Context Selection System.
"""

from typing import List
import re

from ..core.models import TextSegment


def validate_query(query: str) -> None:
    """Validate a query string.

    Args:
        query: Query string to validate

    Raises:
        ValueError: If query is invalid
    """
    if not query:
        raise ValueError("Query cannot be empty")

    if not isinstance(query, str):
        raise ValueError("Query must be a string")

    if len(query.strip()) == 0:
        raise ValueError("Query cannot be only whitespace")

    if len(query) > 10000:
        raise ValueError("Query too long (max 10000 characters)")

    # Check for potentially malicious content
    if any(char in query for char in ['<script', 'javascript:', 'data:']):
        raise ValueError("Query contains potentially unsafe content")


def validate_segments(segments: List[TextSegment]) -> None:
    """Validate a list of text segments.

    Args:
        segments: List of segments to validate

    Raises:
        ValueError: If segments are invalid
    """
    if not segments:
        raise ValueError("Segments list cannot be empty")

    if not isinstance(segments, list):
        raise ValueError("Segments must be a list")

    if len(segments) > 10000:
        raise ValueError("Too many segments (max 10000)")

    # Validate each segment
    segment_ids = set()
    for i, segment in enumerate(segments):
        if not isinstance(segment, TextSegment):
            raise ValueError(f"Segment {i} is not a TextSegment instance")

        # Check for duplicate IDs
        if segment.id in segment_ids:
            raise ValueError(f"Duplicate segment ID: {segment.id}")
        segment_ids.add(segment.id)

        # Validate segment content
        if not segment.text or not segment.text.strip():
            raise ValueError(f"Segment {segment.id} has empty text")

        if len(segment.text) > 100000:
            raise ValueError(f"Segment {segment.id} too long (max 100000 characters)")

        if segment.position < 0:
            raise ValueError(f"Segment {segment.id} has invalid position: {segment.position}")


def validate_budget(budget: int) -> None:
    """Validate a token budget.

    Args:
        budget: Token budget to validate

    Raises:
        ValueError: If budget is invalid
    """
    if not isinstance(budget, int):
        raise ValueError("Budget must be an integer")

    if budget <= 0:
        raise ValueError("Budget must be positive")

    if budget > 100000:
        raise ValueError("Budget too large (max 100000 tokens)")


def validate_text_length(text: str, max_length: int = 100000) -> None:
    """Validate text length.

    Args:
        text: Text to validate
        max_length: Maximum allowed length

    Raises:
        ValueError: If text is too long
    """
    if len(text) > max_length:
        raise ValueError(f"Text too long (max {max_length} characters)")


def sanitize_text(text: str) -> str:
    """Sanitize text by removing potentially harmful content.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Remove potential script tags and javascript
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'data:', '', text, flags=re.IGNORECASE)

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def validate_model_name(model_name: str) -> None:
    """Validate embedding model name.

    Args:
        model_name: Model name to validate

    Raises:
        ValueError: If model name is invalid
    """
    if not model_name or not isinstance(model_name, str):
        raise ValueError("Model name must be a non-empty string")

    if len(model_name) > 200:
        raise ValueError("Model name too long")

    # Check for potentially malicious characters
    if any(char in model_name for char in ['<', '>', '&', '"', "'", ';', '(', ')']):
        raise ValueError("Model name contains invalid characters")


def validate_cache_size(cache_size: int) -> None:
    """Validate cache size.

    Args:
        cache_size: Cache size to validate

    Raises:
        ValueError: If cache size is invalid
    """
    if not isinstance(cache_size, int):
        raise ValueError("Cache size must be an integer")

    if cache_size < 0:
        raise ValueError("Cache size cannot be negative")

    if cache_size > 100000:
        raise ValueError("Cache size too large (max 100000 entries)")


def is_valid_query_type(query_type: str) -> bool:
    """Check if query type is valid.

    Args:
        query_type: Query type to check

    Returns:
        True if valid, False otherwise
    """
    valid_types = ['definition', 'process', 'explanation', 'entity', None]
    return query_type in valid_types


def validate_scoring_weights(weights: dict) -> None:
    """Validate scoring weights configuration.

    Args:
        weights: Dictionary of scoring weights

    Raises:
        ValueError: If weights are invalid
    """
    required_weights = ['semantic_weight', 'tfidf_weight', 'temporal_weight', 'position_weight', 'diversity_weight']

    for weight_name in required_weights:
        if weight_name not in weights:
            raise ValueError(f"Missing required weight: {weight_name}")

        weight = weights[weight_name]
        if not isinstance(weight, (int, float)):
            raise ValueError(f"{weight_name} must be numeric")

        if not 0 <= weight <= 1:
            raise ValueError(f"{weight_name} must be between 0 and 1, got {weight}")

    # Check that weights sum to something reasonable
    total = sum(weights[w] for w in required_weights)
    if abs(total - 1.0) > 0.5:  # Allow some flexibility
        print(f"⚠️  Warning: Scoring weights sum to {total:.2f}, consider normalizing")