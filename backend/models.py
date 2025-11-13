"""
Pydantic models for request/response validation across all API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# Chat Models
class Message(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message")
    history: List[Message] = Field(default=[], description="Conversation history")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    detected_lang: str = Field(..., description="Detected language code")


# Image Models
class ImageRequest(BaseModel):
    """Request model for image generation endpoint."""
    prompt: str = Field(..., description="Text prompt for image generation")
    guidance_scale: Optional[float] = Field(default=8.5, description="Guidance scale for generation")


class ImageResponse(BaseModel):
    """Response model for image generation endpoint."""
    image_base64: str = Field(..., description="Base64 encoded generated image")


# Translation Models
class TranslationRequest(BaseModel):
    """Request model for translation endpoint."""
    text: str = Field(..., description="Text to translate")
    from_lang: str = Field(default="en", alias="from", description="Source language code")
    to_lang: str = Field(default="ur", alias="to", description="Target language code")
    
    class Config:
        populate_by_name = True


class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""
    translated_text: str = Field(..., description="Translated text")
    source_language: Optional[str] = Field(None, description="Detected source language")
    target_language: Optional[str] = Field(None, description="Target language")


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
