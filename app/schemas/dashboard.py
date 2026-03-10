from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_leads: int
    active_leads: int
    stale_leads: int
    appointments_today: int
    open_deals: int
    sold_deals: int