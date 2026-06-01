from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.core.permissions import Permission, has_permission
from app.db.session import get_db
from app.models.appointment import Appointment
from app.models.deal import Deal
from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User

router = APIRouter()


@router.get("/salesperson-page/{user_id}")
def salesperson_detail_page(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not has_permission(current_user, Permission.USER_VIEW):
        return RedirectResponse(url="/api/v1/dashboard-page", status_code=303)

    salesperson = db.query(User).filter(User.id == user_id).first()
    if not salesperson:
        return RedirectResponse(url="/api/v1/stats-page", status_code=303)

    leads = (
        db.query(Lead)
        .join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == user_id)
        .order_by(Lead.created_at.desc())
        .all()
    )

    appointments = (
        db.query(Appointment)
        .join(LeadSalesperson, Appointment.lead_id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == user_id)
        .order_by(Appointment.appointment_at.desc())
        .all()
    )

    # attach lead name to each appointment
    lead_map = {lead.id: lead for lead in leads}
    for appt in appointments:
        lead = lead_map.get(appt.lead_id)
        appt.lead_name = f"{lead.first_name} {lead.last_name}" if lead else f"Lead #{appt.lead_id}"

    deals = (
        db.query(Deal)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == user_id)
        .order_by(Deal.created_at.desc())
        .all()
    )

    # attach lead name to each deal
    for deal in deals:
        lead = lead_map.get(deal.lead_id)
        deal.lead_name = f"{lead.first_name} {lead.last_name}" if lead else f"Lead #{deal.lead_id}"

    active_leads = sum(1 for l in leads if l.status == "active")
    sold_deals = sum(1 for d in deals if d.status == "sold")

    return templates.TemplateResponse(
        "salesperson_detail.html",
        {
            "request": request,
            "sp": salesperson,
            "leads": leads,
            "appointments": appointments,
            "deals": deals,
            "active_leads": active_leads,
            "sold_deals": sold_deals,
            "current_user": current_user,
        },
    )