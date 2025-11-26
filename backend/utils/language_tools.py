from functools import lru_cache
from typing import Any, Callable

try:
    from transformers import pipeline  # type: ignore
except ImportError:  # pragma: no cover - ensure graceful fallback
    pipeline = None  # type: ignore

try:
    import argostranslate.translate  # type: ignore
except ImportError:  # pragma: no cover
    argostranslate = None  # type: ignore

# Cache the HF pipeline; creating per-request is too slow
@lru_cache(maxsize=1)
def _lang_detect_pipeline() -> Callable[[str], Any]:
    if pipeline is None:
        raise RuntimeError("transformers is required for language detection")
    return pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")


def detect_language(text: str) -> str:
    # Limit input length for speed
    try:
        result = _lang_detect_pipeline()(text[:256])[0]
        return result["label"]
    except Exception:
        return "en"


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    # Expect translations to be pre-installed in the container/image; if missing, return passthrough
    try:
        if argostranslate is None:
            raise RuntimeError("argostranslate is not installed")

        available_translations = argostranslate.translate.get_installed_languages()
        from_lang_obj = next((lang for lang in available_translations if lang.code == from_lang), None)
        to_lang_obj = next((lang for lang in available_translations if lang.code == to_lang), None)
        if from_lang_obj and to_lang_obj:
            translation = from_lang_obj.get_translation(to_lang_obj)
            return translation.translate(text)
    except Exception:
        pass
    return text 
