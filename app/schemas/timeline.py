from datetime import datetime

from pydantic import BaseModel


class TimelineItemResponse(BaseModel):
    type: str
    timestamp: datetime
    content: str
    user_id: int | None = None