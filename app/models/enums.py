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