from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.pages.deps import get_current_web_user, templates
from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import login_user

router = APIRouter()


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
        samesite="strict",
        secure=settings.COOKIE_SECURE,
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/api/v1/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response