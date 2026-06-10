"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(..., description="Async DSN for the app (asyncpg)")
    database_url_sync: str = Field(..., description="Sync DSN for Alembic (psycopg2)")

    # Environment
    environment: str = Field(default="local")
    log_level: str = Field(default="INFO")


    # Auth / JWT (Admin Slice 1 A2)
    jwt_secret_key: str = Field(..., description="HS256 signing key for access tokens")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)
settings = Settings()
