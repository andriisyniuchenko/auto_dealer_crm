from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.appointment_service import (
    create_appointment,
    get_all_appointments,
    update_appointment,
)

router = APIRouter()


@router.get("/appointments-page")
def appointments_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointments = get_all_appointments(db, current_user)
    for appointment in appointments:
        appointment.lead_name = f"{appointment.lead.first_name} {appointment.lead.last_name}"

    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "appointments": appointments,
            "current_user": current_user,
        },
    )


@router.get("/appointments/create/{lead_id}")
def appointment_create_page(
    request: Request,
    lead_id: int,
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        "appointment_create.html",
        {
            "request": request,
            "lead_id": lead_id,
            "current_user": current_user,
        },
    )


@router.post("/appointments/create/{lead_id}")
def appointment_create(
    request: Request,
    lead_id: int,
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointment_datetime = datetime.fromisoformat(
        f"{appointment_date}T{appointment_time}"
    )

    appointment_data = AppointmentCreate(
        appointment_at=appointment_datetime,
        notes=notes,
        status="scheduled",
    )

    create_appointment(
        db=db,
        lead_id=lead_id,
        appointment_data=appointment_data,
        current_user=current_user,
    )

    return RedirectResponse(
        url=f"/api/v1/leads-page/{lead_id}",
        status_code=303,
    )


@router.post("/appointments-page/{lead_id}/{appointment_id}/update")
def update_appointment_page(
    lead_id: int,
    appointment_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointment_data = AppointmentUpdate(status=status)

    update_appointment(db, appointment_id, appointment_data, current_user)

    return RedirectResponse(
        url="/api/v1/appointments-page",
        status_code=303,
    )