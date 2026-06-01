from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserStatusUpdate
from app.services.user_service import list_users, set_user_active

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_VIEW)),
):
    return list_users(db)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TEAM_MANAGE)),
):
    return set_user_active(db, user_id, data.is_active, current_user)