from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.schemas.lead import LeadCreate, LeadUpdate
from app.models.user import User
from fastapi import HTTPException

from datetime import datetime, UTC


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


def update_lead(db: Session, lead_id: int, lead_data: LeadUpdate, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    update_data = lead_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    return lead


def get_stale_leads(db: Session, current_user: User):
    if current_user.role.value in ["manager", "general_manager"]:
        leads = (
            db.query(Lead)
            .order_by(Lead.last_contacted_at.asc(), Lead.created_at.desc())
            .all()
        )
    else:
        leads = (
            db.query(Lead)
            .join(LeadSalesperson)
            .filter(LeadSalesperson.user_id == current_user.id)
            .order_by(Lead.last_contacted_at.asc(), Lead.created_at.desc())
            .all()
        )

    result = []

    for lead in leads:
        if lead.last_contacted_at is None:
            days_since_contact = "Never contacted"
            last_contacted = "Never contacted"
        else:
            last_contacted = lead.last_contacted_at
            delta = datetime.now(UTC).date() - lead.last_contacted_at.date()
            days_since_contact = delta.days

        result.append({
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "phone": lead.phone,
            "email": lead.email,
            "city": lead.city,
            "state": lead.state,
            "source": lead.source,
            "interest": lead.interest,
            "notes": lead.notes,
            "status": lead.status,
            "last_contacted_at": last_contacted,
            "days_since_contact": days_since_contact,
        })

    return result


def remove_salesperson_from_lead(db: Session, lead_id: int, salesperson_id: int):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    link = (
        db.query(LeadSalesperson)
        .filter(
            LeadSalesperson.lead_id == lead_id,
            LeadSalesperson.user_id == salesperson_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Salesperson is not assigned to this lead")

    assigned_count = (
        db.query(LeadSalesperson)
        .filter(LeadSalesperson.lead_id == lead_id)
        .count()
    )

    if assigned_count <= 1:
        raise HTTPException(status_code=400, detail="Lead must have at least one salesperson")

    db.delete(link)
    db.commit()

    return {"message": "Salesperson removed from lead successfully"}