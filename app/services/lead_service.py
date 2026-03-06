from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.schemas.lead import LeadCreate
from app.models.user import User


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
        return db.query(Lead).all()

    return (
        db.query(Lead)
        .join(LeadSalesperson)
        .filter(LeadSalesperson.user_id == current_user.id)
        .all()
    )