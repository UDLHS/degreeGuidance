"""Cutoff coverage safeguard (data-integrity guard).

cutoff_coverage_gaps() lists active catalog courses with no cutoff for a year.
For 2023 (the loaded 2024/2025 handbook), exactly four courses legitimately have
no Section-9 cutoff (no 2023 intake): 103D, 104H, 105L, 140P. This test pins that
set, so a regression that drops a real course's cutoffs (as happened when 007K
was misread as 006K) fails loudly here.
"""

from __future__ import annotations

from apps.worker.jobs.ingest_zscores import cutoff_coverage_gaps

EXPECTED_2023_GAPS = {"103D", "104H", "105L", "140P"}


async def test_cutoff_coverage_gaps_2023(db_session):
    gaps = set(await cutoff_coverage_gaps(db_session, 2023))
    assert gaps == EXPECTED_2023_GAPS, (
        f"Unexpected courses without 2023 cutoffs: {sorted(gaps ^ EXPECTED_2023_GAPS)}"
    )
