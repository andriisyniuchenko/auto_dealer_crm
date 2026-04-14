from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.lead_service import (
    assign_salesperson_to_lead,
    create_lead,
    get_inactive_leads_with_salespeople,
    get_lead_by_id,
    get_leads_with_salespeople,
    remove_salesperson_from_lead,
    update_lead,
)
from app.services.timeline_service import get_lead_timeline

router = APIRouter()


@router.get("/leads-page")
def leads_page(
    request: Request,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    leads = get_leads_with_salespeople(db, current_user, search=search, status=status)

    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "leads": leads,
            "current_user": current_user,
            "search": search or "",
            "status": status or "",
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
    request: Request,
    lead_id: int,
    salesperson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager")),
):
    try:
        remove_salesperson_from_lead(db, lead_id, salesperson_id)
        return RedirectResponse(url=f"/api/v1/leads-page/{lead_id}", status_code=303)

    except HTTPException as e:
        lead = get_lead_by_id(db, lead_id, current_user)
        timeline = get_lead_timeline(db, lead_id, current_user)

        assigned_salespeople = (
            db.query(User)
            .join(LeadSalesperson, User.id == LeadSalesperson.user_id)
            .filter(LeadSalesperson.lead_id == lead.id)
            .all()
        )
        all_salespeople = db.query(User).filter(User.role == "salesperson").all()

        return templates.TemplateResponse(
            "lead_detail.html",
            {
                "request": request,
                "lead": lead,
                "timeline": timeline,
                "salespeople": [u.email for u in assigned_salespeople],
                "assigned_salespeople": assigned_salespeople,
                "all_salespeople": all_salespeople,
                "error_message": e.detail,
                "current_user": current_user,
            },
            status_code=400,
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


@router.get("/inactive-leads-page")
def inactive_leads_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    leads = get_inactive_leads_with_salespeople(db, current_user)

    return templates.TemplateResponse(
        "inactive_leads.html",
        {
            "request": request,
            "leads": leads,
            "current_user": current_user,
        },
    )
