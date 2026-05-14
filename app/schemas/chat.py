from datetime import datetime

from pydantic import BaseModel

from app.models.enums import MessageRole


class ChatMessageCreate(BaseModel):
    role: MessageRole
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    session_id: str
    lead_id: int | None = None
    messages: list[ChatMessageCreate]


class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    lead_id: int | None
    created_at: datetime
    messages: list[ChatMessageResponse]

    class Config:
        from_attributes = True