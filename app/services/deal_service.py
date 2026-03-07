from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.schemas.deal import DealCreate


def create_deal(db: Session, deal: DealCreate, current_user: User):
    lead = db.query(Lead).filter(Lead.id == deal.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if current_user.role.value not in ["manager", "general_manager"]:
        link = (
            db.query(LeadSalesperson)
            .filter(
                LeadSalesperson.lead_id == deal.lead_id,
                LeadSalesperson.user_id == current_user.id,
            )
            .first()
        )
        if not link:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    existing_deal = db.query(Deal).filter(Deal.lead_id == deal.lead_id).first()
    if existing_deal:
        raise HTTPException(status_code=400, detail="Deal already exists for this lead")

    new_deal = Deal(
        lead_id=deal.lead_id,
        vehicle=deal.vehicle,
        price=deal.price,
    )

    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)

    return new_deal