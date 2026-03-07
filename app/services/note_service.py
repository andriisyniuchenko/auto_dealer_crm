from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate
from app.services.lead_service import get_lead_by_id


def create_note(db: Session, lead_id: int, note_data: NoteCreate, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    new_note = Note(
        lead_id=lead.id,
        user_id=current_user.id,
        content=note_data.content,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


def get_notes_by_lead(db: Session, lead_id: int, current_user: User):
    lead = get_lead_by_id(db, lead_id, current_user)

    return (
        db.query(Note)
        .filter(Note.lead_id == lead.id)
        .order_by(Note.created_at.desc())
        .all()
    )