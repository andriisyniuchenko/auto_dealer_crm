# Auto Dealer CRM API

Backend CRM system for a car dealership built with **FastAPI** and
**PostgreSQL**.

The system manages leads, sales activity, appointments, and deals while
supporting **role-based access control** for dealership staff.

---

## Tech Stack

- Python 3.14
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication

---

## Roles

**General Manager**
- Full system access

**Manager**
- Lead assignment
- Sales oversight
- Access to all leads and statistics

**Finance Manager**
- Finance-related workflows

**Salesperson**
- Access to own leads
- Access to shared leads (50/50)
- Appointments, notes, activities, and deals

---

## Features

-   Manager-controlled user registration
-   JWT authentication
-   Role-based access control

### Lead Management

-   Lead creation
-   Lead assignment to salespeople
-   Shared lead ownership (50/50)
-   Lead status management
-   Lead timeline (notes, activities, appointments, deals)
-   Stale lead detection

### Sales Activity

-   Notes history
-   Activity tracking
-   Last contacted tracking

### Appointments

-   Appointment creation
-   Appointment status updates
-   Today's appointments view
-   Calendar endpoint

### Deals

-   Deal creation
-   Deal status management
-   Split deals (0.5 / 1.0 credit)
-   Deal statistics per salesperson

### Dashboard

-   Total leads
-   Active leads
-   Stale leads
-   Appointments today
-   Open deals
-   Sold deals
---

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Project Structure

```text
app/
├── api
├── services
├── models
├── schemas
├── db
├── core
└── tasks
```

---

## Access Control

This system is designed as an internal dealership CRM.

Public self-registration is disabled.  
New users can only be created by users with **manager** or **general_manager** roles.

---

## Tests

Run tests with:

```bash
pytest