"""Knowledge-base browser (Phase 6 plan gate).

Reuses the factsheets sentinel pattern: a dedicated inactive course ('997')
gets a factsheet + a hand-planted index row, so stale detection, the chunk
inspector, and reindex-stale targeting are all proven without Gemini or Redis.
"""

from __future__ import annotations

import hashlib
import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

PREFIX = "authtest-kb-"
SENTINEL_CODE = "997Z"
SENTINEL_NUMBER = "997"


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


async def _purge(db: AsyncSession) -> None:
    await db.rollback()
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
    await db.execute(text("DELETE FROM factsheets WHERE course_number = :n"), {"n": SENTINEL_NUMBER})
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": SENTINEL_CODE})
    await db.commit()


@pytest_asyncio.fixture
async def stale_sentinel(db_session: AsyncSession):
    """A factsheet whose index was built from OLDER content -> must show stale."""
    await _purge(db_session)
    uni = (await db_session.execute(text("SELECT university_id FROM universities LIMIT 1"))).scalar()
    await db_session.execute(
        text(
            "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
            "VALUES (:c, :n, :u, 'KB Test Course', false)"
        ),
        {"c": SENTINEL_CODE, "n": SENTINEL_NUMBER, "u": uni},
    )
    new_content = "# KB Test\n\n## Overview\n\nnew edited content " * 3
    await db_session.execute(
        text(
            "INSERT INTO factsheets (course_number, content, content_hash) VALUES (:n, :c, :h)"
        ),
        {"n": SENTINEL_NUMBER, "c": new_content,
         "h": hashlib.sha256(new_content.encode()).hexdigest()},
    )
    # index row built from OLD content (different hash)
    source_id = (
        await db_session.execute(
            text(
                "INSERT INTO document_sources (source_type, course_number, title, file_path, content_hash) "
                "VALUES ('factsheet', :n, 'KB Test', :fp, :h) RETURNING source_id"
            ),
            {"n": SENTINEL_NUMBER, "fp": f"db:factsheets/{SENTINEL_NUMBER}",
             "h": hashlib.sha256(b"OLD content").hexdigest()},
        )
    ).scalar()
    await db_session.execute(
        text(
            "INSERT INTO chunks (source_id, chunk_index, heading, content, token_count) "
            "VALUES (:s, 0, 'Overview', 'old chunk text', 3)"
        ),
        {"s": source_id},
    )
    await db_session.commit()
    yield source_id
    await _purge(db_session)


@pytest_asyncio.fixture(autouse=True)
def _no_redis(monkeypatch):
    calls: list[str] = []

    async def _fake(*, course_number: str):
        calls.append(course_number)

    monkeypatch.setattr("apps.api.routers.admin_knowledge.enqueue_index_factsheet", _fake)
    yield calls


async def test_requires_auth(client: AsyncClient):
    assert (await client.get("/api/admin/knowledge")).status_code == 401


async def test_list_flags_stale(client: AsyncClient, admin_token, stale_sentinel):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get("/api/admin/knowledge", headers=h)
    assert r.status_code == 200
    d = r.json()
    assert d["totals"]["sources"] >= 1
    mine = [i for i in d["items"] if i["course_number"] == SENTINEL_NUMBER]
    assert mine and mine[0]["stale"] is True
    assert mine[0]["chunk_count"] == 1
    assert mine[0]["embedded_count"] == 0  # planted chunk has no embedding


async def test_chunk_inspector(client: AsyncClient, admin_token, stale_sentinel):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get(f"/api/admin/knowledge/{stale_sentinel}/chunks", headers=h)
    assert r.status_code == 200
    chunks = r.json()
    assert len(chunks) == 1
    assert chunks[0]["heading"] == "Overview"
    assert chunks[0]["has_embedding"] is False
    assert chunks[0]["content"] == "old chunk text"
    assert (
        await client.get("/api/admin/knowledge/999999/chunks", headers=h)
    ).status_code == 404


async def test_reindex_stale_targets_only_stale(
    client: AsyncClient, admin_token, stale_sentinel, _no_redis, db_session: AsyncSession
):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.post("/api/admin/knowledge/reindex-stale", headers=h)
    assert r.status_code == 200
    d = r.json()
    # the stale sentinel is queued; fresh factsheets (hashes matching) are NOT
    assert SENTINEL_NUMBER in d["course_numbers"]
    assert d["enqueued"] == len(_no_redis)
    fresh = (
        await db_session.execute(
            text(
                "SELECT f.course_number FROM factsheets f "
                "JOIN document_sources ds ON ds.source_type='factsheet' "
                " AND ds.course_number = f.course_number "
                " AND ds.content_hash = f.content_hash LIMIT 1"
            )
        )
    ).scalar()
    if fresh:  # at least one genuinely fresh factsheet exists in dev data
        assert fresh not in d["course_numbers"]
    # audited
    n = (
        await db_session.execute(
            text("SELECT count(*) FROM admin_actions WHERE action_type='knowledge.reindex_stale'")
        )
    ).scalar()
    assert n >= 1