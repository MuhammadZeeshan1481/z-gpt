from transformers import pipeline
import argostranslate.package
import argostranslate.translate
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Lazy loading of language detection model
_language_detector = None

def get_language_detector():
    """Lazy load the language detection pipeline"""
    global _language_detector
    if _language_detector is None:
        logger.info("Loading language detection model...")
        _language_detector = pipeline(
            "text-classification",
            model="papluca/xlm-roberta-base-language-detection"
        )
        logger.info("Language detection model loaded")
    return _language_detector

# Initialize translation packages
def initialize_translation_packages():
    """Initialize translation packages if not already installed"""
    try:
        logger.info("Checking translation packages...")
        argostranslate.package.update_package_index()
        installed_packages = argostranslate.package.get_installed_packages()
        
        if not installed_packages:
            logger.info("No translation packages found. Installing en-ur and ur-en...")
            available_packages = argostranslate.package.get_available_packages()

            for pkg in available_packages:
                if (pkg.from_code == "en" and pkg.to_code == "ur") or \
                   (pkg.from_code == "ur" and pkg.to_code == "en"):
                    logger.info(f"Installing package: {pkg.from_code} -> {pkg.to_code}")
                    argostranslate.package.install_from_path(pkg.download())
            logger.info("Translation packages installed")
        else:
            logger.info(f"Found {len(installed_packages)} translation packages")
    except Exception as e:
        logger.error(f"Failed to initialize translation packages: {e}")

# Initialize on module load
initialize_translation_packages()

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    
    Args:
        text: Input text to detect language
        
    Returns:
        Language code (e.g., 'en', 'ur', 'es')
        
    Raises:
        ValueError: If text is empty or invalid
        RuntimeError: If language detection fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        detector = get_language_detector()
        # Use first 100 characters for detection
        sample = text[:100].strip()
        result = detector(sample)[0]
        lang_code = result["label"]
        logger.debug(f"Detected language: {lang_code} (confidence: {result['score']:.2f})")
        return lang_code
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        # Default to English if detection fails
        logger.warning("Defaulting to English")
        return "en"

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """
    Translate text from one language to another.
    
    Args:
        text: Text to translate
        from_lang: Source language code
        to_lang: Target language code
        
    Returns:
        Translated text
        
    Raises:
        ValueError: If input is invalid
        RuntimeError: If translation fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if not from_lang or not to_lang:
        raise ValueError("Language codes cannot be empty")
    
    # If source and target are the same, return original text
    if from_lang == to_lang:
        return text
    
    try:
        available_translations = argostranslate.translate.get_installed_languages()
        from_lang_obj = next(
            (lang for lang in available_translations if lang.code == from_lang),
            None
        )
        to_lang_obj = next(
            (lang for lang in available_translations if lang.code == to_lang),
            None
        )
        
        if not from_lang_obj:
            logger.warning(f"Source language '{from_lang}' not available, returning original text")
            return text
            
        if not to_lang_obj:
            logger.warning(f"Target language '{to_lang}' not available, returning original text")
            return text
        
        translation = from_lang_obj.get_translation(to_lang_obj)
        if not translation:
            logger.warning(f"No translation path from {from_lang} to {to_lang}, returning original text")
            return text
            
        translated = translation.translate(text)
        logger.debug(f"Translated text from {from_lang} to {to_lang}")
        return translated
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        # Return original text if translation fails
        logger.warning("Returning original text due to translation failure")
        return text 
