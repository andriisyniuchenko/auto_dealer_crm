from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True