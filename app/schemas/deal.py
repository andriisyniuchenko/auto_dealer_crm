from pydantic import BaseModel, field_validator
from datetime import datetime
from app.models.enums import DealStatus


class DealCreate(BaseModel):
    lead_id: int
    vehicle: str
    price: int

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class DealSalesperson(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class DealResponse(BaseModel):
    id: int
    lead_id: int
    vehicle: str
    price: int
    status: DealStatus
    created_at: datetime
    closed_at: datetime | None = None
    salespeople: list[DealSalesperson] = []

    class Config:
        from_attributes = True


class DealClose(BaseModel):
    status: DealStatus