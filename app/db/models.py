from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    stripe_payment_intent_id = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="usd")
    status = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
