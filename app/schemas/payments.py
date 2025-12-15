from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    amount_cents: int
    currency: str = "usd"


class CreatePaymentResponse(BaseModel):
    client_secret: str