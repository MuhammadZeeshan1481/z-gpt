from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import chat, image, translate

app = FastAPI(title="Z-GPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
