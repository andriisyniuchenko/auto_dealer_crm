from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

ROLE_RANK = {
    UserRole.general_manager.value: 3,
    UserRole.manager.value: 2,
    UserRole.finance_manager.value: 1,
    UserRole.salesperson.value: 0,
}


def list_users(db: Session):
    return (
        db.query(User)
        .order_by(User.role, User.first_name, User.last_name)
        .all()
    )


def can_manage_user(actor: User, target: User) -> bool:
    """Whether actor may change target's active status.

    A general_manager may manage anyone; a manager may manage only roles
    strictly below manager in the hierarchy. Nobody may manage themselves.
    """
    if actor.id == target.id:
        return False
    if actor.role.value == UserRole.general_manager.value:
        return True
    if actor.role.value == UserRole.manager.value:
        return ROLE_RANK[target.role.value] < ROLE_RANK[UserRole.manager.value]
    return False


def set_user_active(
    db: Session, user_id: int, is_active: bool, current_user: User
) -> User:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == target.id:
        raise HTTPException(status_code=400, detail="You cannot change your own status")

    if not can_manage_user(current_user, target):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to modify this user"
        )

    if not is_active and target.role.value == UserRole.general_manager.value:
        active_gm_count = (
            db.query(User)
            .filter(User.role == UserRole.general_manager, User.is_active == True)
            .count()
        )
        if active_gm_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate the last active general manager",
            )

    target.is_active = is_active
    db.commit()
    db.refresh(target)
    return target