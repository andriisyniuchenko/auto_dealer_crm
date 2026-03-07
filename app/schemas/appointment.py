from datetime import datetime

from pydantic import BaseModel

from app.models.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    appointment_at: datetime
    status: AppointmentStatus = AppointmentStatus.scheduled


class AppointmentResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    appointment_at: datetime
    status: AppointmentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    status: AppointmentStatus