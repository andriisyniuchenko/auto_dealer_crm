from enum import Enum

from app.models.user import User, UserRole


class Permission(str, Enum):

    # Leads
    LEAD_VIEW = "lead:view"           # view/work leads assigned to you
    LEAD_VIEW_ALL = "lead:view_all"   # see every lead, regardless of ownership
    LEAD_CREATE = "lead:create"
    LEAD_UPDATE = "lead:update"
    LEAD_ASSIGN = "lead:assign"       # assign/remove salespeople on a lead

    # Deals
    DEAL_VIEW = "deal:view"
    DEAL_VIEW_ALL = "deal:view_all"
    DEAL_CREATE = "deal:create"
    DEAL_CLOSE = "deal:close"

    # Appointments
    APPOINTMENT_VIEW = "appointment:view"
    APPOINTMENT_VIEW_ALL = "appointment:view_all"
    APPOINTMENT_MANAGE = "appointment:manage"   # create/update

    # Notes
    NOTE_VIEW = "note:view"
    NOTE_CREATE = "note:create"

    # Activities
    ACTIVITY_VIEW = "activity:view"
    ACTIVITY_CREATE = "activity:create"

    # Dashboard
    DASHBOARD_VIEW = "dashboard:view"
    DASHBOARD_VIEW_ALL = "dashboard:view_all"   # company-wide numbers

    # Stats / reporting
    STATS_VIEW = "stats:view"

    # Team / users
    USER_VIEW = "user:view"           # view team list and salesperson details
    TEAM_MANAGE = "team:manage"       # register users, activate/deactivate


_SALESPERSON: set[Permission] = {
    Permission.LEAD_VIEW,
    Permission.LEAD_CREATE,
    Permission.LEAD_UPDATE,
    Permission.DEAL_VIEW,
    Permission.DEAL_CREATE,
    Permission.DEAL_CLOSE,
    Permission.APPOINTMENT_VIEW,
    Permission.APPOINTMENT_MANAGE,
    Permission.NOTE_VIEW,
    Permission.NOTE_CREATE,
    Permission.ACTIVITY_VIEW,
    Permission.ACTIVITY_CREATE,
    Permission.DASHBOARD_VIEW,
}


_MANAGER: set[Permission] = _SALESPERSON | {
    Permission.LEAD_VIEW_ALL,
    Permission.LEAD_ASSIGN,
    Permission.DEAL_VIEW_ALL,
    Permission.APPOINTMENT_VIEW_ALL,
    Permission.DASHBOARD_VIEW_ALL,
    Permission.STATS_VIEW,
    Permission.USER_VIEW,
    Permission.TEAM_MANAGE,
}


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.salesperson: _SALESPERSON,
    UserRole.finance_manager: set(_MANAGER),
    UserRole.manager: _MANAGER,
    UserRole.general_manager: _MANAGER,
}


def has_permission(user: User | None, permission: Permission | str) -> bool:
    if user is None:
        return False
    perm = permission if isinstance(permission, Permission) else Permission(permission)
    return perm in ROLE_PERMISSIONS.get(user.role, set())