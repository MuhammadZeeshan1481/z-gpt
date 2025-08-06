from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.core.llm_handler import generate_reply
from backend.utils.language_tools import detect_language, translate_text

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    detected_lang: str

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        detected_lang = detect_language(request.message)
        input_text = (
            translate_text(request.message, from_lang=detected_lang, to_lang="en")
            if detected_lang != "en"
            else request.message
        )

        reply_en = generate_reply(input_text, request.history or [])
        final_reply = (
            translate_text(reply_en, from_lang="en", to_lang=detected_lang)
            if detected_lang != "en"
            else reply_en
        )

        return ChatResponse(response=final_reply.strip(), detected_lang=detected_lang)

    except Exception as e:
        raise HTTPException(status_code=500, detail="LLM processing failed")
