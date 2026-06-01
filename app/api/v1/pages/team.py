from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.core.permissions import Permission, has_permission
from app.db.session import get_db
from app.models.user import User
from app.services.user_service import can_manage_user, list_users, set_user_active

router = APIRouter()


@router.get("/team-page")
def team_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not has_permission(current_user, Permission.TEAM_MANAGE):
        return RedirectResponse(url="/api/v1/dashboard-page", status_code=303)

    users = list_users(db)
    for u in users:
        u.can_manage = can_manage_user(current_user, u)

    return templates.TemplateResponse(
        "team.html",
        {
            "request": request,
            "active_users": [u for u in users if u.is_active],
            "inactive_users": [u for u in users if not u.is_active],
            "current_user": current_user,
            "error": request.query_params.get("error"),
        },
    )


@router.post("/team-page/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not has_permission(current_user, Permission.TEAM_MANAGE):
        return RedirectResponse(url="/api/v1/dashboard-page", status_code=303)

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        return RedirectResponse(url="/api/v1/team-page", status_code=303)

    try:
        set_user_active(db, user_id, not target.is_active, current_user)
    except HTTPException as exc:
        return RedirectResponse(
            url=f"/api/v1/team-page?error={quote(exc.detail)}", status_code=303
        )

    return RedirectResponse(url="/api/v1/team-page", status_code=303)