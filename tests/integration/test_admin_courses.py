"""Admin course endpoint tests (Admin Slice 1, Part B2 — masterplan §16.4).

Role gate (401/403/200), create (+FK validation), patch (allowlist + updated_at
bump + audit before/after), 404/409/422 paths, list filter/pagination.

Test courses use codes prefixed 'ZZ'; throwaway users prefixed 'authtest-'.
Teardown deletes test courses, then the admin's admin_actions (RESTRICT FK),
then the users.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

CODE = "ZZ001"


@pytest_asyncio.fixture
async def real_university_id(db_session: AsyncSession) -> int:
    # use a real university (the one 001A belongs to) so FK validation passes
    return (
        await db_session.execute(
            text("SELECT university_id FROM courses WHERE course_code = '001A'")
        )
    ).scalar_one()


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
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(text("DELETE FROM courses WHERE course_code LIKE 'ZZ%'"))
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


# ---- role gate ----

async def test_list_requires_token(client: AsyncClient):
    assert (await client.get("/api/admin/courses")).status_code == 401


async def test_list_rejects_student(client: AsyncClient, student_token: str):
    assert (await client.get("/api/admin/courses", headers=_auth(student_token))).status_code == 403


async def test_list_ok_and_joined(client: AsyncClient, admin_token: str):
    r = await client.get("/api/admin/courses?q=001A&limit=5", headers=_auth(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    a001 = next(i for i in body["items"] if i["course_code"] == "001A")
    assert a001["university_code"] is not None  # join populated


# ---- create ----

async def test_create_course(client: AsyncClient, admin_token: str, real_university_id: int, db_session: AsyncSession):
    r = await client.post(
        "/api/admin/courses",
        headers=_auth(admin_token),
        json={
            "course_code": CODE,
            "university_id": real_university_id,
            "name_en": "ZZ Test Degree",
            "selection_basis": "all_island_merit",
            "requires_aptitude_test": True,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["course_code"] == CODE
    assert body["selection_basis"] == "all_island_merit"
    assert body["requires_aptitude_test"] is True
    assert body["university_code"] is not None
    n = (
        await db_session.execute(
            text("SELECT count(*) FROM admin_actions WHERE action_type='course.create' AND target_id=:t"),
            {"t": CODE},
        )
    ).scalar_one()
    assert n == 1


async def test_create_duplicate_is_409(client: AsyncClient, admin_token: str, real_university_id: int):
    payload = {"course_code": CODE, "university_id": real_university_id, "name_en": "Dup"}
    assert (await client.post("/api/admin/courses", headers=_auth(admin_token), json=payload)).status_code == 201
    assert (await client.post("/api/admin/courses", headers=_auth(admin_token), json=payload)).status_code == 409


async def test_create_unknown_university_is_422(client: AsyncClient, admin_token: str):
    r = await client.post(
        "/api/admin/courses",
        headers=_auth(admin_token),
        json={"course_code": "ZZ777", "university_id": 999999, "name_en": "Orphan"},
    )
    assert r.status_code == 422


# ---- patch ----

async def test_patch_bumps_updated_at_and_logs(client: AsyncClient, admin_token: str, real_university_id: int, db_session: AsyncSession):
    await client.post(
        "/api/admin/courses",
        headers=_auth(admin_token),
        json={"course_code": CODE, "university_id": real_university_id, "name_en": "Before", "is_active": True},
    )
    before_ts = (
        await db_session.execute(text("SELECT updated_at FROM courses WHERE course_code=:c"), {"c": CODE})
    ).scalar_one()

    r = await client.patch(
        f"/api/admin/courses/{CODE}",
        headers=_auth(admin_token),
        json={"is_active": False, "name_en": "After"},
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False
    assert r.json()["name_en"] == "After"

    after_ts = (
        await db_session.execute(text("SELECT updated_at FROM courses WHERE course_code=:c"), {"c": CODE})
    ).scalar_one()
    assert after_ts > before_ts  # updated_at was bumped

    row = (
        await db_session.execute(
            text("SELECT before_value, after_value FROM admin_actions WHERE action_type='course.update' AND target_id=:t"),
            {"t": CODE},
        )
    ).first()
    assert row.before_value["is_active"] is True
    assert row.after_value["is_active"] is False
    assert row.after_value["name_en"] == "After"


async def test_patch_missing_is_404(client: AsyncClient, admin_token: str):
    r = await client.patch("/api/admin/courses/ZZ404", headers=_auth(admin_token), json={"is_active": False})
    assert r.status_code == 404


async def test_patch_invalid_selection_basis_is_422(client: AsyncClient, admin_token: str, real_university_id: int):
    await client.post(
        "/api/admin/courses",
        headers=_auth(admin_token),
        json={"course_code": CODE, "university_id": real_university_id, "name_en": "X"},
    )
    r = await client.patch(
        f"/api/admin/courses/{CODE}", headers=_auth(admin_token), json={"selection_basis": "bogus"}
    )
    assert r.status_code == 422  # Pydantic Literal rejects it before the DB


# ---- filter / pagination ----

async def test_filter_active_and_pagination(client: AsyncClient, admin_token: str):
    r = await client.get("/api/admin/courses?is_active=true&limit=3", headers=_auth(admin_token))
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) <= 3
    assert all(item["is_active"] is True for item in body["items"])
