from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User


def get_sales_stats(db: Session):
    # Seed stats with all salespeople at 0
    all_salespeople = db.query(User).filter(User.role == "salesperson").all()
    stats: dict[int, dict] = {
        u.id: {"user_id": u.id, "email": u.email, "name": u.full_name, "sold_count": 0.0}
        for u in all_salespeople
    }

    # Single query with JOINs instead of N+1 loops
    rows = (
        db.query(Deal, LeadSalesperson, User)
        .join(LeadSalesperson, Deal.lead_id == LeadSalesperson.lead_id)
        .join(User, LeadSalesperson.user_id == User.id)
        .filter(Deal.status == "sold")
        .all()
    )

    # Group by deal to calculate correct share per salesperson
    deals_salespeople: dict[int, list[tuple]] = defaultdict(list)
    for deal, sp, user in rows:
        deals_salespeople[deal.id].append((user.id, user.full_name, user.email))

    for deal_id, salespeople in deals_salespeople.items():
        share = 1 / len(salespeople)
        for user_id, full_name, email in salespeople:
            stats[user_id]["sold_count"] += share

    return list(stats.values())