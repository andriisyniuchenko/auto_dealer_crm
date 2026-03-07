from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.schemas.lead import LeadCreate
from app.models.user import User
from fastapi import HTTPException


def create_lead(db: Session, lead: LeadCreate, user_id: int):
    new_lead = Lead(
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone=lead.phone,
        email=lead.email,
        city=lead.city,
        state=lead.state,
        source=lead.source,
        interest=lead.interest,
        notes=lead.notes,
        status=lead.status,
    )

    db.add(new_lead)
    db.flush()

    lead_user_link = LeadSalesperson(
        lead_id=new_lead.id,
        user_id=user_id,
    )

    db.add(lead_user_link)
    db.commit()
    db.refresh(new_lead)

    return new_lead

def get_leads(db: Session, current_user: User):
    if current_user.role.value in ["manager", "general_manager"]:
        return db.query(Lead).order_by(Lead.created_at.desc()).all()

    return (
        db.query(Lead)
        .join(LeadSalesperson)
        .filter(LeadSalesperson.user_id == current_user.id)
        .order_by(Lead.created_at.desc())
        .all()
    )


def assign_salesperson_to_lead(db: Session, lead_id: int, salesperson_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    salesperson = db.query(User).filter(User.id == salesperson_id).first()
    if not salesperson:
        raise HTTPException(status_code=404, detail="User not found")

    if salesperson.role.value != "salesperson":
        raise HTTPException(status_code=400, detail="User is not a salesperson")

    existing_link = (
        db.query(LeadSalesperson)
        .filter(
            LeadSalesperson.lead_id == lead_id,
            LeadSalesperson.user_id == salesperson_id,
        )
        .first()
    )
    if existing_link:
        raise HTTPException(status_code=400, detail="Salesperson already assigned to this lead")

    assigned_count = (
        db.query(LeadSalesperson)
        .filter(LeadSalesperson.lead_id == lead_id)
        .count()
    )
    if assigned_count >= 2:
        raise HTTPException(status_code=400, detail="Lead cannot have more than 2 salespeople")

    new_link = LeadSalesperson(
        lead_id=lead_id,
        user_id=salesperson_id,
    )

    db.add(new_link)
    db.commit()

    return {"message": "Salesperson assigned successfully"}


def get_lead_by_id(db: Session, lead_id: int, current_user: User):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if current_user.role.value in ["manager", "general_manager"]:
        return lead

    lead_link = (
        db.query(LeadSalesperson)
        .filter(
            LeadSalesperson.lead_id == lead_id,
            LeadSalesperson.user_id == current_user.id,
        )
        .first()
    )

    if not lead_link:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return lead