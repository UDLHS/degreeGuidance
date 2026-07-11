"""W1 budget-guard behavior on the real endpoints (no Gemini calls ever).

- Chat: budget exhausted -> polite 429 BEFORE any provider call.
- Recommendations: budget exhausted -> still 200; the interest dimension is
  simply skipped (inert), because eligibility/ranking never need Gemini.
- Rate-limit middleware: exempts the in-process test transport (no client
  socket), so the whole suite runs unthrottled — asserted explicitly here.
"""

from __future__ import annotations

from datetime import date

from httpx import AsyncClient

from core.ratelimit import DailyBudget

BASE = {
    "z_score": 2.0,
    "district_code": "COLOMBO",
    "stream_code": "BIO_SCIENCE",
    "subjects": [
        {"subject": "Biology", "grade": "A"},
        {"subject": "Chemistry", "grade": "A"},
        {"subject": "Physics", "grade": "A"},
    ],
}


def _exhausted() -> DailyBudget:
    b = DailyBudget(daily_limit=0, today=lambda: date(2026, 1, 1))
    return b


async def test_chat_429s_when_budget_exhausted(client: AsyncClient, monkeypatch):
    import apps.api.guards as guards

    monkeypatch.setattr(guards, "gemini_budget", _exhausted())

    async def _must_not_run(**kwargs):  # the whole point: no provider call
        raise AssertionError("run_chat must not be called when budget is exhausted")

    monkeypatch.setattr("apps.api.routers.chat.run_chat", _must_not_run)

    r = await client.post(
        "/api/v1/chat",
        json={"session_id": "budget-test", "message": "hello"},
    )
    assert r.status_code == 429
    assert "capacity" in r.json()["detail"]


async def test_recommendations_degrade_gracefully_without_budget(
    client: AsyncClient, monkeypatch
):
    import apps.api.guards as guards

    monkeypatch.setattr(guards, "gemini_budget", _exhausted())

    def _must_not_create_client():
        raise AssertionError("Gemini client must not be created when budget is exhausted")

    monkeypatch.setattr("core.scoring.service._get_client", _must_not_create_client)

    r = await client.post(
        "/api/v1/recommendations",
        json={**BASE, "interests": "I love coding and building software"},
    )
    assert r.status_code == 200
    b = r.json()
    assert b["eligible_count"] >= 1  # core function intact
    for rec in b["recommendations"]:
        dims = {d["name"] for d in rec["breakdown"]}
        assert "interest" not in dims  # dimension inert, not an error


async def test_sandbox_shares_the_budget(client: AsyncClient, monkeypatch, db_session):
    import uuid

    from sqlalchemy import text

    from core.security import create_access_token, hash_password

    import apps.api.guards as guards

    monkeypatch.setattr(guards, "gemini_budget", _exhausted())

    uid = uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"authtest-budget-{uid.hex[:8]}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    try:
        tok = create_access_token(subject=str(uid), role="admin")
        r = await client.post(
            "/api/admin/agent-configs/test",
            json={"message": "test"},
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r.status_code == 429
    finally:
        await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
        await db_session.commit()


async def test_middleware_exempts_test_transport(client: AsyncClient):
    """A burst far beyond the public per-minute limit stays 200 in-process —
    the limiter keys on a real client, which the ASGI test transport lacks."""
    for _ in range(6):
        assert (await client.get("/api/v1/years")).status_code == 200