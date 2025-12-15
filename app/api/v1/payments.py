from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.schemas.payments import CreatePaymentRequest, CreatePaymentResponse
from app.services.stripe_service import create_payment_intent, retrieve_event
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Payment


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(req: CreatePaymentRequest, db: AsyncSession = Depends(get_db)):
# add basic validation
    if req.amount_cents <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="amount must be > 0")
    intent = await create_payment_intent(req.amount_cents, req.currency, metadata={"purpose": "demo"})
    # persist minimal info
    db_payment = Payment(
    stripe_payment_intent_id=intent["id"],
    amount=req.amount_cents,
    currency=req.currency,
    status=intent["status"],
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)


    return {"client_secret": intent["client_secret"]}




@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = await retrieve_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        # Handle event types of interest
    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        # TODO: fulfill order, update DB, idempotency handling

    return {"status": "ok"}