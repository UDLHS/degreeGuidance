"""Admin-account management (Phase 3 of docs/PHASE2_STUDENT_ADMIN_PLAN.md).

GET   /api/admin/users        — list admin accounts (+ last login from auth_events)
POST  /api/admin/users        — create a new admin (email + password), audited
PATCH /api/admin/users/{id}   — deactivate / reactivate (never delete), audited

Plan decision D5: all admins have equal permissions (get_current_admin already
treats 'admin' and 'superadmin' identically), so any admin may manage admins.
Safety: you cannot deactivate yourself; deactivation takes effect immediately
because both /login and get_current_admin check is_active on every request.
Passwords are bcrypt-hashed (core.security.hash_password) and never logged —
audit rows record the account change, not the credential.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from core.models.auth import User
from core.security import hash_password

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:users"],
    dependencies=[Depends(get_current_admin)],
)


class AdminUserOut(BaseModel):
    user_id: str
    email: str
    display_name: str | None
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None


class AdminUserListResponse(BaseModel):
    total: int
    items: list[AdminUserOut]


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AdminUserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    display_name: str | None = Field(default=None, max_length=150)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Enter a valid email address")
        return v


class AdminUserUpdate(BaseModel):
    is_active: bool


_LIST_SQL = """
    SELECT u.user_id, u.email, u.display_name, u.role, u.is_active, u.created_at,
           (SELECT max(e.created_at) FROM auth_events e
             WHERE e.user_id = u.user_id AND e.event_type = 'login_success') AS last_login
    FROM users u
    WHERE u.role IN ('admin', 'superadmin')
"""


def _row_to_out(r) -> AdminUserOut:
    return AdminUserOut(
        user_id=str(r.user_id),
        email=r.email,
        display_name=r.display_name,
        role=r.role,
        is_active=r.is_active,
        created_at=r.created_at,
        last_login=r.last_login,
    )


@router.get("/users", response_model=AdminUserListResponse)
async def list_admins(db: AsyncSession = Depends(get_db)) -> AdminUserListResponse:
    rows = (await db.execute(text(_LIST_SQL + " ORDER BY u.created_at"))).all()
    return AdminUserListResponse(total=len(rows), items=[_row_to_out(r) for r in rows])


@router.post("/users", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
async def create_admin(
    payload: AdminUserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AdminUserOut:
    email = payload.email.strip().lower()
    existing = (
        await db.execute(text("SELECT 1 FROM users WHERE email = :e"), {"e": email})
    ).first()
    if existing:
        # Also covers an existing STUDENT with this email — we never silently
        # convert a student account into an admin; pick a different email.
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already in use")

    user = User(
        email=email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await log_admin_action(
        db, admin=admin, action_type="admin_user.create",
        target_table="users", target_id=str(user.user_id),
        before=None, after={"email": email, "role": "admin", "is_active": True},
        request=request,
    )
    await db.commit()
    row = (
        await db.execute(text(_LIST_SQL + " AND u.user_id = :id"), {"id": user.user_id})
    ).first()
    return _row_to_out(row)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
async def update_admin(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AdminUserOut:
    target = await db.get(User, user_id)
    if target is None or target.role not in ("admin", "superadmin"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Admin account not found")
    if target.user_id == admin.user_id and payload.is_active is False:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="You cannot deactivate your own account — ask another admin.",
        )

    before = {"is_active": target.is_active}
    target.is_active = payload.is_active
    await log_admin_action(
        db, admin=admin,
        action_type="admin_user.deactivate" if not payload.is_active else "admin_user.reactivate",
        target_table="users", target_id=str(user_id),
        before=before, after={"is_active": payload.is_active}, request=request,
        notes=target.email,
    )
    await db.commit()
    row = (
        await db.execute(text(_LIST_SQL + " AND u.user_id = :id"), {"id": user_id})
    ).first()
    return _row_to_out(row)
