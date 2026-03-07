from pydantic import BaseModel


class SalesStatResponse(BaseModel):
    user_id: int
    email: str
    sold_count: float