"""Application configuration."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "LLM Tracer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./llm_tracer.db"

    # PostgreSQL (alternative to DATABASE_URL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "llm_tracer"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-a-secure-random-key"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    def get_database_url(self) -> str:
        """Get the database URL, preferring DATABASE_URL if set."""
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL

        # Check if PostgreSQL env vars are set
        if os.getenv("POSTGRES_HOST"):
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        return self.DATABASE_URL


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
