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

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()