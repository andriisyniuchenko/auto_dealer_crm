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


class LeadAssign(BaseModel):
    salesperson_id: int


class LeadUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    city: str | None = None
    state: str | None = None
    source: str | None = None
    interest: str | None = None
    notes: str | None = None
    status: str | None = None
