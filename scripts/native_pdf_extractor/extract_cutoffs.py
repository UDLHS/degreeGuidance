"""Native PDF cutoff extractor for UGC handbook — v7 (rotation-aware).

Uses pdfplumber to read the rotation transformation matrix of each text char,
which lets us correctly handle the rotated table structure that confuses
plain pdftotext.

WHY ROTATION-AWARE:
The entire cutoff table is rendered ROTATED on each page (landscape table
fitted onto portrait page). District rows and z-score values are rotated too,
not just the column headers. Plain pdftotext output mangles this because it
tries to render rotated text in the same character grid as horizontal text.
This causes character fusion like "Scores001K" and "001UCourses".

By reading the rotation matrix directly, we can:
- Identify rotated text (the entire data table)
- Cluster chars by their X position (each cluster = one district row)
- Reverse the char order to get readable text
- Extract Uni-Codes from the header cluster
- Match values to codes by position (no column-shift bugs)

WORKS ON:
- 2024/25 handbook (has Uni-Codes in header)
- Should work on older handbooks where labels are rotated (label fallback)

REQUIREMENTS:
- pdfplumber (pip install pdfplumber)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber is required. Install with:", file=sys.stderr)
    print("  pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


DISTRICTS_ORDER = [
    "COLOMBO", "GAMPAHA", "KALUTARA",
    "MATALE", "KANDY", "NUWARA ELIYA",
    "GALLE", "MATARA", "HAMBANTOTA",
    "JAFFNA", "KILINOCHCHI", "MANNAR", "MULLAITIVU", "VAVUNIYA",
    "TRINCOMALEE", "BATTICALOA", "AMPARA",
    "PUTTALAM", "KURUNEGALA",
    "ANURADHAPURA", "POLONNARUWA",
    "BADULLA", "MONARAGALA",
    "KEGALLE", "RATNAPURA",
]
DISTRICT_SET = set(DISTRICTS_ORDER)
DISTRICTS_SORTED_BY_LEN = sorted(DISTRICT_SET, key=len, reverse=True)

ZSCORE_RE = re.compile(r'[+-]?\d+\.\d{3,4}|NQC')
UNICODE_RE = re.compile(r'(?<!\d)(\d{3}[A-Z])(?![A-Za-z])')

# Cluster tolerance: chars within X-units of each other belong to the same row
# (since the table is rotated, "row" in the original = constant X in rotated view)
CLUSTER_X_TOLERANCE = 1.0


# ── Cluster rotated chars by X position ─────────────────────────────────────

def get_rotated_chars(page) -> list[dict]:
    return [c for c in page.chars if not c['upright']]


def cluster_by_x(chars: list[dict], tolerance: float = CLUSTER_X_TOLERANCE) -> list[list[dict]]:
    """Group chars where adjacent X positions differ by ≤ tolerance."""
    if not chars:
        return []
    by_x = sorted(chars, key=lambda c: c['matrix'][4])
    clusters = [[by_x[0]]]
    cx = by_x[0]['matrix'][4]
    for c in by_x[1:]:
        x = c['matrix'][4]
        if x - cx <= tolerance:
            clusters[-1].append(c)
        else:
            clusters.append([c])
        cx = x
    return clusters


def cluster_text(cluster: list[dict]) -> str:
    """Get readable text from a cluster (sort by Y ascending, then reverse)."""
    sorted_chars = sorted(cluster, key=lambda c: c['top'])
    return ''.join(c['text'] for c in sorted_chars)[::-1]


# ── Identify rows in the table ──────────────────────────────────────────────

def parse_district_row(text: str) -> Optional[tuple[str, list[str]]]:
    for d in DISTRICTS_SORTED_BY_LEN:
        if text.startswith(d):
            rest = text[len(d):]
            values = ZSCORE_RE.findall(rest)
            if len(values) >= 5:
                return d, values
    return None


def find_header_codes(clusters: list[list[dict]]) -> tuple[list[str], int]:
    """Find the cluster containing the most Uni-Codes.
    
    Returns (codes, cluster_index). Codes preserve column order (left-to-right).
    Duplicates are kept (caller decides how to handle).
    """
    # Prefer clusters where unique-code count is ≥15. Among those, prefer the
    # cluster with the highest unique-code count. Ties broken by total length.
    best_codes: list[str] = []
    best_unique = 0
    best_idx = -1
    for i, cluster in enumerate(clusters):
        text = cluster_text(cluster)
        codes = UNICODE_RE.findall(text)
        unique_count = len(set(codes))
        if unique_count < 15:
            continue
        if (unique_count > best_unique or
                (unique_count == best_unique and len(codes) > len(best_codes))):
            best_codes = codes
            best_unique = unique_count
            best_idx = i
    return best_codes, best_idx


# ── Page-level extraction ───────────────────────────────────────────────────

def is_cutoff_page(page) -> bool:
    """Heuristic: page has many rotated chars (cutoff tables are heavily rotated).
    
    pdfplumber's extract_text() returns reversed text on rotated pages, so we
    check both forward and reversed forms for district/z-score patterns.
    """
    rotated_count = sum(1 for c in page.chars if not c['upright'])
    if rotated_count < 500:
        return False
    text = page.extract_text() or ""
    # Try both forward and reversed
    candidates = [text, text[::-1]]
    for t in candidates:
        upper = t.upper()
        dh = sum(1 for d in DISTRICT_SET if d in upper)
        zc = len(re.findall(r'\b\d\.\d{4}\b|\bNQC\b', t))
        if dh >= 10 and zc >= 50:
            return True
    return False


def extract_page_cutoffs(page, valid_codes: set[str], verbose: bool = False) -> dict:
    """Extract {course_code: {district: z_score}} from a single page."""
    chars = get_rotated_chars(page)
    if len(chars) < 100:
        return {}
    
    clusters = cluster_by_x(chars)
    codes, header_idx = find_header_codes(clusters)
    
    if len(codes) < 15:
        if verbose:
            print(f"    Only {len(codes)} codes found — skipping", file=sys.stderr)
        return {}
    
    # Keep all extracted codes for proper column alignment.
    # Codes not in the seed are still kept — the user can add them later.
    unknown_codes = [c for c in codes if c not in valid_codes]
    if verbose:
        if unknown_codes:
            print(f"    CODES NOT IN SEED ({len(unknown_codes)}): {unknown_codes}")
        if len(codes) != len(set(codes)):
            dups = [c for c in codes if codes.count(c) > 1]
            print(f"    WARNING: duplicate codes in header: {sorted(set(dups))}")
    
    result: dict[str, dict[str, str]] = {}
    rows_found = 0
    for i, cluster in enumerate(clusters):
        if i == header_idx:
            continue
        text = cluster_text(cluster)
        parsed = parse_district_row(text)
        if not parsed:
            continue
        district, values = parsed
        rows_found += 1
        for j, value in enumerate(values):
            if j < len(codes):
                result.setdefault(codes[j], {})[district] = value
    
    if verbose:
        print(f"    {len(codes)} codes × {rows_found} districts = "
              f"{sum(len(d) for d in result.values())} cells")
    return result


# ── Whole-handbook extraction ───────────────────────────────────────────────

def extract_handbook(pdf_path: str, aliases_lookup: dict[str, str],
                     verbose: bool = False) -> tuple[dict, list[int]]:
    valid_codes = set(aliases_lookup.values())
    all_cutoffs: dict[str, dict[str, str]] = {}
    pages_processed: list[int] = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for pn in range(total):
            page = pdf.pages[pn]
            if not is_cutoff_page(page):
                continue
            page_num = pn + 1
            pages_processed.append(page_num)
            if verbose:
                print(f"  Page {page_num}:")
            page_data = extract_page_cutoffs(page, valid_codes, verbose=verbose)
            for code, dv in page_data.items():
                all_cutoffs.setdefault(code, {}).update(dv)
    
    return all_cutoffs, pages_processed


# ── Output ──────────────────────────────────────────────────────────────────

def load_aliases(p: str) -> dict[str, str]:
    out = {}
    with open(p, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            out[r['alias_text']] = r['course_code']
    return out


def load_code_to_alias(p: str) -> dict[str, str]:
    out = {}
    with open(p, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r['course_code'] not in out:
                out[r['course_code']] = r['alias_text']
    return out


def write_wide_csv(cutoffs: dict, output_path: str,
                   header_format: str = 'unicode',
                   headers_map: Optional[dict[str, str]] = None) -> None:
    codes = sorted(cutoffs.keys())
    headers = ([headers_map.get(c, c) for c in codes]
               if (header_format == 'alias' and headers_map) else codes)
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow([''] + headers)
        for d in DISTRICTS_ORDER:
            w.writerow([d] + [cutoffs[c].get(d, '') for c in codes])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('pdf')
    p.add_argument('--output', '-o', default='cutoffs_extracted.csv')
    p.add_argument('--aliases', required=True)
    p.add_argument('--header-format', choices=['unicode', 'alias'], default='unicode')
    p.add_argument('--verbose', '-v', action='store_true')
    args = p.parse_args()
    
    if not Path(args.pdf).exists():
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 1
    
    aliases = load_aliases(args.aliases)
    print(f"Loaded {len(aliases)} aliases.")
    
    print(f"\nExtracting from {args.pdf}...")
    cutoffs, pages = extract_handbook(args.pdf, aliases, args.verbose)
    
    if not cutoffs:
        print("WARNING: no cutoff data extracted.", file=sys.stderr)
        return 3
    
    cells = sum(len(d) for d in cutoffs.values())
    full = sum(1 for d in cutoffs.values() if len(d) == 25)
    print(f"\nCutoff pages: {len(pages)}")
    print(f"Courses extracted: {len(cutoffs)}")
    print(f"With all 25 districts: {full}")
    print(f"Total cells: {cells}")
    
    hmap = load_code_to_alias(args.aliases) if args.header_format == 'alias' else None
    write_wide_csv(cutoffs, args.output, args.header_format, hmap)
    print(f"\nWrote {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
