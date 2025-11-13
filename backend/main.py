from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import chat, image, translate
from backend.config import settings

app = FastAPI(title="Z-GPT", debug=settings.DEBUG)

# Configure CORS with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting APIs
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(image.router, prefix="/image", tags=["Image"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])


@app.get("/")
def root():
    return {"status": "Z-GPT Backend Running"}
