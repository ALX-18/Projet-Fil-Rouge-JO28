"""Quick audit helper for colleague snapshot assets."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN_DATA = ROOT / "data" / "raw" / "olympics_dataset.csv"
COL_DATA = ROOT / "Projet-Fil-Rouge-JO28-main" / "olympics_dataset.csv"
COL_TABLES = ROOT / "reports" / "colleague_snapshot" / "outputs" / "tables"


def dataset_summary(path: Path) -> tuple[int, int, str | None, str | None]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = 0
        year_min = None
        year_max = None
        year_idx = header.index("Year") if "Year" in header else None
        for row in reader:
            rows += 1
            if year_idx is not None and year_idx < len(row):
                try:
                    y = int(float(row[year_idx]))
                except Exception:
                    continue
                year_min = y if year_min is None else min(year_min, y)
                year_max = y if year_max is None else max(year_max, y)
    return rows, len(header), str(year_min), str(year_max)


def main() -> None:
    m_rows, m_cols, m_min, m_max = dataset_summary(MAIN_DATA)
    c_rows, c_cols, c_min, c_max = dataset_summary(COL_DATA)

    print("Main dataset:", m_rows, "rows", m_cols, "cols", f"years {m_min}-{m_max}")
    print("Colleague dataset:", c_rows, "rows", c_cols, "cols", f"years {c_min}-{c_max}")

    if COL_TABLES.exists():
        tables = sorted(p.name for p in COL_TABLES.glob("*.csv"))
        print(f"Colleague tables imported: {len(tables)}")
        for name in tables:
            print(" -", name)
    else:
        print("No colleague tables found at", COL_TABLES)


if __name__ == "__main__":
    main()