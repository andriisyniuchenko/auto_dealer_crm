from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _verify_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != settings.WEBSITE_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
    _: None = Depends(_verify_api_key),
):
    session = db.query(ChatSession).filter(ChatSession.session_id == data.session_id).first()

    if session:
        db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
        if data.lead_id is not None:
            session.lead_id = data.lead_id
    else:
        session = ChatSession(
            session_id=data.session_id,
            lead_id=data.lead_id,
        )
        db.add(session)
        db.flush()

    for msg in data.messages:
        db.add(ChatMessage(
            session_id=session.id,
            role=msg.role,
            content=msg.content,
        ))

    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(_verify_api_key),
):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session