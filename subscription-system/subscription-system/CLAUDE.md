# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Docker (recommended)
```bash
docker compose up --build          # Start PostgreSQL + FastAPI
docker compose exec web python -m app.seed   # Seed test data
```

### Local development
```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
pip install -r requirements.txt
cp .env.example .env               # Edit DATABASE_URL and SECRET_KEY
python -m app.seed                 # Create tables and seed data
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

API docs: `http://127.0.0.1:8000/docs` (Swagger) or `/redoc`

Seeded test credentials: `admin@techberry.kz` / `staff@techberry.kz`, password `password123`

There are no automated tests or linter configs in this project.

## Architecture

Multi-tenant B2B SaaS backend (FastAPI + SQLAlchemy 2.0 + PostgreSQL 16).

**Data model:** `Company` → owns → `SubscriptionPlan`, `Customer`, `User`. A `Subscription` links a `Customer` to a `SubscriptionPlan` with a date range and status.

**Five tables:** `companies`, `users`, `subscription_plans`, `customers`, `subscriptions`. All tenant-scoped resources filter by `company_id` extracted from the JWT.

**Request flow:**
```
Client → CORS middleware → OAuth2Bearer → get_current_user() → require_roles() → route handler → DB
```

## Key patterns

**Auth & RBAC** (`app/api/deps.py`, `app/core/security.py`):
- JWT (HS256, PyJWT) contains `{sub, role, company_id, exp}`
- `get_current_user()` validates the token and returns the user row
- `require_roles(*roles)` is a factory that returns a FastAPI dependency; wrap endpoints with `Depends(require_roles("admin"))`
- Roles: `admin`, `employee`, `customer` (UserRole enum)

**Multi-tenant isolation:** All list/get/delete routes filter by `user.company_id`. Helper functions `_get_owned_customer` and `_get_owned_subscription` raise 404 if a resource doesn't belong to the requesting company.

**Database session:** Generator-based `get_db()` dependency via `Depends(get_db)`. Tables are created with `Base.metadata.create_all()` on app startup (no Alembic migrations).

**Schema layout:** `app/schemas/` has paired Create/Update/Out Pydantic models. Cross-field validation uses `@model_validator(mode="after")`. Money fields are `NUMERIC(10,2)` in the DB and `Decimal` in Python.

**Cascade rules:** Deleting a `Company` cascades to plans, customers, subscriptions. Deleting a `Plan` is blocked (`RESTRICT`) if active subscriptions reference it.

**Reports endpoint** (`app/api/routes/reports.py`): Three-way JOIN across customers → subscriptions → plans, filtered by company and status; computes `days_remaining` in the query.

## Environment variables

See `.env.example`. Critical vars:
- `DATABASE_URL` — PostgreSQL connection string (psycopg2 format)
- `SECRET_KEY` — 64-char hex for JWT signing (`openssl rand -hex 32`)
- `CORS_ORIGINS` — comma-separated origins or `"*"`
