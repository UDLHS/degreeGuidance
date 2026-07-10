"""Admin conversations viewer + usage endpoints (Phase 2 plan §2.1/§2.2).

Sentinel isolation: this suite inserts its own conversations/messages (session
ids prefixed 'convtest-') and its own admin, and removes them all afterward —
assertions never depend on real chat history.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

SESSION_PREFIX = "convtest-"


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"authtest-conv-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(
        text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid}
    )
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


@pytest_asyncio.fixture
async def sentinel_conversation(db_session: AsyncSession):
    cid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO conversations (conversation_id, session_id) VALUES (:c, :s)"
        ),
        {"c": cid, "s": f"{SESSION_PREFIX}{cid.hex[:10]}"},
    )
    await db_session.execute(
        text(
            "INSERT INTO messages (conversation_id, role, content, tool_calls) VALUES "
            "(:c, 'user', 'convtest: what is the cutoff for medicine?', NULL), "
            "(:c, 'assistant', 'convtest: the 2024 cutoff is …', '[\"lookup_course\"]'::jsonb)"
        ),
        {"c": cid},
    )
    await db_session.commit()
    yield str(cid)
    await db_session.execute(
        text(
            "DELETE FROM conversations WHERE session_id LIKE :p"
        ),
        {"p": f"{SESSION_PREFIX}%"},
    )
    await db_session.commit()


async def test_list_requires_auth(client: AsyncClient):
    r = await client.get("/api/admin/conversations")
    assert r.status_code == 401


async def test_list_and_search(client: AsyncClient, admin_token, sentinel_conversation):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get(
        "/api/admin/conversations", params={"q": "convtest: what is the cutoff"}, headers=h
    )
    assert r.status_code == 200
    d = r.json()
    assert d["total"] >= 1
    match = [i for i in d["items"] if i["conversation_id"] == sentinel_conversation]
    assert match, "sentinel conversation must be findable by message text"
    assert match[0]["message_count"] == 2
    assert match[0]["student_email"] is None
    assert match[0]["preview"].startswith("convtest:")


async def test_detail_shows_tool_calls(client: AsyncClient, admin_token, sentinel_conversation):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get(f"/api/admin/conversations/{sentinel_conversation}", headers=h)
    assert r.status_code == 200
    d = r.json()
    roles = [m["role"] for m in d["messages"]]
    assert roles == ["user", "assistant"]
    assert d["messages"][1]["tool_calls"] == ["lookup_course"]


async def test_flag_toggle_and_filter(
    client: AsyncClient, admin_token, sentinel_conversation, db_session: AsyncSession
):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.patch(
        f"/api/admin/conversations/{sentinel_conversation}",
        json={"flagged": True},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["flagged"] is True

    # appears under flagged filter
    r2 = await client.get("/api/admin/conversations", params={"flagged": "true"}, headers=h)
    ids = [i["conversation_id"] for i in r2.json()["items"]]
    assert sentinel_conversation in ids

    # the mutation is audited
    n = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions WHERE action_type = 'conversation.flag' "
                "AND target_id = :t"
            ),
            {"t": sentinel_conversation},
        )
    ).scalar()
    assert n >= 1


async def test_usage_shape(client: AsyncClient, admin_token, sentinel_conversation):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = await client.get("/api/admin/usage", headers=h)
    assert r.status_code == 200
    u = r.json()
    for section in ("conversations", "messages", "tool_usage", "eligibility"):
        assert section in u
    assert u["conversations"]["total"] >= 1
    # the sentinel's lookup_course call is counted
    assert u["tool_usage"].get("lookup_course", 0) >= 1
    assert "by_year_viewed" in u["eligibility"]  # year-dynamic, never hardcoded