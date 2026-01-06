# FastAPI Payments API

A **FastAPI** backend for managing payments with **Stripe**, built with **SQLAlchemy** (async), **SQLite/PostgreSQL**, and fully tested with **pytest** and **httpx**. Designed for high-performance and easy scalability.

---

## Table of Contents

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Requirements](#requirements)  
4. [Installation & Setup](#installation--setup)  
5. [Environment Variables](#environment-variables)  
6. [Database Setup](#database-setup)  
7. [Running the Application](#running-the-application)  
8. [Running Tests](#running-tests)  
9. [Project Structure](#project-structure)  
10. [API Endpoints](#api-endpoints)  
11. [Contributing](#contributing)  
12. [License](#license)  

---

## Features

- Create and manage Stripe payment intents.  
- Async database operations using **SQLAlchemy Async ORM**.  
- Test coverage with **pytest**, **pytest-asyncio**, and **httpx**.  
- In-memory test database for fast, isolated tests.  
- Clear separation of API, services, and database layers.  
- Ready for deployment with Docker, Gunicorn, or Uvicorn.  

---

## Tech Stack

- **Python 3.11+**  
- **FastAPI** – Async web framework  
- **SQLAlchemy** – Async ORM  
- **SQLite** (dev/test) / **PostgreSQL** (prod)  
- **Stripe API** – Payment gateway  
- **pytest** – Unit and integration tests  
- **httpx** – Async HTTP testing client  

---

## Requirements

- Python 3.11 or higher  
- pip >= 23  
- PostgreSQL 14+ (for production)  

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` should include:

```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
aiosqlite
asyncpg
pytest
pytest-asyncio
httpx
python-dotenv
stripe
```

---

## Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/payments-api.git
cd payments-api
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root:

```dotenv
# Stripe
STRIPE_API_KEY=sk_test_xxxxxxxxxxxxx

# Database (Postgres)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/payments_db

# FastAPI settings
APP_HOST=0.0.0.0
APP_PORT=8000
```

---

## Database Setup

### Development (SQLite)

No setup required — in-memory database is used for local testing.  

### Production (PostgreSQL)

```bash
psql -U postgres
CREATE DATABASE payments_db;
```

Run migrations:

```bash
# If using Alembic
alembic upgrade head
```

---

## Running the Application

Start FastAPI with **Uvicorn**:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for **Swagger UI**.

---

## Running Tests

Run **all tests**:

```bash
pytest --asyncio-mode=auto --maxfail=1 --disable-warnings -q
```

Tests use **in-memory SQLite** for isolation.  
Mocks **Stripe API** calls for safe, deterministic testing.  

---

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── __init__.py
│       └── payments.py        # Payment endpoints
├── core/
│   ├── __init__.py
│   └── config.py              # App settings
├── db/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy models
│   └── session.py             # DB session/engine
├── services/
│   ├── __init__.py
│   └── stripe_service.py      # Stripe logic
├── schemas/
│   ├── __init__.py
│   └── payments.py            # Pydantic schemas
├── __init__.py
└── main.py                    # FastAPI entrypoint

tests/
├── __init__.py
└── test_payments.py           # API tests

.env
requirements.txt
README.md

```

---

## API Endpoints

### POST `/api/v1/payments/create`

Create a Stripe payment intent.

**Request Body:**

```json
{
  "amount_cents": 5000,
  "currency": "usd"
}
```

**Response:**

```json
{
  "client_secret": "cs_test_123"
}
```

> **Note:** Only `client_secret` is returned by the API. Database persists full payment info.  

---

## Contributing

1. Fork the repository  
2. Create a feature branch  
3. Write tests  
4. Submit a pull request  

---

## License

MIT License © 2026 Haris Ahmad Mubashir

