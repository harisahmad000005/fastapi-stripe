import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Payment
from app.main import app

@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_payment_success(mocker, test_db):
    # Mock Stripe payment intent
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }
    mocker.patch(
        "app.api.v1.payments.create_payment_intent",
        return_value=mock_intent,
    )

    from app.api.v1.payments import get_db as original_get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[original_get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 5000, "currency": "usd"},
        )

    assert response.status_code == 200
    data = response.json()

    # Check database record matches
    result = await test_db.execute(
        Payment.__table__.select().where(Payment.id == data["id"])
    )
    payment_in_db = result.first()
    assert payment_in_db is not None
    assert payment_in_db.amount == 5000
    assert payment_in_db.currency == "usd"
    assert payment_in_db.status == mock_intent["status"]

    # Check response matches DB record
    assert data["id"] == payment_in_db.id
    assert data["amount"] == payment_in_db.amount
    assert data["currency"] == payment_in_db.currency
    assert data["status"] == payment_in_db.status
