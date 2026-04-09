from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.user import User
from app.schemas.appointment import AppointmentCreate
from app.services.lead_service import get_lead_by_id

from fastapi import HTTPException
from app.schemas.appointment import AppointmentUpdate
from app.models.lead_salesperson import LeadSalesperson


def create_appointment(
    db: Session,
    lead_id: int,
    appointment_data: AppointmentCreate,
    current_user: User,
):
    lead = get_lead_by_id(db, lead_id, current_user)

    new_appointment = Appointment(
        lead_id=lead.id,
        user_id=current_user.id,
        appointment_at=appointment_data.appointment_at,
        status=appointment_data.status.value,
    )

    db.add(new_appointment)

    lead.last_contacted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(new_appointment)

    return new_appointment


def get_appointments_by_lead(
    db: Session, lead_id: int, current_user: User, page: int = 1, limit: int = 20
):
    lead = get_lead_by_id(db, lead_id, current_user)

    query = (
        db.query(Appointment)
        .filter(Appointment.lead_id == lead.id)
        .order_by(Appointment.appointment_at.desc())
    )

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": -(-total // limit),
        "limit": limit,
    }


def update_appointment(
    db: Session,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User,
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    is_manager = current_user.role.value in ["manager", "general_manager"]
    is_assigned = (
        db.query(LeadSalesperson)
        .filter(
            LeadSalesperson.lead_id == appointment.lead_id,
            LeadSalesperson.user_id == current_user.id,
        )
        .first()
    )

    if not is_manager and not is_assigned:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    appointment.status = appointment_data.status.value

    db.commit()
    db.refresh(appointment)

    return appointment


def get_today_appointments(db: Session, current_user: User):
    tz = ZoneInfo("America/Los_Angeles")

    now = datetime.now(tz)
    today = now.date()

    start = datetime.combine(today, time.min, tz)
    end = datetime.combine(today, time.max, tz)

    if current_user.role.value in ["manager", "general_manager"]:
        return (
            db.query(Appointment)
            .filter(
                Appointment.appointment_at >= start,
                Appointment.appointment_at <= end,
            )
            .order_by(Appointment.appointment_at.asc())
            .all()
        )

    return (
        db.query(Appointment)
        .join(LeadSalesperson, Appointment.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Appointment.appointment_at >= start,
            Appointment.appointment_at <= end,
        )
        .order_by(Appointment.appointment_at.asc())
        .all()
    )


def get_all_appointments(db: Session, current_user: User):
    if current_user.role.value in ["manager", "general_manager"]:
        return (
            db.query(Appointment)
            .order_by(Appointment.appointment_at.asc())
            .all()
        )

    return (
        db.query(Appointment)
        .join(LeadSalesperson, Appointment.lead_id == LeadSalesperson.lead_id)
        .filter(LeadSalesperson.user_id == current_user.id)
        .order_by(Appointment.appointment_at.asc())
        .all()
    )