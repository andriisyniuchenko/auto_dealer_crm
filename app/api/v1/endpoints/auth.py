from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import create_user, login_user

from app.api.deps import get_current_active_user, require_roles
from app.models.user import User

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    return create_user(db, user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = login_user(db, form_data.username, form_data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return token

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/manager-only")
def manager_only(current_user: User = Depends(require_roles("manager", "general_manager"))):
    return {"message": f"Hello, {current_user.email}. You have manager access."}