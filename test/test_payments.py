import pytest
from httpx import AsyncClient
from app.main import app

# ------------------------------
# Test create_payment endpoint
# ------------------------------
@pytest.mark.asyncio
async def test_create_payment_success(mocker):
    # Mock the function where the route actually uses it
    # Note: app.api.v1.payments imports create_payment_intent, so we patch that path
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }

    mocker.patch(
        "app.api.v1.payments.create_payment_intent",
        return_value=mock_intent,
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 5000, "currency": "usd"},
        )

    assert response.status_code == 200
    assert response.json() == mock_intent


# ------------------------------
# Test retrieve_event endpoint
# ------------------------------
@pytest.mark.asyncio
async def test_stripe_webhook(mocker):
    mock_event = {"id": "evt_test_123", "type": "payment_intent.succeeded"}

    # Patch the function where the route imports it
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
