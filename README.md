# FastAPI Stripe Production Scaffold


## Features
- FastAPI async app
- Stripe PaymentIntent integration
- Stripe webhook verification
- Async SQLAlchemy + Postgres
- Dockerfile + docker-compose
- Tests and CI scaffold


## Local dev
1. Copy `.env.example` to `.env` and fill secrets.
2. docker-compose up --build
3. Run migrations (alembic)