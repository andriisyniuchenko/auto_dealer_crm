from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.permissions import Permission, has_permission
from app.models.deal import Deal
from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User
from app.services.appointment_service import get_today_appointments

STALE_DAYS = 7


def _get_stale_leads(db: Session, current_user: User):
    """Active leads never contacted or not contacted in 7+ days."""
    threshold = datetime.now(timezone.utc) - timedelta(days=STALE_DAYS)

    query = (
        db.query(Lead)
        .filter(
            Lead.status == LeadStatus.active.value,
            (Lead.last_contacted_at == None) | (Lead.last_contacted_at < threshold),
        )
    )

    if not has_permission(current_user, Permission.LEAD_VIEW_ALL):
        query = query.join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id).filter(
            LeadSalesperson.user_id == current_user.id
        )

    leads = query.order_by(Lead.last_contacted_at.asc().nullsfirst()).limit(8).all()

    result = []
    for lead in leads:
        if lead.last_contacted_at is None:
            days = None
        else:
            days = (datetime.now(timezone.utc).date() - lead.last_contacted_at.date()).days
        result.append({
            "id": lead.id,
            "name": f"{lead.first_name} {lead.last_name}",
            "days_since_contact": days,
        })
    return result


def _get_top_salespeople(db: Session):
    """Top 3 salespeople by sold deals this month."""
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    rows = (
        db.query(Deal, LeadSalesperson, User)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .join(User, LeadSalesperson.user_id == User.id)
        .filter(
            Deal.status == "sold",
            Deal.closed_at >= month_start,
        )
        .all()
    )

    deals_salespeople: dict[int, list[tuple]] = defaultdict(list)
    for deal, sp, user in rows:
        deals_salespeople[deal.id].append((user.id, user.full_name))

    stats: dict[int, dict] = {}
    for deal_id, salespeople in deals_salespeople.items():
        share = 1 / len(salespeople)
        for user_id, full_name in salespeople:
            if user_id not in stats:
                stats[user_id] = {"name": full_name, "sold_count": 0.0}
            stats[user_id]["sold_count"] += share

    return sorted(stats.values(), key=lambda x: x["sold_count"], reverse=True)[:3]


def _get_revenue(db: Session, current_user: User):
    """Total revenue from sold deals."""
    if has_permission(current_user, Permission.DEAL_VIEW_ALL):
        result = (
            db.query(func.sum(Deal.price))
            .filter(Deal.status == "sold")
            .scalar()
        )
        return result or 0

    # For salesperson: sum prices of their sold deals (full price, not split)
    result = (
        db.query(func.sum(Deal.price))
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .filter(
            LeadSalesperson.user_id == current_user.id,
            Deal.status == "sold",
        )
        .scalar()
    )
    return result or 0


def get_dashboard_data(db: Session, current_user: User):
    tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)

    is_manager = has_permission(current_user, Permission.DASHBOARD_VIEW_ALL)

    if is_manager:
        active_leads = (
            db.query(Lead)
            .filter(Lead.status == LeadStatus.active.value)
            .count()
        )
        open_deals = db.query(Deal).filter(Deal.status == "open").count()
        sold_deals = db.query(Deal).filter(Deal.status == "sold").count()
    else:
        active_leads = (
            db.query(Lead)
            .join(LeadSalesperson, Lead.id == LeadSalesperson.lead_id)
            .filter(
                LeadSalesperson.user_id == current_user.id,
                Lead.status == LeadStatus.active.value,
            )
            .count()
        )
        open_deals = (
            db.query(Deal)
            .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
            .filter(
                LeadSalesperson.user_id == current_user.id,
                Deal.status == "open",
            )
            .count()
        )

        sold_deals_rows = (
            db.query(Deal.id, Deal.lead_id)
            .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
            .filter(
                LeadSalesperson.user_id == current_user.id,
                Deal.status == "sold",
            )
            .all()
        )
        lead_ids = [row.lead_id for row in sold_deals_rows]
        counts = (
            db.query(LeadSalesperson.lead_id, func.count(LeadSalesperson.user_id).label("cnt"))
            .filter(LeadSalesperson.lead_id.in_(lead_ids))
            .group_by(LeadSalesperson.lead_id)
            .all()
        )
        salespeople_count_map = {row.lead_id: row.cnt for row in counts}
        sold_deals = sum(
            1 / salespeople_count_map.get(row.lead_id, 1)
            for row in sold_deals_rows
        )

    today_appointments = get_today_appointments(db, current_user)

    return {
        "active_leads": active_leads,
        "appointments_today": len(today_appointments),
        "today_appointments_list": today_appointments,
        "open_deals": open_deals,
        "sold_deals": sold_deals,
        "revenue": _get_revenue(db, current_user),
        "stale_leads": _get_stale_leads(db, current_user),
        "top_salespeople": _get_top_salespeople(db) if is_manager else [],
    }