from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.lead_salesperson import LeadSalesperson
from app.models.enums import LeadStatus


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    phone = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)

    city = Column(String, nullable=True)
    state = Column(String, nullable=True)

    source = Column(String, nullable=True)

    interest = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    status = Column(String, nullable=False, default=LeadStatus.active.value)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_contacted_at = Column(DateTime, nullable=True)

    salespeople = relationship(
        "User",
        secondary=LeadSalesperson.__table__,
        back_populates="leads",
    )