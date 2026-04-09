from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.services.appointment_service import get_today_appointments


def get_dashboard_data(db: Session, current_user: User):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    today = now.date()

    if current_user.role.value in ["manager", "general_manager"]:
        active_leads = (
            db.query(Lead)
            .filter(Lead.status == LeadStatus.active.value)
            .count()
        )

        appointments_today = len(get_today_appointments(db, current_user))

        open_deals = (
            db.query(Deal)
            .filter(Deal.status == "open")
            .count()
        )

        sold_deals = (
            db.query(Deal)
            .filter(Deal.status == "sold")
            .count()
        )

        return {
            "active_leads": active_leads,
            "appointments_today": appointments_today,
            "open_deals": open_deals,
            "sold_deals": sold_deals,
        }

    active_leads = (
        db.query(Lead)
        .join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Lead.status == LeadStatus.active.value,
        )
        .count()
    )

    appointments_today = len(get_today_appointments(db, current_user))

    open_deals = (
        db.query(Deal)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Deal.status == "open",
        )
        .count()
    )

    # Single query: get all sold deals for this salesperson with salespeople count per lead
    sold_deals_rows = (
        db.query(Deal.id, Deal.lead_id, LeadSalesperson.user_id)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Deal.status == "sold",
        )
        .all()
    )

    lead_ids = [row.lead_id for row in sold_deals_rows]

    # Count salespeople per lead in one query
    from sqlalchemy import func
    counts = (
        db.query(LeadSalesperson.lead_id, func.count(LeadSalesperson.user_id).label("cnt"))
        .filter(LeadSalesperson.lead_id.in_(lead_ids))
        .group_by(LeadSalesperson.lead_id)
        .all()
    )
    salespeople_count_map = {row.lead_id: row.cnt for row in counts}

    sold_deals = sum(
        1 / salespeople_count_map.get(row.lead_id, 1)
        for row in sold_deals_rows
    )

    return {
        "active_leads": active_leads,
        "appointments_today": appointments_today,
        "open_deals": open_deals,
        "sold_deals": sold_deals,
    }