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
