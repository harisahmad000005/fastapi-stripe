import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Payment  # Your Payment model
from app.main import app  # Your FastAPI app
import asyncio

# -------------------------------
# Fixture for in-memory SQLite DB
# -------------------------------
@pytest.fixture
async def test_db():
    # Create async in-memory engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create async session factory
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Provide a session for the test
    async with async_session() as session:
        yield session

    # Dispose engine after test
    await engine.dispose()


# -----------------------------------
# Test for creating a payment
# -----------------------------------
@pytest.mark.asyncio
async def test_create_payment_success(mocker, test_db):
    # Mock Stripe payment intent function
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }
    mocker.patch(
        "app.api.v1.payments.create_payment_intent",
        return_value=mock_intent,
    )

    # Override get_db dependency to use in-memory test_db
    from app.api.v1.payments import get_db as original_get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[original_get_db] = override_get_db

    # Make request using AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 5000, "currency": "usd"},
        )

    # -------------------------
    # Assertions
    # -------------------------
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_intent["id"]
    assert data["status"] == mock_intent["status"]

    # Ensure record exists in DB
    payment_in_db = await test_db.get(Payment, mock_intent["id"])
    assert payment_in_db is not None
    assert payment_in_db.amount == 5000
    assert payment_in_db.currency == "usd"
