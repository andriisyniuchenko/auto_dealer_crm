from enum import Enum


class LeadStatus(str, Enum):
    active = "active"
    sold = "sold"
    lost = "lost"
    archived = "archived"