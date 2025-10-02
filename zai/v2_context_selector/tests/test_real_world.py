"""
Real-world validation tests using actual document content.
"""

import pytest
import os
from v2_context_selector.tests import TextSegment, ContextSelector


class TestRealWorldValidation:
    """Tests using real document content."""

    def setup_method(self):
        """Set up real-world test fixtures."""
        self.selector = ContextSelector()

        # Real content segments (literature, technical, etc.)
        self.real_segments = [
            TextSegment(
                "whale_1",
                "Whales are large marine mammals that belong to the order Cetacea. They are fully aquatic, open ocean creatures, and their diet consists of a wide range of marine life.",
                "marine_biology",
                0
            ),
            TextSegment(
                "whale_2",
                "The blue whale is the largest animal ever known to have lived on Earth. These magnificent creatures can reach lengths of up to 100 feet and weigh as much as 200 tons.",
                "marine_biology",
                1
            ),
            TextSegment(
                "captain_1",
                "The captain stood on the ship's bridge, examining the nautical charts. With years of experience at sea, he knew how to navigate through stormy weather and find safe harbor.",
                "maritime",
                0
            ),
            TextSegment(
                "captain_2",
                "Captain Ahab was obsessed with hunting the great white whale. His determination and willingness to risk everything made him a legendary but tragic figure in maritime literature.",
                "literature",
                1
            ),
            TextSegment(
                "ship_1",
                "The vessel was equipped with modern navigation systems including GPS, radar, and sonar. The ship's hull was designed to withstand rough seas and maintain stability in adverse conditions.",
                "maritime",
                0
            ),
            TextSegment(
                "ai_1",
                "Artificial intelligence systems use machine learning algorithms to process large amounts of data and identify patterns that humans might miss. These systems can learn from experience and improve over time.",
                "technology",
                0
            ),
            TextSegment(
                "ai_2",
                "Deep learning neural networks have revolutionized computer vision, natural language processing, and many other fields of artificial intelligence. These systems can achieve human-level performance in specific tasks.",
                "technology",
                1
            )
        ]

    def test_literature_queries(self):
        """Test queries about literature content."""
        queries = [
            ("What is a whale?", ["whale_1", "whale_2"]),
            ("Tell me about Captain Ahab", ["captain_2"]),
            ("Information about ships and vessels", ["ship_1"]),
            ("Marine life and ocean creatures", ["whale_1", "whale_2"])
        ]

        for query, expected_ids in queries:
            result = self.selector.select(query, self.real_segments, budget=500)

            selected_ids = [seg.id for seg in result.selected_segments]

            # Should find relevant content
            assert len(result.selected_segments) > 0, f"No results for query: {query}"
            assert result.execution_time_ms < 100, f"Too slow for query: {query} ({result.execution_time_ms}ms)"

            # Check if expected segments were found
            found_expected = any(exp_id in selected_ids for exp_id in expected_ids)
            assert found_expected, f"Expected content not found for query: {query}. Found: {selected_ids}"

    def test_technical_queries(self):
        """Test queries about technical content."""
        queries = [
            ("What is artificial intelligence?", ["ai_1", "ai_2"]),
            ("How do machine learning algorithms work?", ["ai_1"]),
            ("Deep learning and neural networks", ["ai_2"]),
            ("Computer vision and AI systems", ["ai_1", "ai_2"])
        ]

        for query, expected_ids in queries:
            result = self.selector.select(query, self.real_segments, budget=500)

            selected_ids = [seg.id for seg in result.selected_segments]

            # Should find relevant content
            assert len(result.selected_segments) > 0, f"No results for query: {query}"
            assert result.execution_time_ms < 100, f"Too slow for query: {query} ({result.execution_time_ms}ms)"

            # Check if expected segments were found
            found_expected = any(exp_id in selected_ids for exp_id in expected_ids)
            assert found_expected, f"Expected content not found for query: {query}. Found: {selected_ids}"

    def test_mixed_domain_queries(self):
        """Test queries that span multiple domains."""
        queries = [
            "Compare whales and AI systems",
            "Technology in maritime navigation",
            "Literature about marine biology"
        ]

        for query in queries:
            result = self.selector.select(query, self.real_segments, budget=800)

            # Should find some relevant content even for complex queries
            assert len(result.selected_segments) > 0, f"No results for complex query: {query}"
            assert result.execution_time_ms < 150, f"Too slow for complex query: {query} ({result.execution_time_ms}ms)"

    def test_no_results_scenario(self):
        """Test queries that should not match any content."""
        queries = [
            "Quantum physics entanglement",
            "Ancient Roman architecture",
            "Medieval European history",
            "Space exploration rocket technology"
        ]

        for query in queries:
            result = self.selector.select(query, self.real_segments, budget=500)

            # May return empty or minimal results for unrelated queries
            # Should not crash and should complete quickly
            assert result.execution_time_ms < 100, f"Too slow for unrelated query: {query}"

    def test_confidence_scores(self):
        """Test confidence score calculation."""
        # High confidence query (clear match)
        result1 = self.selector.select("blue whale largest animal", self.real_segments, budget=500)
        assert result1.confidence_score > 0.1, "Low confidence for clear match"
        assert len(result1.selected_segments) > 0, "No results for clear match"

        # Low confidence query (vague or no match)
        result2 = self.selector.select("something unrelated", self.real_segments, budget=500)
        # Confidence may be low but should be valid
        assert 0 <= result2.confidence_score <= 1, "Invalid confidence score"

    def test_budget_impact(self):
        """Test how budget affects selection results."""
        query = "artificial intelligence and machine learning"

        # Small budget
        result_small = self.selector.select(query, self.real_segments, budget=100)

        # Large budget
        result_large = self.selector.select(query, self.real_segments, budget=1000)

        # Larger budget should select equal or more segments
        assert len(result_large.selected_segments) >= len(result_small.selected_segments)
        assert result_large.budget_used >= result_small.budget_used

        # Both should find relevant AI content
        ai_segments_small = [s for s in result_small.selected_segments if s.document_id == "technology"]
        ai_segments_large = [s for s in result_large.selected_segments if s.document_id == "technology"]

        assert len(ai_segments_small) > 0, "Small budget should find AI content"
        assert len(ai_segments_large) > 0, "Large budget should find AI content"

    def test_performance_with_real_content(self):
        """Test performance characteristics with real content."""
        query = "marine biology and whale behavior"

        # Multiple runs to check consistency
        times = []
        for _ in range(5):
            result = self.selector.select(query, self.real_segments, budget=500)
            times.append(result.execution_time_ms)
            assert len(result.selected_segments) > 0

        # Performance should be consistent
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        assert avg_time < 100, f"Average time too high: {avg_time:.1f}ms"
        assert max_time < 200, f"Max time too high: {max_time:.1f}ms"
        assert (max_time - min_time) < avg_time, f"Performance too variable: {min_time:.1f}-{max_time:.1f}ms"

    def test_segment_quality_validation(self):
        """Test segment quality with real content."""
        for segment in self.real_segments:
            # All segments should have reasonable properties
            assert len(segment.text) > 50, f"Segment too short: {segment.id}"
            assert len(segment.text) < 1000, f"Segment too long: {segment.id}"
            assert segment.word_count > 10, f"Too few words: {segment.id}"
            assert segment.position >= 0, f"Invalid position: {segment.id}"
            assert segment.document_id, f"Missing document ID: {segment.id}"

    def test_debug_information(self):
        """Test debug information in results."""
        query = "neural networks and deep learning"
        result = self.selector.select(query, self.real_segments, budget=500)

        # Debug info should be available
        assert 'debug_info' in result.__dict__, "Missing debug info"
        assert isinstance(result.debug_info, dict), "Debug info should be a dictionary"

        # Should contain query analysis
        if 'query_analysis' in result.debug_info:
            query_analysis = result.debug_info['query_analysis']
            assert hasattr(query_analysis, 'original_query'), "Missing original query in analysis"
            assert hasattr(query_analysis, 'clean_query'), "Missing clean query in analysis"

        # Should contain score distribution
        if 'score_distribution' in result.debug_info:
            scores = result.debug_info['score_distribution']
            assert 'mean' in scores, "Missing mean score"
            assert 'std' in scores, "Missing std score"
            assert 'min' in scores, "Missing min score"
            assert 'max' in scores, "Missing max score"


class TestMobyDickValidation:
    """Specific tests using Moby Dick content (if available)."""

    def setup_method(self):
        """Set up Moby Dick test fixtures."""
        self.selector = ContextSelector()

        # Moby Dick segments (simulated based on real content)
        self.moby_segments = [
            TextSegment(
                "moby_1",
                "Call me Ishmael. Some years ago never mind how long precisely having little or no money in my purse, and nothing particular to interest me on shore.",
                "moby_dick",
                0
            ),
            TextSegment(
                "moby_2",
                "Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses.",
                "moby_dick",
                1
            ),
            TextSegment(
                "moby_3",
                "There now is your insular city of the Manhattoes, belted round by wharves as Indian isles by coral reefs surrounded by calm waters.",
                "moby_dick",
                2
            ),
            TextSegment(
                "whale_1",
                "A whale is a mammal, not a fish. It breathes air through lungs, and gives birth to live young which it nurses with milk.",
                "biology",
                0
            ),
            TextSegment(
                "whale_2",
                "The great sperm whale can dive to depths of over 3,000 feet and hold its breath for up to 90 minutes while hunting squid.",
                "biology",
                1
            )
        ]

    def test_moby_dick_queries(self):
        """Test queries about Moby Dick content."""
        queries = [
            ("Call me Ishmael", ["moby_1"]),
            ("Tell me about November", ["moby_2"]),
            ("Information about New York City", ["moby_3"]),
            ("What are whales?", ["whale_1", "whale_2"]),
            ("Sperm whale diving behavior", ["whale_2"])
        ]

        for query, expected_ids in queries:
            result = self.selector.select(query, self.moby_segments, budget=500)

            selected_ids = [seg.id for seg in result.selected_segments]

            # Should find relevant content
            assert len(result.selected_segments) > 0, f"No results for Moby Dick query: {query}"
            assert result.execution_time_ms < 100, f"Too slow for Moby Dick query: {query}"

            # Check if expected content was found
            found_expected = any(exp_id in selected_ids for exp_id in expected_ids)
            assert found_expected, f"Expected Moby Dick content not found for query: {query}. Found: {selected_ids}"

    def test_cross_content_queries(self):
        """Test queries that combine Moby Dick with whale biology."""
        query = "Whales in Moby Dick literature vs real whale biology"
        result = self.selector.select(query, self.moby_segments, budget=800)

        # Should find content from both domains
        selected_ids = [seg.id for seg in result.selected_segments]
        moby_found = any(seg_id.startswith('moby_') for seg_id in selected_ids)
        whale_found = any(seg_id.startswith('whale_') for seg_id in selected_ids)

        assert len(result.selected_segments) > 0, "No results for cross-content query"
        assert result.execution_time_ms < 150, "Too slow for cross-content query"

        # Should find content from both categories (though not guaranteed)
        print(f"Cross-content query results: {selected_ids}")
        print(f"Moby Dick content found: {moby_found}")
        print(f"Biology content found: {whale_found}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])