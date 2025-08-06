from fastapi import APIRouter, HTTPException
import argostranslate.package, argostranslate.translate
import os

router = APIRouter()

def translate_text(text: str, from_code: str, to_code: str) -> str:
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if not from_lang or not to_lang:
        raise HTTPException(status_code=400, detail="Language not supported or model not installed")

    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

@router.post("/translate")
def handle_translation(request: dict):
    try:
        text = request.get("text", "")
        from_lang = request.get("from", "en")
        to_lang = request.get("to", "ur")

        translated = translate_text(text, from_lang, to_lang)
        return {"translated_text": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
