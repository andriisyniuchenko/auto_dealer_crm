from datetime import datetime

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.services.lead_service import get_lead_by_id


def create_activity(db: Session, lead_id: int, activity_data: ActivityCreate, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    new_activity = Activity(
        lead_id=lead.id,
        user_id=current_user.id,
        type=activity_data.type.value,
        content=activity_data.content,
    )

    db.add(new_activity)

    lead.last_contacted_at = datetime.utcnow()

    db.commit()
    db.refresh(new_activity)

    return new_activity


def get_activities_by_lead(db: Session, lead_id: int, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    return (
        db.query(Activity)
        .filter(Activity.lead_id == lead.id)
        .order_by(Activity.created_at.desc())
        .all()
    )