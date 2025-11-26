from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, select

from backend.db.models import ChatMessage, ChatSession, User


def get_user(session: Session, user_id: str) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, *, email: str, full_name: Optional[str], hashed_password: str) -> User:
    user = User(email=email, full_name=full_name, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def upsert_session(session: Session, session_id: Optional[str], title: Optional[str], user_id: str) -> ChatSession:
    db_session: Optional[ChatSession] = None
    if session_id:
        db_session = session.get(ChatSession, session_id)
        if db_session and db_session.user_id != user_id:
            db_session = None
    if not db_session:
        db_session = ChatSession(title=title, user_id=user_id)
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
    else:
        if title and not db_session.title:
            db_session.title = title
        db_session.updated_at = datetime.now(timezone.utc)
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
    return db_session


def record_message(
    session_db: Session,
    session_obj: ChatSession,
    role: str,
    content: str,
) -> ChatMessage:
    message = ChatMessage(session_id=session_obj.id, role=role, content=content)
    session_db.add(message)
    session_db.commit()
    session_db.refresh(message)
    session_obj.updated_at = datetime.now(timezone.utc)
    session_db.add(session_obj)
    session_db.commit()
    return message


def list_sessions(session_db: Session, user_id: str) -> List[ChatSession]:
    statement = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
    )
    return list(session_db.exec(statement).all())


def get_session_with_messages(session_db: Session, session_id: str, user_id: str) -> Optional[ChatSession]:
    session_obj = session_db.get(ChatSession, session_id)
    if session_obj and session_obj.user_id != user_id:
        return None
    if session_obj:
        session_obj.messages  # force lazy load
    return session_obj


def list_messages(session_db: Session, session_id: str) -> List[ChatMessage]:
    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(session_db.exec(statement).all())


def delete_session(session_db: Session, session_id: str, user_id: str) -> bool:
    session_obj = session_db.get(ChatSession, session_id)
    if session_obj and session_obj.user_id != user_id:
        return False
    if not session_obj:
        return False
    session_db.delete(session_obj)
    session_db.commit()
    return True
