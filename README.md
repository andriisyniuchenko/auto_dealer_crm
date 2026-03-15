# Auto Dealer CRM

Auto Dealer CRM is a full‑stack backend system for managing dealership sales workflow.

## Features
- Role-based access (Manager / Salesperson)
- Lead lifecycle management (active, archived, etc.)
- Deals tracking (open / sold)
- Shared lead ownership (50/50)
- Dashboard metrics
- Authentication (JWT)
- Dockerized environment
- PostgreSQL database
- Alembic migrations
- Demo data seeding via Makefile

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker / Docker Compose
- Makefile

## Quick Start

### Run project
```bash
make up
```

### Seed demo data
```bash
make demo
```

### Stop project
```bash
make down
```

### Reset database
```bash
make reset
```

## Demo Users
Manager:
- email: manager@test.com
- password: 123456

Sales:
- sales1@test.com
- sales2@test.com

## Notes
- Seed is manual (not automatic)
- First manager bootstrap supported
- Designed for AWS deployment

