"""Phase 9 — the new-course gate: approved must mean visible.

A new course from a handbook used to be approvable, appliable and promotable
with no eligible streams — producing a course no student could ever see, with
no error anywhere (the checklist counted it and shrugged). A second door was
just as silent: promoting while a new course sat unreviewed dropped its cutoff
rows (unknown_course_alias) and the course was absent from the year entirely.

These pin the gate that closes both:
  - approve refuses without university + name + streams (D1);
  - approve refuses an ICT-only course (no student sits ICT, so it would still
    be invisible);
  - apply creates the course LIVE with its streams, in one transaction;
  - promote refuses while ANY new course in the run is unfinished.

Sentinel course 996Y, sentinel exam year 2035, purge-first.
"""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

COURSE = "996Y"
SENTINEL_YEAR = 2035


async def _purge(db: AsyncSession) -> None:
    await db.execute(
        text("DELETE FROM course_stream_eligibility WHERE course_code = :c"), {"c": COURSE}
    )
    await db.execute(text("DELETE FROM handbook_changes WHERE course_code = :c"), {"c": COURSE})
    # apply auto-queues a factsheet draft for the new course (Phase 9.4)
    await db.execute(
        text("DELETE FROM factsheet_drafts WHERE course_number = :n"), {"n": COURSE[:3]}
    )
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": COURSE})
    await db.execute(
        text("DELETE FROM ingestion_runs WHERE year = :y AND run_type = 'pdf_extraction'"),
        {"y": SENTINEL_YEAR},
    )
    await db.commit()


@pytest.fixture(autouse=True)
def _no_draft_queue(monkeypatch):
    """apply auto-enqueues factsheet-draft generation (9.4) — spy it out so
    these tests need no Redis and leave nothing on the queue."""
    calls: list[dict] = []

    async def _fake(*, course_number: str, run_id: str | None = None):
        calls.append({"course_number": course_number, "run_id": run_id})

    monkeypatch.setattr(
        "apps.api.routers.admin_ingestions.enqueue_generate_factsheet_draft", _fake
    )
    return calls


@pytest_asyncio.fixture
async def gate(db_session: AsyncSession):
    """An admin plus a successful extraction run carrying one pending course_added."""
    from core.security import create_access_token, hash_password

    uid = uuid.uuid4()
    rid = uuid.uuid4()
    await _purge(db_session)  # a crashed prior run must not poison this one
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"p9-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.execute(
        text(
            "INSERT INTO ingestion_runs (run_id, run_type, year, status) "
            "VALUES (:r, 'pdf_extraction', :y, 'success')"
        ),
        {"r": rid, "y": SENTINEL_YEAR},
    )
    await db_session.execute(
        text(
            "INSERT INTO handbook_changes (run_id, change_type, course_code, status, summary) "
            "VALUES (:r, 'course_added', :c, 'pending', 'sentinel new course')"
        ),
        {"r": rid, "c": COURSE},
    )
    await db_session.commit()

    change_id = (
        await db_session.execute(
            text("SELECT change_id FROM handbook_changes WHERE run_id = :r"), {"r": rid}
        )
    ).scalar_one()
    university_id = (
        await db_session.execute(
            text("SELECT university_id FROM universities ORDER BY university_id LIMIT 1")
        )
    ).scalar_one()

    yield {
        "token": create_access_token(subject=str(uid), role="admin"),
        "run_id": str(rid),
        "change_id": change_id,
        "university_id": university_id,
    }

    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await _purge(db_session)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _patch_url(gate: dict) -> str:
    return f"/api/admin/ingestions/{gate['run_id']}/changes/{gate['change_id']}"


async def test_approve_without_streams_is_refused(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """D1: no streams => the course would be invisible => it cannot be approved."""
    r = await client.patch(
        _patch_url(gate),
        headers=_auth(gate["token"]),
        json={
            "status": "approved",
            "university_id": gate["university_id"],
            "name_en": "Sentinel Course",
        },
    )
    assert r.status_code == 422
    assert "stream" in r.json()["detail"].lower()

    # and the refusal must be real — the change stays pending
    status = (
        await db_session.execute(
            text("SELECT status FROM handbook_changes WHERE change_id = :i"),
            {"i": gate["change_id"]},
        )
    ).scalar_one()
    assert status == "pending"


async def test_approve_rejects_unknown_stream_code(client: AsyncClient, gate: dict):
    r = await client.patch(
        _patch_url(gate),
        headers=_auth(gate["token"]),
        json={
            "status": "approved",
            "university_id": gate["university_id"],
            "name_en": "Sentinel Course",
            "stream_codes": ["NOT_A_STREAM"],
        },
    )
    assert r.status_code == 422
    assert "NOT_A_STREAM" in r.json()["detail"]


async def test_reject_needs_no_details(client: AsyncClient, gate: dict):
    """The gate is on approve only — rejecting a misread code stays one click."""
    r = await client.patch(
        _patch_url(gate), headers=_auth(gate["token"]), json={"status": "rejected"}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"


async def test_approve_then_apply_creates_a_visible_course(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """The whole point: apply produces a LIVE course with its streams, so
    'approved' and 'visible to students' can never drift apart again."""
    r = await client.patch(
        _patch_url(gate),
        headers=_auth(gate["token"]),
        json={
            "status": "approved",
            "university_id": gate["university_id"],
            "name_en": "Sentinel Course",
            "stream_codes": ["PHYSICAL_SCIENCE", "BIO_SCIENCE"],
        },
    )
    assert r.status_code == 200

    r = await client.post(
        f"/api/admin/ingestions/{gate['run_id']}/changes/apply", headers=_auth(gate["token"])
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["applied_added"] == 1, body
    assert body["skipped"] == []

    row = (
        await db_session.execute(
            text("SELECT is_active FROM courses WHERE course_code = :c"), {"c": COURSE}
        )
    ).first()
    assert row is not None, "the course must exist"
    assert row.is_active is True, "created live — D1: approved means visible"

    streams = (
        await db_session.execute(
            text(
                "SELECT s.code FROM course_stream_eligibility cse "
                "JOIN streams s ON s.stream_id = cse.stream_id "
                "WHERE cse.course_code = :c ORDER BY s.code"
            ),
            {"c": COURSE},
        )
    ).scalars().all()
    assert list(streams) == ["BIO_SCIENCE", "PHYSICAL_SCIENCE"]


async def test_promote_refuses_while_a_new_course_is_unfinished(
    client: AsyncClient, gate: dict
):
    """Second door: an unreviewed new course never gets created, so its cutoffs
    would be dropped by the loader and the course would be missing for the whole
    year. Promote must refuse before doing any work."""
    r = await client.post(
        f"/api/admin/ingestions/{gate['run_id']}/promote", headers=_auth(gate["token"])
    )
    assert r.status_code == 409, r.text
    detail = r.json()["detail"]
    assert COURSE in str(detail)
    assert detail["unfinished_new_courses"][0]["course_code"] == COURSE


async def test_book_prefill_resolves_a_real_university(db_session: AsyncSession):
    """9.2 pre-fill: the book's own Uni-Codes section already carries the name,
    university and page — the admin should confirm facts, not retype them."""
    from apps.api.routers.admin_ingestions import _book_prefill

    uni = (
        await db_session.execute(
            text("SELECT university_id, name_en FROM universities ORDER BY university_id LIMIT 1")
        )
    ).first()
    artifact = {
        "book_code_rows": [
            {
                "code": COURSE,
                "course_name": "Sentinel Course",
                # the book prints universities upper-cased — normalisation must bridge it
                "university": uni.name_en.upper(),
                "page_number": 152,
            }
        ]
    }
    out = await _book_prefill(db_session, artifact, {})
    assert out[COURSE]["name_en"] == "Sentinel Course"
    assert out[COURSE]["university_id"] == uni.university_id
    assert out[COURSE]["book_page"] == 152


async def test_book_prefill_never_guesses_an_unknown_university(db_session: AsyncSession):
    """An unresolved university is left for the admin to pick — a wrong guess
    that gets rubber-stamped is worse than a blank."""
    from apps.api.routers.admin_ingestions import _book_prefill

    artifact = {
        "book_code_rows": [
            {
                "code": COURSE,
                "course_name": "Sentinel Course",
                "university": "COLLEGE OF NOWHERE",
                "page_number": 3,
            }
        ]
    }
    out = await _book_prefill(db_session, artifact, {})
    assert "university_id" not in out[COURSE]
    assert out[COURSE]["book_university"] == "COLLEGE OF NOWHERE"


async def test_book_prefill_suggests_streams_from_the_column_tag(db_session: AsyncSession):
    """The cutoff column's bracket tag is a real book signal — but only ever a
    suggestion, and silent when the book says nothing (stream_tags' rule)."""
    from types import SimpleNamespace

    from apps.api.routers.admin_ingestions import _book_prefill

    out = await _book_prefill(
        db_session,
        {"book_code_rows": []},
        {
            "107L": [SimpleNamespace(raw_label="Food Business Management [Commerce Stream]")],
            "996Y": [SimpleNamespace(raw_label="Plain Course With No Tag")],
        },
    )
    assert out["107L"]["suggested_stream_codes"] == ["COMMERCE"]
    # no tag => no suggestion => the admin must choose consciously
    assert "996Y" not in out or "suggested_stream_codes" not in out.get("996Y", {})


async def test_section_22_overrides_the_column_tag(db_session: AsyncSession):
    """9.2b: the cutoff column's bracket tag is a hint on ONE column; §2.2 is
    the book stating the rule for the course. The statement must win."""
    from types import SimpleNamespace

    from apps.api.routers.admin_ingestions import _book_prefill

    out = await _book_prefill(
        db_session,
        {"book_code_rows": []},
        {COURSE: [SimpleNamespace(raw_label="Something [Commerce Stream]")]},
        {COURSE[:3]: {"stream_codes": ["ARTS", "COMMERCE"], "page_number": 117}},
    )
    assert out[COURSE]["suggested_stream_codes"] == ["ARTS", "COMMERCE"]
    assert out[COURSE]["book_details_page"] == 117


async def test_prefill_carries_the_books_requirements_and_incompleteness(
    db_session: AsyncSession,
):
    """The admin must see the book's own words and be told when what we read is
    only a floor — otherwise they tick a short list and the course goes
    invisible to students who qualify by the other route (124's class).

    The Uni-Code comes from the confirmed column (by_code), as it does in a real
    run: §2.2 documents a course by number and cannot invent which university
    letter it maps to.
    """
    from types import SimpleNamespace

    from apps.api.routers.admin_ingestions import _book_prefill

    out = await _book_prefill(
        db_session,
        {"book_code_rows": []},
        {COURSE: [SimpleNamespace(raw_label="Sentinel Course")]},
        {
            COURSE[:3]: {
                "stream_codes": ["BIOSYSTEMS_TECH", "ENGINEERING_TECH"],
                "streams_may_be_incomplete": True,
                "requirements_text": "At least 'S' grades in any three subjects ...",
                "proposed_intake": 50,
                "name": "Sentinel From Book",
            }
        },
    )
    d = out[COURSE]
    assert d["streams_may_be_incomplete"] is True
    assert d["book_requirements_text"].startswith("At least")
    assert d["book_intake"] == 50
    assert d["name_en"] == "Sentinel From Book"


async def _seed_book_details(db: AsyncSession, run_id: str, payload: dict) -> None:
    import json as _json

    from core.ingestion.artifact_store import put_artifact

    await put_artifact(
        db, run_id, "course_details.json", _json.dumps(payload).encode("utf-8")
    )
    await db.commit()


async def _a_course_with_several_streams(db: AsyncSession):
    """A real catalog course with 2-5 streams: more than one so we can claim the
    book grants fewer, fewer than all six so we can claim it grants one more."""
    return (
        await db.execute(
            text(
                "SELECT c.course_number, string_agg(DISTINCT s.code, ',') AS streams "
                "FROM courses c "
                "JOIN course_stream_eligibility cse ON cse.course_code = c.course_code "
                "JOIN streams s ON s.stream_id = cse.stream_id "
                "WHERE c.is_active AND c.course_number IS NOT NULL "
                "GROUP BY c.course_number "
                "HAVING count(DISTINCT s.code) BETWEEN 2 AND 5 "
                "ORDER BY c.course_number LIMIT 1"
            )
        )
    ).first()


async def test_audit_reports_a_course_we_over_grant(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """131's shape: we serve a stream the book does not grant, so students are
    shown a degree they cannot enter. Nothing compared the two for a year."""
    row = await _a_course_with_several_streams(db_session)
    assert row is not None, "fixture needs a multi-stream course in the catalog"
    db_streams = sorted(set(row.streams.split(",")))
    book_says = db_streams[:1]  # the book grants fewer than we do

    await _seed_book_details(
        db_session,
        gate["run_id"],
        {row.course_number: {"stream_codes": book_says, "page_number": 117, "name": "Book Name"}},
    )
    r = await client.get(
        f"/api/admin/ingestions/{gate['run_id']}/catalog-audit", headers=_auth(gate["token"])
    )
    assert r.status_code == 200, r.text
    item = next(i for i in r.json()["items"] if i["course_number"] == row.course_number)
    assert item["severity"] == "over_granted"
    assert item["only_in_db"] == db_streams[1:]
    assert item["page_number"] == 117


async def test_audit_reports_a_course_we_hide_and_ranks_it_first(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """The costly direction: the book grants a stream we don't, so students who
    could apply never see the course. It must sort above 'over_granted'."""
    from core.ingestion.course_details import ALL_SIX_STREAMS

    row = await _a_course_with_several_streams(db_session)
    assert row is not None, "fixture needs a 2-5 stream course in the catalog"
    db_streams = sorted(set(row.streams.split(",")))
    # the helper guarantees < 6 streams, so one of the six is always free
    missing = next(s for s in ALL_SIX_STREAMS if s not in db_streams)

    await _seed_book_details(
        db_session,
        gate["run_id"],
        {row.course_number: {"stream_codes": sorted([*db_streams, missing])}},
    )
    r = await client.get(
        f"/api/admin/ingestions/{gate['run_id']}/catalog-audit", headers=_auth(gate["token"])
    )
    body = r.json()
    item = next(i for i in body["items"] if i["course_number"] == row.course_number)
    assert item["severity"] == "invisible"
    assert item["only_in_book"] == [missing]
    assert body["items"][0]["severity"] == "invisible", "invisible must rank first"


async def test_audit_is_silent_when_the_book_agrees(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    row = await _a_course_with_several_streams(db_session)
    await _seed_book_details(
        db_session,
        gate["run_id"],
        {row.course_number: {"stream_codes": sorted(set(row.streams.split(",")))}},
    )
    r = await client.get(
        f"/api/admin/ingestions/{gate['run_id']}/catalog-audit", headers=_auth(gate["token"])
    )
    assert all(i["course_number"] != row.course_number for i in r.json()["items"])


async def test_audit_survives_an_artifact_from_an_older_build(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """An unknown field must not explode a run — a missing one just means the
    book said nothing."""
    row = await _a_course_with_several_streams(db_session)
    await _seed_book_details(
        db_session,
        gate["run_id"],
        {row.course_number: {"stream_codes": ["ARTS"], "some_future_field": "???"}},
    )
    r = await client.get(
        f"/api/admin/ingestions/{gate['run_id']}/catalog-audit", headers=_auth(gate["token"])
    )
    assert r.status_code == 200, r.text


async def test_promote_allows_a_rejected_new_course(
    client: AsyncClient, gate: dict, db_session: AsyncSession
):
    """A rejected change IS finished — the admin decided. It must not block."""
    r = await client.patch(
        _patch_url(gate), headers=_auth(gate["token"]), json={"status": "rejected"}
    )
    assert r.status_code == 200

    from apps.api.routers.admin_ingestions import _unfinished_new_courses

    blockers = await _unfinished_new_courses(db_session, uuid.UUID(gate["run_id"]))
    assert blockers == []


async def test_apply_auto_queues_a_factsheet_draft(
    client: AsyncClient, gate: dict, db_session: AsyncSession, _no_draft_queue: list
):
    """Phase 9.4: a course that just arrived gets its factsheet draft started
    from this book, so the slot the admin sees is pre-filled, never empty."""
    r = await client.patch(
        _patch_url(gate),
        headers=_auth(gate["token"]),
        json={
            "status": "approved",
            "university_id": gate["university_id"],
            "name_en": "Sentinel Course",
            "stream_codes": ["ARTS"],
        },
    )
    assert r.status_code == 200
    r = await client.post(
        f"/api/admin/ingestions/{gate['run_id']}/changes/apply", headers=_auth(gate["token"])
    )
    assert r.status_code == 200, r.text

    assert _no_draft_queue == [{"course_number": COURSE[:3], "run_id": gate["run_id"]}]
    status = (
        await db_session.execute(
            text("SELECT status FROM factsheet_drafts WHERE course_number = :n"),
            {"n": COURSE[:3]},
        )
    ).scalar_one()
    assert status == "queued"
