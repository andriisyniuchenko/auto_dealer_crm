from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base

from app.models.enums import DealStatus


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    vehicle = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    status = Column(String, nullable=False, default=DealStatus.open.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    lead = relationship("Lead")