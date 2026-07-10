"""Agent-config system (Phase 4 plan gate).

Proves the plan's promises without calling Gemini:
- placeholder rendering injects LIVE facts (years/course count from this DB)
  and is brace-safe (admin text with { } never crashes);
- the resolver serves the built-in default when no row is active, the DB row
  when one is, and cache invalidation makes activation immediate;
- CRUD + activate + rollback + revert-to-builtin are admin-gated and audited;
- the sandbox endpoint runs a draft config and persists nothing (orchestrator
  stubbed via monkeypatch).
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.chat.agent_config import (
    DEFAULT_PROMPT_TEMPLATE,
    invalidate_agent_config_cache,
    render_template,
    resolve_agent_settings,
)
from core.security import create_access_token, hash_password

PREFIX = "authtest-agent-"


@pytest_asyncio.fixture(autouse=True)
def _fresh_cache():
    invalidate_agent_config_cache()
    yield
    invalidate_agent_config_cache()


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
    await db_session.execute(text("DELETE FROM agent_configs"))
    await db_session.execute(
        text(
            "DELETE FROM admin_actions WHERE admin_user_id IN "
            "(SELECT user_id FROM users WHERE email LIKE :p)"
        ),
        {"p": f"{PREFIX}%"},
    )
    await db_session.execute(text("DELETE FROM users WHERE email LIKE :p"), {"p": f"{PREFIX}%"})
    await db_session.commit()
    invalidate_agent_config_cache()


def test_render_is_bracesafe_and_substitutes():
    facts = {"available_years": "2024, 2023", "latest_year": "2024",
             "course_count": "265", "today": "July 10, 2026"}
    out = render_template(
        "Years: {available_years}. Latest {latest_year}. {course_count} courses. "
        "Literal {braces} and {unknown_token} survive.",
        facts,
    )
    assert "2024, 2023" in out and "265 courses" in out
    assert "{braces}" in out and "{unknown_token}" in out  # untouched, no crash


async def test_builtin_default_renders_live_facts(db_session: AsyncSession):
    resolved = await resolve_agent_settings(db_session)
    assert resolved.source == "builtin"
    # live facts injected — no placeholder residue, no stale hardcoded facts
    for token in ("{available_years}", "{latest_year}", "{course_count}", "{today}"):
        assert token not in resolved.base_prompt
    assert "261 UGC courses" not in resolved.base_prompt  # the old drift, gone
    years = (
        await db_session.execute(text("SELECT DISTINCT year FROM z_score_cutoffs ORDER BY year DESC"))
    ).scalars().all()
    if years:  # whatever is promoted right now must appear — year-agnostic by data
        assert str(years[0]) in resolved.base_prompt


async def test_config_lifecycle_and_resolution(
    client: AsyncClient, admin_token, db_session: AsyncSession
):
    h = {"Authorization": f"Bearer {admin_token}"}

    # default endpoint exposes the template + live facts
    d = (await client.get("/api/admin/agent-configs/default", headers=h)).json()
    assert d["system_prompt_template"] == DEFAULT_PROMPT_TEMPLATE
    assert "latest_year" in d["live_facts"]

    # create + activate a custom config with a marker + a placeholder
    r = await client.post(
        "/api/admin/agent-configs",
        json={
            "name": "test v1",
            "system_prompt_template": "AGENTTEST-MARKER prompt. Latest year: {latest_year}. "
            + "x" * 50,
            "model_name": "models/test-model",
            "web_search_default": False,
            "max_tool_turns": 3,
            "activate": True,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    cfg_id = r.json()["config_id"]
    assert r.json()["is_active"] is True

    # the resolver now serves it, with facts rendered
    invalidate_agent_config_cache()
    resolved = await resolve_agent_settings(db_session)
    assert resolved.source == f"db:{cfg_id}"
    assert "AGENTTEST-MARKER" in resolved.base_prompt
    assert "{latest_year}" not in resolved.base_prompt
    assert resolved.model_name == "models/test-model"
    assert resolved.max_tool_turns == 3
    assert resolved.web_search_default is False

    # activation is audited
    n = (
        await db_session.execute(
            text("SELECT count(*) FROM admin_actions WHERE action_type = 'agent_config.create'")
        )
    ).scalar()
    assert n >= 1

    # revert to builtin (rollback path)
    r2 = await client.post("/api/admin/agent-configs/deactivate", headers=h)
    assert r2.status_code == 200 and r2.json()["active_source"] == "builtin"
    invalidate_agent_config_cache()
    resolved2 = await resolve_agent_settings(db_session)
    assert resolved2.source == "builtin"

    # activate the old version again (one-click rollback the other way)
    r3 = await client.post(f"/api/admin/agent-configs/{cfg_id}/activate", headers=h)
    assert r3.status_code == 200 and r3.json()["is_active"] is True
    invalidate_agent_config_cache()
    assert (await resolve_agent_settings(db_session)).source == f"db:{cfg_id}"


async def test_sandbox_runs_draft_without_persisting(
    client: AsyncClient, admin_token, db_session: AsyncSession, monkeypatch
):
    async def fake_chat(**kwargs):
        # the draft agent must reach the loop with the draft's prompt
        assert "SANDBOX-DRAFT" in kwargs["agent"].base_prompt
        return "stubbed reply", ["lookup_course"]

    monkeypatch.setattr("apps.api.routers.admin_agent.run_chat", fake_chat)
    h = {"Authorization": f"Bearer {admin_token}"}
    before = (
        await db_session.execute(text("SELECT count(*) FROM conversations"))
    ).scalar()

    r = await client.post(
        "/api/admin/agent-configs/test",
        json={
            "message": "test question",
            "system_prompt_template": "SANDBOX-DRAFT template with {latest_year}. " + "x" * 40,
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reply"] == "stubbed reply"
    assert body["tools_used"] == ["lookup_course"]
    assert "SANDBOX-DRAFT" in body["rendered_prompt_preview"]

    after = (
        await db_session.execute(text("SELECT count(*) FROM conversations"))
    ).scalar()
    assert after == before  # nothing persisted


async def test_agent_endpoints_require_auth(client: AsyncClient):
    assert (await client.get("/api/admin/agent-configs")).status_code == 401
    assert (await client.post("/api/admin/agent-configs/test", json={"message": "x"})).status_code == 401