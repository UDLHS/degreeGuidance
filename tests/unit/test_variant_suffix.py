"""Tests for strip_variant_suffix (core.ingestion.column_mapper): only a bare
single-letter ' - A'/' - B' track marker is removed, so the base name can be
matched against the book's Uni-Code section. Multi-word ' - Mass Media' style
suffixes (which ARE part of a distinct course name) must survive."""

from __future__ import annotations

from core.ingestion.column_mapper import strip_variant_suffix, _VARIANT_SUFFIX_RE


def test_strips_bare_letter_track_marker():
    out = strip_variant_suffix(
        "MANAGEMENT STUDIES (TV) - B [Any subject combination] (University of Vavuniya, Sri Lanka)"
    )
    assert " - B" not in out
    assert "MANAGEMENT STUDIES (TV)" in out
    assert "Vavuniya" in out  # university preserved for the section lookup


def test_strips_a_marker_with_star():
    out = strip_variant_suffix("ARTS (SAB) - A * [Arts Stream] (Sabaragamuwa University of Sri Lanka)")
    assert " - A " not in out
    assert "ARTS (SAB)" in out


def test_keeps_multiword_suffix():
    # 'Arts (SP) - Mass Media' is a real distinct course name, NOT a track split.
    label = "Arts (SP) - Mass Media (Sripalee Campus, University of Colombo)"
    assert strip_variant_suffix(label) == label
    assert not _VARIANT_SUFFIX_RE.search(label)


def test_no_suffix_unchanged():
    label = "FOOD BUSINESS MANAGEMENT [Commerce Stream] (Sabaragamuwa University of Sri Lanka)"
    assert strip_variant_suffix(label) == label
