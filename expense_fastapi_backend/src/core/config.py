import os
from functools import lru_cache
from typing import List

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load env vars from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(..., description="SQLAlchemy-compatible database URL, e.g. postgresql+psycopg://user:pass@host:port/db")

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for signing tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, description="JWT access token expiration in minutes")

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"], description="List of allowed CORS origins")

    APP_NAME: str = Field("Expense Tracker API", description="FastAPI application name")
    APP_VERSION: str = Field("0.1.0", description="FastAPI application version")
    APP_DESCRIPTION: str = Field(
        "Backend API for handling authentication and expense tracking with PostgreSQL persistence.",
        description="App description for OpenAPI docs",
    )


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Get app settings with caching to avoid repeated environment parsing."""
    # Support comma-separated CORS origins in env
    cors_raw = os.getenv("CORS_ORIGINS")
    cors_list = [o.strip() for o in cors_raw.split(",")] if cors_raw else None

    data = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        "CORS_ORIGINS": cors_list if cors_list is not None else ["*"],
        "APP_NAME": os.getenv("APP_NAME", "Expense Tracker API"),
        "APP_VERSION": os.getenv("APP_VERSION", "0.1.0"),
        "APP_DESCRIPTION": os.getenv(
            "APP_DESCRIPTION",
            "Backend API for handling authentication and expense tracking with PostgreSQL persistence.",
        ),
    }
    return Settings(**data)
