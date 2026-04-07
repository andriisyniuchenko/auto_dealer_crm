from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()


@router.get("/dashboard-page")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    dashboard = get_dashboard_data(db, current_user)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "dashboard": dashboard,
            "current_user": current_user,
        },
    )