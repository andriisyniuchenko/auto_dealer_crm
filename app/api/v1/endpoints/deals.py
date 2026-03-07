from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.deal import DealCreate, DealResponse
from app.services.deal_service import create_deal

router = APIRouter(
    prefix="/deals",
    tags=["Deals"]
)

@router.post("/", response_model=DealResponse)
def create_deal_endpoint(
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("salesperson", "manager", "general_manager")),
):
    return create_deal(db, deal, current_user)