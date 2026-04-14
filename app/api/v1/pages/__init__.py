from fastapi import APIRouter

from app.api.v1.pages import activity, appointments, auth, dashboard, deals, leads, salesperson, stats

router = APIRouter(tags=["pages"])
router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(leads.router)
router.include_router(appointments.router)
router.include_router(deals.router)
router.include_router(activity.router)
router.include_router(stats.router)
router.include_router(salesperson.router)