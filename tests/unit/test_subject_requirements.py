"""Unit tests for the subject-requirement checker, using REAL rules read
directly from the 2024/2025 handbook §2.2 (not invented examples)."""

from __future__ import annotations

from core.eligibility.subject_requirements import (
    SubjectResult,
    evaluate_subject_rule,
)


def _s(*pairs: tuple[str, str]) -> list[SubjectResult]:
    return [SubjectResult(subject=sub, grade=grade) for sub, grade in pairs]


# Engineering (008): "At least three 'S' grades in Chemistry, Combined
# Mathematics and Physics" -- exact, no substitution.
ENGINEERING_RULE = {
    "type": "and",
    "conditions": [
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Combined Mathematics", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
    ],
}


def test_engineering_pcm_student_qualifies():
    pcm = _s(("Physics", "S"), ("Chemistry", "S"), ("Combined Mathematics", "S"))
    assert evaluate_subject_rule(ENGINEERING_RULE, pcm) is True


def test_engineering_pmi_student_does_not_qualify():
    """The exact case the user raised: Physics+Maths+ICT, no Chemistry."""
    pmi = _s(("Physics", "S"), ("Combined Mathematics", "S"), ("Information & Communication Technology", "S"))
    assert evaluate_subject_rule(ENGINEERING_RULE, pmi) is False


# Medicine (001): "At least two 'C' grades and a 'S' grade in Biology,
# Chemistry and Physics" -- all three named, two of the three at C, one at S.
# Modeled as: each of the 3 subjects present at >= S, AND at least 2 of them at >= C.
MEDICINE_RULE = {
    "type": "and",
    "conditions": [
        {"type": "subject_min_grade", "subject": "Biology", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Chemistry", "min_grade": "S"},
        {"type": "subject_min_grade", "subject": "Physics", "min_grade": "S"},
        {
            "type": "count_from_list",
            "subjects": ["Biology", "Chemistry", "Physics"],
            "count": 2,
            "min_grade": "C",
        },
    ],
}


def test_medicine_two_c_one_s_qualifies():
    student = _s(("Biology", "C"), ("Chemistry", "C"), ("Physics", "S"))
    assert evaluate_subject_rule(MEDICINE_RULE, student) is True


def test_medicine_all_s_no_c_fails():
    student = _s(("Biology", "S"), ("Chemistry", "S"), ("Physics", "S"))
    assert evaluate_subject_rule(MEDICINE_RULE, student) is False


def test_medicine_missing_subject_fails():
    student = _s(("Biology", "C"), ("Chemistry", "C"), ("Combined Mathematics", "S"))
    assert evaluate_subject_rule(MEDICINE_RULE, student) is False


# IT (026): "3 passes including at least a 'C' grade in one of {Higher Maths,
# Combined Maths, Maths, Physics}"
IT_RULE = {
    "type": "and",
    "conditions": [
        {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
        {
            "type": "one_of_min_grade",
            "subjects": ["Higher Mathematics", "Combined Mathematics", "Mathematics", "Physics"],
            "min_grade": "C",
        },
    ],
}


def test_it_qualifies_with_combined_maths_credit():
    student = _s(("Combined Mathematics", "C"), ("Physics", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(IT_RULE, student) is True


def test_it_fails_without_credit_in_maths_or_physics():
    student = _s(("Combined Mathematics", "S"), ("Physics", "S"), ("Chemistry", "S"))
    assert evaluate_subject_rule(IT_RULE, student) is False


# MIT (027) -- the OR pattern: 3 from Bio/PhysSci stream, OR 2 from that stream
# + ICT as the third, PLUS a C grade in one of 4 maths/physics subjects.
MIT_RULE = {
    "type": "and",
    "conditions": [
        {
            "type": "one_of_min_grade",
            "subjects": ["Higher Mathematics", "Combined Mathematics", "Mathematics", "Physics"],
            "min_grade": "C",
        },
        {
            "type": "or",
            "conditions": [
                {
                    "type": "count_from_list",
                    "subjects": ["Biology", "Chemistry", "Physics", "Combined Mathematics", "Mathematics", "Higher Mathematics"],
                    "count": 3,
                    "min_grade": "S",
                },
                {
                    "type": "and",
                    "conditions": [
                        {
                            "type": "count_from_list",
                            "subjects": ["Biology", "Chemistry", "Physics", "Combined Mathematics", "Mathematics", "Higher Mathematics"],
                            "count": 2,
                            "min_grade": "S",
                        },
                        {"type": "subject_min_grade", "subject": "Information & Communication Technology", "min_grade": "S"},
                    ],
                },
            ],
        },
    ],
}


def test_mit_qualifies_via_ict_substitution():
    """2 Physical-Science subjects + ICT as the third -- the alternate path."""
    student = _s(("Combined Mathematics", "C"), ("Physics", "S"), ("Information & Communication Technology", "S"))
    assert evaluate_subject_rule(MIT_RULE, student) is True


def test_mit_fails_with_only_one_stream_subject_and_no_ict():
    student = _s(("Combined Mathematics", "C"), ("Accounting", "S"), ("Economics", "S"))
    assert evaluate_subject_rule(MIT_RULE, student) is False


# stream_is -- Tourism & Hospitality Management (092)-style rule: Commerce /
# BioSci / PhysSci students need no extra subject gate; Arts-stream students
# specifically need >=1 of {Economics, Geography, Business Statistics}.
TOURISM_HOSPITALITY_RULE = {
    "type": "or",
    "conditions": [
        {
            "type": "and",
            "conditions": [
                {"type": "stream_is", "streams": ["COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"]},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ],
        },
        {
            "type": "and",
            "conditions": [
                {"type": "stream_is", "streams": ["ARTS"]},
                {"type": "one_of_min_grade", "subjects": ["Economics", "Geography", "Business Statistics"], "min_grade": "S"},
                {"type": "any_n_subjects", "count": 3, "min_grade": "S"},
            ],
        },
    ],
}


def test_stream_is_commerce_student_no_extra_gate():
    student = _s(("Business Studies", "S"), ("Economics", "S"), ("Accounting", "S"))
    assert evaluate_subject_rule(TOURISM_HOSPITALITY_RULE, student, stream_code="COMMERCE") is True


def test_stream_is_arts_student_with_anchor_subject_passes():
    student = _s(("Geography", "S"), ("History", "S"), ("Sinhala", "S"))
    assert evaluate_subject_rule(TOURISM_HOSPITALITY_RULE, student, stream_code="ARTS") is True


def test_stream_is_arts_student_without_anchor_subject_fails():
    student = _s(("History", "S"), ("Sinhala", "S"), ("Tamil", "S"))
    assert evaluate_subject_rule(TOURISM_HOSPITALITY_RULE, student, stream_code="ARTS") is False


def test_stream_is_unlisted_stream_fails_both_branches():
    # ENGINEERING_TECH isn't covered by either branch -- correctly excluded
    # (course_stream_eligibility wouldn't route this student here anyway).
    student = _s(("Engineering Technology", "S"), ("Science for Technology", "S"), ("Mathematics", "S"))
    assert evaluate_subject_rule(TOURISM_HOSPITALITY_RULE, student, stream_code="ENGINEERING_TECH") is False


# -- validate_subject_rule (Phase 9 D6: a typo must die at the gate) ----------

from core.eligibility.subject_requirements import validate_subject_rule  # noqa: E402

_SUBJECTS = {"Biology", "Chemistry", "Physics", "Combined Mathematics", "Economics"}
_STREAMS = {"ARTS", "COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE"}


def _v(rule):
    return validate_subject_rule(rule, known_subjects=_SUBJECTS, known_streams=_STREAMS)


def test_validator_accepts_a_real_handbook_rule():
    assert _v(ENGINEERING_RULE) == []


def test_validator_accepts_any_n_subjects():
    assert _v({"type": "any_n_subjects", "count": 3, "min_grade": "S"}) == []


def test_validator_names_a_misspelled_subject():
    errs = _v({"type": "count_from_list", "subjects": ["Bio", "Chemistry"], "count": 2})
    assert any("Bio" in e for e in errs)


def test_validator_rejects_unknown_type_and_non_dict():
    assert _v({"type": "what_even"})
    assert _v(["not", "a", "rule"])
    assert _v(None)


def test_validator_rejects_empty_combinators_and_bad_counts():
    assert _v({"type": "and", "conditions": []})
    assert _v({"type": "count_from_list", "subjects": ["Biology"], "count": 0})
    assert _v({"type": "any_n_subjects", "count": True})


def test_validator_rejects_bad_grade_and_unknown_stream():
    assert _v({"type": "any_n_subjects", "count": 3, "min_grade": "Z"})
    assert _v({"type": "stream_is", "streams": ["ICT"]})


def test_validator_walks_nested_trees_with_paths():
    errs = _v({
        "type": "or",
        "conditions": [
            {"type": "subject_min_grade", "subject": "Economics", "min_grade": "B"},
            {"type": "subject_min_grade", "subject": "Econ", "min_grade": "B"},
        ],
    })
    assert len(errs) == 1
    assert "conditions[1]" in errs[0] and "Econ" in errs[0]


def test_every_rule_the_validator_accepts_actually_evaluates():
    """The validator and the evaluator must agree on the grammar: a rule that
    passes validation can never blow up at serve time."""
    ok = {
        "type": "and",
        "conditions": [
            {"type": "one_of_min_grade", "subjects": ["Biology", "Chemistry"], "min_grade": "C"},
            {"type": "stream_is", "streams": ["BIO_SCIENCE"]},
            {"type": "any_n_subjects", "count": 3},
        ],
    }
    assert _v(ok) == []
    evaluate_subject_rule(ok, _s(("Biology", "A"), ("Chemistry", "B"), ("Physics", "S")), "BIO_SCIENCE")
