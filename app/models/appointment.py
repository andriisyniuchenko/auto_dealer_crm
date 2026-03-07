from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.enums import AppointmentStatus


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    appointment_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default=AppointmentStatus.scheduled.value)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    lead = relationship("Lead")
    user = relationship("User")