"""Unit tests for the deterministic scorer (masterplan §9). Pure, no DB."""

from __future__ import annotations

from core.scoring.engine import (
    ScorableCourse,
    ScoringProfile,
    score_course,
    score_courses,
)

CONFIG = {
    "weights": {
        "interest": 0.30,
        "career": 0.25,
        "z_margin": 0.15,
        "university": 0.15,
        "industry": 0.15,
    },
    "thresholds": {
        "safe_score": 0.6,
        "safe_margin": 0.10,
        "ambitious_score": 0.6,
        "ambitious_margin": 0.05,
        "hidden_score": 0.5,
        "marginal_band": 0.05,
        "z_margin_tanh_scale": 4.0,
    },
}


def _course(code: str, margin: float, uni: str = "CMB", uni_district: int = 1) -> ScorableCourse:
    return ScorableCourse(
        course_code=code,
        cutoff_z_score=2.0,
        student_margin=margin,
        university_code=uni,
        university_district_id=uni_district,
    )


def test_no_preferences_only_zmargin_active():
    profile = ScoringProfile(z_score=2.5, district_id=1)
    assert profile.has_preferences is False
    scored = score_course(_course("001A", margin=0.5), profile, CONFIG)
    names = [d.name for d in scored.breakdown]
    assert names == ["z_margin"]  # university inert without preferred unis
    assert scored.breakdown[0].weight == 1.0  # renormalized to the only active dim
    assert scored.total_score == scored.breakdown[0].raw_score


def test_zmargin_at_cutoff_is_half():
    profile = ScoringProfile(z_score=2.0, district_id=1)
    scored = score_course(_course("001A", margin=0.0), profile, CONFIG)
    assert scored.breakdown[0].raw_score == 0.5  # tanh(0)=0 -> mapped to 0.5


def test_higher_margin_ranks_first():
    profile = ScoringProfile(z_score=2.5, district_id=1)
    courses = [_course("LOW", margin=0.05), _course("HIGH", margin=0.6)]
    ranked = score_courses(courses, profile, CONFIG)
    assert [s.course_code for s in ranked] == ["HIGH", "LOW"]
    assert ranked[0].total_score > ranked[1].total_score


def test_preferred_university_activates_and_boosts():
    profile = ScoringProfile(z_score=2.5, district_id=1, preferred_university_codes=frozenset({"CMB"}))
    assert profile.has_preferences is True
    preferred = score_course(_course("P", margin=0.3, uni="CMB"), profile, CONFIG)
    other = score_course(_course("O", margin=0.3, uni="PDN", uni_district=9), profile, CONFIG)
    names = {d.name for d in preferred.breakdown}
    assert names == {"z_margin", "university"}  # two active dims now
    # both dims renormalize to 0.5 each (0.15 / (0.15+0.15))
    assert all(round(sum(d.weight for d in s.breakdown), 4) == 1.0 for s in (preferred, other))
    uni_raw = {d.name: d.raw_score for d in preferred.breakdown}["university"]
    assert uni_raw == 1.0
    assert preferred.total_score > other.total_score  # same margin, preferred uni wins


def test_bucket_safe_for_comfortable_margin():
    profile = ScoringProfile(z_score=2.6, district_id=1)
    scored = score_course(_course("S", margin=0.6), profile, CONFIG)  # big margin -> high z score
    assert scored.bucket == "safe"
    assert scored.is_marginal is False


def test_bucket_ambitious_high_fit_low_margin():
    # ambitious needs total>=0.6 AND margin<0.05 — only reachable when another
    # dimension lifts the total. Preferred-uni does that here.
    profile = ScoringProfile(z_score=2.02, district_id=1, preferred_university_codes=frozenset({"CMB"}))
    scored = score_course(_course("A", margin=0.02, uni="CMB"), profile, CONFIG)
    assert scored.is_marginal is True
    assert scored.bucket == "ambitious"


def test_marginal_flag_within_band():
    profile = ScoringProfile(z_score=2.03, district_id=1)
    assert score_course(_course("M", margin=0.03), profile, CONFIG).is_marginal is True
    assert score_course(_course("N", margin=0.20), profile, CONFIG).is_marginal is False
