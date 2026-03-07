from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse
from app.services.note_service import create_note, get_notes_by_lead

router = APIRouter(prefix="/leads/{lead_id}/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse)
def create_lead_note(
    lead_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return create_note(db, lead_id, note_data, current_user)


@router.get("/", response_model=list[NoteResponse])
def read_lead_notes(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "general_manager", "salesperson")),
):
    return get_notes_by_lead(db, lead_id, current_user)