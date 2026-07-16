"""Phase 9.4 — factsheet drafts: machine-written, human-gated (D3/D4).

The invariant these tests pin: a draft can NEVER reach the advisor's index
while it is a draft. Drafts live in factsheet_drafts, a table the index job
does not read; approve is the single door, and it goes through the same
versioned/audited write path as a hand edit.

Sentinel course 995X / number '995' (996-998 are taken by other suites);
purge-first. Both queue enqueues are spied — no Redis, no Gemini, no DDG.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

SENTINEL_CODE = "995X"
SENTINEL_NUMBER = "995"

DRAFT_MD = (
    "# Sentinel Studies\n\n## Overview\n\nA sentinel course of study used only by tests, "
    "long enough to clear the 50-character floor.\n\n## Career Paths in Sri Lanka\n\n- none\n"
)


async def _purge(db: AsyncSession) -> None:
    await db.execute(
        text("DELETE FROM factsheet_drafts WHERE course_number = :n"), {"n": SENTINEL_NUMBER}
    )
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
    await db.execute(
        text("DELETE FROM course_stream_eligibility WHERE course_code = :c"),
        {"c": SENTINEL_CODE},
    )
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": SENTINEL_CODE})
    await db.commit()


@pytest_asyncio.fixture
async def drafts(db_session: AsyncSession):
    """Admin + an active sentinel course (995X) with one eligible stream."""
    uid = uuid.uuid4()
    await _purge(db_session)
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"fsdraft-admin-{uid.hex[:8]}@example.com", "ph": hash_password("x")},
    )
    university_id = (
        await db_session.execute(
            text("SELECT university_id FROM universities ORDER BY university_id LIMIT 1")
        )
    ).scalar_one()
    await db_session.execute(
        text(
            "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
            "VALUES (:c, :n, :u, 'Sentinel Studies (Test University)', true)"
        ),
        {"c": SENTINEL_CODE, "n": SENTINEL_NUMBER, "u": university_id},
    )
    await db_session.execute(
        text(
            "INSERT INTO course_stream_eligibility (course_code, stream_id) "
            "SELECT :c, stream_id FROM streams WHERE code = 'ARTS'"
        ),
        {"c": SENTINEL_CODE},
    )
    await db_session.commit()

    yield {"token": create_access_token(subject=str(uid), role="admin")}

    await db_session.execute(
        text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid}
    )
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await _purge(db_session)


@pytest.fixture
def enqueue_spies(monkeypatch):
    """Both queue hops -> recorders (no Redis)."""
    calls = {"generate": [], "index": []}

    async def _fake_generate(*, course_number: str, run_id: str | None = None):
        calls["generate"].append({"course_number": course_number, "run_id": run_id})

    async def _fake_index(*, course_number: str):
        calls["index"].append({"course_number": course_number})

    monkeypatch.setattr(
        "apps.api.routers.admin_factsheets.enqueue_generate_factsheet_draft", _fake_generate
    )
    monkeypatch.setattr(
        "apps.api.routers.admin_factsheets.enqueue_index_factsheet", _fake_index
    )
    return calls


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _url(suffix: str = "") -> str:
    return f"/api/admin/factsheets/{SENTINEL_NUMBER}{suffix}"


async def _make_ready_draft(db: AsyncSession, content: str = DRAFT_MD) -> None:
    await db.execute(
        text(
            "INSERT INTO factsheet_drafts (course_number, status, content, provenance) "
            "VALUES (:n, 'ready', :c, '{\"book_found\": false}'::jsonb) "
            "ON CONFLICT (course_number) DO UPDATE SET "
            "  status = 'ready', content = :c, error = NULL"
        ),
        {"n": SENTINEL_NUMBER, "c": content},
    )
    await db.commit()


# ── generate ─────────────────────────────────────────────────────────────────

async def test_generate_draft_enqueues_and_lands_queued(
    client: AsyncClient, drafts: dict, db_session: AsyncSession, enqueue_spies: dict
):
    r = await client.post(_url("/generate-draft"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "queued"
    assert enqueue_spies["generate"] == [{"course_number": SENTINEL_NUMBER, "run_id": None}]

    # while it is generating, a second click is refused rather than doubled
    r = await client.post(_url("/generate-draft"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 409


async def test_generate_draft_unknown_course_is_422(
    client: AsyncClient, drafts: dict, enqueue_spies: dict
):
    r = await client.post(
        "/api/admin/factsheets/994/generate-draft", headers=_auth(drafts["token"]), json={}
    )
    assert r.status_code == 422
    assert enqueue_spies["generate"] == []


# ── the D4 invariant ─────────────────────────────────────────────────────────

async def test_a_ready_draft_is_not_in_factsheets_or_the_index(
    client: AsyncClient, drafts: dict, db_session: AsyncSession
):
    """Structural D4: a draft row exists, yet factsheets and document_sources
    (what the index job writes / the advisor reads) know nothing about it."""
    await _make_ready_draft(db_session)
    fs = (
        await db_session.execute(
            text("SELECT 1 FROM factsheets WHERE course_number = :n"), {"n": SENTINEL_NUMBER}
        )
    ).first()
    ds = (
        await db_session.execute(
            text("SELECT 1 FROM document_sources WHERE course_number = :n"),
            {"n": SENTINEL_NUMBER},
        )
    ).first()
    assert fs is None and ds is None

    r = await client.get(_url("/draft"), headers=_auth(drafts["token"]))
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


# ── approve ──────────────────────────────────────────────────────────────────

async def test_approve_publishes_via_the_hand_edit_path(
    client: AsyncClient, drafts: dict, db_session: AsyncSession, enqueue_spies: dict
):
    await _make_ready_draft(db_session)
    edited = DRAFT_MD + "\n## Special Notes\n\nEdited by the admin before approval.\n"
    r = await client.post(
        _url("/draft/approve"), headers=_auth(drafts["token"]), json={"content": edited}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["version"] == 1 and body["content"] == edited

    # the draft row is gone; the factsheet exists; the reindex was enqueued
    gone = (
        await db_session.execute(
            text("SELECT 1 FROM factsheet_drafts WHERE course_number = :n"),
            {"n": SENTINEL_NUMBER},
        )
    ).first()
    assert gone is None
    assert enqueue_spies["index"] == [{"course_number": SENTINEL_NUMBER}]

    # both the save and the approval are audited
    actions = {
        r.action_type
        for r in (
            await db_session.execute(
                text(
                    "SELECT action_type FROM admin_actions "
                    "WHERE target_id = :n AND action_type LIKE 'factsheet%'"
                ),
                {"n": SENTINEL_NUMBER},
            )
        ).all()
    }
    assert {"factsheet.create", "factsheet.draft_approve"} <= actions


async def test_approve_without_ready_draft_is_refused(
    client: AsyncClient, drafts: dict, db_session: AsyncSession, enqueue_spies: dict
):
    r = await client.post(_url("/draft/approve"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 404

    await db_session.execute(
        text(
            "INSERT INTO factsheet_drafts (course_number, status) VALUES (:n, 'queued')"
        ),
        {"n": SENTINEL_NUMBER},
    )
    await db_session.commit()
    r = await client.post(_url("/draft/approve"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 409
    assert enqueue_spies["index"] == []


# ── reject / replace ─────────────────────────────────────────────────────────

async def test_reject_keeps_the_row_and_regenerate_replaces_it(
    client: AsyncClient, drafts: dict, db_session: AsyncSession, enqueue_spies: dict
):
    await _make_ready_draft(db_session)
    r = await client.post(_url("/draft/reject"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"

    # a rejected draft does not block a fresh generation
    r = await client.post(_url("/generate-draft"), headers=_auth(drafts["token"]), json={})
    assert r.status_code == 200
    assert r.json()["status"] == "queued"
    assert len(enqueue_spies["generate"]) == 1


# ── list surfacing ───────────────────────────────────────────────────────────

async def test_list_carries_draft_status(
    client: AsyncClient, drafts: dict, db_session: AsyncSession
):
    await _make_ready_draft(db_session)
    r = await client.get("/api/admin/factsheets", headers=_auth(drafts["token"]))
    assert r.status_code == 200
    row = next(i for i in r.json()["items"] if i["course_number"] == SENTINEL_NUMBER)
    assert row["draft_status"] == "ready"
    assert row["has_factsheet"] is False


# ── the worker job itself (Gemini + DDG stubbed) ─────────────────────────────

@pytest.fixture
def job_mod(engine, monkeypatch):
    """The job module with its session factory bound to THIS test's engine —
    the global AsyncSessionLocal's engine belongs to another test's event loop
    (see conftest's per-test-engine design)."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from apps.worker.jobs import generate_factsheet as mod

    monkeypatch.setattr(mod, "AsyncSessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    return mod


async def test_job_writes_ready_row_with_provenance(
    drafts: dict, db_session: AsyncSession, monkeypatch, job_mod
):
    monkeypatch.setattr(job_mod, "_generate", lambda prompt: DRAFT_MD)

    def _boom(*a, **k):
        raise RuntimeError("no network in tests")

    monkeypatch.setattr(job_mod, "_web_search", _boom)

    result = await job_mod.generate_factsheet_draft_job(None, course_number=SENTINEL_NUMBER)
    assert result["status"] == "ready"

    row = (
        await db_session.execute(
            text(
                "SELECT status, content, provenance FROM factsheet_drafts "
                "WHERE course_number = :n"
            ),
            {"n": SENTINEL_NUMBER},
        )
    ).mappings().one()
    assert row["status"] == "ready" and row["content"] == DRAFT_MD
    prov = row["provenance"]
    # web failure degraded (recorded), it did not fail the draft
    assert "web_note" in prov and prov["web_results"] == 0
    assert prov["model"]  # which writer produced it is always recorded


async def test_job_failure_lands_loud_on_the_row(
    drafts: dict, db_session: AsyncSession, monkeypatch, job_mod
):
    def _boom(prompt):
        raise RuntimeError("Gemini exploded")

    monkeypatch.setattr(job_mod, "_generate", _boom)
    monkeypatch.setattr(job_mod, "_web_search", lambda *a, **k: [])

    result = await job_mod.generate_factsheet_draft_job(None, course_number=SENTINEL_NUMBER)
    assert result["status"] == "failed"

    row = (
        await db_session.execute(
            text(
                "SELECT status, error FROM factsheet_drafts WHERE course_number = :n"
            ),
            {"n": SENTINEL_NUMBER},
        )
    ).mappings().one()
    assert row["status"] == "failed"
    assert "Gemini exploded" in row["error"]
