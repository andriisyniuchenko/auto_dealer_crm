from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.schemas.deal import DealCreate, DealClose

from datetime import datetime



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


def close_deal(db: Session, deal_id: int, deal_data: DealClose, current_user: User):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

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

    if deal.status != "open":
        raise HTTPException(status_code=400, detail="Deal is already closed")

    if deal_data.status.value not in ["sold", "lost", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid close status")

    deal.status = deal_data.status.value
    deal.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(deal)

    return deal


def get_deals(db: Session, current_user: User):

    if current_user.role.value in ["manager", "general_manager"]:
        return db.query(Deal).all()

    return (
        db.query(Deal)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == current_user.id)
        .all()
    )


def get_deal_by_id(db: Session, deal_id: int, current_user: User):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if current_user.role.value in ["manager", "general_manager"]:
        return deal

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

    salespeople = (
        db.query(User)
        .join(LeadSalesperson, User.id == LeadSalesperson.user_id)
        .filter(LeadSalesperson.lead_id == deal.lead_id)
        .all()
    )

    deal.salespeople = salespeople
    return deal