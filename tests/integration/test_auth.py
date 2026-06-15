"""Auth mechanism tests (Admin Slice 1 A2).

Covers: password hashing, JWT roundtrip, the auth_events table, login
success/failure, the require_admin dependency (401 no token / 403 student /
200 admin) via GET /api/auth/me, and auth_event logging.

Test users use emails prefixed 'authtest-' and are cleaned up (with their
auth_events) after each test by the autouse fixture below.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.auth import User
from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

PW = "Sup3rSecret!"


@pytest_asyncio.fixture(autouse=True)
async def _clean_auth_test_rows(db_session: AsyncSession):
    yield
    await db_session.execute(
        text("DELETE FROM auth_events WHERE email LIKE 'authtest-%'")
    )
    await db_session.execute(text("DELETE FROM users WHERE email LIKE 'authtest-%'"))
    await db_session.commit()


async def _make_user(db: AsyncSession, role: str) -> User:
    user = User(
        email=f"authtest-{uuid.uuid4()}@example.com",
        display_name="Auth Test",
        password_hash=hash_password(PW),
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ---- pure crypto (no DB) ----

def test_password_roundtrip():
    h = hash_password(PW)
    assert h.startswith("$2b$")
    assert verify_password(PW, h) is True
    assert verify_password("wrong", h) is False
    assert verify_password("x", "") is False


def test_token_roundtrip():
    tok = create_access_token(subject="abc", role="admin")
    claims = decode_access_token(tok)
    assert claims["sub"] == "abc"
    assert claims["role"] == "admin"
    assert claims["type"] == "access"


# ---- schema ----

async def test_auth_events_table_exists(db_session: AsyncSession):
    val = (
        await db_session.execute(text("SELECT to_regclass('public.auth_events')"))
    ).scalar_one()
    assert val == "auth_events"


# ---- login + require_admin via /me ----

async def test_login_success_and_me(client: AsyncClient, db_session: AsyncSession):
    user = await _make_user(db_session, role="admin")
    r = await client.post("/api/auth/login", json={"email": user.email, "password": PW})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin"
    token = body["access_token"]

    r2 = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200, r2.text
    assert r2.json()["email"] == user.email
    assert r2.json()["role"] == "admin"


async def test_login_wrong_password_is_401(client: AsyncClient, db_session: AsyncSession):
    user = await _make_user(db_session, role="admin")
    r = await client.post(
        "/api/auth/login", json={"email": user.email, "password": "nope"}
    )
    assert r.status_code == 401
    # a login_failure row was recorded for this email
    n = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM auth_events "
                "WHERE email = :e AND event_type = 'login_failure'"
            ),
            {"e": user.email},
        )
    ).scalar_one()
    assert n == 1


async def test_login_unknown_email_is_401(client: AsyncClient):
    r = await client.post(
        "/api/auth/login",
        json={"email": "authtest-nobody@example.com", "password": PW},
    )
    assert r.status_code == 401


async def test_me_without_token_is_401(client: AsyncClient):
    r = await client.get("/api/auth/me")
    assert r.status_code == 401


async def test_me_rejects_student_role_403(client: AsyncClient, db_session: AsyncSession):
    user = await _make_user(db_session, role="student")
    login = await client.post(
        "/api/auth/login", json={"email": user.email, "password": PW}
    )
    assert login.status_code == 200  # students CAN log in
    token = login.json()["access_token"]
    r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403  # but cannot reach an admin-gated route


async def test_me_rejects_garbage_token_401(client: AsyncClient):
    r = await client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"}
    )
    assert r.status_code == 401


async def test_login_success_logs_event(client: AsyncClient, db_session: AsyncSession):
    user = await _make_user(db_session, role="admin")
    await client.post("/api/auth/login", json={"email": user.email, "password": PW})
    n = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM auth_events "
                "WHERE email = :e AND event_type = 'login_success'"
            ),
            {"e": user.email},
        )
    ).scalar_one()
    assert n == 1
