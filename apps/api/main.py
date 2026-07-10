"""FastAPI application entrypoint.

Mounts the eligibility router, the auth router (Admin Slice 1 A2), and a health
check. Run with: uvicorn apps.api.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers import (
    admin_agent,
    admin_aliases,
    admin_conversations,
    admin_courses,
    admin_cutoffs,
    admin_factsheets,
    admin_ingestions,
    admin_requirements,
    admin_users,
    auth,
    chat,
    eligibility,
    recommendations,
    reference,
    student,
)

app = FastAPI(
    title="Degree Guidance API",
    version="0.7.0",
    description="Sri Lankan university admissions guidance — eligibility + admin auth.",
)

app.include_router(chat.router)
app.include_router(student.router)
app.include_router(eligibility.router)
app.include_router(recommendations.router)
app.include_router(reference.router)
app.include_router(auth.router)
app.include_router(admin_agent.router)
app.include_router(admin_aliases.router)
app.include_router(admin_conversations.router)
app.include_router(admin_courses.router)
app.include_router(admin_cutoffs.router)
app.include_router(admin_factsheets.router)
app.include_router(admin_ingestions.router)
app.include_router(admin_requirements.router)
app.include_router(admin_users.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
