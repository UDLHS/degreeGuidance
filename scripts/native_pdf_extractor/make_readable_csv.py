"""Create a human-readable copy of the extracted cutoffs CSV.

Adds the full course name next to each course code in the column headers,
making it easy to manually verify cutoffs against the source PDF.

Column headers become: "001A | Medicine (University of Colombo)"

Codes that aren't in courses.csv get flagged with "(NOT IN SEED)" — review
these and decide whether to add them to courses.csv.

Usage:
    python3 make_readable_csv.py <extracted_csv> <courses_csv> --output <readable_csv>

Example:
    python3 make_readable_csv.py \\
        data/cutoffs_extracted/zscores_2023.csv \\
        data/seeds/courses.csv \\
        --output data/cutoffs_extracted/zscores_2023_readable.csv
"""
import argparse, csv, sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('extracted_csv', help='CSV with Uni-Code columns from extract_cutoffs.py')
    p.add_argument('courses_csv', help='courses.csv with course_code → name_en mapping')
    p.add_argument('--output', '-o', required=True, help='Output CSV path')
    args = p.parse_args()

    if not Path(args.extracted_csv).exists():
        print(f"ERROR: {args.extracted_csv} not found", file=sys.stderr)
        return 1
    if not Path(args.courses_csv).exists():
        print(f"ERROR: {args.courses_csv} not found", file=sys.stderr)
        return 2

    code_to_name = {}
    with open(args.courses_csv, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            code_to_name[r['course_code']] = r['name_en']

    with open(args.extracted_csv, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))

    if len(rows) < 2:
        print("ERROR: extracted CSV too short", file=sys.stderr)
        return 3

    header = rows[0]
    new_header = ['DISTRICT']
    unknown = []
    for code in header[1:]:
        name = code_to_name.get(code)
        if name:
            new_header.append(f"{code} | {name}")
        else:
            new_header.append(f"{code} | (NOT IN SEED)")
            unknown.append(code)

    with open(args.output, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(new_header)
        for row in rows[1:]:
            w.writerow(row)

    print(f"Wrote {args.output}")
    print(f"  Districts: {len(rows) - 1}")
    print(f"  Courses:   {len(header) - 1}")
    if unknown:
        print(f"\nWARNING: {len(unknown)} codes are NOT in courses.csv (add them later):")
        for c in unknown:
            print(f"  {c}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
