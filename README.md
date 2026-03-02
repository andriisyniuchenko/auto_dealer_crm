# Auto Dealer CRM API

Backend CRM system for a U.S. car dealership.

This project simulates a real internal dealership system with role-based
access control and production-oriented business logic.

**Status:** In Progress

------------------------------------------------------------------------

## Overview

The system is designed to manage:

-   Lead distribution and ownership\
-   Sales activity tracking (calls, messages)\
-   Deal lifecycle management\
-   Finance workflows\
-   Role-based access permissions

------------------------------------------------------------------------

## Tech Stack

-   Python 3.11+
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic (planned)
-   JWT Authentication (planned)
-   Docker (planned)

------------------------------------------------------------------------

## Roles

-   **General Manager** --- full system access\
-   **Manager** --- lead assignment and analytics\
-   **Finance Manager** --- deals and credit data\
-   **Salesperson** --- access to own leads only\
-   **Online Salesperson** --- shared leads (50/50 model)

------------------------------------------------------------------------

## Planned Modules

-   Authentication & Authorization\
-   Leads Management\
-   Activity Tracking\
-   Deal Management\
-   Finance Module\
-   Reporting & Analytics

------------------------------------------------------------------------

## Local Development

``` bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload
```

------------------------------------------------------------------------

## Roadmap

1.  Core project structure\
2.  Authentication & RBAC\
3.  Leads module\
4.  Activity tracking\
5.  Deal lifecycle management\
6.  Finance workflows\
7.  Docker setup
