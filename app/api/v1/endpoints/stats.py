from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import SalesStatResponse
from app.services.stats_service import get_sales_stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/sales", response_model=list[SalesStatResponse])
def read_sales_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    return get_sales_stats(db)