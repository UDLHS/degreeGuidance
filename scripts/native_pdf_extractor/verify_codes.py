"""Cross-check extracted Uni-Codes against the course NAMES printed in the handbook.

WHY THIS EXISTS
The cutoff extractor reads Uni-Codes from the rotated code-header of each Section-9
page via OCR-like clustering, which can misread a code (e.g. 007K -> 006K) or drop
one. A misread silently attaches a column of cutoffs to the WRONG course — invisible
to row/value checks. But the COURSE NAMES on each page are *upright, exact text* in
the PDF, so we can verify every column: does the extracted code's catalog name match
the course name printed above its column?

This is the validation gate for every yearly re-ingest. Run it after extraction and
BEFORE trusting/loading the cutoffs:

    python -m scripts.native_pdf_extractor.verify_codes \
        --pdf data/raw_handbooks/handbook_2024.pdf \
        --courses data/seeds/courses.csv

It prints any extracted code whose course name is NOT found among that page's printed
headers — each of those must be reviewed (genuine misread vs. a wording/abbreviation
variant) before the data is trusted. Exit code is non-zero if anything is flagged.
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import sys

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber is required (pip install pdfplumber).", file=sys.stderr)
    sys.exit(1)

from scripts.native_pdf_extractor.extract_cutoffs import (
    cluster_by_x,
    find_header_codes,
    get_rotated_chars,
    is_cutoff_page,
)

# Words dropped before comparison (noise) and known catalog/handbook abbreviations.
_STOP = {"OF", "THE", "AND", "SRI", "LANKA", "UNIVERSITY", "A", "B"}
_ABBR = {"BIO": "BIOLOGICAL", "SC": "SCIENCE", "PHY": "PHYSICAL", "TECH": "TECHNOLOGY"}


def _words(s: str) -> set[str]:
    out = set()
    for w in re.findall(r"[A-Z0-9]+", s.upper()):
        if w in _STOP:
            continue
        out.add(_ABBR.get(w, w))
    return out


def load_catalog(courses_csv: str) -> dict[str, set[str]]:
    """course_code -> significant word-set of its name_en."""
    catalog: dict[str, set[str]] = {}
    with open(courses_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            catalog[row["course_code"]] = _words(row["name_en"])
    return catalog


def page_header_word_sets(page) -> list[set[str]]:
    """Reconstruct each column header (upright, right-to-left text) as a word-set."""
    up = [c for c in page.chars if c["upright"]]
    lines: dict[int, list] = collections.defaultdict(list)
    for c in up:
        lines[round(c["top"])].append(c)
    items = []
    for top in sorted(lines):
        cs = sorted(lines[top], key=lambda c: c["x0"], reverse=True)
        items.append((top, "".join(c["text"] for c in cs).strip()))
    blocks, cur, last = [], [], None
    for top, text in items:
        if last is not None and top - last > 12 and cur:
            blocks.append(" ".join(cur))
            cur = []
        cur.append(text)
        last = top
    if cur:
        blocks.append(" ".join(cur))
    return [_words(b) for b in blocks if "UNIVERSITY" in b.upper() or "CAMPUS" in b.upper()]


def verify(pdf_path: str, catalog: dict[str, set[str]]) -> list[tuple[int, str, str]]:
    """Return [(page_number, code, reason)] for codes not supported by a printed name."""
    flagged: list[tuple[int, str, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pn in range(len(pdf.pages)):
            page = pdf.pages[pn]
            if not is_cutoff_page(page):
                continue
            codes, _ = find_header_codes(cluster_by_x(get_rotated_chars(page)))
            headers = page_header_word_sets(page)
            for code in codes:
                cw = catalog.get(code)
                if cw is None:
                    flagged.append((pn + 1, code, "code not in catalog (likely misread/new)"))
                elif not any(cw <= h for h in headers):
                    flagged.append((pn + 1, code, "catalog name not found among page headers"))
    return flagged


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify handbook Uni-Codes against printed course names")
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--courses", default="data/seeds/courses.csv", help="course_code,name_en catalog CSV")
    args = ap.parse_args()

    catalog = load_catalog(args.courses)
    flagged = verify(args.pdf, catalog)
    if not flagged:
        print("OK: every extracted code matches a printed course name.")
        return 0
    print(f"REVIEW NEEDED — {len(flagged)} code(s) not auto-matched to a printed name:")
    for pn, code, reason in flagged:
        print(f"  page {pn}: {code} — {reason}")
    print("\nEach must be checked: genuine misread (fix it) vs. wording/abbreviation variant (ok).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
