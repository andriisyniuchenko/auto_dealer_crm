from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.deal import DealCreate, DealResponse, DealClose
from app.services.deal_service import create_deal, close_deal, get_deals

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


@router.patch("/{deal_id}/close", response_model=DealResponse)
def close_deal_endpoint(
    deal_id: int,
    deal_data: DealClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("salesperson", "manager", "general_manager")),
):
    return close_deal(db, deal_id, deal_data, current_user)


@router.get("/my", response_model=list[DealResponse])
def get_my_deals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("salesperson", "manager", "general_manager")),
):
    return get_deals(db, current_user)