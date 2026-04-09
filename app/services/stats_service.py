from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User


def get_sales_stats(db: Session):
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
        deals_salespeople[deal.id].append((user.id, user.email))

    stats: dict[int, dict] = {}
    for deal_id, salespeople in deals_salespeople.items():
        share = 1 / len(salespeople)
        for user_id, email in salespeople:
            if user_id not in stats:
                stats[user_id] = {"user_id": user_id, "email": email, "sold_count": 0.0}
            stats[user_id]["sold_count"] += share

    return list(stats.values())