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
        if db.query(Lead).count() > 0:
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
        sales4 = User(
            first_name="Priya",
            last_name="Sharma",
            email="priya.sharma@dealer.com",
            hashed_password=hash_password("Sales123"),
            role="salesperson",
            is_active=True,
        )

        db.add_all([manager, sales1, sales2, sales3, sales4])
        db.commit()
        for u in [manager, sales1, sales2, sales3, sales4]:
            db.refresh(u)

        # ── Leads ────────────────────────────────────────────────────────────
        lead1 = Lead(
            first_name="David", last_name="Harris",
            phone="2065550101", email="david.harris@email.com",
            city="Seattle", state="WA", source="Website",
            interest="2025 Subaru Forester",
            trade_in="2018 Toyota RAV4, ~95k miles",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(2),
        )
        lead2 = Lead(
            first_name="Jennifer", last_name="Torres",
            phone="2065550102", email="j.torres@email.com",
            city="Bellevue", state="WA", source="Walk-in",
            interest="2025 Subaru Solterra",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(1),
        )
        lead3 = Lead(
            first_name="Robert", last_name="Kim",
            phone="2065550103", email="rkim@email.com",
            city="Redmond", state="WA", source="Referral",
            interest="2025 Subaru Outback Wilderness",
            trade_in="2020 Subaru Impreza, ~60k miles",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(9),  # stale
        )
        lead4 = Lead(
            first_name="Amanda", last_name="Price",
            phone="2065550104",
            city="Kirkland", state="WA", source="Facebook",
            interest="2026 Subaru Trailseeker",
            status=LeadStatus.active.value,
            last_contacted_at=None,  # never contacted — stale
        )
        lead5 = Lead(
            first_name="Kevin", last_name="Zhao",
            phone="2065550105", email="kzhao@email.com",
            city="Tacoma", state="WA", source="Website",
            interest="2025 Subaru Crosstrek Sport",
            trade_in="2017 Honda Civic, ~110k miles",
            status=LeadStatus.sold.value,
            last_contacted_at=days_ago(5),
        )
        lead6 = Lead(
            first_name="Lisa", last_name="Morgan",
            phone="2065550106", email="lmorgan@email.com",
            city="Renton", state="WA", source="Referral",
            interest="2025 Subaru Solterra",
            status=LeadStatus.sold.value,
            last_contacted_at=days_ago(3),
        )
        lead7 = Lead(
            first_name="Chris", last_name="Evans",
            phone="2065550107",
            city="Everett", state="WA", source="Walk-in",
            interest="2025 Subaru WRX",
            status=LeadStatus.lost.value,
            last_contacted_at=days_ago(14),
        )
        lead8 = Lead(
            first_name="Natalie", last_name="Brooks",
            phone="2065550108", email="n.brooks@email.com",
            city="Seattle", state="WA", source="Website",
            interest="2025 Subaru Ascent",
            trade_in="2016 Ford Explorer, ~130k miles",
            status=LeadStatus.active.value,
            last_contacted_at=None,  # never contacted — stale
        )
        lead9 = Lead(
            first_name="Tyler", last_name="Patel",
            phone="2065550109", email="tyler.patel@email.com",
            city="Bellevue", state="WA", source="Website",
            interest="2026 Subaru Trailseeker",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(1),
        )
        lead10 = Lead(
            first_name="Grace", last_name="Yamamoto",
            phone="2065550110", email="gyamamoto@email.com",
            city="Seattle", state="WA", source="Referral",
            interest="2025 Subaru BRZ",
            status=LeadStatus.sold.value,
            last_contacted_at=days_ago(7),
        )
        lead11 = Lead(
            first_name="Daniel", last_name="Foster",
            phone="2065550111",
            city="Issaquah", state="WA", source="Walk-in",
            interest="2025 Subaru Forester Hybrid",
            trade_in="2019 Mazda CX-5, ~75k miles",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(4),
        )
        lead12 = Lead(
            first_name="Olivia", last_name="Chen",
            phone="2065550112", email="olivia.chen@email.com",
            city="Kirkland", state="WA", source="Facebook",
            interest="2025 Subaru Solterra",
            status=LeadStatus.active.value,
            last_contacted_at=days_ago(12),  # stale
        )

        all_leads = [lead1, lead2, lead3, lead4, lead5, lead6,
                     lead7, lead8, lead9, lead10, lead11, lead12]
        db.add_all(all_leads)
        db.commit()
        for lead in all_leads:
            db.refresh(lead)

        # ── Assignments ──────────────────────────────────────────────────────
        assignments = [
            (sales1, lead1), (sales1, lead3), (sales1, lead5), (sales1, lead11),
            (sales2, lead2), (sales2, lead4), (sales2, lead6), (sales2, lead9),
            (sales3, lead7), (sales3, lead8), (sales3, lead12),
            (sales4, lead10), (sales4, lead11),  # lead11 shared: sales1 + sales4
            (sales1, lead6),                      # lead6 shared: sales1 + sales2
        ]
        for user, lead in assignments:
            db.add(LeadSalesperson(user_id=user.id, lead_id=lead.id))
        db.commit()

        # ── Deals ────────────────────────────────────────────────────────────
        deal1 = Deal(lead_id=lead1.id, vehicle="2025 Subaru Forester Premium",
                     price=34995, status=DealStatus.open.value)

        deal2 = Deal(lead_id=lead5.id, vehicle="2025 Subaru Crosstrek Sport",
                     price=31495, status=DealStatus.sold.value,
                     closed_at=days_ago(5))

        deal3 = Deal(lead_id=lead6.id, vehicle="2025 Subaru Solterra Premium",
                     price=47995, status=DealStatus.sold.value,
                     closed_at=days_ago(3))

        deal4 = Deal(lead_id=lead7.id, vehicle="2025 Subaru WRX",
                     price=33495, status=DealStatus.lost.value,
                     closed_at=days_ago(14))

        deal5 = Deal(lead_id=lead10.id, vehicle="2025 Subaru BRZ Limited",
                     price=35995, status=DealStatus.sold.value,
                     closed_at=days_ago(7))

        deal6 = Deal(lead_id=lead9.id, vehicle="2026 Subaru Trailseeker",
                     price=52495, status=DealStatus.open.value)

        all_deals = [deal1, deal2, deal3, deal4, deal5, deal6]
        db.add_all(all_deals)
        db.commit()
        for deal in all_deals:
            db.refresh(deal)

        # ── Appointments ─────────────────────────────────────────────────────
        db.add(Appointment(lead_id=lead1.id, user_id=sales1.id,
                           appointment_at=today_at(9, 30), status="confirmed"))
        db.add(Appointment(lead_id=lead2.id, user_id=sales2.id,
                           appointment_at=today_at(11, 0), status="scheduled"))
        db.add(Appointment(lead_id=lead9.id, user_id=sales2.id,
                           appointment_at=today_at(14, 0), status="confirmed"))
        db.add(Appointment(lead_id=lead11.id, user_id=sales1.id,
                           appointment_at=today_at(16, 30), status="scheduled"))
        # tomorrow
        db.add(Appointment(lead_id=lead8.id, user_id=sales3.id,
                           appointment_at=days_ago(-1).replace(hour=10, minute=0, second=0, microsecond=0),
                           status="scheduled"))

        # ── Activities ───────────────────────────────────────────────────────
        db.add(Activity(lead_id=lead1.id, user_id=sales1.id, type="call",
                        content="Discussed Forester trim levels. Very interested in Premium. Trade-in noted.",
                        created_at=days_ago(2)))
        db.add(Activity(lead_id=lead2.id, user_id=sales2.id, type="email",
                        content="Sent Solterra brochure and EV incentive info. Customer excited about range.",
                        created_at=days_ago(1)))
        db.add(Activity(lead_id=lead3.id, user_id=sales1.id, type="call",
                        content="Left voicemail. No response yet.",
                        created_at=days_ago(9)))
        db.add(Activity(lead_id=lead5.id, user_id=sales1.id, type="visit",
                        content="Test drove Crosstrek Sport. Loved the EyeSight. Ready to sign.",
                        created_at=days_ago(6)))
        db.add(Activity(lead_id=lead6.id, user_id=sales2.id, type="call",
                        content="Negotiated final price on Solterra. Agreed on $47,995 with free charging install.",
                        created_at=days_ago(4)))
        db.add(Activity(lead_id=lead9.id, user_id=sales2.id, type="email",
                        content="Sent Trailseeker pre-order info and expected delivery timeline.",
                        created_at=days_ago(1)))
        db.add(Activity(lead_id=lead10.id, user_id=sales4.id, type="visit",
                        content="Test drove BRZ Limited. Customer loved the manual transmission option.",
                        created_at=days_ago(8)))
        db.add(Activity(lead_id=lead11.id, user_id=sales1.id, type="sms",
                        content="Confirmed appointment for tomorrow at 4:30pm.",
                        created_at=days_ago(4)))

        db.commit()

        print("\nDemo data seeded successfully.")
        print("\nLogin credentials:")
        print("  Manager:   manager@dealer.com   / Manager1")
        print("  Sales 1:   james.carter@dealer.com / Sales123")
        print("  Sales 2:   emily.nguyen@dealer.com / Sales123")
        print("  Sales 3:   marcus.webb@dealer.com  / Sales123")
        print("  Sales 4:   priya.sharma@dealer.com / Sales123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()