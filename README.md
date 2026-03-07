# Auto Dealer CRM API

Backend CRM system for a U.S. car dealership built with FastAPI and PostgreSQL.

The project implements a production-style backend architecture with role-based access control, lead management, deal tracking, and sales statistics.

**Status:** Active Development

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

## Current Features

### Authentication
- User registration
- JWT authentication
- Role-based access control

### Leads
- Create leads
- Update leads
- Assign / remove salespeople
- Shared lead ownership (50/50)
- Stale leads tracking
- Last contacted tracking

### Notes & Activity
- Lead notes history
- Activity timeline (call, sms, email, visit)

### Appointments
- Schedule appointments
- Update appointment status
- View today's appointments

### Deals
- Create deal from lead
- Close deal (`sold`, `lost`, `cancelled`)

### Sales Statistics
- Sold vehicles per salesperson
- Automatic 50/50 split for shared deals

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

## Planned

- Finance module
- Dashboard endpoints
- Background reminders
- Docker deployment
