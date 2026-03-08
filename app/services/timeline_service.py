from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.appointment import Appointment
from app.models.deal import Deal
from app.models.note import Note
from app.models.user import User
from app.services.lead_service import get_lead_by_id


def get_lead_timeline(db: Session, lead_id: int, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    timeline = []

    timeline.append({
        "type": "lead_created",
        "timestamp": lead.created_at,
        "content": f"Lead created: {lead.first_name} {lead.last_name}",
        "user_id": None,
    })

    notes = db.query(Note).filter(Note.lead_id == lead.id).all()
    for note in notes:
        timeline.append({
            "type": "note",
            "timestamp": note.created_at,
            "content": note.content,
            "user_id": note.user_id,
        })

    activities = db.query(Activity).filter(Activity.lead_id == lead.id).all()
    for activity in activities:
        timeline.append({
            "type": activity.type,
            "timestamp": activity.created_at,
            "content": activity.content or f"{activity.type} activity",
            "user_id": activity.user_id,
        })

    appointments = db.query(Appointment).filter(Appointment.lead_id == lead.id).all()
    for appointment in appointments:
        timeline.append({
            "type": "appointment",
            "timestamp": appointment.created_at,
            "content": f"Appointment scheduled for {appointment.appointment_at} ({appointment.status})",
            "user_id": appointment.user_id,
        })

    deals = db.query(Deal).filter(Deal.lead_id == lead.id).all()
    for deal in deals:
        timeline.append({
            "type": "deal_created",
            "timestamp": deal.created_at,
            "content": f"Deal created for {deal.vehicle} (${deal.price})",
            "user_id": None,
        })

        if deal.closed_at:
            timeline.append({
                "type": "deal_closed",
                "timestamp": deal.closed_at,
                "content": f"Deal closed as {deal.status}",
                "user_id": None,
            })

    timeline.sort(key=lambda x: x["timestamp"], reverse=True)

    return timeline