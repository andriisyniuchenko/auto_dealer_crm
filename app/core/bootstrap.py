import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_first_admin(db: Session):
    users_count = db.query(User).count()

    if users_count == 0:
        admin = User(
            first_name=settings.FIRST_ADMIN_FIRST_NAME,
            last_name=settings.FIRST_ADMIN_LAST_NAME,
            email=settings.FIRST_ADMIN_EMAIL,
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            role="manager",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("First admin created")