from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import payments
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="FastAPI Stripe Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments.router, prefix="/api/v1")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
