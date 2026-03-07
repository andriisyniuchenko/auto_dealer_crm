from pydantic import BaseModel


class DealCreate(BaseModel):
    lead_id: int
    vehicle: str
    price: int


class DealResponse(BaseModel):
    id: int
    lead_id: int
    vehicle: str
    price: int
    status: str

    class Config:
        from_attributes = True