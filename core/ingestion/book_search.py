"""Whole-book presence check — the course_removed coverage safeguard.

A course may only be flagged 'removed' when it is absent from the ENTIRE
book text, not merely from the pages the grid extractor read. This fixes the
false positives where courses printed outside the main cutoff tables
(e.g. 007K/103D/104H/105L/140P live on 2024 pp.150-156, far from the
pp.179-188 grids) were wrongly reported as removed.

Deterministic and conservative by design: presence is checked by printed
code (word-bounded) and by the normalized course name (university stripped).
A same-named course at another university keeps the name present, so this
under-flags rather than over-flags removals — the safe direction for data
students rely on. (Phase 3's LLM pass can sharpen name+university matching.)
"""

from __future__ import annotations

import re

from core.ingestion.column_mapper import normalize_label
from core.ingestion.pdf_pages import iter_pages_chunked


def build_book_text(pdf_path: str) -> str:
    """Normalized text of every page, forward AND reversed.

    Rotated/mirrored pages (the cutoff tables and 2025-style labels) extract
    back-to-front, so both directions are indexed.

    Iterated in chunks (iter_pages_chunked) so pdfminer's per-page memory
    accumulation is released across the ~200-page book instead of stacking
    into an OOM on a memory-constrained worker — see core/ingestion/pdf_pages.
    """
    parts: list[str] = []
    for _pn, page in iter_pages_chunked(pdf_path):
        t = page.extract_text() or ""
        parts.append(t)
        parts.append(t[::-1])
    return normalize_label(" ".join(" ".join(parts).split()))


def _base_name(name_en: str) -> str:
    """Course name without the trailing university parenthetical.

    'Teaching English as a Second Language (TESL) (Sabaragamuwa University …)'
    -> 'Teaching English as a Second Language (TESL)'.
    """
    s = name_en.strip()
    if s.endswith(")") and "(" in s:
        # drop only the LAST balanced parenthetical group
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    return s[:i].strip()
    return s


def code_present(book_text: str, code: str) -> bool:
    return re.search(rf"(?<![A-Z0-9]){re.escape(code.upper())}(?![A-Z0-9])", book_text) is not None


def strip_parentheticals(text: str) -> str:
    """Remove (…) groups and collapse whitespace — used on BOTH sides of the
    name check so stripping stays symmetric."""
    return re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", " ", text)).strip()


def name_present(
    book_text: str, name_en: str, book_text_noparens: str | None = None
) -> bool:
    """True when the course's base name appears in the book text.

    Parenthetical acronyms like '(TESL)' or '(TV)' are stripped from OUR
    phrase — so the comparison must also run against a paren-stripped copy of
    the book text, or 'Management Studies (TV) - B' can never match: the
    stripped phrase 'MANAGEMENT STUDIES - B' is not a substring of the printed
    'MANAGEMENT STUDIES (TV) - B'. That asymmetry falsely flagged 040R/040W
    as removed (and an admin, told they were absent, approved it)."""
    phrase = strip_parentheticals(normalize_label(_base_name(name_en)))
    if len(phrase) < 4:
        return False
    if phrase in book_text:
        return True
    if book_text_noparens is None:
        book_text_noparens = strip_parentheticals(book_text)
    return phrase in book_text_noparens


def present_courses(
    book_text: str, courses: list[tuple[str, str]]
) -> set[str]:
    """Codes of the [(course_code, name_en), ...] found anywhere in the book."""
    noparens = strip_parentheticals(book_text)
    found: set[str] = set()
    for code, name in courses:
        if code_present(book_text, code) or name_present(book_text, name, noparens):
            found.add(code)
    return found
