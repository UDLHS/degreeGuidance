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
    jwt_access_token_expire_minutes: int = Field(default=720)  # 12h — admin panel has no token refresh

    # Redis / background jobs (Arq)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis DSN for the Arq broker and cache",
    )

    # Ingestion working directory — uploaded PDFs + extracted CSVs (C2)
    ingestion_work_dir: str = Field(default="data/ingestion_work")

    # Arq job timeout. Arq's default is 300 s — the 15 MB 2025 handbook needs
    # ~8-10 min on a free-tier CPU (the 5.9 MB 2024 book measured 221 s), so
    # extractions were killed mid-run. Sized for books several times larger
    # than any seen so far; a yearly admin operation can afford the wait.
    worker_job_timeout_seconds: int = Field(default=3600)

    # Permanent per-year archive: pre-promote snapshots + promoted artifacts
    # (raw PDF, final CSV, overrides/unmapped) — Phase 7 of the Phase-2 plan;
    # also the retention layer future year-comparison chat features read.
    archive_dir: str = Field(default="data/archive")

    # Browser origins allowed to call the API directly (comma-separated).
    # Only the handbook upload goes browser->API: Vercel caps proxied request
    # bodies at 4.5 MB, and handbooks are 6-15 MB, so the file bypasses the
    # BFF using a short-lived ticket. Everything else stays same-origin.
    # Prod sets CORS_ALLOW_ORIGINS to the deployed web app's origin.
    cors_allow_origins: str = Field(default="http://localhost:3000")

    # W1 abuse/cost guards. Chat is the expensive path (Gemini + web search per
    # message); the general public tier is cheap DB reads. The daily budget
    # bounds total Gemini spend across chat + interest embeddings + the admin
    # sandbox — when exhausted, chat 429s politely and interest-ranking
    # degrades to inert (eligibility itself never needs Gemini).
    rate_limit_chat_per_minute: int = Field(default=8)
    rate_limit_public_per_minute: int = Field(default=120)
    gemini_daily_call_budget: int = Field(default=1500)

    # Gemini API (RAG + chatbot)
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_embedding_model: str = Field(default="models/gemini-embedding-001")
    gemini_chat_model: str = Field(default="models/gemini-3.1-flash-lite")
    gemini_embedding_dim: int = Field(default=768)


settings = Settings()
