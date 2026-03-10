from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import login_user
from app.services.dashboard_service import get_dashboard_data
from app.services.lead_service import get_leads
from app.services.lead_service import get_lead_by_id
from app.services.timeline_service import get_lead_timeline

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/login-page")
def login_page(request: Request):

    token = request.cookies.get("access_token")

    if token:
        return RedirectResponse(url="/api/v1/dashboard-page")

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None,
            "current_user": None,
        },
    )


@router.post("/login-page")
def login_page_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    token = login_user(db, username, password)

    if not token:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password",
            },
            status_code=401,
        )

    response = RedirectResponse(
        url="/api/v1/dashboard-page",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token['access_token']}",
        httponly=True,
    )
    return response


@router.get("/dashboard-page")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    dashboard = get_dashboard_data(db, current_user)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "dashboard": dashboard,
            "current_user": current_user,
        },
    )


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/api/v1/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/leads-page")
def leads_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    leads = get_leads(db, current_user)

    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "leads": leads,
            "current_user": current_user,
        },
    )

@router.get("/leads-page/{lead_id}")
def lead_detail_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lead = get_lead_by_id(db, lead_id, current_user)
    timeline = get_lead_timeline(db, lead_id, current_user)

    return templates.TemplateResponse(
        "lead_detail.html",
        {
            "request": request,
            "lead": lead,
            "timeline": timeline,
            "current_user": current_user,
        },
    )