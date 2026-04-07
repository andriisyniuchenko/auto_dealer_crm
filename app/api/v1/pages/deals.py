from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.db.session import get_db
from app.schemas.deal import DealClose, DealCreate
from app.services.deal_service import close_deal, create_deal, get_deals
from app.services.lead_service import get_lead_by_id

router = APIRouter()


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