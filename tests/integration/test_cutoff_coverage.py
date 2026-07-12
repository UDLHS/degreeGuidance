"""Cutoff coverage safeguard (data-integrity guard).

cutoff_coverage_gaps() lists active catalog courses with no cutoff for a year.
These tests pin the empirically-verified gap sets for the promoted years, so a
regression that drops a real course's cutoffs (as happened when 007K was
misread as 006K) fails loudly here.

YEAR CONVENTION (settled 2026-07-12): a year label = the A/L examination year
the book's results come from — the book's own "Based on the results of the
G.C.E. (A/L) Examination YYYY" line. handbook_YYYY.pdf is the book HANDED TO
cohort YYYY and carries exam YYYY-1 cutoffs:
    handbook_2023.pdf -> exam year 2022
    handbook_2024.pdf -> exam year 2023
    handbook_2025.pdf -> exam year 2024

2022 gaps (9) — each justified from handbook_2023.pdf itself:
  103D, 104H, 105L  — no cutoff column printed in that book (no intake).
  139C              — Polymer Science, NEW course that cycle ("(New)", p117);
                      a first-year course has no prior-year cutoffs to print.
  040R, 040W, 042L  — codes that only exist from handbook_2024 on. The older
                      book prints these as ' - B' columns of the BASE codes;
                      their numbers live as stream overrides under
                      022R/022W/021L (course_stream_cutoff_overrides).
  271D              — MIT (Bio Science Stream), same class: its own code only
                      from handbook_2024 on; the older book has a single MIT
                      column (027D).
  140P              — Service Management (Gampaha Wickramarachchi), new course
                      with no printed cutoff column in either book — same
                      class as 103D/104H/105L. (An earlier pin note claimed
                      the rebuilt extractor had found data for it; that was a
                      misread — it was merely inactive at the time. The
                      handbook-sync auto-deactivated it as "not in book"; the
                      admin re-activated it 2026-07-11, which is the honest
                      state: offered, no cutoff history yet.)

2023 gaps (4): 103D, 104H, 105L, 140P — no cutoff column in handbook_2024.pdf;
the variant codes and 139C all carry printed columns there.
"""

from __future__ import annotations

from apps.worker.jobs.ingest_zscores import cutoff_coverage_gaps

EXPECTED_2022_GAPS = {
    "103D", "104H", "105L",          # no cutoff column in handbook_2023.pdf
    "139C",                           # new course that cycle, no prior-year results
    "040R", "040W", "042L", "271D",  # handbook_2024-era codes; older data = base-code stream overrides
    "140P",                           # new course, no cutoff column in either book
}

EXPECTED_2023_GAPS = {"103D", "104H", "105L", "140P"}


async def test_cutoff_coverage_gaps_2022(db_session):
    gaps = set(await cutoff_coverage_gaps(db_session, 2022))
    assert gaps == EXPECTED_2022_GAPS, (
        f"Unexpected courses without 2022 cutoffs: {sorted(gaps ^ EXPECTED_2022_GAPS)}"
    )


async def test_cutoff_coverage_gaps_2023(db_session):
    gaps = set(await cutoff_coverage_gaps(db_session, 2023))
    assert gaps == EXPECTED_2023_GAPS, (
        f"Unexpected courses without 2023 cutoffs: {sorted(gaps ^ EXPECTED_2023_GAPS)}"
    )
