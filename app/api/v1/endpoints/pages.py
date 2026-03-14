from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.config import settings
from app.db.session import get_db
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.schemas.deal import DealClose, DealCreate
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.appointment_service import (
    create_appointment,
    get_all_appointments,
    update_appointment,
)
from app.services.auth_service import login_user
from app.services.dashboard_service import get_dashboard_data
from app.services.deal_service import close_deal, create_deal, get_deals
from app.services.lead_service import (
    assign_salesperson_to_lead,
    create_lead,
    get_lead_by_id,
    get_leads_with_salespeople,
    remove_salesperson_from_lead,
    update_lead,
)
from app.services.timeline_service import get_lead_timeline
from app.services.activity_service import create_activity


router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def get_current_web_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get("access_token")

    def redirect_to_login():
        response = RedirectResponse(
            url="/api/v1/login-page",
            status_code=303,
        )
        response.delete_cookie("access_token")
        return response

    if not token:
        return redirect_to_login()

    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email = payload.get("sub")

        if not email:
            return redirect_to_login()

    except JWTError:
        return redirect_to_login()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return redirect_to_login()

    return user


@router.get("/login-page")
def login_page(request: Request):
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
                "current_user": None,
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


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/api/v1/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response


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


@router.get("/leads-page")
def leads_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    leads = get_leads_with_salespeople(db, current_user)

    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "leads": leads,
            "current_user": current_user,
        },
    )


@router.get("/leads-page/create")
def create_lead_page(
    request: Request,
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        "lead_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("/leads-page/create")
def create_lead_page_post(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    source: str = Form(None),
    interest: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead_data = LeadCreate(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        city=city,
        state=state,
        source=source,
        interest=interest,
        notes=notes,
    )

    create_lead(db, lead_data, current_user.id)

    return RedirectResponse(url="/api/v1/leads-page", status_code=302)


@router.get("/leads-page/{lead_id}")
def lead_detail_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)
    timeline = get_lead_timeline(db, lead_id, current_user)

    salespeople = [user.email for user in lead.salespeople]

    assigned_salespeople = (
        db.query(User)
        .join(LeadSalesperson, User.id == LeadSalesperson.user_id)
        .filter(LeadSalesperson.lead_id == lead.id)
        .all()
    )

    all_salespeople = (
        db.query(User)
        .filter(User.role == "salesperson")
        .all()
    )

    return templates.TemplateResponse(
        "lead_detail.html",
        {
            "request": request,
            "lead": lead,
            "timeline": timeline,
            "salespeople": salespeople,
            "assigned_salespeople": assigned_salespeople,
            "all_salespeople": all_salespeople,
            "current_user": current_user,
        },
    )


@router.get("/appointments-page")
def appointments_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointments = get_all_appointments(db, current_user)
    for appointment in appointments:
        appointment.lead_name = f"{appointment.lead.first_name} {appointment.lead.last_name}"

    return templates.TemplateResponse(
        "appointments.html",
        {
            "request": request,
            "appointments": appointments,
            "current_user": current_user,
        },
    )


@router.get("/deals-page")
def deals_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    deals = get_deals(db, current_user)

    return templates.TemplateResponse(
        "deals.html",
        {
            "request": request,
            "deals": deals,
            "current_user": current_user,
        },
    )


@router.get("/appointments/create/{lead_id}")
def appointment_create_page(
    request: Request,
    lead_id: int,
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    return templates.TemplateResponse(
        "appointment_create.html",
        {
            "request": request,
            "lead_id": lead_id,
            "current_user": current_user,
        },
    )


@router.post("/appointments/create/{lead_id}")
def appointment_create(
    request: Request,
    lead_id: int,
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointment_datetime = datetime.fromisoformat(
        f"{appointment_date}T{appointment_time}"
    )

    appointment_data = AppointmentCreate(
        appointment_at=appointment_datetime,
        notes=notes,
        status="scheduled",
    )

    create_appointment(
        db=db,
        lead_id=lead_id,
        appointment_data=appointment_data,
        current_user=current_user,
    )

    return RedirectResponse(
        url=f"/api/v1/leads-page/{lead_id}",
        status_code=303,
    )


@router.post("/leads-page/{lead_id}/assign-salesperson")
def assign_salesperson_page(
    request: Request,
    lead_id: int,
    salesperson_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    try:
        assign_salesperson_to_lead(db, lead_id, salesperson_id)

        return RedirectResponse(
            url=f"/api/v1/leads-page/{lead_id}",
            status_code=303,
        )

    except HTTPException as e:
        lead = get_lead_by_id(db, lead_id, current_user)
        timeline = get_lead_timeline(db, lead_id, current_user)

        salespeople = [user.email for user in lead.salespeople]

        assigned_salespeople = (
            db.query(User)
            .join(LeadSalesperson, User.id == LeadSalesperson.user_id)
            .filter(LeadSalesperson.lead_id == lead.id)
            .all()
        )

        all_salespeople = (
            db.query(User)
            .filter(User.role == "salesperson")
            .all()
        )

        return templates.TemplateResponse(
            "lead_detail.html",
            {
                "request": request,
                "lead": lead,
                "timeline": timeline,
                "salespeople": salespeople,
                "assigned_salespeople": assigned_salespeople,
                "all_salespeople": all_salespeople,
                "error_message": e.detail,
                "current_user": current_user,
            },
            status_code=400,
        )


@router.post("/leads-page/{lead_id}/remove-salesperson/{salesperson_id}")
def remove_salesperson_page(
    lead_id: int,
    salesperson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    remove_salesperson_from_lead(db, lead_id, salesperson_id)

    return RedirectResponse(
        url=f"/api/v1/leads-page/{lead_id}",
        status_code=303,
    )


@router.get("/leads-page/{lead_id}/edit")
def edit_lead_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)

    return templates.TemplateResponse(
        "lead_edit.html",
        {
            "request": request,
            "lead": lead,
            "current_user": current_user,
        },
    )


@router.post("/leads-page/{lead_id}/edit")
def edit_lead_page_post(
    lead_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    source: str = Form(""),
    interest: str = Form(""),
    notes: str = Form(""),
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead_data = LeadUpdate(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email or None,
        city=city or None,
        state=state or None,
        source=source or None,
        interest=interest or None,
        notes=notes or None,
        status=status,
    )

    update_lead(db, lead_id, lead_data, current_user)

    return RedirectResponse(
        url=f"/api/v1/leads-page/{lead_id}",
        status_code=303,
    )


@router.post("/appointments-page/{lead_id}/{appointment_id}/update")
def update_appointment_page(
    lead_id: int,
    appointment_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    appointment_data = AppointmentUpdate(status=status)

    update_appointment(db, appointment_id, appointment_data, current_user)

    return RedirectResponse(
        url="/api/v1/appointments-page",
        status_code=303,
    )


@router.get("/deals-page/create/{lead_id}")
def create_deal_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)

    return templates.TemplateResponse(
        "deal_create.html",
        {
            "request": request,
            "lead": lead,
            "current_user": current_user,
        },
    )


@router.post("/deals-page/create/{lead_id}")
def create_deal_page_post(
    lead_id: int,
    vehicle: str = Form(...),
    price: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    deal_data = DealCreate(
        lead_id=lead_id,
        vehicle=vehicle,
        price=price,
    )

    create_deal(db, deal_data, current_user)

    return RedirectResponse(
        url="/api/v1/deals-page",
        status_code=303,
    )


@router.post("/deals-page/{deal_id}/close")
def close_deal_page(
    deal_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    deal_data = DealClose(status=status)

    close_deal(db, deal_id, deal_data, current_user)

    return RedirectResponse(
        url="/api/v1/deals-page",
        status_code=303,
    )


@router.get("/leads-page/{lead_id}/call")
def call_lead_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)

    return templates.TemplateResponse(
        "call_lead.html",
        {
            "request": request,
            "lead": lead,
            "current_user": current_user,
        },
    )


@router.post("/leads-page/{lead_id}/call")
def call_lead_page_post(
    lead_id: int,
    result: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    activity_data = ActivityCreate(
        type="call",
        content=f"Call result: {result}. {notes}".strip(),
    )

    create_activity(
        db=db,
        lead_id=lead_id,
        activity_data=activity_data,
        current_user=current_user,
    )

    return RedirectResponse(
        url=f"/api/v1/leads-page/{lead_id}",
        status_code=303,
    )