from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.deal import Deal
from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.models.user import User
from app.services.appointment_service import get_today_appointments
from app.services.lead_service import get_stale_leads


def get_dashboard_data(db: Session, current_user: User):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    today = now.date()

    if current_user.role.value in ["manager", "general_manager"]:
        total_leads = db.query(Lead).count()
        active_leads = db.query(Lead).filter(Lead.status == LeadStatus.active.value).count()
        stale_leads = len(get_stale_leads(db, current_user))
        appointments_today = len(get_today_appointments(db, current_user))
        open_deals = db.query(Deal).filter(Deal.status == "open").count()
        sold_deals = db.query(Deal).filter(Deal.status == "sold").count()

        return {
            "total_leads": total_leads,
            "active_leads": active_leads,
            "stale_leads": stale_leads,
            "appointments_today": appointments_today,
            "open_deals": open_deals,
            "sold_deals": sold_deals,
        }

    # salesperson dashboard
    from app.models.lead_salesperson import LeadSalesperson

    total_leads = (
        db.query(Lead)
        .join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == current_user.id)
        .count()
    )

    active_leads = (
        db.query(Lead)
        .join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Lead.status == LeadStatus.active.value,
        )
        .count()
    )

    stale_leads = len(get_stale_leads(db, current_user))
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

    sold_deals = (
        db.query(Deal)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Deal.status == "sold",
        )
        .count()
    )

    return {
        "total_leads": total_leads,
        "active_leads": active_leads,
        "stale_leads": stale_leads,
        "appointments_today": appointments_today,
        "open_deals": open_deals,
        "sold_deals": sold_deals,
    }