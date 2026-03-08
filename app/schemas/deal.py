from pydantic import BaseModel
from datetime import datetime
from app.models.enums import DealStatus


class DealCreate(BaseModel):
    lead_id: int
    vehicle: str
    price: int


class DealResponse(BaseModel):
    id: int
    lead_id: int
    vehicle: str
    price: int
    status: DealStatus
    created_at: datetime
    closed_at: datetime | None = None
    salespeople: list[DealSalesperson]

    class Config:
        from_attributes = True


class DealClose(BaseModel):
    status: DealStatus


class DealSalesperson(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True