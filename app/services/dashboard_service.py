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

    sold_deals = 0.0
    sold_deals_query = (
        db.query(Deal)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Deal.status == "sold",
        )
        .all()
    )

    for deal in sold_deals_query:
        salespeople_count = (
            db.query(LeadSalesperson)
            .filter(LeadSalesperson.lead_id == deal.lead_id)
            .count()
        )

        if salespeople_count == 2:
            sold_deals += 0.5
        else:
            sold_deals += 1.0

    return {
        "active_leads": active_leads,
        "appointments_today": appointments_today,
        "open_deals": open_deals,
        "sold_deals": sold_deals,
    }