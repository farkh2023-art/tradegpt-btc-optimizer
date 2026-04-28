from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "TradeGPT BTC Optimizer"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./tradegpt.db"

    AI_PROVIDER: str = "mock"  # openai | anthropic | mock
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # eToro integration — lecture seule uniquement
    ETORO_API_ENABLED: bool = False
    ETORO_API_BASE_URL: str = "https://public-api.etoro.com"
    ETORO_PUBLIC_API_KEY: Optional[str] = None
    ETORO_USER_KEY: Optional[str] = None
    ETORO_MODE: str = "read_only"
    ETORO_ALLOW_REAL_ORDERS: bool = False  # doit rester false — jamais modifier


settings = Settings()
