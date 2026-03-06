from sqlalchemy import Column, ForeignKey, Integer
from app.db.session import Base


class LeadSalesperson(Base):
    __tablename__ = "lead_salespeople"

    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)