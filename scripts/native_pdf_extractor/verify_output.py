"""Sanity check on extracted CSV."""
import csv, sys
from pathlib import Path

def verify(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        print(f"ERROR: {csv_path} not found", file=sys.stderr)
        return 1
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        print("ERROR: CSV too short", file=sys.stderr)
        return 2

    headers = rows[0]
    data_rows = rows[1:]
    n_courses = len(headers) - 1
    n_districts = len(data_rows)
    print(f"Districts: {n_districts}")
    print(f"Courses:   {n_courses}")

    nqc = num = empty = 0
    for row in data_rows:
        for cell in row[1:]:
            c = cell.strip()
            if not c: empty += 1
            elif c == 'NQC': nqc += 1
            else: num += 1
    print(f"\nNumeric: {num}")
    print(f"NQC:     {nqc}")
    print(f"Empty:   {empty}")
    print(f"\nFirst column: {headers[1]}, Last column: {headers[-1]}")
    print(f"\n{data_rows[0][0]} first 5 values:")
    for h, v in zip(headers[1:6], data_rows[0][1:6]):
        print(f"  {h}: {v}")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify_output.py <extracted_csv>", file=sys.stderr)
        sys.exit(1)
    sys.exit(verify(sys.argv[1]))
