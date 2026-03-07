from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.lead_salesperson import LeadSalesperson
from app.models.user import User


def get_sales_stats(db: Session):
    sold_deals = db.query(Deal).filter(Deal.status == "sold").all()

    stats = {}

    for deal in sold_deals:
        salespeople = (
            db.query(LeadSalesperson)
            .filter(LeadSalesperson.lead_id == deal.lead_id)
            .all()
        )

        if not salespeople:
            continue

        share = 1 / len(salespeople)

        for sp in salespeople:
            user = db.query(User).filter(User.id == sp.user_id).first()
            if not user:
                continue

            if user.id not in stats:
                stats[user.id] = {
                    "user_id": user.id,
                    "email": user.email,
                    "sold_count": 0.0,
                }

            stats[user.id]["sold_count"] += share

    return list(stats.values())