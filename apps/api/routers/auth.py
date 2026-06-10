"""Auth router: POST /api/auth/login, GET /api/auth/me (Admin Slice 1 A2).

login verifies email+password and mints a JWT (any active user may obtain one;
authorization happens per-route via get_current_admin). Every attempt is logged
to auth_events. /me is a protected probe that returns the current admin — it is
also how the require_admin dependency is exercised.
"""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_admin, get_db
from core.config import settings
from core.models.auth import AuthEvent, User
from core.schemas.auth import CurrentUser, LoginRequest, TokenResponse
from core.security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _ip_hash(request: Request) -> str | None:
    if request.client is None:
        return None
    return hashlib.sha256(request.client.host.encode("utf-8")).hexdigest()


def _record(db: AsyncSession, *, user_id, email: str, event_type: str, request: Request) -> None:
    db.add(
        AuthEvent(
            user_id=user_id,
            email=email,
            event_type=event_type,
            ip_hash=_ip_hash(request),
            user_agent=request.headers.get("user-agent"),
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    email = payload.email.strip().lower()
    user = (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()

    if user is None or not user.is_active or not verify_password(
        payload.password, user.password_hash or ""
    ):
        _record(
            db,
            user_id=(user.user_id if user else None),
            email=email,
            event_type="login_failure",
            request=request,
        )
        await db.commit()
        # Same message whether the email is unknown or the password is wrong,
        # so we don't leak which accounts exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    token = create_access_token(subject=str(user.user_id), role=user.role)
    _record(db, user_id=user.user_id, email=email, event_type="login_success", request=request)
    await db.commit()
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        role=user.role,
    )


@router.get("/me", response_model=CurrentUser)
async def me(current: User = Depends(get_current_admin)) -> CurrentUser:
    return CurrentUser(
        user_id=str(current.user_id),
        email=current.email,
        display_name=current.display_name,
        role=current.role,
    )
