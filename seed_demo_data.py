from app.db.session import SessionLocal
from app.models.user import User
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.lead_salesperson import LeadSalesperson
from app.core.security import hash_password
from app.models.enums import LeadStatus, DealStatus


def seed():
    db = SessionLocal()

    try:
        if db.query(User).count() > 0:
            print("Demo data already exists")
            return

        manager = User(
            email="manager@test.com",
            hashed_password=hash_password("123456"),
            role="manager",
            is_active=True,
        )

        sales1 = User(
            email="sales1@test.com",
            hashed_password=hash_password("123456"),
            role="salesperson",
            is_active=True,
        )

        sales2 = User(
            email="sales2@test.com",
            hashed_password=hash_password("123456"),
            role="salesperson",
            is_active=True,
        )

        db.add_all([manager, sales1, sales2])
        db.commit()
        db.refresh(manager)
        db.refresh(sales1)
        db.refresh(sales2)

        lead1 = Lead(
            first_name="John",
            last_name="Smith",
            phone="1111111111",
            status=LeadStatus.active.value,
        )

        lead2 = Lead(
            first_name="Mike",
            last_name="Johnson",
            phone="2222222222",
            status=LeadStatus.active.value,
        )

        lead3 = Lead(
            first_name="Anna",
            last_name="Brown",
            phone="3333333333",
            status=LeadStatus.archived.value,
        )

        db.add_all([lead1, lead2, lead3])
        db.commit()
        db.refresh(lead1)
        db.refresh(lead2)
        db.refresh(lead3)

        db.add(LeadSalesperson(user_id=sales1.id, lead_id=lead1.id))
        db.add(LeadSalesperson(user_id=sales2.id, lead_id=lead2.id))

        db.add(LeadSalesperson(user_id=sales1.id, lead_id=lead3.id))
        db.add(LeadSalesperson(user_id=sales2.id, lead_id=lead3.id))

        db.commit()

        deal1 = Deal(
            lead_id=lead1.id,
            vehicle="2024 Subaru Crosstrek",
            price=28995,
            status=DealStatus.open.value,
        )

        deal2 = Deal(
            lead_id=lead3.id,
            vehicle="2025 Toyota Camry",
            price=31995,
            status=DealStatus.sold.value,
        )

        db.add_all([deal1, deal2])
        db.commit()

        print("Demo data seeded")

    finally:
        db.close()


if __name__ == "__main__":
    seed()