"""Validates the curated course_requirements data against the real DB.

Two layers: (1) every seeded rule must be a well-formed, evaluable tree
(structural), and (2) spot-checks of specific real courses against known-true
and known-false subject combinations, read directly from the handbook
(semantic) -- catches transcription mistakes the structural check can't see.
"""

from __future__ import annotations

from sqlalchemy import text

from core.eligibility.subject_requirements import SubjectResult, evaluate_subject_rule


def _s(*pairs: tuple[str, str]) -> list[SubjectResult]:
    return [SubjectResult(subject=sub, grade=grade) for sub, grade in pairs]


async def test_seeded_count_and_no_typo_course_numbers(db_session):
    rows = (await db_session.execute(text("SELECT course_number FROM course_requirements"))).scalars().all()
    assert len(rows) == 125
    real = (await db_session.execute(text("SELECT DISTINCT course_number FROM courses"))).scalars().all()
    real_set = set(real)
    assert all(cn in real_set for cn in rows), "a curated course_number doesn't exist in courses"


async def test_every_seeded_rule_evaluates_without_error(db_session):
    rows = (await db_session.execute(text("SELECT course_number, subject_rule FROM course_requirements"))).all()
    probe = _s(*[(s, "A") for s in [
        "Chemistry", "Physics", "Biology", "Combined Mathematics", "Mathematics", "Higher Mathematics",
        "Information & Communication Technology", "Accounting", "Business Studies", "Economics",
        "Business Statistics", "Agricultural Science", "Engineering Technology", "Biosystems Technology",
        "Science for Technology", "English", "Sinhala", "Tamil", "Art", "Music", "Dancing", "Drama & Theatre",
    ]])
    for r in rows:
        evaluate_subject_rule(r.subject_rule, probe)  # raises on malformed tree


async def _rule_for(db_session, course_number: str) -> dict:
    row = (
        await db_session.execute(
            text("SELECT subject_rule FROM course_requirements WHERE course_number = :n"),
            {"n": course_number},
        )
    ).first()
    assert row is not None, f"no curated rule for {course_number}"
    return row.subject_rule


async def test_computer_science_012_real_cases(db_session):
    rule = await _rule_for(db_session, "012")
    # "C grade in one of {CombMaths,Physics,HigherMaths}; + 2 more S from the 6-list"
    qualifies = _s(("Combined Mathematics", "C"), ("Physics", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(rule, qualifies) is True
    fails_no_credit = _s(("Combined Mathematics", "S"), ("Physics", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(rule, fails_no_credit) is False


async def test_translation_studies_098_real_cases(db_session):
    rule = await _rule_for(db_session, "098")
    via_sinhala_credit = _s(("Sinhala", "C"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, via_sinhala_credit) is True
    via_english_s = _s(("English", "S"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, via_english_s) is True
    neither_path = _s(("History", "S"), ("Geography", "S"), ("Economics", "S"))
    assert evaluate_subject_rule(rule, neither_path) is False


async def test_law_025_real_cases(db_session):
    rule = await _rule_for(db_session, "025")
    three_from_list_a = _s(("Economics", "S"), ("History", "S"), ("Political Science", "S"))
    assert evaluate_subject_rule(rule, three_from_list_a) is True
    one_from_a_two_languages = _s(("Economics", "S"), ("Sinhala", "S"), ("English", "S"))
    assert evaluate_subject_rule(rule, one_from_a_two_languages) is True
    three_languages_only_no_list_a = _s(("Sinhala", "S"), ("Tamil", "S"), ("English", "S"))
    # neither path: path A needs 3 from list A; path B needs >=1 from A + 2 from B.
    # 3 pure languages satisfies path B's "2 from B" but has 0 from list A -- fails.
    assert evaluate_subject_rule(rule, three_languages_only_no_list_a) is False


async def test_financial_economics_131_b_grade_gate(db_session):
    rule = await _rule_for(db_session, "131")
    economics_b = _s(("Economics", "B"), ("Accounting", "S"), ("Business Studies", "S"))
    assert evaluate_subject_rule(rule, economics_b) is True
    economics_c_not_enough = _s(("Economics", "C"), ("Accounting", "S"), ("Business Studies", "S"))
    assert evaluate_subject_rule(rule, economics_c_not_enough) is False
