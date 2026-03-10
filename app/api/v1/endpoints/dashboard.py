from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def read_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("salesperson", "manager", "general_manager")),
):
    return get_dashboard_data(db, current_user)