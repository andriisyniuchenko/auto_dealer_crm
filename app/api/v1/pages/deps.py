from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

DEALER_TZ = ZoneInfo("America/Los_Angeles")


def _localdt(dt: datetime, fmt: str) -> str:
    """Convert UTC datetime to dealer local time and format it."""
    if dt is None:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(DEALER_TZ).strftime(fmt)


templates = Jinja2Templates(directory="app/templates")
templates.env.globals["localdt"] = _localdt


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