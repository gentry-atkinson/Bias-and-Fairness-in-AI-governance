"""
data_loading.py
---------------
Raw file discovery and low-level loading helpers for the Travis County
criminal justice dataset.

Run from the project root:
    python src/data_loading.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

CORE_CSV_FILES = [
    "Booking2010_2012v3.csv",
    "Booking2013_2016v3.csv",
    "CaseData_v2.csv",
    "PreTrial Charge-Interview.csv",
]

PRIORITY_WORKBOOKS = [
    "PersonData.xlsx",
    "PreTrial to Booking Info.xlsx",
    "CaseIDtoBookingChargeIDUPDATED.xlsx",
]

DATASET_SPECS: list[dict] = [
    {"dataset": "booking_2010_2012", "path": RAW_DATA_DIR / "Booking2010_2012v3.csv", "kind": "csv"},
    {"dataset": "booking_2013_2016", "path": RAW_DATA_DIR / "Booking2013_2016v3.csv", "kind": "csv"},
    {"dataset": "case_data", "path": RAW_DATA_DIR / "CaseData_v2.csv", "kind": "csv"},
    {"dataset": "pretrial_charge_interview", "path": RAW_DATA_DIR / "PreTrial Charge-Interview.csv", "kind": "csv"},
    {"dataset": "person_data", "path": RAW_DATA_DIR / "PersonData.xlsx", "kind": "excel", "sheet": "PersonData"},
    {"dataset": "pretrial_defendants", "path": RAW_DATA_DIR / "PreTrial Defendants.xlsx", "kind": "excel", "sheet": "Sheet1"},
    {"dataset": "pretrial_booking_bridge", "path": RAW_DATA_DIR / "PreTrial to Booking Info.xlsx", "kind": "excel", "sheet": "Booking"},
    {"dataset": "events", "path": RAW_DATA_DIR / "Events.xlsx", "kind": "excel", "sheet": "Events"},
    {"dataset": "mental_health_events", "path": RAW_DATA_DIR / "Mental Health Flag Events.xlsx", "kind": "excel", "sheet": "Sheet1"},
    {"dataset": "revocation", "path": RAW_DATA_DIR / "revocationV2.xlsx", "kind": "excel", "sheet": "revocation"},
    {"dataset": "sentencing_pre2013", "path": RAW_DATA_DIR / "SentencingDataPre2013.xlsx", "kind": "excel", "sheet": "SentencingDataPre2013"},
    {"dataset": "sentencing_post2013", "path": RAW_DATA_DIR / "SentencingDataPost2013.xlsx", "kind": "excel", "sheet": "SentencingDataPost2013"},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_file_inventory(data_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Return a DataFrame listing every file in data_dir with size info."""
    records = [
        {
            "file": p.name,
            "suffix": p.suffix.lower(),
            "size_mb": round(p.stat().st_size / (1024 * 1024), 2),
        }
        for p in sorted(data_dir.iterdir())
        if p.is_file()
    ]
    return pd.DataFrame(records).sort_values(["suffix", "file"]).reset_index(drop=True)


def read_csv_header(path: Path) -> list[str]:
    """Return the header row of a CSV file."""
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return next(csv.reader(fh))


def preview_csv_rows(path: Path, limit: int = 3) -> list[dict]:
    """Return the first *limit* rows of a CSV as a list of dicts."""
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)
    return rows


def schema_preview(files: list[str] = CORE_CSV_FILES) -> pd.DataFrame:
    """Return a DataFrame showing column counts and first columns for each CSV."""
    rows = []
    for name in files:
        header = read_csv_header(RAW_DATA_DIR / name)
        rows.append({
            "file": name,
            "column_count": len(header),
            "first_columns": ", ".join(header[:12]),
        })
    return pd.DataFrame(rows)


def inspect_workbook(file_name: str) -> pd.DataFrame:
    """Return a sheet-level summary of an Excel workbook."""
    path = RAW_DATA_DIR / file_name
    xf = pd.ExcelFile(path)
    rows = []
    for sheet in xf.sheet_names:
        preview = pd.read_excel(path, sheet_name=sheet, nrows=0)
        rows.append({
            "workbook": file_name,
            "sheet_name": sheet,
            "column_count": len(preview.columns),
            "first_columns": ", ".join(preview.columns.astype(str)[:10]),
        })
    return pd.DataFrame(rows)


def load_dataset(spec: dict) -> pd.DataFrame:
    """Load one dataset from DATASET_SPECS."""
    if spec["kind"] == "csv":
        return pd.read_csv(spec["path"], low_memory=False)
    return pd.read_excel(spec["path"], sheet_name=spec["sheet"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Raw data dir : {RAW_DATA_DIR}")
    print()

    inventory = build_file_inventory()
    print(f"Raw files ({len(inventory)}):")
    print(inventory.to_string(index=False))
    print()

    print("CSV schema preview:")
    print(schema_preview().to_string(index=False))
    print()

    print("Workbook sheet summary:")
    for wb in PRIORITY_WORKBOOKS:
        wb_path = RAW_DATA_DIR / wb
        if wb_path.exists():
            print(inspect_workbook(wb).to_string(index=False))
