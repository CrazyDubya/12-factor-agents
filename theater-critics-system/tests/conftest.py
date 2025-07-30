"""
Theater Critics System - Pytest Configuration and Fixtures

This module provides shared fixtures and configuration for all tests.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import asyncio
import pytest

# Import main classes for testing
from main import (
    CriticEnsemble,
    CriticReview,
    CriticType,
    ReviewScore,
    SceneData,
    TheaterCritic,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_scene_data() -> SceneData:
    """Provide a sample SceneData object for testing."""
    return SceneData(
        title="Test Scene - Defying Gravity",
        musical="Wicked",
        description="Elphaba's climactic moment of self-realization and defiance at the end of Act I",
        lyrics="""Something has changed within me
Something is not the same
I'm through with playing by the rules
Of someone else's game

Too late for second-guessing
Too late to go back to sleep
It's time to trust my instincts  
Close my eyes and leap!""",
        stage_directions="Elphaba rises above the stage on a mechanical lift, cape billowing, as the ensemble looks up in awe and fear",
        character_notes="Elphaba transforms from outcast to empowered individual, accepting her differences as strengths",
    )


@pytest.fixture
def minimal_scene_data() -> SceneData:
    """Provide a minimal SceneData object for edge case testing."""
    return SceneData(
        title="Minimal Test Scene",
        musical="Test Musical",
        description="A minimal scene for testing edge cases",
    )


@pytest.fixture
def sample_review_scores() -> ReviewScore:
    """Provide sample review scores for testing."""
    return ReviewScore(
        overall=8.5,
        musical_composition=8.0,
        performance_quality=9.0,
        production_elements=7.5,
        narrative_integration=8.2,
        audience_engagement=8.8,
        specialty_score=8.3,
    )


@pytest.fixture
def sample_critic_review(sample_review_scores) -> CriticReview:
    """Provide a sample CriticReview for testing."""
    return CriticReview(
        critic_name="Test Critic",
        critic_type=CriticType.PRIMARY,
        model_used="test-model",
        review_text="This is a comprehensive test review of the scene.",
        scores=sample_review_scores,
        key_strengths=[
            "Strong vocal performance",
            "Emotional impact",
            "Technical excellence",
        ],
        areas_for_improvement=["Staging could be more dynamic", "Some lyrics unclear"],
        specialty_analysis="From a comprehensive perspective, this scene demonstrates excellent theatrical craft.",
    )


@pytest.fixture
def mock_ollama_response() -> Dict[str, Any]:
    """Provide a mock Ollama API response."""
    return {
        "response": json.dumps(
            {
                "review_text": "This is a powerful and emotionally resonant scene that showcases excellent musical theater craft.",
                "scores": {
                    "overall": 8.5,
                    "musical_composition": 8.0,
                    "performance_quality": 9.0,
                    "production_elements": 7.5,
                    "narrative_integration": 8.2,
                    "audience_engagement": 8.8,
                    "specialty_score": 8.3,
                },
                "key_strengths": [
                    "Powerful vocal performance requirements",
                    "Strong emotional arc",
                    "Memorable musical composition",
                ],
                "areas_for_improvement": [
                    "Complex staging requirements",
                    "High technical demands",
                ],
                "specialty_analysis": "This scene represents a pinnacle moment in musical theater, combining technical excellence with emotional depth.",
            }
        )
    }


@pytest.fixture
def mock_ollama_invalid_response() -> Dict[str, Any]:
    """Provide an invalid Ollama API response for error testing."""
    return {"response": "This is just plain text without JSON formatting."}


@pytest.fixture
def mock_theater_critic(mock_ollama_response):
    """Provide a mocked TheaterCritic for testing."""
    critic = TheaterCritic(
        name="Test Critic",
        critic_type=CriticType.PRIMARY,
        model="test-model",
        specialty="comprehensive analysis",
    )

    # Mock the _query_ollama method
    critic._query_ollama = AsyncMock(return_value=mock_ollama_response["response"])

    return critic


@pytest.fixture
def mock_critic_ensemble(mock_theater_critic):
    """Provide a mocked CriticEnsemble for testing."""
    ensemble = CriticEnsemble()

    # Replace critics with mocked versions
    ensemble.critics = {
        CriticType.PRIMARY: mock_theater_critic,
        CriticType.ACADEMIC: mock_theater_critic,
        CriticType.POPULAR: mock_theater_critic,
    }
    ensemble.primary_critic = mock_theater_critic

    return ensemble


@pytest.fixture
def sample_analysis_results() -> List[Dict[str, Any]]:
    """Provide sample analysis results for testing."""
    return [
        {
            "rank": 1,
            "musical_name": "Test Musical 1",
            "scene_title": "Opening Number",
            "scores": {"overall_score": 8.5, "component_1": 8.0, "component_2": 9.0},
            "analysis_details": {
                "strengths": ["Strong opening", "Good energy"],
                "improvements": ["Could be louder"],
            },
        },
        {
            "rank": 2,
            "musical_name": "Test Musical 2",
            "scene_title": "Finale",
            "scores": {"overall_score": 7.8, "component_1": 7.5, "component_2": 8.1},
            "analysis_details": {
                "strengths": ["Emotional impact", "Good resolution"],
                "improvements": ["Pacing issues"],
            },
        },
    ]


@pytest.fixture
def temp_analysis_file(tmp_path, sample_analysis_results):
    """Create a temporary analysis file for testing."""
    analysis_file = tmp_path / "test_analysis.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "analysis_metadata": {
                    "analysis_type": "Test Analysis",
                    "total_scenes": 2,
                },
                "rankings": sample_analysis_results,
            },
            f,
            indent=2,
        )

    return analysis_file


@pytest.fixture
def temp_scene_files(tmp_path):
    """Create temporary scene files for testing."""
    scene_dir = tmp_path / "scenes"
    scene_dir.mkdir()

    # Create sample scene files
    scene1 = scene_dir / "scene_01.json"
    scene1_data = {
        "title": "Opening Number",
        "musical": "Test Musical",
        "description": "The opening scene",
        "lyrics": "Welcome to our show tonight",
        "stage_directions": "Curtain rises",
        "character_notes": "Ensemble enters",
    }

    with open(scene1, "w", encoding="utf-8") as f:
        json.dump(scene1_data, f, indent=2)

    scene2 = scene_dir / "scene_02.json"
    scene2_data = {
        "title": "Finale",
        "musical": "Test Musical",
        "description": "The closing scene",
        "lyrics": "Thank you for joining us tonight",
        "stage_directions": "Curtain falls",
        "character_notes": "Cast takes bow",
    }

    with open(scene2, "w", encoding="utf-8") as f:
        json.dump(scene2_data, f, indent=2)

    return scene_dir


@pytest.fixture
def mock_httpx_client():
    """Provide a mocked httpx client for API testing."""
    return MagicMock()


# Pytest markers for test organization
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "analysis: mark test as analysis-specific")
    config.addinivalue_line("markers", "dashboard: mark test as dashboard/UI related")


# Test configuration constants
TEST_TIMEOUT = 30  # seconds
API_TIMEOUT = 10  # seconds
OLLAMA_BASE_URL = "http://localhost:11434"
TEST_MODEL = "test-model:latest"

# Test data constants
VALID_SCORE_RANGE = (0.0, 10.0)
EXPECTED_CRITIC_TYPES = [
    CriticType.PRIMARY,
    CriticType.ACADEMIC,
    CriticType.POPULAR,
    CriticType.EXPERIMENTAL,
    CriticType.COMMERCIAL,
    CriticType.EMOTION,
]
