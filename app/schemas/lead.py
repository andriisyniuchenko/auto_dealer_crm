import re
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from app.models.enums import LeadStatus
from datetime import datetime


class LeadBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None = None
    city: str | None = None
    state: str | None = None
    source: str | None = None
    interest: str | None = None
    notes: str | None = None
    status: LeadStatus = LeadStatus.active

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone must contain between 7 and 15 digits")
        return v


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: int

    class Config:
        from_attributes = True


class LeadAssign(BaseModel):
    salesperson_id: int


class LeadUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    city: str | None = None
    state: str | None = None
    source: str | None = None
    interest: str | None = None
    notes: str | None = None
    status: LeadStatus | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone must contain between 7 and 15 digits")
        return v

class StaleLeadResponse(LeadResponse):
    last_contacted_at: datetime | str
    days_since_contact: int | str