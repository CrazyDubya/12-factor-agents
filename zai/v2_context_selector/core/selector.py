"""
Core context selection logic for the V2 Context Selection System.
"""

import time
import re
import math
import numpy as np
from typing import List, Dict, Optional, Tuple

from .models import TextSegment, SelectionResult, QueryAnalysis
from .embedding_manager import EmbeddingManager
from ..config.settings import Config
from ..utils.tfidf import TFIDFProcessor
from ..utils.validation import validate_query, validate_segments


class ContextSelector:
    """Main context selection interface.

    Provides a clean, high-level API for selecting relevant text segments
    from large document collections using hybrid semantic-keyword scoring.

    Attributes:
        config: Configuration object
        embedding_manager: Embedding generation and caching
        tfidf_processor: TF-IDF computation
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the context selector.

        Args:
            config: Configuration object, uses default if None
        """
        self.config = config or Config()
        self.embedding_manager = EmbeddingManager(
            model_name=self.config.embedding_model,
            cache_size=self.config.cache_size,
            enable_warmup=self.config.enable_warmup
        )
        self.tfidf_processor = TFIDFProcessor()

        # Performance tracking
        self.queries_processed = 0
        self.total_execution_time = 0.0

        print(f"✅ ContextSelector initialized (dim={self.embedding_manager.get_dimension()})")

    def select(self, query: str, segments: List[TextSegment],
               budget: Optional[int] = None) -> SelectionResult:
        """Select relevant segments for a query.

        Args:
            query: Query string
            segments: List of text segments to search
            budget: Token budget for selection (uses config default if None)

        Returns:
            SelectionResult with selected segments and metadata
        """
        start_time = time.time()

        # Validate inputs
        validate_query(query)
        validate_segments(segments)

        # Use default budget if not provided
        if budget is None:
            budget = self.config.default_budget

        # Analyze query for feature selection
        query_analysis = self._analyze_query(query)

        # Select appropriate method based on configuration and query analysis
        if self.config.enable_phase2_features:
            result = self._select_with_phase2_features(query, segments, budget, query_analysis)
        else:
            result = self._select_phase1_optimized(query, segments, budget, query_analysis)

        # Update performance tracking
        execution_time = (time.time() - start_time) * 1000
        result.execution_time_ms = execution_time
        result.query = query
        result.total_segments_available = len(segments)

        self.queries_processed += 1
        self.total_execution_time += execution_time

        return result

    def _analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query to determine optimal processing strategy.

        Args:
            query: Query string to analyze

        Returns:
            QueryAnalysis with feature recommendations
        """
        # Clean query (remove punctuation, lowercase)
        clean_query = ' '.join(re.findall(r'\b\w+\b', query.lower()))

        # Check for time-sensitive keywords
        time_sensitive_keywords = ['current', 'recent', 'latest', 'new', 'today', 'now']
        is_time_sensitive = any(keyword in clean_query for keyword in time_sensitive_keywords)

        # Check if query would benefit from expansion
        expansion_keywords = ['what', 'how', 'why', 'explain', 'describe']
        requires_expansion = any(keyword in clean_query for keyword in expansion_keywords)

        # Calculate complexity score (0-1)
        complexity_score = min(1.0, len(clean_query.split()) / 10.0)

        # Extract keywords (simple approach)
        keywords = [word for word in clean_query.split() if len(word) > 3]

        # Determine query type
        query_type = None
        if clean_query.startswith('what'):
            query_type = 'definition'
        elif clean_query.startswith('how'):
            query_type = 'process'
        elif clean_query.startswith('why'):
            query_type = 'explanation'
        elif clean_query.startswith('who') or clean_query.startswith('where'):
            query_type = 'entity'

        return QueryAnalysis(
            original_query=query,
            clean_query=clean_query,
            is_time_sensitive=is_time_sensitive,
            requires_expansion=requires_expansion,
            complexity_score=complexity_score,
            keywords=keywords,
            query_type=query_type
        )

    def _select_phase1_optimized(self, query: str, segments: List[TextSegment],
                                 budget: int, query_analysis: QueryAnalysis) -> SelectionResult:
        """Select segments using Phase 1 optimized method.

        Args:
            query: Query string
            segments: List of segments to search
            budget: Token budget
            query_analysis: Query analysis results

        Returns:
            SelectionResult with selected segments
        """
        # Precompute TF-IDF
        self.tfidf_processor.precompute(segments)

        # Expand query if enabled
        if self.config.enable_enhanced_query_expansion and query_analysis.requires_expansion:
            expanded_query = self._expand_query(query_analysis.clean_query)
        else:
            expanded_query = query_analysis.clean_query

        # Get embeddings
        query_embedding = self.embedding_manager.encode(expanded_query)
        segment_texts = [seg.text for seg in segments]
        segment_embeddings = self.embedding_manager.encode_batch(segment_texts)

        # Compute semantic similarities
        semantic_similarities = self._compute_cosine_similarity(query_embedding, segment_embeddings)

        # Compute TF-IDF scores
        tfidf_scores = np.array([
            self.tfidf_processor.compute_score(expanded_query, i) for i in range(len(segments))
        ])

        # Normalize TF-IDF scores
        tfidf_scores = tfidf_scores / (np.max(tfidf_scores) + 1e-8)

        # Combine scores (Phase 1 formula)
        combined_scores = (
            self.config.semantic_weight * semantic_similarities +
            self.config.tfidf_weight * tfidf_scores
        )

        # Apply length penalty
        length_penalties = self._compute_length_penalties(segments)
        final_scores = combined_scores - length_penalties

        # Select segments within budget
        selected_indices = self._select_segments_by_score(final_scores, segments, budget)

        # Create result
        selected_segments = [segments[i] for i in selected_indices]

        return SelectionResult(
            selected_segments=selected_segments,
            method="phase1_optimized",
            execution_time_ms=0.0,  # Will be set by caller
            query="",  # Will be set by caller
            total_segments_available=len(segments),
            budget_used=sum(len(segments[i].text.split()) for i in selected_indices),
            confidence_score=self._compute_confidence_score(final_scores[selected_indices]),
            debug_info={
                'query_analysis': query_analysis,
                'expanded_query': expanded_query,
                'score_distribution': {
                    'mean': float(np.mean(final_scores)),
                    'std': float(np.std(final_scores)),
                    'min': float(np.min(final_scores)),
                    'max': float(np.max(final_scores))
                }
            }
        )

    def _select_with_phase2_features(self, query: str, segments: List[TextSegment],
                                     budget: int, query_analysis: QueryAnalysis) -> SelectionResult:
        """Select segments using Phase 2 enhanced features.

        Args:
            query: Query string
            segments: List of segments to search
            budget: Token budget
            query_analysis: Query analysis results

        Returns:
            SelectionResult with selected segments
        """
        # Start with Phase 1 baseline
        result = self._select_phase1_optimized(query, segments, budget, query_analysis)
        result.method = "phase2_selective_enhanced"

        # Apply selective Phase 2 features based on query analysis
        additional_features_applied = []

        # Temporal ranking if time-sensitive query
        if (self.config.enable_temporal_ranking and query_analysis.is_time_sensitive):
            temporal_scores = self._compute_temporal_scores(segments, query_analysis)
            # Enhance scores with temporal information
            for i, idx in enumerate([seg.id for seg in result.selected_segments]):
                if idx < len(temporal_scores):
                    result.debug_info[f'temporal_score_{idx}'] = float(temporal_scores[idx])
            additional_features_applied.append('temporal_ranking')

        # Semantic diversity if enabled
        if self.config.enable_semantic_diversity and len(result.selected_segments) > 1:
            diversity_scores = self._compute_diversity_scores(result.selected_segments)
            result.debug_info['diversity_scores'] = [float(score) for score in diversity_scores]
            additional_features_applied.append('semantic_diversity')

        result.debug_info['additional_features'] = additional_features_applied

        return result

    def _expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms.

        Args:
            query: Original query

        Returns:
            Expanded query string
        """
        expanded_terms = [query]

        for term, synonyms in self.config.expansion_terms.items():
            if term in query:
                # Add top 2 synonyms to avoid query bloat
                expanded_terms.extend(synonyms[:2])

        return ' '.join(expanded_terms)

    def _compute_cosine_similarity(self, query_embedding: np.ndarray,
                                  segment_embeddings: List[np.ndarray]) -> np.ndarray:
        """Compute cosine similarity between query and segments.

        Args:
            query_embedding: Query embedding vector
            segment_embeddings: List of segment embedding vectors

        Returns:
            Array of cosine similarities
        """
        similarities = []
        for seg_embedding in segment_embeddings:
            # Compute cosine similarity
            dot_product = np.dot(query_embedding, seg_embedding)
            norm_query = np.linalg.norm(query_embedding)
            norm_segment = np.linalg.norm(seg_embedding)

            if norm_query > 0 and norm_segment > 0:
                similarity = dot_product / (norm_query * norm_segment)
            else:
                similarity = 0.0

            similarities.append(similarity)

        return np.array(similarities)

    def _compute_length_penalties(self, segments: List[TextSegment]) -> np.ndarray:
        """Compute length penalties for segments.

        Args:
            segments: List of text segments

        Returns:
            Array of length penalties
        """
        segment_lengths = np.array([len(seg.text) for seg in segments])

        # Only penalize very long segments
        penalties = np.maximum(0, (segment_lengths - self.config.length_penalty_threshold) / 4000)
        penalties = np.minimum(penalties, self.config.max_length_penalty)

        return penalties

    def _compute_temporal_scores(self, segments: List[TextSegment],
                                query_analysis: QueryAnalysis) -> np.ndarray:
        """Compute temporal relevance scores.

        Args:
            segments: List of text segments
            query_analysis: Query analysis results

        Returns:
            Array of temporal relevance scores
        """
        # For now, return uniform scores. Can be enhanced with actual temporal logic.
        return np.ones(len(segments)) * 0.5

    def _compute_diversity_scores(self, selected_segments: List[TextSegment]) -> List[float]:
        """Compute semantic diversity scores for selected segments.

        Args:
            selected_segments: List of selected segments

        Returns:
            List of diversity scores
        """
        # Simple Jaccard-based diversity
        diversity_scores = []
        for i, segment in enumerate(selected_segments):
            current_words = set(segment.text.lower().split())
            other_words = set()

            for j, other_segment in enumerate(selected_segments):
                if i != j:
                    other_words.update(other_segment.text.lower().split())

            # Jaccard similarity
            intersection = len(current_words & other_words)
            union = len(current_words | other_words)
            similarity = intersection / union if union > 0 else 0.0

            # Convert to diversity score (inverse of similarity)
            diversity = 1.0 - similarity
            diversity_scores.append(diversity)

        return diversity_scores

    def _select_segments_by_score(self, scores: np.ndarray, segments: List[TextSegment],
                                  budget: int) -> List[int]:
        """Select segments by score within budget constraints.

        Args:
            scores: Array of segment scores
            segments: List of text segments
            budget: Token budget

        Returns:
            List of selected segment indices
        """
        # Sort segments by score (descending)
        sorted_indices = np.argsort(scores)[::-1]

        selected_indices = []
        total_tokens = 0

        for idx in sorted_indices:
            segment = segments[idx]
            segment_tokens = len(segment.text.split())

            if total_tokens + segment_tokens <= budget:
                selected_indices.append(idx)
                total_tokens += segment_tokens
            else:
                break

        return selected_indices

    def _compute_confidence_score(self, selected_scores: np.ndarray) -> float:
        """Compute confidence score for selection.

        Args:
            selected_scores: Scores of selected segments

        Returns:
            Confidence score between 0 and 1
        """
        if len(selected_scores) == 0:
            return 0.0

        # Use mean score as confidence, normalized to [0, 1]
        mean_score = np.mean(selected_scores)
        return max(0.0, min(1.0, mean_score))

    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics.

        Returns:
            Dictionary with performance statistics
        """
        avg_execution_time = (self.total_execution_time / self.queries_processed
                             if self.queries_processed > 0 else 0.0)

        return {
            'queries_processed': self.queries_processed,
            'total_execution_time_ms': self.total_execution_time,
            'average_execution_time_ms': avg_execution_time,
            'cache_stats': self.embedding_manager.get_cache_stats(),
            'config': self.config.to_dict()
        }

    def reset_stats(self) -> None:
        """Reset performance statistics."""
        self.queries_processed = 0
        self.total_execution_time = 0.0
        print("✅ Performance statistics reset")

    def update_config(self, **kwargs) -> None:
        """Update configuration.

        Args:
            **kwargs: Configuration parameters to update
        """
        self.config = self.config.copy(**kwargs)
        print(f"✅ Configuration updated: {list(kwargs.keys())}")

    def preload_documents(self, segments: List[TextSegment]) -> None:
        """Preload embeddings for documents.

        Args:
            segments: List of segments to preload
        """
        texts = [seg.text for seg in segments]
        self.embedding_manager.preload_embeddings(texts)
        self.tfidf_processor.precompute(segments)
        print(f"✅ Preloaded {len(segments)} segments")