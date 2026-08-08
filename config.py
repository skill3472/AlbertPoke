from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DB_URL: str

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Captcha (Altcha)
    ALTCHA_HMAC_KEY: str
    ALTCHA_MAX_NUMBER: int = 100_000
    ALTCHA_CHALLENGE_EXPIRE_MINUTES: int = 10

    # Pokes
    POKE_RATE_LIMIT_SECONDS: int = 60

    # Web Push (VAPID)
    VAPID_PUBLIC_KEY: str
    VAPID_PRIVATE_KEY: str
    VAPID_SUBJECT: str

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / ".env")

settings = Settings()