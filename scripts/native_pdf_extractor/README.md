# Native PDF Cutoff Extractor (v7 — rotation-aware)

Reads UGC handbook cutoff tables using rotation-aware PDF text extraction.

## Two-script workflow

1. **`extract_cutoffs.py`** — extracts cutoff values into a CSV with Uni-Code
   columns (`001A`, `001B`, ...). This is what gets fed to the ingestion job.

2. **`make_readable_csv.py`** — companion script that produces a human-readable
   version of the same data, with column headers like `001A | Medicine (Uni
   of Colombo)`. Use this for manual verification against the source PDF
   before running ingestion.

## Requirements

```bash
pip install pdfplumber
```

## Usage

```bash
# Step 1: Extract cutoffs
python3 extract_cutoffs.py path/to/handbook.pdf \
    --aliases ../data/seeds/course_aliases.csv \
    --output ../data/cutoffs_extracted/zscores_2023.csv \
    --verbose

# Step 2: Build a readable version for manual review
python3 make_readable_csv.py \
    ../data/cutoffs_extracted/zscores_2023.csv \
    ../data/seeds/courses.csv \
    --output ../data/cutoffs_extracted/zscores_2023_readable.csv
```

Open the `_readable.csv` in a spreadsheet to verify a few rows against the
source PDF — each column header tells you exactly what course it is.

## Verified accuracy (2024/25 handbook)

- 10 cutoff pages processed (179-188)
- 261 unique courses extracted
- All 25 districts present
- **6,525 / 6,525 cells match (100.00%)** against PDF source text
- 5 codes flagged as "NOT IN SEED" — these are real codes in the handbook
  that aren't yet in `courses.csv` (add them as needed)

## How it works

The 2024 handbook cutoff tables are rendered with the entire table rotated.
Plain `pdftotext` mangles this because it tries to render rotated text on the
same character grid as horizontal text. Instead, we use **pdfplumber** which
exposes the PDF transformation matrix for each character.

For each cutoff page:
1. Pull all rotated chars (the entire data table is rotated)
2. Cluster chars by X position with tolerance 1.0 (each cluster = one row in
   the original landscape table)
3. Reverse char order in each cluster to get readable text
4. Find the cluster with the most Uni-Codes (`\d{3}[A-Z]` patterns) — that's
   the header row, giving codes in column order
5. Find clusters that start with district names — those are data rows
6. Match values to codes by column position (no column-shift bugs)

## Diagnostics

With `--verbose`, each page reports:
- Number of codes × number of districts × cells extracted
- Any codes NOT in `course_aliases.csv` (flagged for seeding)
- Duplicate codes in the header (rare, usually a column-overlap edge case)
