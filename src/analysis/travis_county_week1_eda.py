"""Week 1 exploration helpers for the Travis County research dataset."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

CORE_FILES = [
    "Booking2010_2012v3.csv",
    "Booking2013_2016v3.csv",
    "CaseData_v2.csv",
    "PreTrial Charge-Interview.csv",
]


@dataclass(frozen=True)
class DatasetRecord:
    """Basic file-level inventory metadata."""

    name: str
    suffix: str
    size_mb: float


def iter_raw_files(data_dir: Path = RAW_DATA_DIR) -> Iterable[Path]:
    """Yield raw dataset files in name order."""

    return sorted(path for path in data_dir.iterdir() if path.is_file())


def build_inventory(data_dir: Path = RAW_DATA_DIR) -> list[DatasetRecord]:
    """Build a simple inventory of raw dataset files."""

    inventory = []
    for path in iter_raw_files(data_dir):
        inventory.append(
            DatasetRecord(
                name=path.name,
                suffix=path.suffix.lower(),
                size_mb=round(path.stat().st_size / (1024 * 1024), 2),
            )
        )
    return inventory


def read_csv_header(path: Path) -> list[str]:
    """Return column names from a CSV file."""

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        return next(reader)


def preview_csv_rows(path: Path, limit: int = 3) -> list[dict[str, str]]:
    """Return the first few rows of a CSV file as dictionaries."""

    rows: list[dict[str, str]] = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            if index >= limit:
                break
            rows.append(row)
    return rows


def print_inventory() -> None:
    """Print a file inventory for the raw data directory."""

    print("Raw Travis County files")
    print("=" * 80)
    for record in build_inventory():
        print(f"- {record.name} | {record.suffix or 'no suffix'} | {record.size_mb} MB")


def print_core_schema_previews() -> None:
    """Print header and sample-row previews for the core CSV files."""

    print("\nCore CSV schema previews")
    print("=" * 80)
    for filename in CORE_FILES:
        path = RAW_DATA_DIR / filename
        if not path.exists():
            print(f"\n{filename}\n  missing from data/raw")
            continue

        header = read_csv_header(path)
        sample_rows = preview_csv_rows(path)
        print(f"\n{filename}")
        print(f"  column_count: {len(header)}")
        print(f"  first_columns: {header[:12]}")
        if sample_rows:
            first_row = sample_rows[0]
            first_items = list(first_row.items())[:8]
            print(f"  first_row_sample: {dict(first_items)}")


def main() -> None:
    """Run the week 1 exploration workflow."""

    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(f"Raw data directory not found: {RAW_DATA_DIR}")

    print_inventory()
    print_core_schema_previews()


if __name__ == "__main__":
    main()