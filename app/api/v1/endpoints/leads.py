from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.lead import LeadCreate, LeadResponse, LeadAssign
from app.services.lead_service import create_lead, get_leads, assign_salesperson_to_lead, get_lead_by_id
from app.api.deps import require_roles
from app.models.user import User

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


@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead_by_id(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_lead_by_id(db, lead_id, current_user)