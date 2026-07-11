"""Memory-bounded chunked page iteration (core/ingestion/pdf_pages).

The extraction pipeline's whole-book sweeps read the PDF in chunks, closing
and reopening the handle between them, to stop pdfminer's per-page memory
accumulation from OOM-killing a memory-constrained worker. These tests pin
the correctness contract that refactor rests on: chunked iteration must visit
every page exactly once, in order, yielding the same text a single open would.
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber
import pytest

from core.ingestion.pdf_pages import PAGE_CHUNK, count_pages, iter_pages_chunked, reclaim

HANDBOOK = Path(__file__).resolve().parents[2] / "data" / "raw_handbooks" / "handbook_2024.pdf"

pytestmark = pytest.mark.skipif(not HANDBOOK.exists(), reason="2024 handbook PDF not present")


def test_count_pages_matches_single_open():
    with pdfplumber.open(str(HANDBOOK)) as pdf:
        expected = len(pdf.pages)
    assert count_pages(str(HANDBOOK)) == expected
    assert expected > PAGE_CHUNK  # book is big enough to actually exercise chunking


def test_iter_visits_every_page_once_in_order():
    seen = [pn for pn, _page in iter_pages_chunked(str(HANDBOOK))]
    assert seen == list(range(1, count_pages(str(HANDBOOK)) + 1))


def test_chunked_text_matches_single_open():
    """The whole point: chunked reads must not change what we extract."""
    with pdfplumber.open(str(HANDBOOK)) as pdf:
        baseline = [(i + 1, (p.extract_text() or "")) for i, p in enumerate(pdf.pages)]
    chunked = [(pn, (page.extract_text() or "")) for pn, page in iter_pages_chunked(str(HANDBOOK))]
    assert chunked == baseline


def test_small_chunk_size_still_complete():
    """A chunk size below the page count forces many reopens — still whole."""
    seen = [pn for pn, _page in iter_pages_chunked(str(HANDBOOK), chunk_size=7)]
    assert seen == list(range(1, count_pages(str(HANDBOOK)) + 1))


def test_reclaim_is_safe_to_call():
    reclaim()  # must never raise, on glibc or otherwise
