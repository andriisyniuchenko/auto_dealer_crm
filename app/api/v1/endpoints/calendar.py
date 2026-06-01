from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.appointment import AppointmentResponse
from app.services.appointment_service import get_today_appointments

router = APIRouter(prefix="/appointments", tags=["calendar"])


@router.get("/today", response_model=list[AppointmentResponse])
def read_today_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.APPOINTMENT_VIEW)),
):
    return get_today_appointments(db, current_user)