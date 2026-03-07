from enum import Enum


class LeadStatus(str, Enum):
    active = "active"
    sold = "sold"
    lost = "lost"
    archived = "archived"


class ActivityType(str, Enum):
    call = "call"
    sms = "sms"
    email = "email"
    note = "note"
    visit = "visit"


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"
    no_show = "no_show"