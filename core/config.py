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

    # Redis / background jobs (Arq)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis DSN for the Arq broker and cache",
    )

    # Ingestion working directory — uploaded PDFs + extracted CSVs (C2)
    ingestion_work_dir: str = Field(default="data/ingestion_work")

    # Gemini API (RAG + chatbot)
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_embedding_model: str = Field(default="models/gemini-embedding-001")
    gemini_chat_model: str = Field(default="models/gemini-2.5-flash")
    gemini_embedding_dim: int = Field(default=768)


settings = Settings()
