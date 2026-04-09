from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.bootstrap import create_first_admin
from app.db import models_registry
from app.db.session import SessionLocal


app = FastAPI(
    title="Auto Dealer CRM API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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