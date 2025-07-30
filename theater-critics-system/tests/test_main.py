"""
Theater Critics System - Core Module Tests

This module tests the main theater critics functionality including
TheaterCritic, CriticEnsemble, and ConsensusAnalyzer classes.
"""

import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from main import (
    ConsensusAnalyzer,
    CriticEnsemble,
    CriticReview,
    CriticType,
    ReviewScore,
    SceneData,
    TheaterCritic,
    print_review_summary,
)


class TestSceneData:
    """Test SceneData dataclass functionality."""

    @pytest.mark.unit
    def test_scene_data_creation(self, sample_scene_data):
        """Test SceneData object creation with all fields."""
        assert sample_scene_data.title == "Test Scene - Defying Gravity"
        assert sample_scene_data.musical == "Wicked"
        assert "self-realization" in sample_scene_data.description
        assert "Something has changed" in sample_scene_data.lyrics
        assert "mechanical lift" in sample_scene_data.stage_directions
        assert "transforms" in sample_scene_data.character_notes

    @pytest.mark.unit
    def test_scene_data_minimal(self, minimal_scene_data):
        """Test SceneData with minimal required fields."""
        assert minimal_scene_data.title == "Minimal Test Scene"
        assert minimal_scene_data.musical == "Test Musical"
        assert minimal_scene_data.lyrics is None
        assert minimal_scene_data.stage_directions is None
        assert minimal_scene_data.character_notes is None


class TestReviewScore:
    """Test ReviewScore dataclass functionality."""

    @pytest.mark.unit
    def test_review_score_creation(self, sample_review_scores):
        """Test ReviewScore object creation."""
        assert sample_review_scores.overall == 8.5
        assert sample_review_scores.musical_composition == 8.0
        assert sample_review_scores.performance_quality == 9.0
        assert sample_review_scores.specialty_score == 8.3

    @pytest.mark.unit
    def test_review_score_range_validation(self):
        """Test that review scores are in valid range."""
        scores = ReviewScore(5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 7.5)

        # All scores should be between 0 and 10
        for field_name in scores.__dataclass_fields__:
            score_value = getattr(scores, field_name)
            assert (
                0.0 <= score_value <= 10.0
            ), f"{field_name} score {score_value} out of valid range"


class TestCriticReview:
    """Test CriticReview dataclass functionality."""

    @pytest.mark.unit
    def test_critic_review_creation(self, sample_critic_review):
        """Test CriticReview object creation."""
        assert sample_critic_review.critic_name == "Test Critic"
        assert sample_critic_review.critic_type == CriticType.PRIMARY
        assert sample_critic_review.model_used == "test-model"
        assert "comprehensive test review" in sample_critic_review.review_text
        assert len(sample_critic_review.key_strengths) == 3
        assert len(sample_critic_review.areas_for_improvement) == 2


class TestTheaterCritic:
    """Test TheaterCritic class functionality."""

    @pytest.mark.unit
    def test_critic_initialization(self):
        """Test TheaterCritic initialization."""
        critic = TheaterCritic(
            name="Test Critic",
            critic_type=CriticType.ACADEMIC,
            model="test-model",
            specialty="musical theory",
        )

        assert critic.name == "Test Critic"
        assert critic.critic_type == CriticType.ACADEMIC
        assert critic.model == "test-model"
        assert critic.specialty == "musical theory"
        assert "localhost:11434" in critic.ollama_url

    @pytest.mark.unit
    def test_build_analysis_prompt(self, sample_scene_data):
        """Test analysis prompt building."""
        critic = TheaterCritic(
            name="Test Critic",
            critic_type=CriticType.PRIMARY,
            model="test-model",
            specialty="comprehensive analysis",
        )

        prompt = critic._build_analysis_prompt(sample_scene_data)

        # Check that prompt contains expected elements
        assert "Test Critic" in prompt
        assert "comprehensive analysis" in prompt
        assert sample_scene_data.title in prompt
        assert sample_scene_data.musical in prompt
        assert "JSON format" in prompt
        assert "scores" in prompt

    @pytest.mark.unit
    def test_get_specialty_prompt(self):
        """Test specialty prompt generation for different critic types."""
        test_cases = [
            (CriticType.PRIMARY, "comprehensive analysis"),
            (CriticType.ACADEMIC, "musical theory"),
            (CriticType.POPULAR, "audience appeal"),
            (CriticType.EXPERIMENTAL, "artistic risk-taking"),
            (CriticType.COMMERCIAL, "production value"),
            (CriticType.EMOTION, "emotional impact"),
        ]

        for critic_type, expected_content in test_cases:
            critic = TheaterCritic("Test", critic_type, "test-model", "test")
            prompt = critic._get_specialty_prompt()
            assert expected_content.lower() in prompt.lower()

    @pytest.mark.unit
    def test_parse_response_valid_json(self, mock_ollama_response, sample_scene_data):
        """Test parsing valid JSON response from Ollama."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        review = critic._parse_response(
            mock_ollama_response["response"], sample_scene_data
        )

        assert isinstance(review, CriticReview)
        assert review.critic_name == "Test"
        assert review.scores.overall == 8.5
        assert len(review.key_strengths) == 3
        assert len(review.areas_for_improvement) == 2

    @pytest.mark.unit
    def test_parse_response_invalid_json(self, sample_scene_data):
        """Test parsing invalid JSON response (fallback behavior)."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")
        invalid_response = "This is not JSON at all!"

        review = critic._parse_response(invalid_response, sample_scene_data)

        assert isinstance(review, CriticReview)
        assert review.critic_name == "Test"
        assert review.scores.overall == 7.0  # Fallback score
        assert "Analysis provided in narrative form" in review.key_strengths

    @pytest.mark.unit
    def test_create_error_review(self):
        """Test error review creation."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")
        error_msg = "Network timeout"

        review = critic._create_error_review(error_msg)

        assert isinstance(review, CriticReview)
        assert error_msg in review.review_text
        assert review.scores.overall == 5.0  # Error score
        assert "Unable to analyze" in review.key_strengths

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_query_ollama_success(self, mock_ollama_response):
        """Test successful Ollama API query."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await critic._query_ollama("test prompt")

            assert result == mock_ollama_response["response"]

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_query_ollama_timeout(self):
        """Test Ollama API timeout handling."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        with patch("httpx.AsyncClient") as mock_client:
            from httpx import TimeoutException

            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                TimeoutException("Timeout")
            )

            with pytest.raises(Exception, match="Timeout waiting for"):
                await critic._query_ollama("test prompt")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_scene_integration(
        self, sample_scene_data, mock_ollama_response
    ):
        """Test complete scene analysis integration."""
        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        # Mock the HTTP client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            review = await critic.analyze_scene(sample_scene_data)

            assert isinstance(review, CriticReview)
            assert review.critic_name == "Test"
            assert 0.0 <= review.scores.overall <= 10.0


class TestCriticEnsemble:
    """Test CriticEnsemble class functionality."""

    @pytest.mark.unit
    def test_ensemble_initialization(self):
        """Test CriticEnsemble initialization."""
        ensemble = CriticEnsemble()

        # Should have all critic types
        assert len(ensemble.critics) == 6
        assert CriticType.PRIMARY in ensemble.critics
        assert CriticType.ACADEMIC in ensemble.critics
        assert ensemble.primary_critic.critic_type == CriticType.PRIMARY

    @pytest.mark.unit
    def test_select_rotating_critics(self):
        """Test rotating critics selection."""
        ensemble = CriticEnsemble()

        # Test normal selection
        rotating = ensemble.select_rotating_critics(3)
        assert len(rotating) == 3

        # Ensure primary critic is not included
        for critic in rotating:
            assert critic.critic_type != CriticType.PRIMARY

        # Test requesting more than available
        rotating_all = ensemble.select_rotating_critics(10)
        assert len(rotating_all) == 5  # All except primary

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_review_scene_integration(
        self, sample_scene_data, mock_ollama_response
    ):
        """Test complete ensemble scene review."""
        ensemble = CriticEnsemble()

        # Mock all critics to return valid responses
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            reviews = await ensemble.review_scene(
                sample_scene_data, num_rotating_critics=2
            )

            assert len(reviews) == 3  # Primary + 2 rotating
            for review in reviews:
                assert isinstance(review, CriticReview)
                assert 0.0 <= review.scores.overall <= 10.0


class TestConsensusAnalyzer:
    """Test ConsensusAnalyzer class functionality."""

    @pytest.mark.unit
    def test_calculate_consensus_empty(self):
        """Test consensus calculation with empty reviews."""
        consensus = ConsensusAnalyzer.calculate_consensus([])
        assert consensus == {}

    @pytest.mark.unit
    def test_calculate_consensus_single_review(self, sample_critic_review):
        """Test consensus calculation with single review."""
        consensus = ConsensusAnalyzer.calculate_consensus([sample_critic_review])

        assert consensus["consensus_level"] == "Strong Agreement"
        assert consensus["critic_count"] == 1
        assert "average_scores" in consensus
        assert consensus["average_scores"]["overall"] == 8.5

    @pytest.mark.unit
    def test_calculate_consensus_multiple_reviews(self, sample_review_scores):
        """Test consensus calculation with multiple reviews."""
        # Create reviews with different scores
        review1 = CriticReview(
            "Critic 1",
            CriticType.PRIMARY,
            "model1",
            "Review 1",
            ReviewScore(8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0),
            ["Strength 1"],
            ["Improvement 1"],
            "Analysis 1",
        )
        review2 = CriticReview(
            "Critic 2",
            CriticType.ACADEMIC,
            "model2",
            "Review 2",
            ReviewScore(7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0),
            ["Strength 2"],
            ["Improvement 2"],
            "Analysis 2",
        )

        consensus = ConsensusAnalyzer.calculate_consensus([review1, review2])

        assert consensus["critic_count"] == 2
        assert consensus["average_scores"]["overall"] == 7.5
        assert consensus["score_variations"]["overall"] == 1.0
        assert consensus["consensus_level"] == "Strong Agreement"

    @pytest.mark.unit
    def test_consensus_level_classification(self):
        """Test consensus level classification based on variation."""
        # Create reviews with varying disagreement levels
        base_score = ReviewScore(5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0)

        # Strong agreement (variation <= 1.0)
        review1 = CriticReview(
            "C1",
            CriticType.PRIMARY,
            "m1",
            "r1",
            ReviewScore(8.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0),
            [],
            [],
            "",
        )
        review2 = CriticReview(
            "C2",
            CriticType.ACADEMIC,
            "m2",
            "r2",
            ReviewScore(8.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0),
            [],
            [],
            "",
        )

        consensus = ConsensusAnalyzer.calculate_consensus([review1, review2])
        assert consensus["consensus_level"] == "Strong Agreement"

        # Significant disagreement (variation > 3.0)
        review3 = CriticReview(
            "C3",
            CriticType.POPULAR,
            "m3",
            "r3",
            ReviewScore(4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0),
            [],
            [],
            "",
        )

        consensus = ConsensusAnalyzer.calculate_consensus([review1, review3])
        assert consensus["consensus_level"] == "Significant Disagreement"


class TestUtilityFunctions:
    """Test utility functions."""

    @pytest.mark.unit
    def test_print_review_summary(self, sample_critic_review, capsys):
        """Test review summary printing."""
        reviews = [sample_critic_review]
        consensus = ConsensusAnalyzer.calculate_consensus(reviews)

        print_review_summary(reviews, consensus)

        captured = capsys.readouterr()
        assert "THEATER CRITICS ENSEMBLE REVIEW" in captured.out
        assert "Test Critic" in captured.out
        assert "8.5/10.0" in captured.out


# Integration test markers
pytestmark = pytest.mark.integration
