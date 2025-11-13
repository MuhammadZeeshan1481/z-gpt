from fastapi import APIRouter, HTTPException
from backend.models import TranslationRequest, TranslationResponse
import argostranslate.package, argostranslate.translate

router = APIRouter()

def translate_text(text: str, from_code: str, to_code: str) -> str:
    """Translate text using argostranslate."""
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if not from_lang or not to_lang:
        raise HTTPException(status_code=400, detail="Language not supported or model not installed")

    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

@router.post("/translate", response_model=TranslationResponse)
def handle_translation(request: TranslationRequest):
    """Handle translation requests with proper validation."""
    try:
        translated = translate_text(request.text, request.from_lang, request.to_lang)
        return TranslationResponse(
            translated_text=translated,
            source_language=request.from_lang,
            target_language=request.to_lang
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
