"""FastAPI application entrypoint.

Mounts the eligibility router, the auth router (Admin Slice 1 A2), and a health
check. Run with: uvicorn apps.api.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers import (
    admin_aliases,
    admin_courses,
    admin_ingestions,
    auth,
    eligibility,
    recommendations,
    reference,
)

app = FastAPI(
    title="Degree Guidance API",
    version="0.7.0",
    description="Sri Lankan university admissions guidance — eligibility + admin auth.",
)

app.include_router(eligibility.router)
app.include_router(recommendations.router)
app.include_router(reference.router)
app.include_router(auth.router)
app.include_router(admin_aliases.router)
app.include_router(admin_courses.router)
app.include_router(admin_ingestions.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
