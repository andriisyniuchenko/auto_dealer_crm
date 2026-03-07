from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.services.appointment_service import create_appointment, get_appointments_by_lead, update_appointment

router = APIRouter(prefix="/leads/{lead_id}/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse)
def create_lead_appointment(
    lead_id: int,
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return create_appointment(db, lead_id, appointment_data, current_user)


@router.get("/", response_model=list[AppointmentResponse])
def read_lead_appointments(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_appointments_by_lead(db, lead_id, current_user)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_lead_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return update_appointment(db, appointment_id, appointment_data, current_user)