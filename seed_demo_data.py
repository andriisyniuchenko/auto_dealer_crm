from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.appointment import Appointment
from app.models.activity import Activity
from app.models.user import User
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.lead_salesperson import LeadSalesperson
from app.core.security import hash_password
from app.models.enums import LeadStatus, DealStatus


def now() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(n: int) -> datetime:
    return now() - timedelta(days=n)


def today_at(hour: int, minute: int = 0) -> datetime:
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Los_Angeles")
    local = datetime.now(tz).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return local.astimezone(timezone.utc)


def seed():
    db = SessionLocal()

    try:
        if db.query(User).count() > 0:
            print("Demo data already exists, skipping seed.")
            return

        # ── Users ────────────────────────────────────────────────────────────
        manager = User(
            first_name="Sarah",
            last_name="Mitchell",
            email="manager@dealer.com",
            hashed_password=hash_password("Manager1"),
            role="manager",
            is_active=True,
        )
        sales1 = User(
            first_name="James",
            last_name="Carter",
            email="james.carter@dealer.com",
            hashed_password=hash_password("Sales123"),
            role="salesperson",
            is_active=True,
        )
        sales2 = User(
            first_name="Emily",
            last_name="Nguyen",
            email="emily.nguyen@dealer.com",
            hashed_password=hash_password("Sales123"),
            role="salesperson",
            is_active=True,
        )
        sales3 = User(
            first_name="Marcus",
            last_name="Webb",
            email="marcus.webb@dealer.com",
            hashed_password=hash_password("Sales123"),
            role="salesperson",
            is_active=True,
        )

        db.add_all([manager, sales1, sales2, sales3])
        db.commit()
        for u in [manager, sales1, sales2, sales3]:
            db.refresh(u)

        # ── Leads ────────────────────────────────────────────────────────────
        lead1 = Lead(first_name="David", last_name="Harris",
                     phone="2065550101", email="david.harris@email.com",
                     city="Seattle", state="WA", source="Website",
                     interest="2025 Honda CR-V", status=LeadStatus.active.value,
                     last_contacted_at=days_ago(2))

        lead2 = Lead(first_name="Jennifer", last_name="Torres",
                     phone="2065550102", email="j.torres@email.com",
                     city="Bellevue", state="WA", source="Walk-in",
                     interest="2024 Toyota RAV4", status=LeadStatus.active.value,
                     last_contacted_at=days_ago(1))

        lead3 = Lead(first_name="Robert", last_name="Kim",
                     phone="2065550103", email="rkim@email.com",
                     city="Redmond", state="WA", source="Referral",
                     interest="2025 Subaru Outback", status=LeadStatus.active.value,
                     last_contacted_at=days_ago(9))  # stale

        lead4 = Lead(first_name="Amanda", last_name="Price",
                     phone="2065550104", city="Kirkland", state="WA",
                     source="Facebook", interest="2024 Ford Mustang",
                     status=LeadStatus.active.value,
                     last_contacted_at=None)  # never contacted — stale

        lead5 = Lead(first_name="Kevin", last_name="Zhao",
                     phone="2065550105", email="kzhao@email.com",
                     city="Tacoma", state="WA", source="Website",
                     interest="2025 Mazda CX-5", status=LeadStatus.sold.value,
                     last_contacted_at=days_ago(5))

        lead6 = Lead(first_name="Lisa", last_name="Morgan",
                     phone="2065550106", email="lmorgan@email.com",
                     city="Renton", state="WA", source="Referral",
                     interest="2024 Hyundai Tucson", status=LeadStatus.sold.value,
                     last_contacted_at=days_ago(3))

        lead7 = Lead(first_name="Chris", last_name="Evans",
                     phone="2065550107", city="Everett", state="WA",
                     source="Walk-in", interest="2025 Chevrolet Equinox",
                     status=LeadStatus.lost.value,
                     last_contacted_at=days_ago(14))

        lead8 = Lead(first_name="Natalie", last_name="Brooks",
                     phone="2065550108", email="n.brooks@email.com",
                     city="Seattle", state="WA", source="Website",
                     interest="2024 Kia Sportage", status=LeadStatus.active.value,
                     last_contacted_at=None)  # never contacted — stale

        db.add_all([lead1, lead2, lead3, lead4, lead5, lead6, lead7, lead8])
        db.commit()
        for lead in [lead1, lead2, lead3, lead4, lead5, lead6, lead7, lead8]:
            db.refresh(lead)

        # ── Assignments ──────────────────────────────────────────────────────
        assignments = [
            (sales1, lead1), (sales1, lead3), (sales1, lead5),
            (sales2, lead2), (sales2, lead4), (sales2, lead6),
            (sales3, lead7), (sales3, lead8),
            (sales1, lead6),  # shared deal: sales1 + sales2 on lead6
        ]
        for user, lead in assignments:
            db.add(LeadSalesperson(user_id=user.id, lead_id=lead.id))
        db.commit()

        # ── Deals ────────────────────────────────────────────────────────────
        deal1 = Deal(lead_id=lead1.id, vehicle="2025 Honda CR-V",
                     price=34500, status=DealStatus.open.value)

        deal2 = Deal(lead_id=lead5.id, vehicle="2025 Mazda CX-5",
                     price=32995, status=DealStatus.sold.value,
                     closed_at=days_ago(5))

        deal3 = Deal(lead_id=lead6.id, vehicle="2024 Hyundai Tucson",
                     price=29995, status=DealStatus.sold.value,
                     closed_at=days_ago(3))

        deal4 = Deal(lead_id=lead7.id, vehicle="2025 Chevrolet Equinox",
                     price=31000, status=DealStatus.lost.value,
                     closed_at=days_ago(14))

        db.add_all([deal1, deal2, deal3, deal4])
        db.commit()
        for deal in [deal1, deal2, deal3, deal4]:
            db.refresh(deal)

        # ── Appointments ─────────────────────────────────────────────────────
        db.add(Appointment(lead_id=lead1.id, user_id=sales1.id,
                           appointment_at=today_at(10, 0), status="confirmed"))
        db.add(Appointment(lead_id=lead2.id, user_id=sales2.id,
                           appointment_at=today_at(13, 30), status="scheduled"))
        db.add(Appointment(lead_id=lead3.id, user_id=sales1.id,
                           appointment_at=today_at(15, 0), status="scheduled"))
        db.add(Appointment(lead_id=lead8.id, user_id=sales3.id,
                           appointment_at=days_ago(-1).replace(hour=11),
                           status="scheduled"))  # tomorrow

        # ── Activities ───────────────────────────────────────────────────────
        db.add(Activity(lead_id=lead1.id, user_id=sales1.id,
                        type="call", content="Discussed CR-V trim levels. Very interested.",
                        created_at=days_ago(2)))
        db.add(Activity(lead_id=lead2.id, user_id=sales2.id,
                        type="email", content="Sent RAV4 brochure and financing options.",
                        created_at=days_ago(1)))
        db.add(Activity(lead_id=lead5.id, user_id=sales1.id,
                        type="visit", content="Test drove CX-5 Sport. Ready to buy.",
                        created_at=days_ago(6)))
        db.add(Activity(lead_id=lead6.id, user_id=sales2.id,
                        type="call", content="Negotiated price. Agreed on $29,995.",
                        created_at=days_ago(4)))

        db.commit()
        print("Demo data seeded successfully.")
        print("\nLogin credentials:")
        print("  Manager:  manager@dealer.com  / Manager1")
        print("  Sales 1:  james.carter@dealer.com / Sales123")
        print("  Sales 2:  emily.nguyen@dealer.com / Sales123")
        print("  Sales 3:  marcus.webb@dealer.com / Sales123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()