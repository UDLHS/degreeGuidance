"""Deterministic column -> course mapping suggestions (Gate 2 input).

For every extracted grid column, propose which catalog course it is:

1. code   — the printed Uni-Code exists in the catalog (confidence 1.0).
2. alias  — the printed label (or code) matches course_aliases.alias_text
            exactly (confidence 1.0). Confirmed mappings are written back as
            aliases, so each year's corrections make the next year automatic.
3. name   — normalized-text similarity between the printed label and
            courses.name_en (which includes the university). Deterministic
            (difflib + token overlap), never an LLM. Confidence = blended
            score; below _MIN_CONFIDENCE no suggestion is made.

The admin confirms every mapping at Gate 2 — suggestions only pre-fill.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ingestion.grid_extractor import GridColumn
from core.models import Course, CourseAlias

_MIN_CONFIDENCE = 0.55

_WORD_RE = re.compile(r"[A-Z0-9]+")
# printed flags + bracketed stream qualifiers are not part of the course name
_MARKS_RE = re.compile(r"[#*]")


def normalize_label(text: str) -> str:
    s = _MARKS_RE.sub(" ", text.upper())
    s = s.replace("&", " AND ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(normalize_label(text)))


def _similarity(a_norm: str, a_tok: set[str], b_norm: str, b_tok: set[str]) -> float:
    if not a_tok or not b_tok:
        return 0.0
    jaccard = len(a_tok & b_tok) / len(a_tok | b_tok)
    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    return 0.5 * jaccard + 0.5 * ratio


@dataclass
class MappingSuggestion:
    column_key: str
    raw_label: str | None
    suggested_course_code: str | None
    confidence: float | None
    source: str | None  # 'code' | 'alias' | 'name' | None


async def suggest_mappings(
    db: AsyncSession, columns: list[GridColumn]
) -> list[MappingSuggestion]:
    course_rows = (
        await db.execute(select(Course.course_code, Course.name_en))
    ).all()
    catalog = {code: name for code, name in course_rows}
    prepared = [
        (code, normalize_label(name), _tokens(name)) for code, name in course_rows
    ]

    alias_rows = (
        await db.execute(select(CourseAlias.alias_text, CourseAlias.course_code))
    ).all()
    aliases = {text: code for text, code in alias_rows}

    out: list[MappingSuggestion] = []
    for col in columns:
        label = col.raw_label or ""

        # 1) printed code, if it exists in the catalog
        if col.code and col.code in catalog:
            out.append(MappingSuggestion(col.column_key, label, col.code, 1.0, "code"))
            continue

        # 2) exact alias on the label or the (possibly misprinted) code
        alias_hit = aliases.get(label.strip()) or (
            aliases.get(col.code) if col.code else None
        )
        if alias_hit and alias_hit in catalog:
            out.append(MappingSuggestion(col.column_key, label, alias_hit, 1.0, "alias"))
            continue

        # 3) deterministic name similarity
        if label:
            l_norm, l_tok = normalize_label(label), _tokens(label)
            best_code, best_score = None, 0.0
            for code, c_norm, c_tok in prepared:
                s = _similarity(l_norm, l_tok, c_norm, c_tok)
                if s > best_score:
                    best_code, best_score = code, s
            if best_code is not None and best_score >= _MIN_CONFIDENCE:
                out.append(MappingSuggestion(
                    col.column_key, label, best_code, round(best_score, 3), "name"
                ))
                continue

        out.append(MappingSuggestion(col.column_key, label or None, None, None, None))
    return out
