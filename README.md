# Auto Dealer CRM

A full-stack CRM web application for automotive dealerships — built with FastAPI, PostgreSQL, and server-side rendered HTML templates.

[![CI](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml/badge.svg)](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## Overview

Auto Dealer CRM helps dealership teams track leads, manage deals, schedule appointments, and log customer interactions — all within a role-based access system. The app ships with both a web UI and a REST API, is fully containerized, and ready to run with a single command.

---

## Features

- **Role-based access control** — General Manager, Manager, Salesperson with per-role data visibility
- **Lead management** — create, search, and filter leads by status or name/phone; track trade-in vehicle info
- **Shared lead ownership** — up to 2 salespeople per lead with automatic 50/50 deal credit split
- **Deal tracking** — create and close deals (Sold / Lost / Cancelled) with price validation
- **Activity logging** — log calls, SMS, emails, visits, and notes per lead
- **Appointment scheduling** — schedule and update customer appointments with status tracking
- **Lead timeline** — chronological history of all interactions, appointments, and deals per lead
- **Dashboard** — role-specific metrics: active leads, today's appointments list, revenue, stale leads that need attention, and top salespeople of the month (managers only)
- **Sales stats page** — leaderboard with deal credit split, visible to managers only
- **Stale lead alerts** — dashboard highlights leads not contacted in 7+ days or never contacted
- **JWT authentication** — cookie-based sessions for web UI, Bearer token support for API
- **Input validation** — email format, phone number (7–15 digits), deal price > 0
- **Demo data seeding** — one command to populate realistic sample data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.14 |
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
│       ├── endpoints/     # JSON API routes (auth, leads, deals, appointments, stats…)
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

**Prerequisites:** Docker + Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/andriisyniuchenko/auto_dealer_crm.git
cd auto_dealer_crm

# 2. Start the application (uses .env.docker — already included)
make up

# 3. Seed demo data
make demo

# 4. Open in browser
open http://localhost:8000
```

---

## Local Development (without Docker)

**Prerequisites:** Python 3.12+, PostgreSQL running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your local database credentials

alembic upgrade head
uvicorn app.main:app --reload
```

---

## Makefile Commands

| Command | Description |
|---|---|
| `make up` | Build and start all services |
| `make down` | Stop all services |
| `make reset` | Drop and recreate the database volume |
| `make demo` | Start services and seed demo data |
| `make logs` | Tail application logs |
| `make rebuild` | Force rebuild Docker image |

---

## Demo Credentials

After running `make demo`:

| Role | Email | Password |
|---|---|---|
| Manager | manager@dealer.com | Manager1 |
| Salesperson | james.carter@dealer.com | Sales123 |
| Salesperson | emily.nguyen@dealer.com | Sales123 |
| Salesperson | marcus.webb@dealer.com | Sales123 |
| Salesperson | priya.sharma@dealer.com | Sales123 |

> On first `make up` (without demo), a default manager account is created using credentials from `.env.docker` (`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`).

---

## API

The app exposes a REST API under `/api/v1/` alongside the web UI.

Interactive docs:
```
http://localhost:8000/docs
```

---

## Running Tests

```bash
pytest tests/
```