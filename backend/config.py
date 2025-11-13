"""
Centralized configuration management for Z-GPT backend.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Hugging Face Configuration
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.1")
    MODEL_DEVICE: str = os.getenv("MODEL_DEVICE", "cpu")
    TRANSLATION_MODEL: str = os.getenv("TRANSLATION_MODEL", "argos_translate")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    USE_LOCAL_MODELS: bool = os.getenv("USE_LOCAL_MODELS", "False").lower() == "true"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if origin.strip()
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical settings."""
        if not cls.HUGGINGFACEHUB_API_TOKEN and not cls.USE_LOCAL_MODELS:
            print("Warning: HUGGINGFACEHUB_API_TOKEN not set and USE_LOCAL_MODELS is False")
        return True


settings = Settings()
