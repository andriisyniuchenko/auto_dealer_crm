from fastapi import APIRouter
from app.api.v1.endpoints import auth, leads, notes, activity, appointments, calendar, deals

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(leads.router)
api_router.include_router(notes.router)
api_router.include_router(activity.router)
api_router.include_router(appointments.router)
api_router.include_router(calendar.router)
api_router.include_router(deals.router)