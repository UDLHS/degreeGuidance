"""Phase 9.5 — actionable notes on the pages where the work happens.

Two surfaces:
- GET /api/admin/requirements/gaps — active course numbers with no baseline
  subject rule, each carrying the BOOK's verbatim wording + page, because
  "no subject rule" alone is just a red dot; "book p.117 says …" is a task.
- /api/admin/courses/onboarding — a missing factsheet now says what the next
  step actually is (a machine draft is queued/ready/failed — Phase 9.4)
  instead of sending the admin off to write one that already exists.

Sentinel course 993X / number '993', sentinel exam year 2037; purge-first.
"""

from __future__ import annotations

import json
import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password

CODE, NUM = "993X", "993"
SENTINEL_YEAR = 2037

BOOK_TEXT = (
    "Minimum eligibility requirements for admission :\n"
    "At least a 'B' grade in Economics and 'S' grades in two other subjects."
)


async def _purge(db: AsyncSession) -> None:
    await db.execute(
        text("DELETE FROM course_stream_eligibility WHERE course_code = :c"), {"c": CODE}
    )
    await db.execute(
        text("DELETE FROM factsheet_drafts WHERE course_number = :n"), {"n": NUM}
    )
    await db.execute(
        text("DELETE FROM course_requirements WHERE course_number = :n"), {"n": NUM}
    )
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": CODE})
    await db.execute(
        text(
            "DELETE FROM ingestion_artifacts WHERE run_id IN "
            "(SELECT run_id FROM ingestion_runs WHERE year = :y)"
        ),
        {"y": SENTINEL_YEAR},
    )
    await db.execute(
        text("DELETE FROM ingestion_runs WHERE year = :y AND run_type = 'pdf_extraction'"),
        {"y": SENTINEL_YEAR},
    )
    await db.commit()


@pytest_asyncio.fixture
async def notes(db_session: AsyncSession):
    """Admin + an active, ruleless sentinel course + a book artifact naming it."""
    uid = uuid.uuid4()
    rid = uuid.uuid4()
    await _purge(db_session)
    await db_session.execute(
        text(
            "INSERT INTO users (user_id, email, password_hash, role, is_active) "
            "VALUES (:id, :em, :ph, 'admin', true)"
        ),
        {"id": uid, "em": f"p95-admin-{uid.hex[:8]}@example.com", "ph": hash_password("x")},
    )
    university_id = (
        await db_session.execute(
            text("SELECT university_id FROM universities ORDER BY university_id LIMIT 1")
        )
    ).scalar_one()
    await db_session.execute(
        text(
            "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
            "VALUES (:c, :n, :u, 'Sentinel Notes Course', true)"
        ),
        {"c": CODE, "n": NUM, "u": university_id},
    )
    # newest run carrying a course_details artifact that mentions the sentinel
    await db_session.execute(
        text(
            "INSERT INTO ingestion_runs (run_id, run_type, year, status) "
            "VALUES (:r, 'pdf_extraction', :y, 'success')"
        ),
        {"r": rid, "y": SENTINEL_YEAR},
    )
    await db_session.execute(
        text(
            "INSERT INTO ingestion_artifacts (run_id, kind, content) "
            "VALUES (:r, 'course_details.json', :c)"
        ),
        {
            "r": rid,
            "c": json.dumps(
                {
                    NUM: {
                        "course_number": NUM,
                        "name": "Sentinel Notes Course",
                        "requirements_text": BOOK_TEXT,
                        "page_number": 99,
                    }
                }
            ).encode(),
        },
    )
    await db_session.commit()

    yield {"token": create_access_token(subject=str(uid), role="admin")}

    await db_session.execute(
        text("DELETE FROM admin_actions WHERE admin_user_id = :u"), {"u": uid}
    )
    await db_session.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
    await _purge(db_session)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_gaps_carry_the_books_own_words(client: AsyncClient, notes: dict):
    r = await client.get("/api/admin/requirements/gaps", headers=_auth(notes["token"]))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["book_year"] == SENTINEL_YEAR

    gap = next(i for i in body["items"] if i["course_number"] == NUM)
    assert gap["book_requirements_text"] == BOOK_TEXT
    assert gap["book_page"] == 99
    assert gap["course_count"] == 1


async def test_gaps_exclude_arts_and_ruled_numbers(client: AsyncClient, notes: dict):
    r = await client.get("/api/admin/requirements/gaps", headers=_auth(notes["token"]))
    numbers = {i["course_number"] for i in r.json()["items"]}
    # Arts (019) has its own dedicated checker — never a gap
    assert "019" not in numbers
    # a curated number (016 Management, seeded since migration 24) is no gap
    assert "016" not in numbers


async def test_gap_closes_when_a_rule_lands(
    client: AsyncClient, notes: dict, db_session: AsyncSession
):
    await db_session.execute(
        text(
            "INSERT INTO course_requirements (course_number, exam_year, subject_rule) "
            "VALUES (:n, NULL, CAST(:r AS jsonb))"
        ),
        {"n": NUM, "r": json.dumps({"type": "any_n_subjects", "count": 3})},
    )
    await db_session.commit()
    r = await client.get("/api/admin/requirements/gaps", headers=_auth(notes["token"]))
    assert all(i["course_number"] != NUM for i in r.json()["items"])


async def test_onboarding_names_the_draft_state(
    client: AsyncClient, notes: dict, db_session: AsyncSession
):
    """A gate-created course has a machine draft in flight (9.4) — the panel
    must point at reviewing it, not at writing a factsheet from scratch."""
    await db_session.execute(
        text(
            "INSERT INTO factsheet_drafts (course_number, status, content) "
            "VALUES (:n, 'ready', 'x')"
        ),
        {"n": NUM},
    )
    await db_session.commit()

    r = await client.get("/api/admin/courses/onboarding", headers=_auth(notes["token"]))
    assert r.status_code == 200, r.text
    item = next(i for i in r.json()["items"] if i["course_code"] == CODE)
    assert item["draft_status"] == "ready"
    assert any("awaiting review" in b for b in item["blockers"])
    # and the plain missing-factsheet wording is gone for this course
    assert not any(b.startswith("no factsheet") for b in item["blockers"])
