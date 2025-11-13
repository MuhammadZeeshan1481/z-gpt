"""Pytest configuration and fixtures for Z-GPT tests."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "message": "Hello, how are you?",
        "history": []
    }


@pytest.fixture
def sample_image_request():
    """Sample image generation request for testing."""
    return {
        "prompt": "A beautiful sunset over mountains"
    }


@pytest.fixture
def sample_translation_request():
    """Sample translation request for testing."""
    return {
        "text": "Hello world",
        "from": "en",
        "to": "ur"
    }
