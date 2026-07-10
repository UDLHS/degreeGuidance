"""Factsheet manager + DB-sourced indexing (Phase 5 plan gate).

Sentinel isolation: a dedicated inactive course (998Z / number '998') carries
all mutations; the Gemini embed call is stubbed; the reindex enqueue is
monkeypatched (no Redis needed). Real factsheet rows are only read.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.worker.jobs.index_factsheets import index_course
from core.security import create_access_token, hash_password

PREFIX = "authtest-fs-"
SENTINEL_CODE = "998Z"
SENTINEL_NUMBER = "998"


class _FakeEmbedResult:
    class _E:
        values = [0.0] * 768

    embeddings = [_E()]


class _FakeModels:
    def embed_content(self, **kwargs):
        return _FakeEmbedResult()


class _FakeClient:
    models = _FakeModels()


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"{PREFIX}{uid.hex[:8]}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(
        text(
            "DELETE FROM admin_actions WHERE admin_user_id IN "
            "(SELECT user_id FROM users WHERE email LIKE :p)"
        ),
        {"p": f"{PREFIX}%"},
    )
    await db_session.execute(text("DELETE FROM users WHERE email LIKE :p"), {"p": f"{PREFIX}%"})
    await db_session.commit()


async def _purge_sentinel(db: AsyncSession) -> None:
    await db.rollback()  # clear any aborted transaction from a failed test body
    await db.execute(
        text(
            "DELETE FROM chunks WHERE source_id IN "
            "(SELECT source_id FROM document_sources WHERE course_number = :n)"
        ),
        {"n": SENTINEL_NUMBER},
    )
    await db.execute(
        text("DELETE FROM document_sources WHERE course_number = :n"), {"n": SENTINEL_NUMBER}
    )
    await db.execute(
        text("DELETE FROM factsheets WHERE course_number = :n"), {"n": SENTINEL_NUMBER}
    )
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": SENTINEL_CODE})
    await db.commit()


@pytest_asyncio.fixture
async def sentinel_course(db_session: AsyncSession):
    await _purge_sentinel(db_session)  # self-heal any leftover from a crashed run
    uni = (await db_session.execute(text("SELECT university_id FROM universities LIMIT 1"))).scalar()
    await db_session.execute(
        text(
            "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
            "VALUES (:c, :n, :u, 'Factsheet Test Course', false)"
        ),
        {"c": SENTINEL_CODE, "n": SENTINEL_NUMBER, "u": uni},
    )
    await db_session.commit()
    yield SENTINEL_NUMBER
    await _purge_sentinel(db_session)


@pytest_asyncio.fixture(autouse=True)
def _no_redis(monkeypatch):
    """Router auto-reindex enqueue → recorder (no Redis)."""
    calls: list[str] = []

    async def _fake(*, course_number: str):
        calls.append(course_number)

    monkeypatch.setattr(
        "apps.api.routers.admin_factsheets.enqueue_index_factsheet", _fake
    )
    yield calls


async def test_migration_seeded_from_files(db_session: AsyncSession):
    n = (await db_session.execute(text("SELECT count(*) FROM factsheets"))).scalar()
    assert n >= 100  # the 129 git factsheets (allow drift as admins add more)
    ok = (
        await db_session.execute(
            text("SELECT content_hash = encode(sha256(content::bytea), 'hex') FROM factsheets LIMIT 1")
        )
    ).scalar()
    assert ok is True  # stored hash really is the content's sha256


async def test_coverage_list_shape(client: AsyncClient, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get("/api/admin/factsheets", headers=h)
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 100
    statuses = {i["index_status"] for i in d["items"]}
    assert statuses <= {"missing", "not_indexed", "stale", "indexed"}
    # every item is an ACTIVE catalog number — derived from the data, so a
    # future handbook year's new courses appear here automatically
    assert all(i["course_number"] for i in d["items"])


async def test_create_update_versioning_and_audit(
    client: AsyncClient, admin_token, sentinel_course, _no_redis, db_session: AsyncSession
):
    h = {"Authorization": f"Bearer {admin_token}"}
    body = "# Test Course\n\n## Overview\n\n" + "sentinel factsheet content " * 5

    # create (v1) + auto-reindex enqueued
    r = await client.put(
        f"/api/admin/factsheets/{sentinel_course}", json={"content": body}, headers=h
    )
    assert r.status_code == 200, r.text
    assert r.json()["version"] == 1
    assert _no_redis == [sentinel_course]

    # no-op save: same content → no version bump, no reindex
    r2 = await client.put(
        f"/api/admin/factsheets/{sentinel_course}", json={"content": body}, headers=h
    )
    assert r2.json()["version"] == 1
    assert _no_redis == [sentinel_course]

    # real edit → v2 + reindex + audit
    r3 = await client.put(
        f"/api/admin/factsheets/{sentinel_course}",
        json={"content": body + "\n\n## New Section\n\nedited"},
        headers=h,
    )
    assert r3.json()["version"] == 2
    assert _no_redis == [sentinel_course, sentinel_course]
    kinds = (
        await db_session.execute(
            text(
                "SELECT action_type FROM admin_actions WHERE target_table='factsheets' "
                "AND target_id=:t ORDER BY action_id"
            ),
            {"t": sentinel_course},
        )
    ).scalars().all()
    assert kinds == ["factsheet.create", "factsheet.update"]

    # unknown course number rejected
    bad = await client.put(
        "/api/admin/factsheets/000", json={"content": body}, headers=h
    )
    assert bad.status_code == 422


async def test_index_course_from_db_with_stub_embeddings(
    sentinel_course, db_session: AsyncSession
):
    import hashlib

    content = (
        "# Test Course\n\n## Overview\n\nsome overview text here\n\n"
        "## Careers\n\ncareer text here"
    )
    await db_session.execute(
        text(
            "INSERT INTO factsheets (course_number, content, content_hash) "
            "VALUES (:n, :c, :h)"
        ),
        {"n": sentinel_course, "c": content,
         "h": hashlib.sha256(content.encode()).hexdigest()},
    )
    await db_session.commit()

    chunks, skipped = await index_course(db_session, _FakeClient(), sentinel_course)
    await db_session.commit()
    # 3 = the H1 title block (chunk 0, headingless — same as every production
    # factsheet) + Overview + Careers
    assert not skipped and chunks == 3

    rows = (
        await db_session.execute(
            text(
                "SELECT ds.title, ds.file_path, "
                "(SELECT count(*) FROM chunks c WHERE c.source_id = ds.source_id) "
                "FROM document_sources ds WHERE ds.course_number = :n"
            ),
            {"n": sentinel_course},
        )
    ).all()
    assert len(rows) == 1
    assert rows[0][0] == "Test Course"
    assert rows[0][1] == f"db:factsheets/{sentinel_course}"
    assert rows[0][2] == 3

    # second run with unchanged content → idempotent skip
    chunks2, skipped2 = await index_course(db_session, _FakeClient(), sentinel_course)
    assert skipped2 and chunks2 == 0

    # changed content → replaced (still exactly one source row)
    new_content = content + "\n\n## More\n\nmore text"
    await db_session.execute(
        text(
            "UPDATE factsheets SET content = :c, content_hash = :h WHERE course_number = :n"
        ),
        {"n": sentinel_course, "c": new_content,
         "h": hashlib.sha256(new_content.encode()).hexdigest()},
    )
    await db_session.commit()
    chunks3, skipped3 = await index_course(db_session, _FakeClient(), sentinel_course)
    await db_session.commit()
    assert not skipped3 and chunks3 == 4  # + the new '## More' section
    n_sources = (
        await db_session.execute(
            text("SELECT count(*) FROM document_sources WHERE course_number = :n"),
            {"n": sentinel_course},
        )
    ).scalar()
    assert n_sources == 1


async def test_requires_auth(client: AsyncClient):
    assert (await client.get("/api/admin/factsheets")).status_code == 401