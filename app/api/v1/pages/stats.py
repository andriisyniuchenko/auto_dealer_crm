from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.services.stats_service import get_sales_stats

router = APIRouter()


@router.get("/stats-page")
def stats_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    if current_user.role.value not in ("manager", "general_manager"):
        return RedirectResponse(url="/api/v1/dashboard-page", status_code=303)

    stats = get_sales_stats(db)
    stats.sort(key=lambda x: x["sold_count"], reverse=True)

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "stats": stats,
            "current_user": current_user,
        },
    )