import stripe
import asyncio
from app.core.config import settings
from concurrent.futures import ThreadPoolExecutor


stripe.api_key = settings.STRIPE_SECRET_KEY
_executor = ThreadPoolExecutor(max_workers=3)


async def create_payment_intent(amount_cents: int, currency: str = "usd", metadata: dict | None = None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: stripe.PaymentIntent.create(
    amount=amount_cents,
    currency=currency,
    automatic_payment_methods={"enabled": True},
    metadata=metadata or {},
    ))


async def retrieve_event(payload: bytes, sig_header: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: stripe.Webhook.construct_event(
    payload=payload, sig_header=sig_header, secret=settings.STRIPE_WEBHOOK_SECRET
    ))