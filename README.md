# Auto Dealer CRM

A full-stack web application for managing automotive dealership sales workflows — built with FastAPI, PostgreSQL, and server-side rendered HTML templates.

[![CI](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml/badge.svg)](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## Overview

Auto Dealer CRM helps dealership teams track leads, manage deals, schedule appointments, and log customer interactions — all within a role-based access system. The app is fully containerized and ready for cloud deployment.

---

## Features

- **Role-based access control** — General Manager, Manager, Finance Manager, Salesperson
- **Lead lifecycle management** — track leads through stages: New → Contacted → Appointment → Test Drive → Negotiation → Finance → Sold/Lost
- **Shared lead ownership** — up to 2 salespeople per lead with automatic 50/50 credit split
- **Deal tracking** — create and close deals with status: Open / Sold / Lost / Cancelled
- **Activity logging** — log calls, SMS, emails, and notes per lead
- **Appointment scheduling** — schedule and manage customer appointments
- **Lead timeline** — chronological history of all interactions per lead
- **Dashboard metrics** — role-specific sales performance data
- **JWT authentication** — cookie-based sessions for web UI, Bearer token support for API
- **Demo data seeding** — one command to populate realistic sample data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 16, SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT (python-jose), bcrypt |
| Frontend | Jinja2 templates, HTML/CSS |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest |

---

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/     # JSON API routes (auth, leads, deals, etc.)
│       ├── pages/         # Server-rendered HTML page routes
│       └── router.py
├── core/                  # Config, security, bootstrap
├── db/                    # Database session and model registry
├── models/                # SQLAlchemy ORM models
├── schemas/               # Pydantic request/response schemas
├── services/              # Business logic layer
├── templates/             # Jinja2 HTML templates
└── main.py
```

---

## Quick Start (Docker)

### Prerequisites

- Docker + Docker Compose

### 1. Create environment file

```bash
cp .env.example .env.docker
```

Edit `.env.docker` with your values:

```env
DATABASE_URL=postgresql://postgres:yourpassword@db:5432/auto_dealer_crm
TEST_DATABASE_URL=postgresql://postgres:yourpassword@db:5432/auto_dealer_crm_test
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=auto_dealer_crm
```

### 2. Start the application

```bash
make up
```

### 3. Seed demo data (optional)

```bash
make demo
```

### 4. Open in browser

```
http://localhost:8000
```

---

## Local Development (without Docker)

### Prerequisites

- Python 3.12+
- PostgreSQL running locally

### 1. Set up environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your local database credentials.

### 3. Run migrations and start

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Makefile Commands

| Command | Description |
|---|---|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make reset` | Drop and recreate the database |
| `make demo` | Seed demo users and sample data |
| `make logs` | Tail application logs |
| `make rebuild` | Rebuild Docker image |

---

## Demo Credentials

After running `make demo`:

| Role | Email | Password |
|---|---|---|
| Manager | manager@test.com | 123456 |
| Salesperson | sales1@test.com | 123456 |
| Salesperson | sales2@test.com | 123456 |

---

## API

The app exposes a REST API under `/api/v1/` alongside the web UI.

Interactive docs available at:
```
http://localhost:8000/docs
```

---

## Running Tests

```bash
pytest tests/
```