from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate):
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)

    if not user:
        return None

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}