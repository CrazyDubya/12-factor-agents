"""
Tests for the ContextSelector main functionality.
"""

import pytest
import time
from v2_context_selector.tests import TextSegment, ContextSelector, Config


class TestContextSelector:
    """Test cases for ContextSelector class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.selector = ContextSelector()
        self.segments = [
            TextSegment("seg1", "Whales are large marine mammals that live in the ocean.", "doc1", 0),
            TextSegment("seg2", "The captain stood on the ship deck, looking at the sea.", "doc1", 1),
            TextSegment("seg3", "Machine learning algorithms learn patterns from data.", "doc2", 0),
            TextSegment("seg4", "Neural networks are inspired by biological neural networks.", "doc2", 1),
            TextSegment("seg5", "Computer vision allows machines to interpret visual information.", "doc3", 0)
        ]

    def test_basic_selection(self):
        """Test basic selection functionality."""
        query = "What are whales?"
        result = self.selector.select(query, self.segments, budget=500)

        assert len(result.selected_segments) > 0
        assert result.method in ["phase1_optimized", "phase2_selective_enhanced"]
        assert result.execution_time_ms < 200
        assert result.query == query
        assert result.total_segments_available == len(self.segments)

    def test_selection_with_budget(self):
        """Test selection with different budget values."""
        query = "machine learning"

        # Small budget
        result_small = self.selector.select(query, self.segments, budget=100)
        assert result_small.budget_used <= 100

        # Large budget
        result_large = self.selector.select(query, self.segments, budget=2000)
        assert result_large.budget_used <= 2000
        assert len(result_large.selected_segments) >= len(result_small.selected_segments)

    def test_empty_query_validation(self):
        """Test that empty queries are rejected."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            self.selector.select("", self.segments, budget=500)

        with pytest.raises(ValueError, match="Query cannot be empty"):
            self.selector.select("   ", self.segments, budget=500)

    def test_empty_segments_validation(self):
        """Test that empty segment lists are rejected."""
        with pytest.raises(ValueError, match="Segments list cannot be empty"):
            self.selector.select("test query", [], budget=500)

    def test_performance_stats(self):
        """Test performance statistics tracking."""
        # Process some queries
        queries = ["whales", "captain", "machine learning"]
        for query in queries:
            self.selector.select(query, self.segments, budget=500)

        stats = self.selector.get_performance_stats()
        assert stats['queries_processed'] == len(queries)
        assert stats['average_execution_time_ms'] > 0
        assert 'cache_stats' in stats
        assert 'config' in stats

    def test_config_update(self):
        """Test configuration updates."""
        original_cache_size = self.selector.config.cache_size

        self.selector.update_config(cache_size=2000)

        assert self.selector.config.cache_size == 2000
        assert self.selector.config.cache_size != original_cache_size

    def test_preload_documents(self):
        """Test document preloading."""
        # Preload should not raise exceptions
        self.selector.preload_documents(self.segments)

        # Query should be faster after preload
        start_time = time.time()
        result1 = self.selector.select("whales", self.segments, budget=500)
        first_query_time = time.time() - start_time

        start_time = time.time()
        result2 = self.selector.select("captain", self.segments, budget=500)
        second_query_time = time.time() - start_time

        # Second query should be faster due to caching
        assert second_query_time <= first_query_time * 1.5  # Allow some variance

    def test_custom_config(self):
        """Test selector with custom configuration."""
        config = Config(
            embedding_model="paraphrase-MiniLM-L3-v2",
            cache_size=500,
            enable_temporal_ranking=False
        )

        selector = ContextSelector(config)
        result = selector.select("whales", self.segments, budget=500)

        assert len(result.selected_segments) > 0
        assert selector.config.cache_size == 500
        assert selector.config.enable_temporal_ranking == False

    def test_selection_result_attributes(self):
        """Test SelectionResult has all required attributes."""
        query = "neural networks"
        result = self.selector.select(query, self.segments, budget=500)

        # Required attributes
        assert hasattr(result, 'selected_segments')
        assert hasattr(result, 'method')
        assert hasattr(result, 'execution_time_ms')
        assert hasattr(result, 'query')
        assert hasattr(result, 'total_segments_available')
        assert hasattr(result, 'budget_used')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'debug_info')

        # Type checks
        assert isinstance(result.selected_segments, list)
        assert isinstance(result.method, str)
        assert isinstance(result.execution_time_ms, (int, float))
        assert isinstance(result.query, str)
        assert isinstance(result.total_segments_available, int)
        assert isinstance(result.budget_used, int)
        assert isinstance(result.confidence_score, (int, float))
        assert isinstance(result.debug_info, dict)

    def test_no_results_scenario(self):
        """Test behavior when no relevant segments are found."""
        # Query that doesn't match any segments
        query = "quantum physics entanglement"
        result = self.selector.select(query, self.segments, budget=500)

        # Should return empty result but no error
        assert isinstance(result.selected_segments, list)
        assert result.method in ["phase1_optimized", "phase2_selective_enhanced"]
        assert result.execution_time_ms < 200

    def test_duplicate_segment_ids(self):
        """Test handling of duplicate segment IDs."""
        segments_with_duplicates = [
            TextSegment("dup_id", "First segment", "doc1", 0),
            TextSegment("dup_id", "Second segment", "doc2", 1),  # Duplicate ID
        ]

        with pytest.raises(ValueError, match="Duplicate segment ID"):
            self.selector.select("test", segments_with_duplicates, budget=500)


class TestContextSelectorPerformance:
    """Performance-related tests for ContextSelector."""

    def setup_method(self):
        """Set up performance test fixtures."""
        self.selector = ContextSelector()
        # Create larger test dataset
        self.large_segments = []
        for i in range(100):
            self.large_segments.append(
                TextSegment(
                    f"seg_{i}",
                    f"This is test segment number {i} with some content about various topics "
                    f"including technology, science, and literature. Segment {i} contains "
                    f"enough text to be meaningful for testing purposes.",
                    f"doc_{i // 10}",
                    i
                )
            )

    def test_performance_with_large_dataset(self):
        """Test performance with larger document sets."""
        query = "technology and science"

        start_time = time.time()
        result = self.selector.select(query, self.large_segments, budget=1000)
        execution_time = (time.time() - start_time) * 1000

        # Should complete within reasonable time
        assert execution_time < 200  # 200ms max for 100 segments
        assert len(result.selected_segments) > 0
        assert result.execution_time_ms < 200

    def test_cache_performance(self):
        """Test caching performance improvements."""
        query = "science and research"

        # First query (cache miss)
        start_time = time.time()
        result1 = self.selector.select(query, self.large_segments, budget=1000)
        first_time = (time.time() - start_time) * 1000

        # Second query (should benefit from cache)
        start_time = time.time()
        result2 = self.selector.select(query, self.large_segments, budget=1000)
        second_time = (time.time() - start_time) * 1000

        # Second query should be faster or at least not significantly slower
        assert second_time <= first_time * 1.2  # Allow 20% variance

        # Cache stats should show hits
        stats = self.selector.get_performance_stats()
        assert stats['cache_stats']['hit_rate'] > 0

    def test_concurrent_queries(self):
        """Test handling of multiple queries in sequence."""
        queries = [
            "technology and innovation",
            "science research methods",
            "literature analysis",
            "data processing",
            "algorithm design"
        ]

        times = []
        for query in queries:
            start_time = time.time()
            result = self.selector.select(query, self.large_segments, budget=500)
            execution_time = (time.time() - start_time) * 1000
            times.append(execution_time)

            # Each query should complete in reasonable time
            assert execution_time < 200
            assert len(result.selected_segments) > 0

        # Average time should be reasonable
        avg_time = sum(times) / len(times)
        assert avg_time < 100


class TestContextSelectorConfigurations:
    """Test different selector configurations."""

    def test_fast_configuration(self):
        """Test fast configuration preset."""
        from v2_context_selector.tests import fast_config

        selector = ContextSelector(fast_config())
        segments = [
            TextSegment("seg1", "Whales are marine mammals.", "doc1", 0),
            TextSegment("seg2", "AI systems learn from data.", "doc2", 0)
        ]

        result = selector.select("whales", segments, budget=500)

        assert len(result.selected_segments) > 0
        assert result.execution_time_ms < 100  # Fast mode should be quicker

    def test_balanced_configuration(self):
        """Test balanced configuration preset."""
        from v2_context_selector.tests import balanced_config

        selector = ContextSelector(balanced_config())
        segments = [
            TextSegment("seg1", "Machine learning algorithms.", "doc1", 0),
            TextSegment("seg2", "Deep neural networks.", "doc2", 0)
        ]

        result = selector.select("machine learning", segments, budget=500)

        assert len(result.selected_segments) > 0
        assert result.execution_time_ms < 150  # Balanced mode

    def test_accurate_configuration(self):
        """Test accurate configuration preset."""
        from v2_context_selector.tests import accurate_config

        selector = ContextSelector(accurate_config())
        segments = [
            TextSegment("seg1", "Computer vision processes images.", "doc1", 0),
            TextSegment("seg2", "Visual recognition algorithms.", "doc2", 0)
        ]

        result = selector.select("computer vision", segments, budget=500)

        assert len(result.selected_segments) > 0
        # Accurate mode might be slower but should still be reasonable
        assert result.execution_time_ms < 200


if __name__ == "__main__":
    pytest.main([__file__])