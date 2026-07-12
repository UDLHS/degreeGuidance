"""Stream-eligibility editor + zero-stream safety warning (Phase 8.1 / 8.4).

The eligibility engine only serves courses with course_stream_eligibility
rows — a course with none is invisible to every student, silently. These
tests pin the editor (GET/PUT replace-set, validated, audited), the warning,
and the plan's gate: the full lifecycle new stub → streams → activate →
sentinel cutoff → the course appears in student eligibility.

Sentinel course 997Z, sentinel exam year 2027 (2028-2034 taken), purge-first.
"""

from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.eligibility.engine import evaluate_eligibility
from core.schemas.eligibility import EligibilityRequest, SubjectInput

COURSE = "997Z"
SENTINEL_YEAR = 2027
PS_SUBJECTS = [
    SubjectInput(subject="Combined Mathematics", grade="A"),
    SubjectInput(subject="Physics", grade="A"),
    SubjectInput(subject="Chemistry", grade="A"),
]


@pytest_asyncio.fixture
async def admin_token(db_session: AsyncSession):
    from core.security import create_access_token, hash_password

    uid = uuid.uuid4()
    # purge-first: a crashed prior run must not poison this one
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": COURSE})
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"streams-admin-{uid}@example.com", "ph": hash_password("x")},
    )
    await db_session.commit()
    yield create_access_token(subject=str(uid), role="admin")
    await db_session.execute(
        text("DELETE FROM z_score_cutoffs WHERE year = :y"), {"y": SENTINEL_YEAR}
    )
    await db_session.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": COURSE})
    await db_session.execute(text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid})
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await db_session.commit()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_stub(client: AsyncClient, token: str, db: AsyncSession) -> None:
    uni_id = (
        await db.execute(text("SELECT university_id FROM universities ORDER BY university_id LIMIT 1"))
    ).scalar_one()
    r = await client.post(
        "/api/admin/courses",
        headers=_auth(token),
        json={
            "course_code": COURSE,
            "course_number": "997",
            "university_id": uni_id,
            "name_en": "Sentinel Onboarding Course",
            "is_active": False,
        },
    )
    assert r.status_code == 201, r.text


async def test_streams_editor_roundtrip_and_validation(
    client: AsyncClient, admin_token: str, db_session: AsyncSession
):
    await _create_stub(client, admin_token, db_session)

    # fresh stub: no streams, inactive -> no warning yet
    r = await client.get(f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token))
    assert r.status_code == 200
    assert r.json() == {
        "course_code": COURSE, "is_active": False, "stream_codes": [], "warning": None,
    }

    # unknown stream code -> friendly 422 naming the offender
    r = await client.put(
        f"/api/admin/courses/{COURSE}/streams",
        headers=_auth(admin_token),
        json={"stream_codes": ["PHYSICAL_SCIENCE", "NOT_A_STREAM"]},
    )
    assert r.status_code == 422
    assert "NOT_A_STREAM" in r.json()["detail"]

    # replace-set (dedup + case-normalise), audited
    r = await client.put(
        f"/api/admin/courses/{COURSE}/streams",
        headers=_auth(admin_token),
        json={"stream_codes": ["physical_science", "PHYSICAL_SCIENCE", "ICT"]},
    )
    assert r.status_code == 200
    assert r.json()["stream_codes"] == ["ICT", "PHYSICAL_SCIENCE"]

    r = await client.get(f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token))
    assert r.json()["stream_codes"] == ["ICT", "PHYSICAL_SCIENCE"]

    audited = (
        await db_session.execute(
            text(
                "SELECT count(*) FROM admin_actions "
                "WHERE action_type = 'course.streams_update' AND target_id = :c"
            ),
            {"c": COURSE},
        )
    ).scalar_one()
    assert audited == 1

    # shrinking back to empty on an INACTIVE course: allowed, no warning
    r = await client.put(
        f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token),
        json={"stream_codes": []},
    )
    assert r.status_code == 200
    assert r.json()["stream_codes"] == [] and r.json()["warning"] is None


async def test_zero_stream_activation_warns(
    client: AsyncClient, admin_token: str, db_session: AsyncSession
):
    await _create_stub(client, admin_token, db_session)

    # activate with zero streams -> the PATCH response itself warns (8.4)
    r = await client.patch(
        f"/api/admin/courses/{COURSE}", headers=_auth(admin_token), json={"is_active": True}
    )
    assert r.status_code == 200
    assert "NO eligible streams" in (r.json()["warning"] or "")

    # the streams view warns too, and emptying while active keeps warning
    r = await client.get(f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token))
    assert "NO eligible streams" in (r.json()["warning"] or "")

    # setting streams clears the warning
    r = await client.put(
        f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token),
        json={"stream_codes": ["PHYSICAL_SCIENCE"]},
    )
    assert r.status_code == 200 and r.json()["warning"] is None


async def test_onboarding_panel_tracks_completeness(
    client: AsyncClient, admin_token: str, db_session: AsyncSession
):
    """Phase 8.2/8.3: a fresh stub shows every blocker; completing the steps
    clears it from the panel. Computed live — nothing stored."""
    await _create_stub(client, admin_token, db_session)

    r = await client.get("/api/admin/courses/onboarding", headers=_auth(admin_token))
    assert r.status_code == 200
    body = r.json()
    entry = next((i for i in body["items"] if i["course_code"] == COURSE), None)
    assert entry is not None, "fresh stub must appear in the onboarding panel"
    assert entry["is_active"] is False
    assert entry["stream_count"] == 0
    assert entry["has_factsheet"] is False  # course number 997 has no factsheet
    assert len(entry["blockers"]) == 3
    # most-broken first: our 3-blocker stub sorts at the very top
    assert body["items"][0]["course_code"] == COURSE

    # complete two of three steps -> still listed, fewer blockers
    await client.put(
        f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token),
        json={"stream_codes": ["PHYSICAL_SCIENCE"]},
    )
    await client.patch(
        f"/api/admin/courses/{COURSE}", headers=_auth(admin_token), json={"is_active": True}
    )
    r = await client.get("/api/admin/courses/onboarding", headers=_auth(admin_token))
    entry = next((i for i in r.json()["items"] if i["course_code"] == COURSE), None)
    assert entry is not None and entry["blockers"] == [
        "no factsheet — the AI advisor knows nothing about it"
    ]

    # factsheet completes the onboarding -> gone from the panel
    await db_session.execute(
        text(
            "INSERT INTO factsheets (course_number, content, content_hash) "
            "VALUES ('997', '# Sentinel', 'deadbeef997') ON CONFLICT DO NOTHING"
        )
    )
    await db_session.commit()
    try:
        r = await client.get("/api/admin/courses/onboarding", headers=_auth(admin_token))
        assert all(i["course_code"] != COURSE for i in r.json()["items"])
    finally:
        await db_session.execute(text("DELETE FROM factsheets WHERE course_number = '997'"))
        await db_session.commit()


async def test_promote_checklist_counts_new_courses(
    client: AsyncClient, admin_token: str, db_session: AsyncSession
):
    """Phase 8.3: the checklist reports this book's course_added stubs as
    X of Y onboarded, listing the pending codes."""
    import uuid as _uuid

    from apps.api.routers.admin_ingestions import build_promote_checklist

    await _create_stub(client, admin_token, db_session)
    rid = _uuid.uuid4()
    await db_session.execute(
        text(
            "INSERT INTO ingestion_runs (run_id, run_type, year, status) "
            "VALUES (:r, 'pdf_extraction', :y, 'success')"
        ),
        {"r": rid, "y": SENTINEL_YEAR},
    )
    await db_session.execute(
        text(
            "INSERT INTO handbook_changes (run_id, change_type, course_code, status) "
            "VALUES (:r, 'course_added', :c, 'applied')"
        ),
        {"r": rid, "c": COURSE},
    )
    await db_session.commit()
    try:
        checklist = await build_promote_checklist(db_session, SENTINEL_YEAR, run_id=str(rid))
        assert checklist["new_courses_total"] == 1
        assert checklist["new_courses_onboarded"] == 0
        assert checklist["new_courses_pending"] == [COURSE]

        # onboard fully -> counts flip
        await client.put(
            f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token),
            json={"stream_codes": ["PHYSICAL_SCIENCE"]},
        )
        await client.patch(
            f"/api/admin/courses/{COURSE}", headers=_auth(admin_token), json={"is_active": True}
        )
        await db_session.execute(
            text(
                "INSERT INTO factsheets (course_number, content, content_hash) "
                "VALUES ('997', '# Sentinel', 'deadbeef997b') ON CONFLICT DO NOTHING"
            )
        )
        await db_session.commit()
        checklist = await build_promote_checklist(db_session, SENTINEL_YEAR, run_id=str(rid))
        assert checklist["new_courses_onboarded"] == 1
        assert checklist["new_courses_pending"] == []
    finally:
        await db_session.execute(text("DELETE FROM factsheets WHERE course_number = '997'"))
        await db_session.execute(
            text("DELETE FROM ingestion_runs WHERE run_id = :r"), {"r": rid}
        )
        await db_session.commit()


async def test_full_onboarding_lifecycle_reaches_students(
    client: AsyncClient, admin_token: str, db_session: AsyncSession
):
    """The Phase 8 gate: stub -> streams -> activate -> cutoff -> a student
    in that stream actually sees the course."""
    await _create_stub(client, admin_token, db_session)

    # invisible while it has no streams/cutoffs, even if a cutoff existed
    did = (
        await db_session.execute(text("SELECT district_id FROM districts WHERE code='COLOMBO'"))
    ).scalar_one()
    await db_session.execute(
        text(
            "INSERT INTO z_score_cutoffs (year, course_code, district_id, z_score) "
            "VALUES (:y, :c, :d, 1.2000)"
        ),
        {"y": SENTINEL_YEAR, "c": COURSE, "d": did},
    )
    await db_session.commit()

    req = EligibilityRequest(
        z_score=1.5, district_code="COLOMBO", stream_code="PHYSICAL_SCIENCE",
        exam_year=SENTINEL_YEAR, subjects=PS_SUBJECTS,
    )
    resp = await evaluate_eligibility(db_session, req)
    assert COURSE not in {i.course_code for i in resp.results}  # no streams yet

    r = await client.put(
        f"/api/admin/courses/{COURSE}/streams", headers=_auth(admin_token),
        json={"stream_codes": ["PHYSICAL_SCIENCE"]},
    )
    assert r.status_code == 200
    resp = await evaluate_eligibility(db_session, req)
    assert COURSE not in {i.course_code for i in resp.results}  # still inactive

    r = await client.patch(
        f"/api/admin/courses/{COURSE}", headers=_auth(admin_token), json={"is_active": True}
    )
    assert r.status_code == 200 and r.json()["warning"] is None

    resp = await evaluate_eligibility(db_session, req)
    hit = next((i for i in resp.results if i.course_code == COURSE), None)
    assert hit is not None, "onboarded course must reach students"
    assert hit.cutoff_z_score == 1.2 and hit.status == "eligible"
