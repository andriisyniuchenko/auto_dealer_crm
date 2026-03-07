from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ActivityType


class ActivityCreate(BaseModel):
    type: ActivityType
    content: str | None = None


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    type: ActivityType
    content: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True