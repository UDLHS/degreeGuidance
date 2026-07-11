"""Cutoff coverage safeguard (data-integrity guard).

cutoff_coverage_gaps() lists active catalog courses with no cutoff for a year.
These tests pin the empirically-verified gap sets for the promoted years, so a
regression that drops a real course's cutoffs (as happened when 007K was
misread as 006K) fails loudly here.

Pinned sets re-verified 2026-07-10 against the rebuilt pipeline's full 2023 +
2024 ingests (every book cutoff column value-matched — nothing extracted was
dropped; see the completeness checks in that session):

2023 gaps (9) — each justified from the 2023 book itself:
  103D, 104H, 105L  — no cutoff column printed in the 2023 book (no intake).
  139C              — Polymer Science, NEW course in 2023 ("(New)", book p117);
                      a first-year course has no prior-year cutoffs to print.
  040R, 040W, 042L  — 2024-book-only variant codes. The 2023 book prints these
                      as ' - B' columns of the BASE codes; their 2023 numbers
                      live as stream overrides under 022R/022W/021L
                      (course_stream_cutoff_overrides), not under these codes.
  271D              — MIT (Bio Science Stream), same class: printed as its own
                      code only from the 2024 book; 2023 has a single MIT
                      column (027D).
  140P              — Service Management (Gampaha Wickramarachchi), new course
                      with no printed cutoff column in EITHER book — same class
                      as 103D/104H/105L. (An earlier pin note claimed the
                      rebuilt extractor had found 2023 data for it; that was a
                      misread — it was merely inactive at the time. The 2023
                      handbook-sync auto-deactivated it as "not in book"; the
                      admin re-activated it 2026-07-11, which is the honest
                      state: offered, no cutoff history yet.)

2024 gaps (4): 103D, 104H, 105L, 140P — no cutoff column in the 2024 book; the
variant codes and 139C all carry printed 2024 columns.
"""

from __future__ import annotations

from apps.worker.jobs.ingest_zscores import cutoff_coverage_gaps

EXPECTED_2023_GAPS = {
    "103D", "104H", "105L",          # no cutoff column in the 2023 book
    "139C",                           # new-in-2023 course, no prior-year results
    "040R", "040W", "042L", "271D",  # 2024-book codes; 2023 data = base-code stream overrides
    "140P",                           # new course, no cutoff column in either book
}

EXPECTED_2024_GAPS = {"103D", "104H", "105L", "140P"}


async def test_cutoff_coverage_gaps_2023(db_session):
    gaps = set(await cutoff_coverage_gaps(db_session, 2023))
    assert gaps == EXPECTED_2023_GAPS, (
        f"Unexpected courses without 2023 cutoffs: {sorted(gaps ^ EXPECTED_2023_GAPS)}"
    )


async def test_cutoff_coverage_gaps_2024(db_session):
    gaps = set(await cutoff_coverage_gaps(db_session, 2024))
    assert gaps == EXPECTED_2024_GAPS, (
        f"Unexpected courses without 2024 cutoffs: {sorted(gaps ^ EXPECTED_2024_GAPS)}"
    )
