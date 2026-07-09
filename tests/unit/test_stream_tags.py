"""Tests for the bracket-tag -> stream-code parser (core.ingestion.stream_tags),
traced against the real labels this feature exists for: Food Business
Management (107L, Sabaragamuwa) prints "[Commerce Stream]" and
"[Biological / Physical Science Stream]" as two separate cutoff-table
columns sharing one Uni-Code."""

from __future__ import annotations

from core.ingestion.stream_tags import (
    parse_streams,
    resolve_group_streams,
    suggest_stream_codes,
)


def test_commerce_stream_tag():
    assert suggest_stream_codes(
        "FOOD BUSINESS MANAGEMENT [Commerce Stream] (Sabaragamuwa University of Sri Lanka)"
    ) == ["COMMERCE"]


def test_combined_bio_physical_stream_tag():
    assert suggest_stream_codes(
        "FOOD BUSINESS MANAGEMENT [Biological / Physical Science Stream] "
        "(Sabaragamuwa University of Sri Lanka)"
    ) == ["BIO_SCIENCE", "PHYSICAL_SCIENCE"]


def test_any_subject_combination_expands_to_all_non_ict_streams():
    codes = suggest_stream_codes(
        "MANAGEMENT STUDIES (TV) - B [Any subject combination] (University of Vavuniya, Sri Lanka)"
    )
    assert set(codes) == {
        "ARTS", "COMMERCE", "BIO_SCIENCE", "PHYSICAL_SCIENCE",
        "ENGINEERING_TECH", "BIOSYSTEMS_TECH",
    }
    assert "ICT" not in codes


def test_no_bracket_tag_returns_empty():
    assert suggest_stream_codes("PRIMARY EDUCATION (University of Colombo)") == []


def test_unrecognised_bracket_text_returns_empty_not_a_guess():
    assert suggest_stream_codes("SOME COURSE [Foo Bar Baz] (Some University)") == []


def test_arts_stream_tag():
    assert suggest_stream_codes("SOME COURSE [Arts Stream] (Some University)") == ["ARTS"]


# ── parse_streams: explicit vs open ('any subject combination') ──────────────

def test_parse_streams_explicit():
    assert parse_streams("X [Commerce Stream] (U)") == (["COMMERCE"], False)


def test_parse_streams_open():
    assert parse_streams("X [Any subject combination] (U)") == ([], True)


def test_parse_streams_none():
    assert parse_streams("X (U)") == ([], False)


# ── resolve_group_streams: the complement rule keeps a group DISJOINT ─────────

# The real 2023 case: Management Studies (TV), Vavuniya — A=Commerce quota,
# B=open quota. The book (p53) reserves 60/40% for Commerce; everyone else
# enters via the open quota. So Commerce -> A, all other non-ICT streams -> B.
# The universe is the 6 non-ICT streams (handbook cross-stream convention),
# NOT course_stream_eligibility (which lists only 022R's home stream COMMERCE
# and would make the complement empty).
def test_group_commerce_vs_any_is_disjoint():
    labels = [
        "MANAGEMENT STUDIES (TV) - A [Commerce Stream] (University of Vavuniya, Sri Lanka)",
        "MANAGEMENT STUDIES (TV) - B [Any subject combination] (University of Vavuniya, Sri Lanka)",
    ]
    a, b = resolve_group_streams(labels)  # default universe = 6 non-ICT streams
    assert a == ["COMMERCE"]
    assert "COMMERCE" not in b          # the whole point: no overlap
    assert set(b) == {"ARTS", "BIO_SCIENCE", "PHYSICAL_SCIENCE",
                      "ENGINEERING_TECH", "BIOSYSTEMS_TECH"}
    assert "ICT" not in b               # matches the migration-16 convention


def test_group_two_explicit_streams_unchanged():
    # Food Business Management (107L): Commerce vs Bio/Physical — both explicit,
    # already disjoint, no open column so the universe is never consulted.
    labels = [
        "FOOD BUSINESS MANAGEMENT [Commerce Stream] (Sabaragamuwa University of Sri Lanka)",
        "FOOD BUSINESS MANAGEMENT [Biological / Physical Science Stream] (Sabaragamuwa University of Sri Lanka)",
    ]
    a, b = resolve_group_streams(labels)
    assert a == ["COMMERCE"]
    assert b == ["BIO_SCIENCE", "PHYSICAL_SCIENCE"]


def test_group_arts_sab_arts_vs_commerce():
    labels = [
        "ARTS (SAB) - A * [Arts Stream] (Sabaragamuwa University of Sri Lanka)",
        "ARTS (SAB) - B * [Commerce Stream] (Sabaragamuwa University of Sri Lanka)",
    ]
    a, b = resolve_group_streams(labels)
    assert a == ["ARTS"]
    assert b == ["COMMERCE"]


def test_group_open_default_universe_is_non_ict():
    labels = [
        "X - A [Commerce Stream] (U)",
        "X - B [Any subject combination] (U)",
    ]
    a, b = resolve_group_streams(labels)  # default universe
    assert a == ["COMMERCE"]
    assert "COMMERCE" not in b
    assert set(b) == {"ARTS", "BIO_SCIENCE", "PHYSICAL_SCIENCE",
                      "ENGINEERING_TECH", "BIOSYSTEMS_TECH"}
