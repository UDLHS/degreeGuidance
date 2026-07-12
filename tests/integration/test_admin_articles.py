"""Admin knowledge articles (Phase 8.6).

CRUD + audit + reindex-enqueue contract for admin-authored knowledge beyond
courses. Embeddings never run here — the enqueue is spied (no Redis, no
Gemini); deletion's index cleanup is exercised against manually planted
document_sources/chunks rows.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

MARKER = "pytest-sentinel-article"


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    # purge-first: crashed prior runs must not poison this one
    await db_session.execute(
        text("DELETE FROM articles WHERE title LIKE :m"), {"m": f"{MARKER}%"}
    )
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"articles-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(
        text(
            "DELETE FROM chunks WHERE source_id IN "
            "(SELECT source_id FROM document_sources WHERE source_type='article' AND title LIKE :m)"
        ),
        {"m": f"{MARKER}%"},
    )
    await db_session.execute(
        text("DELETE FROM document_sources WHERE source_type='article' AND title LIKE :m"),
        {"m": f"{MARKER}%"},
    )
    await db_session.execute(
        text("DELETE FROM articles WHERE title LIKE :m"), {"m": f"{MARKER}%"}
    )
    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest.fixture
def enqueue_spy(monkeypatch):
    calls: list[dict] = []

    async def _fake(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("apps.api.routers.admin_articles.enqueue_index_article", _fake)
    return calls


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_articles_crud_audit_and_reindex_contract(
    client: AsyncClient, admin_token: str, db_session: AsyncSession, enqueue_spy: list
):
    # create -> 201, never_indexed, reindex enqueued, audited
    r = await client.post(
        "/api/admin/articles",
        headers=_auth(admin_token),
        json={"title": f"{MARKER} aptitude guide", "content": "## How tests work\nDetails."},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    aid = body["article_id"]
    assert body["version"] == 1 and body["index_status"] == "never_indexed"
    assert enqueue_spy == [{"article_id": aid}]

    # list shows it with staleness state
    r = await client.get("/api/admin/articles", headers=_auth(admin_token))
    item = next(i for i in r.json()["items"] if i["article_id"] == aid)
    assert item["index_status"] == "never_indexed"

    # no-op save: no version bump, no reindex
    r = await client.put(
        f"/api/admin/articles/{aid}",
        headers=_auth(admin_token),
        json={"title": f"{MARKER} aptitude guide", "content": "## How tests work\nDetails."},
    )
    assert r.status_code == 200 and r.json()["version"] == 1
    assert len(enqueue_spy) == 1

    # real edit: version bump + reindex enqueued
    r = await client.put(
        f"/api/admin/articles/{aid}",
        headers=_auth(admin_token),
        json={"title": f"{MARKER} aptitude guide", "content": "## How tests work\nMore detail."},
    )
    assert r.status_code == 200 and r.json()["version"] == 2
    assert len(enqueue_spy) == 2

    # simulate the worker having indexed the OLD content -> list shows stale
    await db_session.execute(
        text(
            "INSERT INTO document_sources (source_type, course_number, title, file_path, content_hash) "
            "VALUES ('article', NULL, :t, :p, 'not-the-current-hash')"
        ),
        {"t": f"{MARKER} aptitude guide", "p": f"db:articles/{aid}"},
    )
    await db_session.commit()
    r = await client.get(f"/api/admin/articles/{aid}", headers=_auth(admin_token))
    assert r.json()["index_status"] == "stale"

    # audit trail exists for create + update
    n = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions "
                "WHERE action_type IN ('article.create','article.update') AND target_id = :t"
            ),
            {"t": str(aid)},
        )
    ).scalar_one()
    assert n == 2

    # delete removes the row AND its index, audited
    r = await client.delete(f"/api/admin/articles/{aid}", headers=_auth(admin_token))
    assert r.status_code == 204
    left = (
        await db_session.execute(
            text("SELECT count(*) FROM document_sources WHERE file_path = :p"),
            {"p": f"db:articles/{aid}"},
        )
    ).scalar_one()
    assert left == 0
    r = await client.get(f"/api/admin/articles/{aid}", headers=_auth(admin_token))
    assert r.status_code == 404


async def test_articles_require_admin(client: AsyncClient):
    assert (await client.get("/api/admin/articles")).status_code == 401
    assert (
        await client.post("/api/admin/articles", json={"title": "x", "content": "y"})
    ).status_code == 401
