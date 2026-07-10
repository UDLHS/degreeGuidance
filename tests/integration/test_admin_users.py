"""Admin-account management (Phase 3 plan gate).

Covers the full lifecycle the plan requires: an admin creates a second admin →
the new admin can log in and has equal access → deactivation blocks both login
and live tokens immediately → self-deactivation is refused → duplicate email
409 → everything audited. Sentinel emails (authtest-adm-*) cleaned up fully.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

PREFIX = "authtest-adm-"


@pytest_asyncio.fixture
async def creator(db_session: AsyncSession):
    """The acting admin (simulates the signed-in panel user)."""
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"{PREFIX}creator-{uid.hex[:8]}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield {"id": uid, "token": create_access_token(subject=str(uid), role="admin")}
    await db_session.execute(
        text(
            "DELETE FROM admin_actions WHERE admin_user_id IN "
            "(SELECT user_id FROM users WHERE email LIKE :p)"
        ),
        {"p": f"{PREFIX}%"},
    )
    await db_session.execute(
        text("DELETE FROM auth_events WHERE email LIKE :p"), {"p": f"{PREFIX}%"}
    )
    await db_session.execute(text("DELETE FROM users WHERE email LIKE :p"), {"p": f"{PREFIX}%"})
    await db_session.commit()


async def test_requires_auth(client: AsyncClient):
    assert (await client.get("/api/admin/users")).status_code == 401


async def test_full_admin_lifecycle(client: AsyncClient, creator):
    h = {"Authorization": f"Bearer {creator['token']}"}
    new_email = f"{PREFIX}new-{uuid.uuid4().hex[:8]}@example.com"

    # 1. create
    r = await client.post(
        "/api/admin/users",
        json={"email": new_email, "display_name": "Second Admin", "password": "strongpass1"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["email"] == new_email
    assert created["role"] == "admin" and created["is_active"] is True
    new_id = created["user_id"]

    # appears in the list
    listed = (await client.get("/api/admin/users", headers=h)).json()
    assert any(u["user_id"] == new_id for u in listed["items"])

    # 2. the new admin can log in and has EQUAL access (D5)
    login = await client.post(
        "/api/auth/login", json={"email": new_email, "password": "strongpass1"}
    )
    assert login.status_code == 200
    new_token = login.json()["access_token"]
    h2 = {"Authorization": f"Bearer {new_token}"}
    assert (await client.get("/api/admin/users", headers=h2)).status_code == 200
    assert (await client.get("/api/admin/conversations", headers=h2)).status_code == 200

    # 3. duplicate email → 409
    dup = await client.post(
        "/api/admin/users",
        json={"email": new_email, "password": "whatever123"},
        headers=h,
    )
    assert dup.status_code == 409

    # 4. deactivate → login refused AND the live token dies immediately
    r = await client.patch(f"/api/admin/users/{new_id}", json={"is_active": False}, headers=h)
    assert r.status_code == 200 and r.json()["is_active"] is False
    relogin = await client.post(
        "/api/auth/login", json={"email": new_email, "password": "strongpass1"}
    )
    assert relogin.status_code == 401
    assert (await client.get("/api/admin/users", headers=h2)).status_code == 401

    # 5. reactivate → login works again
    r = await client.patch(f"/api/admin/users/{new_id}", json={"is_active": True}, headers=h)
    assert r.status_code == 200 and r.json()["is_active"] is True
    assert (
        await client.post("/api/auth/login", json={"email": new_email, "password": "strongpass1"})
    ).status_code == 200


async def test_cannot_deactivate_self(client: AsyncClient, creator):
    h = {"Authorization": f"Bearer {creator['token']}"}
    r = await client.patch(
        f"/api/admin/users/{creator['id']}", json={"is_active": False}, headers=h
    )
    assert r.status_code == 422


async def test_students_are_not_managed_here(client: AsyncClient, creator, db_session: AsyncSession):
    """A student account must be invisible to (and untouchable by) this API."""
    h = {"Authorization": f"Bearer {creator['token']}"}
    sid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, role, is_active) "
            "VALUES (:id, :em, 'student', true)"
        ),
        {"id": sid, "em": f"{PREFIX}student-{sid.hex[:8]}@example.com"},
    )
    await db_session.commit()
    listed = (await client.get("/api/admin/users", headers=h)).json()
    assert not any(u["user_id"] == str(sid) for u in listed["items"])
    r = await client.patch(f"/api/admin/users/{sid}", json={"is_active": False}, headers=h)
    assert r.status_code == 404


async def test_creation_is_audited(client: AsyncClient, creator, db_session: AsyncSession):
    h = {"Authorization": f"Bearer {creator['token']}"}
    email = f"{PREFIX}audit-{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/admin/users", json={"email": email, "password": "strongpass1"}, headers=h
    )
    assert r.status_code == 201
    n = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions "
                "WHERE action_type = 'admin_user.create' AND target_id = :t"
            ),
            {"t": r.json()["user_id"]},
        )
    ).scalar()
    assert n == 1
    # the audit row must never contain the password
    payload = (
        await db_session.execute(
            text(
                "SELECT after_value::text FROM admin_actions "
                "WHERE action_type = 'admin_user.create' AND target_id = :t"
            ),
            {"t": r.json()["user_id"]},
        )
    ).scalar()
    assert "strongpass1" not in (payload or "")