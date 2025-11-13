"""Tests for Pydantic models and schema validation."""
import pytest
from pydantic import ValidationError
from backend.models import (
    ChatRequest, ChatResponse, Message,
    ImageRequest, ImageResponse,
    TranslationRequest, TranslationResponse,
    ErrorResponse
)


class TestChatModels:
    """Tests for chat-related models."""
    
    def test_message_model_valid(self):
        """Test Message model with valid data."""
        message = Message(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
    
    def test_chat_request_minimal(self):
        """Test ChatRequest with minimal valid data."""
        request = ChatRequest(message="Hello")
        assert request.message == "Hello"
        assert request.history == []
    
    def test_chat_request_with_history(self):
        """Test ChatRequest with conversation history."""
        history = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello")
        ]
        request = ChatRequest(message="How are you?", history=history)
        assert len(request.history) == 2
    
    def test_chat_response(self):
        """Test ChatResponse model."""
        response = ChatResponse(response="I'm good", detected_lang="en")
        assert response.response == "I'm good"
        assert response.detected_lang == "en"


class TestImageModels:
    """Tests for image generation models."""
    
    def test_image_request_valid(self):
        """Test ImageRequest with valid data."""
        request = ImageRequest(prompt="A sunset")
        assert request.prompt == "A sunset"
        assert request.guidance_scale == 8.5
    
    def test_image_request_custom_guidance(self):
        """Test ImageRequest with custom guidance scale."""
        request = ImageRequest(prompt="A sunset", guidance_scale=10.0)
        assert request.guidance_scale == 10.0
    
    def test_image_response(self):
        """Test ImageResponse model."""
        response = ImageResponse(image_base64="base64encodedstring")
        assert response.image_base64 == "base64encodedstring"


class TestTranslationModels:
    """Tests for translation models."""
    
    def test_translation_request_minimal(self):
        """Test TranslationRequest with minimal data."""
        request = TranslationRequest(text="Hello")
        assert request.text == "Hello"
        assert request.from_lang == "en"
        assert request.to_lang == "ur"
    
    def test_translation_request_with_alias(self):
        """Test TranslationRequest using field aliases."""
        data = {"text": "Hello", "from": "en", "to": "fr"}
        request = TranslationRequest(**data)
        assert request.from_lang == "en"
        assert request.to_lang == "fr"
    
    def test_translation_response(self):
        """Test TranslationResponse model."""
        response = TranslationResponse(
            translated_text="Bonjour",
            source_language="en",
            target_language="fr"
        )
        assert response.translated_text == "Bonjour"
        assert response.source_language == "en"


class TestErrorModels:
    """Tests for error response models."""
    
    def test_error_response(self):
        """Test ErrorResponse model."""
        error = ErrorResponse(detail="Something went wrong", error_code="ERR_500")
        assert error.detail == "Something went wrong"
        assert error.error_code == "ERR_500"
