import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.1")
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "argos_translate")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
USE_LOCAL_MODELS = os.getenv("USE_LOCAL_MODELS", "False").lower() == "true"
