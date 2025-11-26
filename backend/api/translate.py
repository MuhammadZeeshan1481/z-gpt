from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ConfigDict

from backend.core.dependencies import get_current_user
from backend.db.models import User

try:
    import argostranslate.package  # type: ignore
    import argostranslate.translate  # type: ignore
    _ARGOS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    argostranslate = None  # type: ignore
    _ARGOS_AVAILABLE = False

router = APIRouter()

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    from_lang: str = Field(alias="from", default="en")
    to_lang: str = Field(alias="to", default="ur")

    model_config = ConfigDict(populate_by_name=True)

class TranslateResponse(BaseModel):
    translated_text: str


def translate_text(text: str, from_code: str, to_code: str) -> str:
    if not _ARGOS_AVAILABLE:
        raise HTTPException(status_code=503, detail={
            "code": "translation_unavailable",
            "message": "Translation service is unavailable",
        })

    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)

    if not from_lang or not to_lang:
        raise HTTPException(status_code=400, detail={
            "code": "unsupported_language",
            "message": "Language not supported or model not installed",
        })

    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

@router.post("/translate", response_model=TranslateResponse)
def handle_translation(
    req: TranslateRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    try:
        translated = translate_text(req.text, req.from_lang, req.to_lang)
        return TranslateResponse(translated_text=translated)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={
            "code": "translation_failed",
            "message": "Translation failed",
            "request_id": getattr(http_request.state, "request_id", None),
        })
