# LEDGR Backend

FastAPI + PostgreSQL backend. For Assignment 2 (Part 4), this implements
and deploys two endpoints from the Personal Ledger feature:

- `POST /api/v1/transactions` — create a transaction
- `GET /api/v1/transactions` — list/filter transactions

Supporting endpoints (`/auth/register`, `/auth/login`, `/categories`) are
included only to make the above two endpoints usable end-to-end (auth +
a valid `category_id`), per the assignment's "you may need to add
supporting services" note. Full endpoint definitions for all three core
features and all security endpoints are documented separately in
`Assignment 2/report/`.

## Stack

- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL, via SQLAlchemy 2.0 + the `psycopg` (v3) driver
- **Migrations:** Alembic
- **Auth:** JWT (`PyJWT`), bcrypt password hashing

## Local development

Requires Docker (for Postgres) and Python 3.12+.

```bash
# 1. Start Postgres
docker compose up -d

# 2. Create a virtualenv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Start the API
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`, with interactive OpenAPI docs
at `http://localhost:8000/docs`.

### Running with Docker directly

```bash
docker build -t ledgr-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://ledgr:ledgr@host.docker.internal:5432/ledgr" \
  -e SECRET_KEY="some-dev-secret" \
  ledgr-backend
```

## Quick smoke test

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Vijay","last_name":"Puttarevaiah","email":"vijay.p@dal.ca","password":"LedgerPass2026!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"vijay.p@dal.ca","password":"LedgerPass2026!"}'
# -> copy the access_token from the response

# Get a category id
curl http://localhost:8000/api/v1/categories -H "Authorization: Bearer <TOKEN>"

# Create a transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"amount":84.20,"type":"expense","date":"2026-06-29","category_id":"<CATEGORY_ID>","vendor":"Atlantic Superstore"}'

# List transactions
curl http://localhost:8000/api/v1/transactions -H "Authorization: Bearer <TOKEN>"
```

## Deploying to Render

This repo includes a `render.yaml` Blueprint and a `Dockerfile`, so Render
builds and runs the same container that was tested locally.

1. Push this `backend/` folder to a GitHub repository.
2. In the Render dashboard: **New > Blueprint**, connect the repository,
   and select this repo/branch. Render will read `render.yaml` and
   provision both the free Postgres database (`ledgr-db`) and the web
   service (`ledgr-backend`) automatically, wiring `DATABASE_URL` between
   them.
3. Wait for the first deploy to finish (the container runs
   `alembic upgrade head` automatically on startup, then starts uvicorn).
4. Render gives you a public URL like
   `https://ledgr-backend-xxxx.onrender.com`. Verify with:
   ```bash
   curl https://ledgr-backend-xxxx.onrender.com/health
   ```
5. Use that base URL (with `/api/v1/...` paths) in Postman for the
   Assignment 2 evidence screenshots.

If you'd rather not use the Blueprint, you can create the two resources
manually in the Render dashboard (New > PostgreSQL, then New > Web
Service pointing at the same repo with `Docker` as the environment) and
copy the database's "Internal Connection String" into the web service's
`DATABASE_URL` environment variable, plus set a `SECRET_KEY` value.

## Database export

To produce the `.sql` dump required by the assignment after you've
created some demo data:

```bash
docker compose exec db pg_dump -U ledgr ledgr > ledgr_dump.sql
```

For the deployed Render database, use the "External Connection String"
shown in the Render dashboard with `pg_dump` from your machine instead.

## Project structure

```
app/
  core/      settings, security (JWT/bcrypt), error helpers
  db/        SQLAlchemy session/engine, default-category seeding
  models/    SQLAlchemy ORM models (User, Category, Transaction)
  schemas/   Pydantic request/response schemas
  api/v1/    route handlers (auth, categories, transactions)
  main.py    FastAPI app, CORS, exception handlers
alembic/     migrations
```
