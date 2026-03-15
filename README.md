# 🚗 Auto Dealer CRM

A role-based CRM system designed for car dealerships to manage leads, deals, appointments, and sales activity.

This project demonstrates real-world backend architecture, business logic implementation, and production-ready deployment practices using FastAPI and PostgreSQL.

---

## ✨ Features

- Role-based access system (Manager / Salesperson)
- Lead lifecycle management
- Deal tracking with shared ownership (50/50 logic)
- Activity timeline (calls, SMS, email, notes, visits)
- Appointment scheduling
- Dashboard with real business metrics
- Active vs inactive lead separation
- Server-side rendered UI (no frontend framework)
- Dockerized environment
- Database migrations with Alembic
- Demo data seeding for testing

---

## 🧠 Business Logic Highlights

This project focuses on real dealership workflows, not just CRUD.

Implemented logic includes:

- Shared lead ownership between salespeople
- Partial deal credit (e.g. 2.5 deals)
- Lead activity timeline affecting contact status
- Inactive lead archival system
- Manager-only user creation
- Sales performance tracking via deals

---

## 🏗 Tech Stack

Backend:
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

Infrastructure:
- Docker
- Docker Compose

Security:
- JWT Authentication
- Role-based authorization
- Password hashing

Rendering:
- Jinja2 Templates

---

## 🐳 Running with Docker

### 1️⃣ Create environment file

Create `.env.docker`:

DATABASE_URL=postgresql://postgres:1234@db:5432/auto_dealer_crm  
SECRET_KEY=supersecretkey  
ALGORITHM=HS256  
ACCESS_TOKEN_EXPIRE_MINUTES=60  

### 2️⃣ Build and start containers

docker compose up --build

### 3️⃣ Run migrations

Already executed automatically on startup.

### 4️⃣ Seed demo data (optional)

Run manually:

docker exec -it auto_dealer_crm_web python seed_demo_data.py

---

## 👤 Demo Users

After seeding:

Manager:  
manager@test.com  
123456  

Sales:  
sales1@test.com  
123456  

sales2@test.com  
123456  

---

## 📊 Dashboard Metrics

Dashboard includes:

- Active leads count
- Appointments today
- Open deals
- Sold deals (with shared deal weighting)

Inactive leads are handled in a separate workflow.

---

## 🧩 Project Purpose

This project was built to demonstrate:

- Production-like backend structure
- Business domain modeling
- Complex relational logic
- Deployment readiness
- Clean service-layer architecture

---

## 📌 Notes

This is a backend-focused project.  
Frontend intentionally minimal to highlight backend architecture and system design.
