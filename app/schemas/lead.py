from pydantic import BaseModel


class LeadBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str | None = None
    city: str | None = None
    state: str | None = None
    source: str | None = None
    interest: str | None = None
    notes: str | None = None
    status: str = "active"


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: int

    class Config:
        from_attributes = True