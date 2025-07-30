"""
Theater Critics System - API Integration Tests

This module tests integration with external APIs, particularly Ollama,
and handles network conditions, timeouts, and error scenarios.
"""

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import asyncio
import httpx
import pytest

from main import CriticType, SceneData, TheaterCritic


@pytest.mark.api
class TestOllamaIntegration:
    """Test Ollama API integration functionality."""

    @pytest.fixture
    def ollama_critic(self) -> TheaterCritic:
        """Create a critic configured for Ollama testing."""
        return TheaterCritic(
            name="API Test Critic",
            critic_type=CriticType.PRIMARY,
            model="gemma2:9b",
            specialty="API testing",
        )

    @pytest.fixture
    def valid_ollama_response(self) -> Dict[str, Any]:
        """Valid Ollama API response structure."""
        return {
            "response": """{
                "review_text": "This scene demonstrates excellent theatrical craftsmanship with powerful emotional resonance.",
                "scores": {
                    "overall": 8.7,
                    "musical_composition": 8.5,
                    "performance_quality": 9.2,
                    "production_elements": 8.0,
                    "narrative_integration": 8.8,
                    "audience_engagement": 9.0,
                    "specialty_score": 8.6
                },
                "key_strengths": [
                    "Compelling emotional arc",
                    "Strong musical composition",
                    "Effective character development"
                ],
                "areas_for_improvement": [
                    "Could benefit from more dynamic staging",
                    "Some pacing issues in the middle section"
                ],
                "specialty_analysis": "From a comprehensive perspective, this scene showcases the best of musical theater tradition while incorporating modern sensibilities."
            }""",
            "done": True,
            "total_duration": 1234567890,
            "load_duration": 123456789,
        }

    @pytest.mark.asyncio
    async def test_successful_ollama_request(
        self, ollama_critic, valid_ollama_response, sample_scene_data
    ):
        """Test successful Ollama API request and response parsing."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.json.return_value = valid_ollama_response
            mock_response.raise_for_status.return_value = None
            mock_response.status_code = 200

            # Setup mock client
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # Execute request
            result = await ollama_critic._query_ollama("test prompt")

            # Verify result
            assert result == valid_ollama_response["response"]

            # Verify request was made correctly
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args

            assert call_args[1]["json"]["model"] == "gemma2:9b"
            assert call_args[1]["json"]["prompt"] == "test prompt"
            assert call_args[1]["json"]["stream"] is False

    @pytest.mark.asyncio
    async def test_ollama_timeout_handling(self, ollama_critic):
        """Test handling of Ollama API timeouts."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup timeout exception
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                httpx.TimeoutException("Request timeout")
            )

            # Execute and verify exception
            with pytest.raises(Exception, match="Timeout waiting for gemma2:9b"):
                await ollama_critic._query_ollama("test prompt")

    @pytest.mark.asyncio
    async def test_ollama_http_error_handling(self, ollama_critic):
        """Test handling of HTTP errors from Ollama API."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup HTTP error
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            http_error = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=mock_response
            )
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                http_error
            )

            # Execute and verify exception
            with pytest.raises(Exception, match="HTTP error 500"):
                await ollama_critic._query_ollama("test prompt")

    @pytest.mark.asyncio
    async def test_ollama_connection_error(self, ollama_critic):
        """Test handling of connection errors to Ollama API."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup connection error
            connection_error = httpx.ConnectError("Connection failed")
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                connection_error
            )

            # Execute and verify exception
            with pytest.raises(Exception, match="Failed to query gemma2:9b"):
                await ollama_critic._query_ollama("test prompt")

    @pytest.mark.asyncio
    async def test_ollama_malformed_response(self, ollama_critic):
        """Test handling of malformed JSON responses from Ollama."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup malformed response
            mock_response = MagicMock()
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # Execute and verify exception
            with pytest.raises(Exception, match="Failed to query gemma2:9b"):
                await ollama_critic._query_ollama("test prompt")

    @pytest.mark.asyncio
    async def test_ollama_partial_response(self, ollama_critic, sample_scene_data):
        """Test handling of partial/incomplete responses from Ollama."""

        partial_response = {
            "response": """{
                "review_text": "Partial response...",
                "scores": {
                    "overall": 7.5
                }
            }""",
            "done": True,
        }

        with patch("main.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = partial_response
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # This should use fallback parsing
            review = await ollama_critic.analyze_scene(sample_scene_data)

            # Should create a fallback review
            assert review.critic_name == "API Test Critic"
            assert review.review_text is not None

    @pytest.mark.asyncio
    async def test_ollama_rate_limiting(self, ollama_critic):
        """Test handling of rate limiting from Ollama API."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup rate limit error
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.text = "Too Many Requests"

            rate_limit_error = httpx.HTTPStatusError(
                "Rate limited", request=MagicMock(), response=mock_response
            )
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                rate_limit_error
            )

            # Execute and verify exception
            with pytest.raises(Exception, match="HTTP error 429"):
                await ollama_critic._query_ollama("test prompt")


@pytest.mark.api
class TestConcurrentAPIRequests:
    """Test concurrent API request handling."""

    @pytest.mark.asyncio
    async def test_concurrent_critic_requests(
        self, valid_ollama_response, sample_scene_data
    ):
        """Test multiple concurrent requests to Ollama API."""

        # Create multiple critics
        critics = [
            TheaterCritic(f"Critic {i}", CriticType.PRIMARY, "test-model", "test")
            for i in range(3)
        ]

        with patch("main.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = valid_ollama_response
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # Execute concurrent requests
            tasks = [critic.analyze_scene(sample_scene_data) for critic in critics]
            reviews = await asyncio.gather(*tasks)

            # Verify all requests completed
            assert len(reviews) == 3
            for review in reviews:
                assert review.scores.overall > 0

            # Verify concurrent requests were made
            assert mock_client.return_value.__aenter__.return_value.post.call_count == 3

    @pytest.mark.asyncio
    async def test_mixed_success_failure_concurrent(
        self, valid_ollama_response, sample_scene_data
    ):
        """Test concurrent requests with mixed success/failure scenarios."""

        critics = [
            TheaterCritic(f"Critic {i}", CriticType.PRIMARY, "test-model", "test")
            for i in range(3)
        ]

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup mixed responses: success, timeout, success
            responses = [
                MagicMock(),  # Success
                httpx.TimeoutException("Timeout"),  # Failure
                MagicMock(),  # Success
            ]

            responses[0].json.return_value = valid_ollama_response
            responses[0].raise_for_status.return_value = None
            responses[2].json.return_value = valid_ollama_response
            responses[2].raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                responses
            )

            # Execute concurrent requests
            tasks = [critic.analyze_scene(sample_scene_data) for critic in critics]
            reviews = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify mixed results
            assert len(reviews) == 3

            # First and third should succeed
            assert not isinstance(reviews[0], Exception)
            assert not isinstance(reviews[2], Exception)

            # Second should be an error review (handled gracefully)
            assert isinstance(reviews[1], Exception) or reviews[1].scores.overall == 5.0


@pytest.mark.api
@pytest.mark.slow
class TestAPIPerformance:
    """Test API performance characteristics."""

    @pytest.mark.asyncio
    async def test_request_timeout_configuration(self, ollama_critic):
        """Test that request timeouts are properly configured."""

        with patch("main.httpx.AsyncClient") as mock_client:
            # Execute request
            await ollama_critic._query_ollama("test prompt")

            # Verify timeout was set
            mock_client.assert_called_once()
            call_args = mock_client.call_args
            assert call_args[1]["timeout"] == 120.0

    @pytest.mark.asyncio
    async def test_large_prompt_handling(self, ollama_critic):
        """Test handling of large prompts."""

        # Create a very large prompt
        large_prompt = "This is a test prompt. " * 1000  # ~24KB

        with patch("main.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": '{"review_text": "Test"}'}
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            # Should handle large prompts without error
            result = await ollama_critic._query_ollama(large_prompt)
            assert result is not None

            # Verify large prompt was sent
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            sent_prompt = call_args[1]["json"]["prompt"]
            assert len(sent_prompt) > 20000


@pytest.mark.api
class TestAPIResilience:
    """Test API resilience and error recovery."""

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, sample_scene_data):
        """Test that system degrades gracefully when API is unavailable."""

        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        with patch("main.httpx.AsyncClient") as mock_client:
            # Simulate complete API failure
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                Exception("API unavailable")
            )

            # Should return error review instead of crashing
            review = await critic.analyze_scene(sample_scene_data)

            assert review is not None
            assert "Analysis failed" in review.review_text
            assert review.scores.overall == 5.0  # Error score

    @pytest.mark.asyncio
    async def test_error_message_preservation(self, sample_scene_data):
        """Test that specific error messages are preserved for debugging."""

        critic = TheaterCritic("Test", CriticType.PRIMARY, "test-model", "test")

        specific_errors = [
            "Connection refused",
            "DNS resolution failed",
            "SSL certificate error",
            "Invalid model name",
        ]

        for error_msg in specific_errors:
            with patch("main.httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    Exception(error_msg)
                )

                review = await critic.analyze_scene(sample_scene_data)

                # Error message should be preserved in review
                assert error_msg in review.review_text

    @pytest.mark.asyncio
    async def test_partial_ensemble_failure(self, sample_scene_data):
        """Test ensemble behavior when some critics fail."""

        from main import CriticEnsemble

        ensemble = CriticEnsemble()

        with patch("main.httpx.AsyncClient") as mock_client:
            # Setup mixed responses: some succeed, some fail
            def side_effect(*args, **kwargs):
                # Randomly succeed or fail based on call count
                if (
                    mock_client.return_value.__aenter__.return_value.post.call_count % 2
                    == 0
                ):
                    raise Exception("Intermittent failure")
                else:
                    mock_response = MagicMock()
                    mock_response.json.return_value = {
                        "response": '{"review_text": "Success", "scores": {"overall": 8.0, "musical_composition": 8.0, "performance_quality": 8.0, "production_elements": 8.0, "narrative_integration": 8.0, "audience_engagement": 8.0, "specialty_score": 8.0}, "key_strengths": ["Test"], "areas_for_improvement": ["Test"], "specialty_analysis": "Test"}'
                    }
                    mock_response.raise_for_status.return_value = None
                    return mock_response

            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                side_effect
            )

            # Should handle partial failures gracefully
            reviews = await ensemble.review_scene(
                sample_scene_data, num_rotating_critics=2
            )

            # Should have some reviews, even if some failed
            assert len(reviews) > 0

            # Should have a mix of successful and error reviews
            successful_reviews = [
                r for r in reviews if "Analysis failed" not in r.review_text
            ]
            error_reviews = [r for r in reviews if "Analysis failed" in r.review_text]

            # At least one should succeed or fail (depending on timing)
            assert len(successful_reviews) + len(error_reviews) == len(reviews)
