from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.lead import LeadCreate, LeadResponse, LeadAssign, LeadUpdate, StaleLeadResponse
from app.services.lead_service import create_lead, get_leads, assign_salesperson_to_lead, get_lead_by_id, update_lead, \
    get_stale_leads, remove_salesperson_from_lead
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.timeline import TimelineItemResponse
from app.services.timeline_service import get_lead_timeline

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadResponse)
def create_new_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return create_lead(db, lead, current_user.id)


@router.get("/", response_model=list[LeadResponse])
def read_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_leads(db, current_user)


@router.post("/{lead_id}/assign")
def assign_salesperson(
    lead_id: int,
    data: LeadAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    return assign_salesperson_to_lead(db, lead_id, data.salesperson_id)


@router.get("/stale", response_model=list[StaleLeadResponse])
def read_stale_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_stale_leads(db, current_user)


@router.get("/{lead_id}/timeline", response_model=list[TimelineItemResponse])
def read_lead_timeline(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_lead_timeline(db, lead_id, current_user)

@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead_by_id(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_lead_by_id(db, lead_id, current_user)


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_existing_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return update_lead(db, lead_id, lead_data, current_user)


@router.delete("/{lead_id}/salespeople/{salesperson_id}")
def remove_salesperson(
    lead_id: int,
    salesperson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    return remove_salesperson_from_lead(db, lead_id, salesperson_id)