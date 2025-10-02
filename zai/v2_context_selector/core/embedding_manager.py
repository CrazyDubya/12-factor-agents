"""
Embedding management for the V2 Context Selection System.
"""

import time
import hashlib
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    import warnings
    warnings.warn("SentenceTransformers not available. Using mock embeddings.")


class EmbeddingManager:
    """Manages text embeddings with caching and performance optimization.

    Handles embedding generation, caching, and model management for the
    context selection system. Supports both real SentenceTransformer models
    and mock embeddings for development/testing.

    Attributes:
        model_name: Name of the embedding model
        embedding_dimension: Dimension of embeddings
        cache_size: Maximum number of cached embeddings
        enable_warmup: Whether to warm up cache with common queries
    """

    def __init__(self, model_name: str = "paraphrase-MiniLM-L3-v2",
                 cache_size: int = 1000, enable_warmup: bool = True):
        """Initialize the embedding manager.

        Args:
            model_name: Name of the sentence transformer model
            cache_size: Maximum number of embeddings to cache
            enable_warmup: Whether to pre-warm cache with common queries
        """
        self.model_name = model_name
        self.cache_size = cache_size
        self.enable_warmup = enable_warmup

        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.embeddings_generated = 0

        # Initialize cache
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self._model = None
        self._embedding_dimension = None

        # Load model
        self._load_model()

        # Warm up cache if enabled
        if enable_warmup:
            self._warm_up_cache()

    def _load_model(self) -> None:
        """Load the embedding model."""
        start_time = time.time()

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print(f"🔄 Pre-loading {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
                self._embedding_dimension = self._model.get_sentence_embedding_dimension()
                load_time = (time.time() - start_time) * 1000
                print(f"✅ Pre-loaded {self.model_name} (dim={self._embedding_dimension}, load_time={load_time:.1f}ms)")
            except Exception as e:
                print(f"❌ Failed to load {self.model_name}: {e}")
                self._fallback_to_mock()
        else:
            self._fallback_to_mock()

    def _fallback_to_mock(self) -> None:
        """Fallback to mock embeddings when SentenceTransformers unavailable."""
        print("⚠️  Using mock embeddings (384-dim)")
        self._model = None
        self._embedding_dimension = 384

    def _warm_up_cache(self) -> None:
        """Warm up cache with common queries."""
        warm_up_queries = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "Explain neural networks",
            "What is data science?",
            "How does computer vision work?",
            "What is natural language processing?",
            "What are the latest developments?",
            "How do algorithms learn?",
            "What is deep learning?",
            "Explain artificial intelligence concepts"
        ]

        start_time = time.time()
        for query in warm_up_queries:
            self.encode(query)

        warm_up_time = (time.time() - start_time) * 1000
        print(f"✅ Cache warmed up with {len(warm_up_queries)} queries ({warm_up_time:.1f}ms)")

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text string to embedding.

        Args:
            text: Text to encode

        Returns:
            Embedding vector as numpy array
        """
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self.embedding_cache:
            self.cache_hits += 1
            return self.embedding_cache[cache_key]

        # Generate embedding
        if self._model is not None:
            embedding = self._model.encode(text, convert_to_numpy=True)
        else:
            # Mock embedding
            embedding = self._generate_mock_embedding(text)

        # Cache the result
        self.cache_misses += 1
        self.embeddings_generated += 1

        # Manage cache size
        if len(self.embedding_cache) >= self.cache_size:
            self._evict_cache()

        self.embedding_cache[cache_key] = embedding
        return embedding

    def encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Encode multiple text strings efficiently.

        Args:
            texts: List of texts to encode

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Check cache for each text
        cached_embeddings = {}
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self.embedding_cache:
                cached_embeddings[i] = self.embedding_cache[cache_key]
                self.cache_hits += 1
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                self.cache_misses += 1

        # Generate embeddings for uncached texts
        if uncached_texts:
            if self._model is not None:
                # Use batch encoding for better performance
                new_embeddings = self._model.encode(uncached_texts, convert_to_numpy=True)
            else:
                # Generate mock embeddings
                new_embeddings = [self._generate_mock_embedding(text) for text in uncached_texts]

            # Cache new embeddings
            for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                cache_key = self._get_cache_key(text)

                # Manage cache size
                if len(self.embedding_cache) >= self.cache_size:
                    self._evict_cache()

                self.embedding_cache[cache_key] = embedding
                self.embeddings_generated += 1
                cached_embeddings[uncached_indices[i]] = embedding

        # Return embeddings in original order
        return [cached_embeddings[i] for i in range(len(texts))]

    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate a mock embedding based on text hash.

        Args:
            text: Text to generate mock embedding for

        Returns:
            Mock embedding vector
        """
        # Generate consistent pseudo-random embedding based on text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)

        embedding = np.random.normal(0, 0.1, self._embedding_dimension)
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)

        return embedding

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text.

        Args:
            text: Text to generate key for

        Returns:
            Cache key string
        """
        return hashlib.md5(text.encode()).hexdigest()

    def _evict_cache(self) -> None:
        """Evict oldest entries from cache to maintain size limit."""
        if len(self.embedding_cache) > self.cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self.embedding_cache.keys())[:len(self.embedding_cache) // 4]
            for key in keys_to_remove:
                del self.embedding_cache[key]

    def get_dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Embedding dimension
        """
        return self._embedding_dimension

    def get_cache_stats(self) -> Dict[str, any]:
        """Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.embedding_cache),
            'max_cache_size': self.cache_size,
            'embeddings_generated': self.embeddings_generated,
            'model_name': self.model_name,
            'embedding_dimension': self._embedding_dimension
        }

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        print("✅ Embedding cache cleared")

    def preload_embeddings(self, texts: List[str]) -> None:
        """Preload embeddings for a list of texts.

        Args:
            texts: List of texts to preload
        """
        print(f"🔄 Preloading {len(texts)} embeddings...")
        start_time = time.time()

        self.encode_batch(texts)

        preload_time = (time.time() - start_time) * 1000
        print(f"✅ Preloaded {len(texts)} embeddings ({preload_time:.1f}ms)")

    def is_real_model(self) -> bool:
        """Check if using real SentenceTransformer model.

        Returns:
            True if using real model, False if using mock embeddings
        """
        return self._model is not None

    def get_model_info(self) -> Dict[str, any]:
        """Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'is_real_model': self.is_real_model(),
            'embedding_dimension': self._embedding_dimension,
            'cache_size': self.cache_size,
            'enable_warmup': self.enable_warmup,
            'available_models': ['paraphrase-MiniLM-L3-v2', 'all-MiniLM-L6-v2'] if SENTENCE_TRANSFORMERS_AVAILABLE else []
        }