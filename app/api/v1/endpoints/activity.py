from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.activity_service import create_activity, get_activities_by_lead

router = APIRouter(prefix="/leads/{lead_id}/activities", tags=["activities"])


@router.post("/", response_model=ActivityResponse)
def create_lead_activity(
    lead_id: int,
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return create_activity(db, lead_id, activity_data, current_user)


@router.get("/", response_model=list[ActivityResponse])
def read_lead_activities(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_activities_by_lead(db, lead_id, current_user)