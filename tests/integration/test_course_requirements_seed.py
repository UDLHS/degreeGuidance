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
    # 125 from migration 25 + 3 specials (040, 042, 271) from migration 30.
    assert len(rows) == 128
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
    """The C-grade in Sinhala-or-Tamil is mandatory always (migration 29
    correction) -- English-S is a separate additional condition, never a
    substitute for it."""
    rule = await _rule_for(db_session, "098")
    via_sinhala_credit = _s(("Sinhala", "C"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, via_sinhala_credit) is True
    via_tamil_credit = _s(("Tamil", "C"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, via_tamil_credit) is True
    english_s_without_sinhala_tamil_credit_fails = _s(("English", "S"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, english_s_without_sinhala_tamil_credit_fails) is False
    sinhala_below_credit_fails = _s(("Sinhala", "S"), ("History", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, sinhala_below_credit_fails) is False
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


async def test_tourism_hospitality_092_stream_conditional(db_session):
    """migration 29: Commerce/BioSci/PhysSci need no extra gate; Arts needs an
    anchor subject."""
    rule = await _rule_for(db_session, "092")
    commerce_any_three = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, commerce_any_three, stream_code="COMMERCE") is True
    arts_with_anchor = _s(("Geography", "S"), ("History", "S"), ("Sinhala", "S"))
    assert evaluate_subject_rule(rule, arts_with_anchor, stream_code="ARTS") is True
    arts_without_anchor = _s(("History", "S"), ("Sinhala", "S"), ("Tamil", "S"))
    assert evaluate_subject_rule(rule, arts_without_anchor, stream_code="ARTS") is False
    wrong_stream = _s(("Engineering Technology", "S"), ("Science for Technology", "S"), ("Mathematics", "S"))
    assert evaluate_subject_rule(rule, wrong_stream, stream_code="ENGINEERING_TECH") is False


async def test_food_business_management_107_stream_conditional(db_session):
    rule = await _rule_for(db_session, "107")
    bio_path = _s(("Chemistry", "S"), ("Biology", "S"), ("Physics", "S"))
    assert evaluate_subject_rule(rule, bio_path, stream_code="BIO_SCIENCE") is True
    commerce_path = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, commerce_path, stream_code="COMMERCE") is True
    # right subjects, wrong nominal stream -- correctly excluded
    assert evaluate_subject_rule(rule, commerce_path, stream_code="ARTS") is False


async def test_business_science_109_stream_conditional(db_session):
    rule = await _rule_for(db_session, "109")
    three_subjects = _s(("Combined Mathematics", "S"), ("Physics", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(rule, three_subjects, stream_code="PHYSICAL_SCIENCE") is True
    two_plus_ict = _s(("Business Studies", "S"), ("Economics", "S"), ("Information & Communication Technology", "S"))
    assert evaluate_subject_rule(rule, two_plus_ict, stream_code="COMMERCE") is True
    assert evaluate_subject_rule(rule, three_subjects, stream_code="ARTS") is False


async def test_indigenous_pharma_tech_124_dual_path(db_session):
    rule = await _rule_for(db_session, "124")
    via_eng_tech_stream = _s(("Engineering Technology", "S"), ("Science for Technology", "S"), ("Mathematics", "S"))
    assert evaluate_subject_rule(rule, via_eng_tech_stream, stream_code="ENGINEERING_TECH") is True
    via_pure_subjects_any_stream = _s(("Chemistry", "S"), ("Physics", "S"), ("Biology", "S"))
    assert evaluate_subject_rule(rule, via_pure_subjects_any_stream, stream_code="BIO_SCIENCE") is True
    neither = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, neither, stream_code="COMMERCE") is False


async def test_management_studies_tv_b_040_any_three_any_stream(db_session):
    """migration 30: same programme as base course 022, open to any stream."""
    rule = await _rule_for(db_session, "040")
    arts_student = _s(("History", "S"), ("Sinhala", "S"), ("Geography", "S"))
    assert evaluate_subject_rule(rule, arts_student) is True
    commerce_student = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, commerce_student) is True


async def test_arts_sab_b_042_any_three(db_session):
    """migration 30: Commerce-quota variant of course 021, no extra subject gate."""
    rule = await _rule_for(db_session, "042")
    commerce_student = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, commerce_student) is True


async def test_mit_bio_science_271_mirrors_027(db_session):
    """migration 30: same eligibility logic as course 027 (MIT), Bio-Science quota track."""
    rule = await _rule_for(db_session, "271")
    qualifies = _s(("Combined Mathematics", "C"), ("Biology", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(rule, qualifies) is True
    via_ict_substitution = _s(("Combined Mathematics", "C"), ("Biology", "S"), ("Information & Communication Technology", "S"))
    assert evaluate_subject_rule(rule, via_ict_substitution) is True
    no_maths_physics_anchor = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(rule, no_maths_physics_anchor) is False
