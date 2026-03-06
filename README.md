# Auto Dealer CRM API

Backend CRM system for a U.S. car dealership.

This project implements an internal dealership CRM with role-based access control, lead management, and production-oriented backend architecture built with FastAPI and PostgreSQL.

**Status:** Active Development

------------------------------------------------------------------------

## Overview

The system is designed to manage:

-   Lead distribution and ownership\
-   Sales activity tracking\
-   Deal lifecycle management\
-   Finance workflows\
-   Role-based access permissions

------------------------------------------------------------------------
## Current Features

- User registration
- JWT authentication
- Role-based access control
- Lead creation
- Role-based lead visibility
- Assigning salespeople to leads
- Shared lead ownership (50/50)
- PostgreSQL database
- Alembic database migrations

------------------------------------------------------------------------
## Tech Stack

-   Python 3.14
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic
-   JWT Authentication
-   Docker (planned)

------------------------------------------------------------------------

## Roles

**General Manager**
- Full system access

**Manager**
- Lead assignment
- Sales oversight
- Access to all leads

**Finance Manager**
- Deals and credit information
- Bank integrations

**Salesperson**
- Access to own leads
- Access to shared leads (50/50 ownership)
------------------------------------------------------------------------

## Planned Modules

- Activity Tracking
- Deal Management
- Finance Module
- Reporting & Analytics

------------------------------------------------------------------------

## Local Development

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

------------------------------------------------------------------------

## Architecture

The project follows a layered backend architecture.

```text
app/
├── api/        # FastAPI routers and endpoints
├── services/   # Business logic layer
├── models/     # SQLAlchemy ORM models
├── schemas/    # Pydantic schemas (request/response validation)
├── db/         # Database session and base configuration
└── core/       # Security, configuration, permissions
```

### Architecture Principles

- **Separation of concerns**
- **Service layer for business logic**
- **Pydantic schemas for request/response validation**
- **SQLAlchemy ORM for database access**
- **Dependency injection with FastAPI**