import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base  # Base now imports Payment model
from app.core.config import get_settings

settings = get_settings()

# ------------------------------
# Event loop for async tests
# ------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ------------------------------
# Async test database fixture
# ------------------------------
@pytest.fixture(scope="function")
async def test_db():
    # Use in-memory SQLite DB for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        # Create all tables (Payment table will exist)
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session
    # Drop all tables after test to clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ------------------------------
# Test create_payment endpoint
# ------------------------------
@pytest.mark.asyncio
async def test_create_payment_success(mocker, test_db):
    # Mock Stripe
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }
    mocker.patch(
        "app.api.v1.payments.create_payment_intent",
        return_value=mock_intent,
    )

    # Override get_db to use in-memory test_db
    from app.api.v1.payments import get_db as original_get_db
    app.dependency_overrides[original_get_db] = lambda: test_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 5000, "currency": "usd"},
        )

    assert response.status_code == 200
    assert response.json() == mock_intent

    # Clean up override
    app.dependency_overrides = {}



# ------------------------------
# Test Stripe webhook endpoint
# ------------------------------
@pytest.mark.asyncio
async def test_stripe_webhook(mocker, test_db):
    mock_event = {"id": "evt_test_123", "type": "payment_intent.succeeded"}

    mocker.patch(
        "app.api.v1.payments.retrieve_event",
        return_value=mock_event,
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/webhook",
            content=b"{}",  # dummy payload
            headers={"stripe-signature": "t0k3n"},
        )

    assert response.status_code == 200
    assert response.json() == mock_event
