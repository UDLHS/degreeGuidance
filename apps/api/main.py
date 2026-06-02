"""FastAPI application entrypoint.

Phase 6 mounts a single router (eligibility) plus a health check. Run with:
    uvicorn apps.api.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers import eligibility

app = FastAPI(
    title="Degree Guidance API",
    version="0.6.0",
    description="Sri Lankan university admissions guidance — eligibility engine.",
)

app.include_router(eligibility.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
