# Auto Dealer CRM

A full-stack CRM web application for automotive dealerships — built with FastAPI, PostgreSQL, and server-side rendered HTML templates. Part of a two-service microservice ecosystem.

[![CI](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml/badge.svg)](https://github.com/andriisyniuchenko/auto_dealer_crm/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## Demo

📹 [Watch demo video](https://youtu.be/8uaZtSdtifc)

---

## Overview

Auto Dealer CRM helps dealership teams track leads, manage deals, schedule appointments, and log customer interactions — all within a role-based access system. The app ships with both a web UI and a REST API, is fully containerized, and ready to run with a single command.

---

## Microservice Architecture

This CRM is one of two services in the Galaxy Motors ecosystem:

```
┌─────────────────────────────────┐        ┌─────────────────────────────────┐
│   Galaxy Motors Website         │        │   Auto Dealer CRM               │
│   auto-dealer-conversation-     │        │   (this repo)                   │
│   service                       │        │                                 │
│                                 │        │                                 │
│  - Vehicle inventory browsing   │        │  - Lead management              │
│  - Filter & search 60 cars      │  HTTP  │  - Deal tracking                │
│  - Lead submission form    ─────┼──POST──▶  - Role-based access            │
│  - AI chat assistant (Jessica)  │  API   │  - Dashboard & stats            │
│                                 │  Key   │                                 │
│  localhost:8001                 │        │  localhost:8000                 │
└─────────────────────────────────┘        └─────────────────────────────────┘
```

Two integration points between the services:

1. **Lead intake** — website form and AI chat assistant both submit leads via `POST /api/v1/leads/public` with an `X-API-Key` header. Returns `{"ok": true, "lead_id": 42}` so the conversation service can link the chat session to the correct lead.
2. **Chat session sync** — after a lead is submitted through the AI assistant, the full conversation is sent to `POST /api/v1/chat/sessions`. The CRM stores it and displays it on the lead detail page as a chat bubble UI (client on left, Jessica on right).

**Companion repo:** [auto-dealer-conversation-service](https://github.com/andriisyniuchenko/auto-dealer-conversation-service)

---

## Features

- **Role-based access control** — General Manager, Manager, Salesperson with per-role data visibility
- **Lead management** — create, search, and filter leads by status or name/phone; track trade-in vehicle info
- **Shared lead ownership** — up to 2 salespeople per lead with automatic 50/50 deal credit split
- **Deal tracking** — create and close deals (Sold / Lost / Canceled) with price validation
- **Activity logging** — log calls, SMS, emails, visits, and notes per lead
- **Appointment scheduling** — schedule and update customer appointments with status tracking
- **Lead timeline** — chronological history of all interactions, appointments, and deals per lead
- **Dashboard** — role-specific metrics: active leads, today's appointments list, revenue, stale leads that need attention, and top salespeople of the month (managers only)
- **Sales stats page** — leaderboard with deal credit split, clickable salesperson profiles, visible to managers only
- **Salesperson detail page** — per-salesperson breakdown of assigned leads, appointments, and deals
- **Stale lead alerts** — dashboard highlights leads not contacted in 7+ days or never contacted
- **Public lead intake API** — `POST /api/v1/leads/public` secured with `X-API-Key`, used by the website and AI chat to submit leads; returns `lead_id` for session linking
- **AI chat session storage** — stores full AI assistant conversation per lead; displayed as chat bubbles on the lead detail page (client left, Jessica right)
- **JWT authentication** — cookie-based sessions for web UI, Bearer token support for API
- **Input validation** — email format, phone number (7–15 digits), deal price > 0
- **Demo data seeding** — one command to populate realistic sample data

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.14, Pydantic v2, pydantic-settings |
| Database | PostgreSQL 16, SQLAlchemy 2.0, psycopg2 |
| Migrations | Alembic |
| Auth | JWT (python-jose), bcrypt, passlib |
| Frontend | Jinja2 templates, HTML/CSS |
| Timezone | zoneinfo (stdlib), UTC storage → America/Los_Angeles display |
| Infrastructure | Docker, Docker Compose, GitHub Actions (CI) |
| Testing | pytest, httpx (50 tests) |

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

# 2. Copy env and set your values
cp .env.example .env
# Edit .env — set SECRET_KEY and WEBSITE_API_KEY

# 3. Start the application
make up

# 4. Seed demo data
make demo

# 5. Open in browser
open http://localhost:8000
```

---

## Local Development (without Docker)

**Prerequisites:** Python 3.14, PostgreSQL running locally

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

> On first `make up` (without demo), a default manager account is created using credentials from `.env` (`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`).

---

## API

The app exposes a REST API under `/api/v1/` alongside the web UI.

Interactive docs:
```
http://localhost:8000/docs
```

### Public Endpoints (no JWT required, `X-API-Key` header)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/leads/public` | Create a lead from an external service |
| `POST` | `/api/v1/chat/sessions` | Save or update a chat session with messages |
| `GET` | `/api/v1/chat/sessions/{session_id}` | Retrieve a chat session with full message history |

**Lead request body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "555-123-4567",
  "source": "AI Chat Widget",
  "interest": "2026 Subaru Forester Limited",
  "email": "john@example.com",
  "notes": "Interested in financing"
}
```
**Lead response:** `{"ok": true, "lead_id": 42}` — the `lead_id` is used by the conversation service to link the chat session to the correct lead.

**Chat session request body:**
```json
{
  "session_id": "uuid",
  "lead_id": 42,
  "messages": [
    {"role": "user", "content": "I'm looking for an SUV"},
    {"role": "assistant", "content": "I'd recommend the 2026 Subaru Forester..."}
  ]
}
```
Chat sessions support upsert — sending again replaces the messages with the latest full conversation.

---

## Running Tests

The project has 50 tests across 4 test modules (auth, leads, appointments, deals), using an in-memory SQLite database — no Docker required.

```bash
pytest tests/
```

```bash
pytest tests/ -v   # verbose output
```