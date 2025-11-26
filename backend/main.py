from contextlib import asynccontextmanager
import logging
import time
import uuid

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis import asyncio as redis
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api import auth, chat, image, translate
from backend.config.settings import get_settings
from backend.core.logging_utils import request_id_ctx_var, setup_logging
from backend.core.observability import setup_metrics, setup_tracing
from backend.db.session import create_database
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.security_headers import SecurityHeadersMiddleware

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger("backend.request")

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.time()
        request.state.request_id = request_id
        token = request_id_ctx_var.set(request_id)
        try:
            response = await call_next(request)
        except Exception:
            logging.exception("Unhandled exception")
            response = JSONResponse(status_code=500, content={
                "error": {"code": "internal_error", "message": "Internal Server Error"},
                "request_id": request_id,
            })
        finally:
            duration_ms = int((time.time() - start) * 1000)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(duration_ms)
            logger.info(
                "%s %s -> %s (%sms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            request_id_ctx_var.reset(token)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    redis_client = None
    if settings.redis_url:
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=False,
        )
        app.state.redis_client = redis_client
    try:
        yield
    finally:
        if redis_client:
            await redis_client.close()
        tracer_provider = getattr(app.state, "tracer_provider", None)
        if tracer_provider:
            tracer_provider.shutdown()


app = FastAPI(title="Z-GPT", debug=settings.app_debug, lifespan=lifespan)
app.state.tracer_provider = setup_tracing(app, settings)
setup_metrics(app, settings)

# CORS per env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request context
app.add_middleware(RequestContextMiddleware)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    limit_per_minute=settings.rate_limit_per_minute,
    window_seconds=settings.rate_limit_window_seconds,
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Health router
health = APIRouter()

@health.get("/healthz")
async def healthz():
    return {"status": "ok"}

@health.get("/readyz")
async def readyz():
    from backend.api.translate import _ARGOS_AVAILABLE  # local import to avoid circular deps

    details = {
        "env": settings.app_env,
        "translation": "available" if _ARGOS_AVAILABLE else "unavailable",
        "image_generation": "enabled" if settings.image_generation_enabled else "disabled",
        "rate_limit": settings.rate_limit_per_minute,
    }
    status = "ready" if details["translation"] == "available" else "degraded"
    return {"status": status, "details": details}

# Mounting APIs
app.include_router(health, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(image.router, prefix="/image", tags=["Image"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])


@app.get("/")
def root():
    return {"status": "Z-GPT Backend Running", "env": settings.app_env}
