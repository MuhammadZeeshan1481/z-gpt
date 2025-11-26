from functools import lru_cache
from typing import List
from pydantic import BaseModel, Field, ConfigDict, field_validator
import os


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    app_debug: bool = Field(default=os.getenv("APP_DEBUG", "false").lower() == "true")
    app_host: str = Field(default=os.getenv("APP_HOST", "0.0.0.0"))
    app_port: int = Field(default=int(os.getenv("APP_PORT", "8000")))

    cors_origins: List[str] = Field(default_factory=lambda: [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()
    ])

    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))

    # LLM providers
    openai_api_key: str | None = Field(default=os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: str | None = Field(default=os.getenv("ANTHROPIC_API_KEY"))
    azure_openai_endpoint: str | None = Field(default=os.getenv("AZURE_OPENAI_ENDPOINT"))
    azure_openai_api_key: str | None = Field(default=os.getenv("AZURE_OPENAI_API_KEY"))

    # Model defaults
    chat_model: str = Field(default=os.getenv("CHAT_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"))
    chat_device: str = Field(default=os.getenv("CHAT_DEVICE", "auto"))
    chat_precision: str = Field(default=os.getenv("CHAT_PRECISION", "float16"))

    image_model: str = Field(default=os.getenv("IMAGE_MODEL", "runwayml/stable-diffusion-v1-5"))
    image_device: str = Field(default=os.getenv("IMAGE_DEVICE", "cpu"))
    image_generation_enabled: bool = Field(default=os.getenv("IMAGE_ENABLED", "true").lower() == "true")

    translate_model: str = Field(default=os.getenv("TRANSLATE_MODEL", "argos_translate"))

    moderation_enabled: bool = Field(default=os.getenv("MODERATION_ENABLED", "true").lower() == "true")

    rate_limit_per_minute: int = Field(default=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")))
    rate_limit_window_seconds: int = Field(default=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")))

    db_url: str = Field(default=os.getenv("DB_URL", "sqlite:///./data/zgpt.db"))
    redis_url: str | None = Field(default=os.getenv("REDIS_URL"))

    jwt_secret_key: str = Field(default=os.getenv("JWT_SECRET_KEY", "changeme"))
    jwt_algorithm: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_access_token_expire_minutes: int = Field(default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
    jwt_refresh_token_expire_minutes: int = Field(default=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", "10080")))

    metrics_enabled: bool = Field(default=os.getenv("METRICS_ENABLED", "true").lower() == "true")
    metrics_endpoint: str = Field(default=os.getenv("METRICS_ENDPOINT", "/metrics"))

    otel_exporter_endpoint: str | None = Field(default=os.getenv("OTEL_EXPORTER_ENDPOINT"))
    otel_exporter_headers: str | None = Field(default=os.getenv("OTEL_EXPORTER_HEADERS"))
    otel_exporter_insecure: bool = Field(default=os.getenv("OTEL_EXPORTER_INSECURE", "false").lower() == "true")
    otel_service_name: str = Field(default=os.getenv("OTEL_SERVICE_NAME", "z-gpt-backend"))

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            parsed = [o.strip() for o in value.split(",") if o.strip()]
            return parsed or ["http://localhost:3000"]
        if isinstance(value, list) and value:
            return value
        return ["http://localhost:3000"]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        normalized = (value or "INFO").upper()
        if normalized not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return normalized

    @field_validator("chat_device", "image_device")
    @classmethod
    def normalize_device(cls, value: str) -> str:
        return (value or "cpu").lower()

    @field_validator("chat_precision")
    @classmethod
    def validate_precision(cls, value: str) -> str:
        allowed = {"float16", "float32", "bfloat16"}
        normalized = (value or "float16").lower()
        if normalized not in allowed:
            raise ValueError("CHAT_PRECISION must be float16, float32, or bfloat16")
        return normalized

    @field_validator("rate_limit_per_minute")
    @classmethod
    def validate_rate_limit(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be greater than zero")
        return value

    @field_validator("rate_limit_window_seconds")
    @classmethod
    def validate_window(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("RATE_LIMIT_WINDOW_SECONDS must be greater than zero")
        return value

    @field_validator("metrics_endpoint")
    @classmethod
    def normalize_metrics_endpoint(cls, value: str) -> str:
        value = value or "/metrics"
        if not value.startswith("/"):
            value = f"/{value}"
        return value

    @property
    def is_prod(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}

    @property
    def otel_headers_dict(self) -> dict[str, str]:
        if not self.otel_exporter_headers:
            return {}
        headers = {}
        for part in self.otel_exporter_headers.split(","):
            if not part.strip():
                continue
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            headers[key.strip()] = value.strip()
        return headers


@lru_cache
def get_settings() -> Settings:
    return Settings()
