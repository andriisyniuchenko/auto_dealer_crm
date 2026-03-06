from enum import Enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.lead_salesperson import LeadSalesperson

class UserRole(str, Enum):
    general_manager = "general_manager"
    manager = "manager"
    finance_manager = "finance_manager"
    salesperson = "salesperson"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(SAEnum(UserRole, name="user_role"), nullable=False, index=True)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    leads = relationship(
        "Lead",
        secondary=LeadSalesperson.__table__,
        back_populates="salespeople",
    )