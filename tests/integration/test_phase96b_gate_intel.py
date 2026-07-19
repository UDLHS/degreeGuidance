"""Phase 9.6b — the gate does the reading so the admin only reviews:

- the diff pairs an added code with a removed course whose name matches —
  a rename surfaced as a NOTE on both cards, never an automatic action;
- the book prefill carries a deterministic subject-rule suggestion when (and
  only when) the book's own sentence parses completely.

Sentinel course 992X / added code 991Y / exam year 2038; purge-first.
"""

from __future__ import annotations


import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.ingestion.handbook_diff import compute_handbook_diff

CODE_REMOVED = "992X"
CODE_ADDED = "991Y"
SENTINEL_YEAR = 2038


async def _purge(db: AsyncSession) -> None:
    await db.execute(text("DELETE FROM courses WHERE course_code = :c"), {"c": CODE_REMOVED})
    await db.commit()


@pytest_asyncio.fixture
async def sentinel(db_session: AsyncSession):
    await _purge(db_session)
    uni = (
        await db_session.execute(
            text("SELECT university_id FROM universities ORDER BY university_id LIMIT 1")
        )
    ).scalar_one()
    await db_session.execute(
        text(
            "INSERT INTO courses (course_code, course_number, university_id, name_en, is_active) "
            "VALUES (:c, '992', :u, 'Sentinel Management Studies (TV)', true)"
        ),
        {"c": CODE_REMOVED, "u": uni},
    )
    await db_session.commit()
    # every OTHER active course is "present in the book", so only the sentinel
    # reads as removed — the diff stays about the two codes under test
    present = {
        r.course_code
        for r in (
            await db_session.execute(text("SELECT course_code FROM courses WHERE is_active"))
        ).all()
    } - {CODE_REMOVED}
    yield present
    await _purge(db_session)


async def test_rename_is_paired_on_both_cards(db_session: AsyncSession, sentinel: set[str]):
    changes = await compute_handbook_diff(
        db_session,
        extracted={CODE_ADDED: {"COLOMBO": "1.2345"}},
        exam_year=SENTINEL_YEAR,
        present_in_book=sentinel,
        book_details={CODE_ADDED: {"name_en": "Sentinel Management Studies"}},
    )
    added = next(c for c in changes if c.change_type == "course_added")
    removed = next(c for c in changes if c.change_type == "course_removed")
    assert removed.course_code == CODE_REMOVED

    hint = added.after_value["possible_rename_of"]
    assert hint["course_code"] == CODE_REMOVED
    assert hint["similarity"] >= 0.8

    back = removed.after_value["possible_rename_to"]
    assert [h["course_code"] for h in back] == [CODE_ADDED]


async def test_dissimilar_names_are_not_paired(db_session: AsyncSession, sentinel: set[str]):
    changes = await compute_handbook_diff(
        db_session,
        extracted={CODE_ADDED: {"COLOMBO": "1.2345"}},
        exam_year=SENTINEL_YEAR,
        present_in_book=sentinel,
        book_details={CODE_ADDED: {"name_en": "Quantum Basket Weaving"}},
    )
    added = next(c for c in changes if c.change_type == "course_added")
    removed = next(c for c in changes if c.change_type == "course_removed")
    assert "possible_rename_of" not in (added.after_value or {})
    assert "possible_rename_to" not in (removed.after_value or {})


async def test_prefill_carries_a_rule_suggestion_only_when_the_sentence_parses(
    db_session: AsyncSession,
):
    from apps.api.routers.admin_ingestions import _book_prefill

    parseable = (
        "At least ‘S’ grades in any three subjects at the G.C.E. "
        "(Advanced Level) Examination."
    )
    unparseable = (
        "At least ‘S’ grades in any three subjects in the Commerce Stream or "
        "Biological Science Stream at the G.C.E. (Advanced Level) Examination."
    )
    out = await _book_prefill(
        db_session,
        {"book_code_rows": []},
        {"991Y": [], "990Y": []},
        {
            "991": {"requirements_text": parseable},
            "990": {"requirements_text": unparseable},
        },
    )
    assert out["991Y"]["suggested_subject_rule"] == {
        "type": "any_n_subjects", "count": 3, "min_grade": "S",
    }
    assert "suggested_subject_rule" not in out["990Y"]
