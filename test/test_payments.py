import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app


@pytest.mark.asyncio
async def test_create_payment_success(mocker):
    mock_intent = {
        "id": "pi_test_123",
        "client_secret": "cs_test_123",
        "status": "requires_payment_method",
    }

    mocker.patch(
        "app.services.stripe_service.create_payment_intent",
        return_value=mock_intent,
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 5000, "currency": "usd"},
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["client_secret"] == "cs_test_123"


@pytest.mark.asyncio
async def test_create_payment_invalid_amount():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/create",
            json={"amount_cents": 0, "currency": "usd"},
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "amount must be > 0"


@pytest.mark.asyncio
async def test_webhook_invalid_signature(mocker):
    mocker.patch(
        "app.services.stripe_service.retrieve_event",
        side_effect=Exception("Invalid signature"),
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/webhook",
            content=b"{}",
            headers={"stripe-signature": "invalid"},
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_webhook_payment_intent_succeeded(mocker):
    event = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": 5000,
                "currency": "usd",
                "status": "succeeded",
            }
        },
    }

    mocker.patch(
        "app.services.stripe_service.retrieve_event",
        return_value=event,
    )

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/payments/webhook",
            content=b"{}",
            headers={"stripe-signature": "valid"},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"
