"""
Configuration settings for the V2 Context Selection System.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import os


@dataclass
class Config:
    """Configuration for the V2 Context Selection System.

    Attributes:
        embedding_model: Name of the sentence transformer model to use
        embedding_dimension: Expected embedding dimension
        cache_size: Maximum number of embeddings to cache
        enable_warmup: Whether to warm up cache with common queries

        # Feature flags
        enable_phase2_features: Master switch for advanced features
        enable_temporal_ranking: Enable time-sensitive query processing
        enable_topic_clustering: Enable topic diversity enforcement
        enable_enhanced_query_expansion: Enable enhanced query expansion
        enable_semantic_diversity: Enable semantic diversity scoring

        # Scoring weights
        semantic_weight: Weight for semantic similarity (0-1)
        tfidf_weight: Weight for TF-IDF score (0-1)
        temporal_weight: Weight for temporal relevance (0-1)
        position_weight: Weight for position bias (0-1)
        diversity_weight: Weight for diversity scoring (0-1)

        # Performance settings
        max_segments_per_query: Maximum segments to consider
        default_budget: Default token budget for queries
        length_penalty_threshold: Character count threshold for length penalty
        max_length_penalty: Maximum length penalty (0-1)

        # Expansion terms for different domains
        expansion_terms: Dictionary of term -> synonyms mapping

        # Performance optimization
        batch_size: Batch size for embedding generation
        max_concurrent_requests: Maximum concurrent requests
        timeout_seconds: Timeout for operations
    """
    # Embedding settings
    embedding_model: str = "paraphrase-MiniLM-L3-v2"
    embedding_dimension: int = 384
    cache_size: int = 1000
    enable_warmup: bool = True

    # Feature flags
    enable_phase2_features: bool = True
    enable_temporal_ranking: bool = True
    enable_topic_clustering: bool = False
    enable_enhanced_query_expansion: bool = True
    enable_semantic_diversity: bool = False

    # Scoring weights (must sum to approximately 1)
    semantic_weight: float = 0.7
    tfidf_weight: float = 0.3
    temporal_weight: float = 0.15
    position_weight: float = 0.1
    diversity_weight: float = 0.2

    # Performance settings
    max_segments_per_query: int = 100
    default_budget: int = 1000
    length_penalty_threshold: int = 2000
    max_length_penalty: float = 0.15

    # Expansion terms (comprehensive mapping)
    expansion_terms: Dict[str, List[str]] = field(default_factory=lambda: {
        # AI/ML terms
        'artificial intelligence': ['ai', 'machine intelligence', 'artificial general intelligence'],
        'machine learning': ['ml', 'algorithms', 'algorithmic learning'],
        'neural networks': ['deep learning', 'neurons', 'neural nets'],
        'data science': ['analytics', 'statistics', 'data analysis'],
        'computer vision': ['image processing', 'visual recognition'],
        'natural language': ['nlp', 'text processing', 'language processing'],

        # Literature terms
        'whale': ['whales', 'cetacean', 'marine mammal', 'sea creature'],
        'captain': ['skipper', 'commander', 'ship master', 'leader'],
        'ship': ['vessel', 'boat', 'craft', 'sailing ship'],
        'sea': ['ocean', 'water', 'marine', 'aquatic'],
        'ocean': ['sea', 'water', 'marine', 'deep'],
        'character': ['person', 'individual', 'figure', 'protagonist'],
        'story': ['narrative', 'tale', 'plot', 'account'],

        # General terms
        'describe': ['description', 'characteristics', 'features', 'details'],
        'information': ['data', 'facts', 'details', 'knowledge'],
        'what': ['define', 'explain', 'describe'],
        'how': ['method', 'process', 'technique', 'procedure'],
        'why': ['reason', 'cause', 'explanation', 'purpose'],
        'main': ['primary', 'principal', 'chief', 'important'],
        'about': ['regarding', 'concerning', 'related to'],
        'details': ['specifics', 'particulars', 'information'],
        'features': ['characteristics', 'attributes', 'qualities'],
        'aspects': ['facets', 'elements', 'components', 'parts'],
        'explain': ['describe', 'detail', 'elaborate', 'clarify'],
        'find': ['locate', 'discover', 'identify', 'search'],
        'show': ['display', 'demonstrate', 'reveal', 'present'],
        'tell': ['inform', 'explain', 'describe', 'relate'],

        # Action verbs
        'analyze': ['examine', 'study', 'investigate', 'review'],
        'compare': ['contrast', 'differentiate', 'distinguish'],
        'create': ['make', 'build', 'develop', 'produce'],
        'improve': ['enhance', 'optimize', 'refine', 'upgrade'],
        'solve': ['resolve', 'address', 'handle', 'fix']
    })

    # Performance optimization
    batch_size: int = 32
    max_concurrent_requests: int = 10
    timeout_seconds: int = 30

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_weights()
        self._validate_performance_settings()

    def _validate_weights(self):
        """Validate that scoring weights are reasonable."""
        total_weight = (self.semantic_weight + self.tfidf_weight +
                       self.temporal_weight + self.position_weight)

        # Allow some flexibility but warn if weights are too far from 1
        if abs(total_weight - 1.0) > 0.3:
            print(f"⚠️  Warning: Scoring weights sum to {total_weight:.2f}, consider normalizing")

        # Check individual weights
        for name, weight in [
            ("semantic", self.semantic_weight),
            ("tfidf", self.tfidf_weight),
            ("temporal", self.temporal_weight),
            ("position", self.position_weight),
            ("diversity", self.diversity_weight)
        ]:
            if not 0 <= weight <= 1:
                raise ValueError(f"{name}_weight must be between 0 and 1, got {weight}")

    def _validate_performance_settings(self):
        """Validate performance-related settings."""
        if self.cache_size <= 0:
            raise ValueError("cache_size must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_segments_per_query <= 0:
            raise ValueError("max_segments_per_query must be positive")
        if self.default_budget <= 0:
            raise ValueError("default_budget must be positive")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables."""
        config = cls()

        # Override with environment variables if present
        if os.getenv('V2_EMBEDDING_MODEL'):
            config.embedding_model = os.getenv('V2_EMBEDDING_MODEL')
        if os.getenv('V2_CACHE_SIZE'):
            config.cache_size = int(os.getenv('V2_CACHE_SIZE'))
        if os.getenv('V2_ENABLE_PHASE2'):
            config.enable_phase2_features = os.getenv('V2_ENABLE_PHASE2').lower() == 'true'
        if os.getenv('V2_ENABLE_TEMPORAL'):
            config.enable_temporal_ranking = os.getenv('V2_ENABLE_TEMPORAL').lower() == 'true'

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'embedding_model': self.embedding_model,
            'embedding_dimension': self.embedding_dimension,
            'cache_size': self.cache_size,
            'enable_warmup': self.enable_warmup,
            'enable_phase2_features': self.enable_phase2_features,
            'enable_temporal_ranking': self.enable_temporal_ranking,
            'enable_topic_clustering': self.enable_topic_clustering,
            'enable_enhanced_query_expansion': self.enable_enhanced_query_expansion,
            'enable_semantic_diversity': self.enable_semantic_diversity,
            'semantic_weight': self.semantic_weight,
            'tfidf_weight': self.tfidf_weight,
            'temporal_weight': self.temporal_weight,
            'position_weight': self.position_weight,
            'diversity_weight': self.diversity_weight,
            'max_segments_per_query': self.max_segments_per_query,
            'default_budget': self.default_budget,
            'length_penalty_threshold': self.length_penalty_threshold,
            'max_length_penalty': self.max_length_penalty,
            'batch_size': self.batch_size,
            'max_concurrent_requests': self.max_concurrent_requests,
            'timeout_seconds': self.timeout_seconds
        }

    def copy(self, **kwargs) -> 'Config':
        """Create a copy of the config with optional overrides."""
        config_dict = self.to_dict()
        config_dict.update(kwargs)
        return self.from_dict(config_dict)


# Default configuration instance
default_config = Config()


# Preset configurations for different use cases
def fast_config() -> Config:
    """Configuration optimized for speed."""
    return default_config.copy(
        enable_topic_clustering=False,
        enable_semantic_diversity=False,
        enable_temporal_ranking=False,
        max_segments_per_query=50,
        cache_size=500
    )


def accurate_config() -> Config:
    """Configuration optimized for accuracy."""
    return default_config.copy(
        enable_phase2_features=True,
        enable_temporal_ranking=True,
        enable_topic_clustering=True,
        enable_semantic_diversity=True,
        max_segments_per_query=200,
        cache_size=2000
    )


def balanced_config() -> Config:
    """Balanced configuration for general use."""
    return default_config.copy(
        enable_temporal_ranking=True,
        enable_topic_clustering=False,
        enable_semantic_diversity=False,
        max_segments_per_query=100,
        cache_size=1000
    )