from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: AnyUrl

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
