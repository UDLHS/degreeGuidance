"""Admin alias endpoint tests (Admin Slice 1, Part B1 — masterplan §16.4).

Covers the JWT role check (401/403/200), the full alias CRUD + the verify flow,
admin_actions logging on every mutation, 409 on duplicate, 422 on unknown course,
and pagination.

Test data: aliases attached to course 001A with alias_text prefixed 'ZZTEST_';
a throwaway admin/student user prefixed 'authtest-'. Teardown deletes test
aliases, then the admin's admin_actions rows (RESTRICT FK), then the users.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

COURSE = "001A"
PFX = "ZZTEST_"


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"authtest-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    token = create_access_token(subject=str(uid), role="admin")
    yield token
    # teardown order matters: aliases -> admin_actions (RESTRICT) -> user
    await db_session.execute(text("DELETE FROM course_aliases WHERE alias_text LIKE :p"), {"p": f"{PFX}%"})
    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest_asyncio.fixture
async def student_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'student', true)"
        ),
        {"id": uid, "em": f"authtest-student-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="student")
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _count_actions(db: AsyncSession, action_type: str, target_id) -> int:
    return (
        await db.execute(
            text(
                "SELECT count(*) FROM admin_actions "
                "WHERE action_type = :a AND target_table = 'course_aliases' AND target_id = :t"
            ),
            {"a": action_type, "t": str(target_id)},
        )
    ).scalar_one()


# ---- role gate ----

async def test_list_requires_token(client: AsyncClient):
    assert (await client.get("/api/admin/aliases")).status_code == 401


async def test_list_rejects_student(client: AsyncClient, student_token: str):
    r = await client.get("/api/admin/aliases", headers=_auth(student_token))
    assert r.status_code == 403


async def test_list_ok_for_admin(client: AsyncClient, admin_token: str):
    r = await client.get("/api/admin/aliases?limit=5", headers=_auth(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 530  # seeded aliases (530 after migration 21 removed the 006K phantom)
    assert len(body["items"]) == 5


# ---- create ----

async def test_create_logs_action(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    r = await client.post(
        "/api/admin/aliases",
        headers=_auth(admin_token),
        json={"course_code": COURSE, "alias_text": f"{PFX}new_alias", "is_verified": False},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["course_code"] == COURSE
    assert body["is_verified"] is False
    assert await _count_actions(db_session, "alias.create", body["alias_id"]) == 1


async def test_create_duplicate_is_409(client: AsyncClient, admin_token: str):
    payload = {"course_code": COURSE, "alias_text": f"{PFX}dup", "is_verified": True}
    first = await client.post("/api/admin/aliases", headers=_auth(admin_token), json=payload)
    assert first.status_code == 201
    second = await client.post("/api/admin/aliases", headers=_auth(admin_token), json=payload)
    assert second.status_code == 409


async def test_create_unknown_course_is_422(client: AsyncClient, admin_token: str):
    r = await client.post(
        "/api/admin/aliases",
        headers=_auth(admin_token),
        json={"course_code": "ZZZZ", "alias_text": f"{PFX}orphan"},
    )
    assert r.status_code == 422


# ---- patch / verify flow ----

async def test_patch_verify_flow(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    created = await client.post(
        "/api/admin/aliases",
        headers=_auth(admin_token),
        json={"course_code": COURSE, "alias_text": f"{PFX}to_verify", "is_verified": False},
    )
    alias_id = created.json()["alias_id"]
    r = await client.patch(
        f"/api/admin/aliases/{alias_id}", headers=_auth(admin_token), json={"is_verified": True}
    )
    assert r.status_code == 200
    assert r.json()["is_verified"] is True
    # the update action recorded before=false, after=true
    row = (
        await db_session.execute(
            text(
                "SELECT before_value, after_value FROM admin_actions "
                "WHERE action_type = 'alias.update' AND target_id = :t"
            ),
            {"t": str(alias_id)},
        )
    ).first()
    assert row is not None
    assert row.before_value["is_verified"] is False
    assert row.after_value["is_verified"] is True


async def test_patch_missing_is_404(client: AsyncClient, admin_token: str):
    r = await client.patch(
        "/api/admin/aliases/999999999", headers=_auth(admin_token), json={"is_verified": True}
    )
    assert r.status_code == 404


# ---- delete ----

async def test_delete_logs_and_removes(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    created = await client.post(
        "/api/admin/aliases",
        headers=_auth(admin_token),
        json={"course_code": COURSE, "alias_text": f"{PFX}to_delete"},
    )
    alias_id = created.json()["alias_id"]
    r = await client.delete(f"/api/admin/aliases/{alias_id}", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json()["deleted"] == alias_id
    assert await _count_actions(db_session, "alias.delete", alias_id) == 1
    # row is gone
    gone = (
        await db_session.execute(
            text("SELECT 1 FROM course_aliases WHERE alias_id = :id"), {"id": alias_id}
        )
    ).first()
    assert gone is None


async def test_delete_missing_is_404(client: AsyncClient, admin_token: str):
    r = await client.delete("/api/admin/aliases/999999999", headers=_auth(admin_token))
    assert r.status_code == 404


# ---- pagination + filter ----

async def test_filter_by_course_and_pagination(client: AsyncClient, admin_token: str):
    r = await client.get(f"/api/admin/aliases?course_code={COURSE}&limit=1", headers=_auth(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) <= 1
    assert all(item["course_code"] == COURSE for item in body["items"])
