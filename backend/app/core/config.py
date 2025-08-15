import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/bankapp"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "My First Bank App"
    DEBUG: bool = False  # Set to False for production

    # Limits
    MAX_DEPOSIT_AMOUNT_CENTS: int = 1000000  # $10,000
    MIN_DEPOSIT_AMOUNT_CENTS: int = 1  # $0.01

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with Heroku environment variables if available
        if os.getenv("DATABASE_URL"):
            # Heroku provides DATABASE_URL, but we need to convert it for asyncpg
            heroku_db_url = os.getenv("DATABASE_URL")
            if heroku_db_url.startswith("postgres://"):
                # Convert postgres:// to postgresql+asyncpg://
                self.DATABASE_URL = heroku_db_url.replace(
                    "postgres://", "postgresql+asyncpg://", 1
                )

        if os.getenv("SECRET_KEY"):
            self.SECRET_KEY = os.getenv("SECRET_KEY")

        # Set DEBUG based on environment
        if os.getenv("DEBUG"):
            self.DEBUG = os.getenv("DEBUG").lower() == "true"


settings = Settings()
