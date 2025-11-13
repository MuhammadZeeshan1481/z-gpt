import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# API Configuration
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
API_KEY = os.getenv("API_KEY", "")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.1")
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "argos_translate")
USE_LOCAL_MODELS = os.getenv("USE_LOCAL_MODELS", "False").lower() == "true"

# Server Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Model Cache
HF_HOME = os.getenv("HF_HOME", "./models")
TRANSFORMERS_CACHE = os.getenv("TRANSFORMERS_CACHE", "./models/transformers")

# Request Limits
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "10"))
MAX_PROMPT_LENGTH = int(os.getenv("MAX_PROMPT_LENGTH", "500"))

# Timeouts (in seconds)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
IMAGE_GENERATION_TIMEOUT = int(os.getenv("IMAGE_GENERATION_TIMEOUT", "120"))
TRANSLATION_TIMEOUT = int(os.getenv("TRANSLATION_TIMEOUT", "10"))
