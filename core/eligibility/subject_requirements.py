"""Deterministic subject-combination prerequisite checker (handbook §2.2).

Evaluates a small JSONB boolean-condition tree (course_requirements.subject_rule)
against a student's actual A/L subjects + grades. Pure Python, no LLM, no DB --
same trust boundary as core/scoring/engine.py (masterplan §20 principle #1: the
eligibility verdict is never touched by an LLM).

Leaf condition types (cover every pattern found across the full §2.2 read):
  subject_min_grade   one named subject at >= a minimum grade
  one_of_min_grade    at least one subject from a list at >= a minimum grade
  count_from_list     at least N subjects from a list, each at >= a minimum grade
  any_n_subjects      just a count of passing subjects, no subject constraint
  stream_is           true iff the student's A/L stream is in a given list --
                       for courses whose rule genuinely differs by stream (e.g.
                       Tourism & Hospitality Mgmt: Commerce/BioSci/PhysSci need
                       no extra subject gate, but Arts-stream students need a
                       specific anchor subject). Stream-level ALLOW/DENY is
                       still course_stream_eligibility's job; this is only for
                       expressing a rule that is conditional ON the stream.
  and / or            combinators

A course with no curated rule is ungated by design (see migration 24) -- callers
should treat "no rule found" as "pass" so curation can be incremental.

Arts (course 019) uses a distinct 4-basket selection system unlike anything else
in the handbook -- deliberately NOT forced into the generic tree above (a
forced-fit risks getting Sri Lanka's single largest-intake course subtly wrong).
It gets its own dedicated checker: see check_arts_basket_rule().
"""

from __future__ import annotations

from dataclasses import dataclass

GRADE_RANK = {"F": 0, "S": 1, "C": 2, "B": 3, "A": 4}


@dataclass(frozen=True)
class SubjectResult:
    subject: str
    grade: str  # one of F/S/C/B/A (case-insensitive)


def _meets_min_grade(result: SubjectResult, min_grade: str) -> bool:
    have = GRADE_RANK.get(result.grade.upper())
    need = GRADE_RANK.get(min_grade.upper())
    if have is None or need is None:
        raise ValueError(f"unknown grade: {result.grade!r} / {min_grade!r}")
    return have >= need


def evaluate_subject_rule(
    rule: dict, subjects: list[SubjectResult], stream_code: str | None = None
) -> bool:
    """Evaluate a subject_rule JSON tree against the student's actual subjects
    (and, for the few rules that need it, their A/L stream)."""
    rtype = rule["type"]

    if rtype == "and":
        return all(evaluate_subject_rule(c, subjects, stream_code) for c in rule["conditions"])
    if rtype == "or":
        return any(evaluate_subject_rule(c, subjects, stream_code) for c in rule["conditions"])

    if rtype == "stream_is":
        return stream_code in set(rule["streams"])

    if rtype == "subject_min_grade":
        return any(
            s.subject == rule["subject"] and _meets_min_grade(s, rule.get("min_grade", "S"))
            for s in subjects
        )

    if rtype == "one_of_min_grade":
        wanted = set(rule["subjects"])
        return any(
            s.subject in wanted and _meets_min_grade(s, rule.get("min_grade", "S"))
            for s in subjects
        )

    if rtype == "count_from_list":
        wanted = set(rule["subjects"])
        min_grade = rule.get("min_grade", "S")
        matched = [s for s in subjects if s.subject in wanted and _meets_min_grade(s, min_grade)]
        return len(matched) >= rule["count"]

    if rtype == "any_n_subjects":
        min_grade = rule.get("min_grade", "S")
        passing = [s for s in subjects if _meets_min_grade(s, min_grade)]
        return len(passing) >= rule["count"]

    raise ValueError(f"unknown subject_rule type: {rtype!r}")
