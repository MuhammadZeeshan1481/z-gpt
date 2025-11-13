from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.api import chat, image, translate
from backend.config.settings import ALLOWED_ORIGINS, DEBUG, REQUIRE_API_KEY
from backend.middleware.auth import verify_api_key, api_key_header, list_api_keys
from backend.middleware.rate_limit import rate_limit_middleware, get_rate_limit_stats
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Z-GPT API",
    description="AI Assistant with Chat, Image Generation, and Translation",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Request timing and rate limiting middleware
@app.middleware("http")
async def add_process_time_and_rate_limit_header(request: Request, call_next):
    start_time = time.time()
    
    # Add rate limit headers if available
    if hasattr(request.state, 'rate_limit_info'):
        rate_info = request.state.rate_limit_info
    else:
        rate_info = None
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    # Add rate limit headers if available
    if rate_info:
        response.headers["X-RateLimit-Limit"] = str(rate_info['limit'])
        response.headers["X-RateLimit-Remaining"] = str(rate_info['remaining'])
        response.headers["X-RateLimit-Reset"] = str(rate_info['reset_in_seconds'])
    
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."},
    )

# Mounting APIs
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(image.router, prefix="/image", tags=["Image"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - Health check"""
    return {
        "status": "healthy",
        "service": "Z-GPT Backend",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "Z-GPT Backend",
        "version": "1.0.0",
        "timestamp": time.time(),
        "auth_required": REQUIRE_API_KEY
    }

@app.get("/admin/keys", tags=["Admin"])
async def list_keys(api_key: str = Depends(api_key_header)):
    """List all API keys (admin only)"""
    key_info = await verify_api_key(api_key)
    
    # Only enterprise tier can list keys
    if key_info['tier'] != 'enterprise':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only enterprise tier can access this endpoint"
        )
    
    return {
        "api_keys": list_api_keys()
    }

@app.get("/admin/stats", tags=["Admin"])
async def get_stats(api_key: str = Depends(api_key_header)):
    """Get API usage statistics (admin only)"""
    key_info = await verify_api_key(api_key)
    
    # Only enterprise tier can view stats
    if key_info['tier'] != 'enterprise':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only enterprise tier can access this endpoint"
        )
    
    return {
        "rate_limit_stats": get_rate_limit_stats(),
        "timestamp": time.time()
    }
