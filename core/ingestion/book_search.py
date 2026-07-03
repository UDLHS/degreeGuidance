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

import pdfplumber

from core.ingestion.column_mapper import normalize_label


def build_book_text(pdf_path: str) -> str:
    """Normalized text of every page, forward AND reversed.

    Rotated/mirrored pages (the cutoff tables and 2025-style labels) extract
    back-to-front, so both directions are indexed.
    """
    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
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


def name_present(book_text: str, name_en: str) -> bool:
    phrase = normalize_label(_base_name(name_en))
    # parenthetical acronyms like '(TESL)' may be typeset apart from the name;
    # match on the wordy part
    phrase = re.sub(r"\([^)]*\)", " ", phrase)
    phrase = re.sub(r"\s+", " ", phrase).strip()
    if len(phrase) < 4:
        return False
    return phrase in book_text


def present_courses(
    book_text: str, courses: list[tuple[str, str]]
) -> set[str]:
    """Codes of the [(course_code, name_en), ...] found anywhere in the book."""
    found: set[str] = set()
    for code, name in courses:
        if code_present(book_text, code) or name_present(book_text, name):
            found.add(code)
    return found
