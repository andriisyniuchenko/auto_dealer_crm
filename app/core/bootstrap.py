from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password


def create_first_admin(db: Session):
    users_count = db.query(User).count()

    if users_count == 0:
        admin = User(
            email="admin@demo.com",
            hashed_password=hash_password("admin123"),
            role="manager",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("First admin created")