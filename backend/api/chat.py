from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from backend.core.llm_handler import generate_reply
from backend.utils.language_tools import detect_language, translate_text
from backend.config.settings import MAX_MESSAGE_LENGTH, MAX_HISTORY_LENGTH
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError('Role must be either "user" or "assistant"')
        return v

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'Content exceeds maximum length of {MAX_MESSAGE_LENGTH}')
        return v.strip()

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to the chatbot", min_length=1, max_length=MAX_MESSAGE_LENGTH)
    history: List[Message] = Field(default=[], description="Conversation history")

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @validator('history')
    def validate_history(cls, v):
        if len(v) > MAX_HISTORY_LENGTH:
            raise ValueError(f'History exceeds maximum length of {MAX_HISTORY_LENGTH}')
        return v

class ChatResponse(BaseModel):
    response: str = Field(..., description="Chatbot response")
    detected_lang: str = Field(..., description="Detected language code")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages with language detection and translation.
    
    - **message**: User message to process
    - **history**: Optional conversation history for context
    
    Returns translated response in the detected language.
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Processing chat message: {request.message[:50]}...")
        
        # Detect language
        detected_lang = detect_language(request.message)
        logger.debug(f"Detected language: {detected_lang}")
        
        # Translate to English if needed
        input_text = (
            translate_text(request.message, from_lang=detected_lang, to_lang="en")
            if detected_lang != "en"
            else request.message
        )
        logger.debug(f"Translated input: {input_text[:50]}...")

        # Generate reply
        reply_en = generate_reply(input_text, request.history or [])
        logger.debug(f"Generated reply: {reply_en[:50]}...")
        
        # Translate back to detected language if needed
        final_reply = (
            translate_text(reply_en, from_lang="en", to_lang=detected_lang)
            if detected_lang != "en"
            else reply_en
        )

        processing_time = time.time() - start_time
        logger.info(f"Chat processing completed in {processing_time:.2f}s")

        return ChatResponse(
            response=final_reply.strip(),
            detected_lang=detected_lang,
            processing_time=processing_time
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"LLM processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message. Please try again later."
        )
