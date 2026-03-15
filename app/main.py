from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db import models_registry
from fastapi.staticfiles import StaticFiles
from app.core.bootstrap import create_first_admin
from app.db.session import SessionLocal
from fastapi.responses import RedirectResponse
from fastapi import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request


app = FastAPI(
    title="Auto Dealer CRM API",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    db = SessionLocal()
    create_first_admin(db)
    db.close()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/api/v1/login-page", status_code=status.HTTP_302_FOUND)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url="/api/v1/login-page")
    raise exc