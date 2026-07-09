"""Tests for the mapping-confirm duplicate-code validation
(apps.api.routers.admin_ingestions._is_valid_stream_split /
_duplicate_mappings): a course code with >1 confirmed column is only allowed
through when it's a genuine disjoint stream split (e.g. 107L's Commerce vs
Bio/Physical Science columns) -- never a real ambiguous duplicate. This
validation is the only thing standing between letting two columns share a
code and ingest_zscores.py's upsert crashing outright (Postgres rejects
ON CONFLICT DO UPDATE hitting the same key twice in one statement)."""

from __future__ import annotations

from apps.api.routers.admin_ingestions import _duplicate_mappings, _is_valid_stream_split
from core.models.cutoffs import ExtractionColumn


def _col(mapped_course_code="107L", override_streams=None, status="confirmed"):
    return ExtractionColumn(
        run_id=None, column_key="k", page_number=1, raw_label="x",
        mapped_course_code=mapped_course_code, override_streams=override_streams,
        status=status,
    )


def test_single_column_is_always_valid():
    assert _is_valid_stream_split([_col()]) is True


def test_disjoint_stream_split_is_valid():
    cols = [_col(override_streams="COMMERCE"), _col(override_streams="BIO_SCIENCE,PHYSICAL_SCIENCE")]
    assert _is_valid_stream_split(cols) is True


def test_plain_plus_one_override_is_valid():
    """A general column (no override) plus one stream-specific outlier."""
    cols = [_col(override_streams=None), _col(override_streams="ICT")]
    assert _is_valid_stream_split(cols) is True


def test_two_plain_columns_same_code_is_invalid():
    cols = [_col(override_streams=None), _col(override_streams=None)]
    assert _is_valid_stream_split(cols) is False


def test_overlapping_streams_is_invalid():
    cols = [_col(override_streams="COMMERCE,BIO_SCIENCE"), _col(override_streams="BIO_SCIENCE")]
    assert _is_valid_stream_split(cols) is False


def test_empty_override_streams_string_treated_as_plain():
    cols = [_col(override_streams=""), _col(override_streams="COMMERCE")]
    # "" normalises to no streams -> counts as the one allowed plain column
    assert _is_valid_stream_split(cols) is True


def test_duplicate_mappings_excludes_valid_stream_split():
    cols = [
        _col(mapped_course_code="107L", override_streams="COMMERCE"),
        _col(mapped_course_code="107L", override_streams="BIO_SCIENCE,PHYSICAL_SCIENCE"),
    ]
    assert _duplicate_mappings(cols) == {}


def test_duplicate_mappings_flags_real_conflict():
    cols = [
        _col(mapped_course_code="096L", override_streams=None),
        _col(mapped_course_code="096L", override_streams=None),
    ]
    assert _duplicate_mappings(cols) == {"096L": 2}


def test_duplicate_mappings_ignores_ignored_columns():
    cols = [
        _col(mapped_course_code="096L", override_streams=None, status="confirmed"),
        _col(mapped_course_code="096L", override_streams=None, status="ignored"),
    ]
    assert _duplicate_mappings(cols) == {}
