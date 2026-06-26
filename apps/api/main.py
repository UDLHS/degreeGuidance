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
    admin_requirements,
    auth,
    chat,
    eligibility,
    recommendations,
    reference,
)

app = FastAPI(
    title="Degree Guidance API",
    version="0.7.0",
    description="Sri Lankan university admissions guidance — eligibility + admin auth.",
)

app.include_router(chat.router)
app.include_router(eligibility.router)
app.include_router(recommendations.router)
app.include_router(reference.router)
app.include_router(auth.router)
app.include_router(admin_aliases.router)
app.include_router(admin_courses.router)
app.include_router(admin_ingestions.router)
app.include_router(admin_requirements.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/debug-db", tags=["meta"])
async def debug_db() -> dict:
    import traceback
    from sqlalchemy import text
    from core.db import engine
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return {"ok": True, "result": result.scalar()}
    except Exception as e:
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()}
