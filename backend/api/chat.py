import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session

from backend.core.llm_handler import generate_reply, stream_reply
from backend.core.moderation import ModerationError, enforce_safe_prompt
from backend.core.dependencies import get_current_user
from backend.db import crud
from backend.db.session import get_session
from backend.utils.language_tools import detect_language, translate_text
from backend.db.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    history: List[Message] = []  # maintained for backward compatibility
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    detected_lang: str
    session_id: str


class ChatSessionSummary(BaseModel):
    id: str
    title: Optional[str]
    updated_at: datetime
    last_message_preview: Optional[str]


class ChatMessageResponse(BaseModel):
    id: Optional[int]
    role: str
    content: str
    created_at: datetime


class ChatSessionDetail(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse]

@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    http_request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        enforce_safe_prompt(request.message)
        detected_lang = detect_language(request.message)
        input_text = (
            translate_text(request.message, from_lang=detected_lang, to_lang="en")
            if detected_lang != "en"
            else request.message
        )

        history = _load_history(db, request.session_id, current_user.id) if request.session_id else (request.history or [])
        session_entry = crud.upsert_session(db, request.session_id, request.message[:60], current_user.id)
        crud.record_message(db, session_entry, "user", request.message)

        reply_en = generate_reply(input_text, history)
        final_reply = (
            translate_text(reply_en, from_lang="en", to_lang=detected_lang)
            if detected_lang != "en"
            else reply_en
        )

        crud.record_message(db, session_entry, "assistant", final_reply.strip())

        return ChatResponse(
            response=final_reply.strip(),
            detected_lang=detected_lang,
            session_id=session_entry.id,
        )

    except ModerationError as exc:
        raise HTTPException(status_code=400, detail={
            "code": "prompt_rejected",
            "message": str(exc),
            "category": exc.category,
            "request_id": getattr(http_request.state, "request_id", None),
        }) from exc
    except Exception as exc:  # pragma: no cover - surfaced via detailed HTTP response
        logger.exception("Chat endpoint failed", extra={"session_id": request.session_id})
        raise HTTPException(status_code=500, detail={
            "code": "llm_processing_failed",
            "message": "LLM processing failed",
            "request_id": getattr(http_request.state, "request_id", None),
        }) from exc


@router.post("/stream")
def chat_stream(
    request: ChatRequest,
    http_request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        enforce_safe_prompt(request.message)
        detected_lang = detect_language(request.message)
        input_text = (
            translate_text(request.message, from_lang=detected_lang, to_lang="en")
            if detected_lang != "en"
            else request.message
        )
        history = _load_history(db, request.session_id, current_user.id) if request.session_id else (request.history or [])
        session_entry = crud.upsert_session(db, request.session_id, request.message[:60], current_user.id)
        crud.record_message(db, session_entry, "user", request.message)
        accumulated: List[str] = []

        def sse_events():
            try:
                # stream English reply first
                for chunk in stream_reply(input_text, history):
                    accumulated.append(chunk)
                    yield f"event: message\ndata: {chunk}\n\n"
            except Exception:
                yield "event: error\ndata: {\"message\": \"stream_failed\"}\n\n"
                return

            final_text_en = "".join(accumulated).strip()
            final_reply = (
                translate_text(final_text_en, from_lang="en", to_lang=detected_lang)
                if detected_lang != "en"
                else final_text_en
            )
            if final_reply:
                crud.record_message(db, session_entry, "assistant", final_reply)
            payload = json.dumps({
                "session_id": session_entry.id,
                "detected_lang": detected_lang,
                "final_text": final_reply,
            })
            yield f"event: done\ndata: {payload}\n\n"

        return StreamingResponse(sse_events(), media_type="text/event-stream")

    except ModerationError as exc:
        raise HTTPException(status_code=400, detail={
            "code": "prompt_rejected",
            "message": str(exc),
            "category": exc.category,
            "request_id": getattr(http_request.state, "request_id", None),
        }) from exc
    except Exception as exc:  # pragma: no cover - surfaced via detailed HTTP response
        logger.exception("Chat stream endpoint failed", extra={"session_id": request.session_id})
        raise HTTPException(status_code=500, detail={
            "code": "llm_stream_failed",
            "message": "Streaming failed",
            "request_id": getattr(http_request.state, "request_id", None),
        }) from exc


@router.get("/sessions", response_model=List[ChatSessionSummary])
def list_chat_sessions(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[ChatSessionSummary]:
    sessions = crud.list_sessions(db, current_user.id)
    summaries = []
    for s in sessions:
        last_message = s.messages[-1].content if s.messages else None
        preview = (last_message[:80] + "…") if last_message and len(last_message) > 80 else last_message
        summaries.append(ChatSessionSummary(
            id=s.id,
            title=s.title,
            updated_at=s.updated_at,
            last_message_preview=preview,
        ))
    return summaries


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_chat_session(
    session_id: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ChatSessionDetail:
    session_obj = crud.get_session_with_messages(db, session_id, current_user.id)
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = [
        ChatMessageResponse(id=m.id, role=m.role, content=m.content, created_at=m.created_at)
        for m in sorted(session_obj.messages, key=lambda msg: msg.created_at)
    ]
    return ChatSessionDetail(
        id=session_obj.id,
        title=session_obj.title,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=messages,
    )


@router.delete("/sessions/{session_id}", status_code=204)
def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    deleted = crud.delete_session(db, session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")


def _load_history(db: Session, session_id: Optional[str], user_id: str) -> List[dict]:
    if not session_id:
        return []
    session_obj = crud.get_session_with_messages(db, session_id, user_id)
    if not session_obj:
        return []
    messages = session_obj.messages
    recent = messages[-8:]
    return [{"role": m.role, "content": m.content} for m in recent]
