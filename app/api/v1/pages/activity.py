from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.models.enums import ActivityType
from app.schemas.activity import ActivityCreate
from app.services.activity_service import create_activity
from app.services.lead_service import get_lead_by_id

router = APIRouter()


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


@router.get("/leads-page/{lead_id}/text")
def text_lead_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)

    return templates.TemplateResponse(
        "text_lead.html",
        {
            "request": request,
            "lead": lead,
            "current_user": current_user,
        },
    )


@router.post("/leads-page/{lead_id}/text")
def text_lead_page_post(
    lead_id: int,
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    activity_data = ActivityCreate(
        type=ActivityType.sms,
        content=message,
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


@router.get("/leads-page/{lead_id}/email")
def email_lead_page(
    lead_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    lead = get_lead_by_id(db, lead_id, current_user)

    return templates.TemplateResponse(
        "email_lead.html",
        {
            "request": request,
            "lead": lead,
            "current_user": current_user,
        },
    )


@router.post("/leads-page/{lead_id}/email")
def email_lead_page_post(
    lead_id: int,
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_web_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user

    activity_data = ActivityCreate(
        type="email",
        content=f"Subject: {subject}. Message: {message}",
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