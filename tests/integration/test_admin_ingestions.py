"""Admin ingestion endpoint tests (Admin Slice 1, Part C1 — masterplan §16.4).

Covers the JWT role gate (401/403) on all three routes, the CSV-direct upload
happy path (Step 4 runs, a cutoff row appears, an admin_actions row is written),
the partial-failure path (unknown alias -> parse_errors surfaced via GET detail),
upload-safety rejections (non-CSV 415, oversized 413, bad year 422), and the
list/detail reads.

IMPORTANT — why a sentinel year + manual teardown:
ingest_zscores() opens its OWN AsyncSessionLocal, so it commits to the real dev
DB on a separate connection that the test's get_db override cannot intercept.
So every upload here uses exam_year=2030 (the max the loader/Form accept, and a
year no real near-term handbook will use — only 2023 is loaded) and a throwaway
'authtest-' admin, and teardown deletes:
  - z_score_cutoffs WHERE year = 2030
  - ingestion_runs   WHERE year = 2030   (parse_errors cascade via FK)
  - the test admin's admin_actions rows (admin_user_id RESTRICT FK)
  - the test users
The real 2023 data is never touched.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

SENTINEL_YEAR = 2030
KNOWN_ALIAS = "MEDICINE (University of Colombo)"  # resolves to course 001A
KNOWN_DISTRICT = "Colombo"  # normalizes to districts.code = COLOMBO


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
    # teardown: sentinel cutoffs -> sentinel runs (cascade parse_errors)
    # -> admin_actions (RESTRICT) -> user
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM ingestion_runs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(
        text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid}
    )
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


@pytest_asyncio.fixture(autouse=True)
async def _dispose_loader_engine():
    """ingest_zscores() uses the shared (pooled) core.db.engine, not the per-test
    NullPool engine. Dispose it after each test — on this test's still-open loop —
    so a pooled connection never gets reused on the next test's event loop
    ('Event loop is closed')."""
    yield
    from core.db import engine as loader_engine

    await loader_engine.dispose()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _upload(content: str, *, year: int = SENTINEL_YEAR, filename: str = "cutoffs.csv",
            content_type: str = "text/csv") -> dict:
    """Build the kwargs for a multipart POST to /api/admin/ingestions."""
    return {
        "files": {"file": (filename, content.encode("utf-8"), content_type)},
        "data": {"exam_year": str(year)},
    }


# ---- role gate ----

async def test_post_requires_token(client: AsyncClient):
    r = await client.post("/api/admin/ingestions", **_upload(f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5"))
    assert r.status_code == 401


async def test_post_rejects_student(client: AsyncClient, student_token: str):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(student_token),
        **_upload(f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5"),
    )
    assert r.status_code == 403


async def test_list_requires_token(client: AsyncClient):
    assert (await client.get("/api/admin/ingestions")).status_code == 401


async def test_list_rejects_student(client: AsyncClient, student_token: str):
    r = await client.get("/api/admin/ingestions", headers=_auth(student_token))
    assert r.status_code == 403


async def test_detail_requires_token(client: AsyncClient):
    r = await client.get(f"/api/admin/ingestions/{uuid.uuid4()}")
    assert r.status_code == 401


# ---- happy path ----

async def test_upload_happy_path(client: AsyncClient, admin_token: str, db_session: AsyncSession):
    csv = f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5000\n"
    r = await client.post("/api/admin/ingestions", headers=_auth(admin_token), **_upload(csv))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "success"
    assert body["processed"] == 1
    assert body["failed"] == 0
    run_id = body["run_id"]

    # the cutoff row landed under the sentinel year for course 001A
    cutoff = (
        await db_session.execute(
            text(
                "SELECT z_score FROM z_score_cutoffs "
                "WHERE year = :y AND course_code = '001A'"
            ),
            {"y": SENTINEL_YEAR},
        )
    ).first()
    assert cutoff is not None
    assert float(cutoff.z_score) == 2.5

    # the upload was audited
    audited = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions "
                "WHERE action_type = 'ingestion.create' "
                "AND target_table = 'ingestion_runs' AND target_id = :t"
            ),
            {"t": run_id},
        )
    ).scalar_one()
    assert audited == 1


# ---- partial failure -> parse_errors ----

async def test_upload_partial_surfaces_parse_errors(
    client: AsyncClient, admin_token: str
):
    csv = f"district,ZZTEST_UNKNOWN_COURSE_LABEL\n{KNOWN_DISTRICT},1.2345\n"
    r = await client.post("/api/admin/ingestions", headers=_auth(admin_token), **_upload(csv))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "partial"
    assert body["failed"] >= 1
    run_id = body["run_id"]

    detail = await client.get(f"/api/admin/ingestions/{run_id}", headers=_auth(admin_token))
    assert detail.status_code == 200
    d = detail.json()
    assert d["parse_error_count"] >= 1
    assert any(e["error_type"] == "unknown_course_alias" for e in d["parse_errors"])


# ---- upload safety ----

async def test_upload_rejects_non_csv(client: AsyncClient, admin_token: str):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(admin_token),
        **_upload("district,x\nColombo,1.0", filename="data.txt"),
    )
    assert r.status_code == 415


async def test_upload_rejects_oversized(client: AsyncClient, admin_token: str):
    big = "x" * (5 * 1024 * 1024 + 16)  # just over the 5 MB cap
    r = await client.post(
        "/api/admin/ingestions", headers=_auth(admin_token), **_upload(big)
    )
    assert r.status_code == 413


async def test_upload_rejects_bad_year(client: AsyncClient, admin_token: str):
    r = await client.post(
        "/api/admin/ingestions",
        headers=_auth(admin_token),
        **_upload(f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5", year=1999),
    )
    assert r.status_code == 422


# ---- list / detail reads ----

async def test_list_returns_created_run(client: AsyncClient, admin_token: str):
    csv = f"district,{KNOWN_ALIAS}\n{KNOWN_DISTRICT},2.5000\n"
    created = await client.post("/api/admin/ingestions", headers=_auth(admin_token), **_upload(csv))
    run_id = created.json()["run_id"]

    r = await client.get(
        f"/api/admin/ingestions?year={SENTINEL_YEAR}", headers=_auth(admin_token)
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert any(item["run_id"] == run_id for item in body["items"])


async def test_detail_unknown_run_is_404(client: AsyncClient, admin_token: str):
    r = await client.get(f"/api/admin/ingestions/{uuid.uuid4()}", headers=_auth(admin_token))
    assert r.status_code == 404
