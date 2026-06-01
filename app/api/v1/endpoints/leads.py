import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadPublicCreate, LeadResponse, LeadAssign, LeadUpdate, StaleLeadResponse
from app.schemas.appointment import AppointmentPublicCreate
from app.models.appointment import Appointment
from app.schemas.pagination import PaginatedResponse
from app.services.lead_service import create_lead, get_leads, assign_salesperson_to_lead, get_lead_by_id, update_lead, \
    get_stale_leads, remove_salesperson_from_lead
from app.api.deps import require_permission
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.timeline import TimelineItemResponse
from app.services.timeline_service import get_lead_timeline

router = APIRouter(prefix="/leads", tags=["leads"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/public")
@limiter.limit("10/minute")
def create_public_lead(
    request: Request,
    lead: LeadPublicCreate,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None),
):
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.WEBSITE_API_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")

    new_lead = Lead(
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone=lead.phone,
        source=lead.source,
        interest=lead.interest,
        email=lead.email,
        notes=lead.notes,
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {"ok": True, "lead_id": new_lead.id}


@router.post("/public/appointments")
@limiter.limit("10/minute")
def create_public_appointment(
    request: Request,
    data: AppointmentPublicCreate,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None),
):
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.WEBSITE_API_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")

    lead = db.get(Lead, data.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    appointment = Appointment(
        lead_id=data.lead_id,
        appointment_at=data.appointment_at,
    )
    db.add(appointment)

    if data.notes:
        lead.notes = (lead.notes + "\n" + data.notes) if lead.notes else data.notes

    db.commit()
    db.refresh(appointment)

    return {"ok": True, "appointment_id": appointment.id}


@router.post("/", response_model=LeadResponse)
def create_new_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_CREATE)),
):
    return create_lead(db, lead, current_user.id)


@router.get("/", response_model=PaginatedResponse[LeadResponse])
def read_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_VIEW)),
):
    return get_leads(db, current_user, page=page, limit=limit, status=status, search=search)


@router.post("/{lead_id}/assign")
def assign_salesperson(
    lead_id: int,
    data: LeadAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_ASSIGN)),
):
    return assign_salesperson_to_lead(db, lead_id, data.salesperson_id)


@router.get("/stale", response_model=list[StaleLeadResponse])
def read_stale_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_VIEW)),
):
    return get_stale_leads(db, current_user)


@router.get("/{lead_id}/timeline", response_model=list[TimelineItemResponse])
def read_lead_timeline(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_VIEW)),
):
    return get_lead_timeline(db, lead_id, current_user)

@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead_by_id(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_VIEW)),
):
    return get_lead_by_id(db, lead_id, current_user)


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_existing_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_UPDATE)),
):
    return update_lead(db, lead_id, lead_data, current_user)


@router.delete("/{lead_id}/salespeople/{salesperson_id}")
def remove_salesperson(
    lead_id: int,
    salesperson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.LEAD_ASSIGN)),
):
    return remove_salesperson_from_lead(db, lead_id, salesperson_id)