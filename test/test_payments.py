import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.models import Base, Payment


# -------------------------------
# In-memory async test database
# -------------------------------
@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


# -------------------------------
# Test: create payment
# -------------------------------
@pytest.mark.asyncio
async def test_create_payment_success(mocker, test_db):
    # Mock Stripe intent
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }

    mocker.patch(
        "app.api.v1.payments.create_payment_intent",
        return_value=mock_intent,
    )

    # Override DB dependency
    from app.api.v1.payments import get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Call API
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

    assert data["amount"] == 5000
    assert data["currency"] == "usd"
    assert data["status"] == mock_intent["status"]

    # Verify DB insert
    result = await test_db.execute(Payment.__table__.select())
    payment = result.first()

    assert payment is not None
    assert payment.amount == 5000
    assert payment.currency == "usd"
    assert payment.status == mock_intent["status"]
