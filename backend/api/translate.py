from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
import argostranslate.package
import argostranslate.translate
from backend.config.settings import MAX_MESSAGE_LENGTH
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate", min_length=1, max_length=MAX_MESSAGE_LENGTH)
    from_lang: str = Field("en", alias="from", description="Source language code (e.g., 'en', 'ur')")
    to_lang: str = Field("ur", alias="to", description="Target language code (e.g., 'en', 'ur')")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('from_lang', 'to_lang')
    def validate_lang_code(cls, v):
        if not v or len(v) < 2 or len(v) > 5:
            raise ValueError('Invalid language code')
        return v.lower()

class TranslationResponse(BaseModel):
    translated_text: str = Field(..., description="Translated text")
    from_lang: str = Field(..., description="Source language code")
    to_lang: str = Field(..., description="Target language code")
    processing_time: float = Field(..., description="Processing time in seconds")

def translate_text_internal(text: str, from_code: str, to_code: str) -> str:
    """Internal translation function with error handling"""
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if not from_lang or not to_lang:
        raise ValueError(f"Language pair {from_code}->{to_code} not supported or model not installed")

    translation = from_lang.get_translation(to_lang)
    if not translation:
        raise ValueError(f"Translation from {from_code} to {to_code} not available")
        
    return translation.translate(text)

@router.post("/", response_model=TranslationResponse, status_code=status.HTTP_200_OK)
async def handle_translation(request: TranslationRequest):
    """
    Translate text between languages.
    
    - **text**: Text to translate
    - **from**: Source language code (e.g., 'en', 'ur')
    - **to**: Target language code (e.g., 'en', 'ur')
    
    Returns translated text.
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Translating text from {request.from_lang} to {request.to_lang}")
        
        translated = translate_text_internal(request.text, request.from_lang, request.to_lang)
        
        processing_time = time.time() - start_time
        logger.info(f"Translation completed in {processing_time:.2f}s")
        
        return TranslationResponse(
            translated_text=translated,
            from_lang=request.from_lang,
            to_lang=request.to_lang,
            processing_time=processing_time
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed. Please try again later."
        )

# Legacy endpoint for backward compatibility
@router.post("/translate", response_model=TranslationResponse, status_code=status.HTTP_200_OK)
async def handle_translation_legacy(request: dict):
    """Legacy translation endpoint for backward compatibility"""
    try:
        text = request.get("text", "")
        from_lang = request.get("from", "en")
        to_lang = request.get("to", "ur")
        
        translation_request = TranslationRequest(
            text=text,
            from_lang=from_lang,
            to_lang=to_lang
        )
        
        return await handle_translation(translation_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
