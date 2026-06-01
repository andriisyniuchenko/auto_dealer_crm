from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def read_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DASHBOARD_VIEW)),
):
    return get_dashboard_data(db, current_user)