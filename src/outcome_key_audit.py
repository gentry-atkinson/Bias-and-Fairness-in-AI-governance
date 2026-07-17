"""
outcome_key_audit.py
--------------------

Audit possible outcome variables and join keys for the Travis County
risk assessment project.

This script does NOT merge outcomes yet.

It checks:
1. Which raw files contain possible outcome columns
2. Which join keys overlap with complete_defendants
3. Which files are good candidates for outcome integration

Run from project root:
    python src/outcome_key_audit.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

COMPLETE_DEFENDANTS_PATH = (
    INTERIM_DATA_DIR / "travis_county_complete_defendants_df.csv"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Files to audit
# ---------------------------------------------------------------------

RAW_FILES = {
    "CaseData_v2.csv": "csv",
    "PreTrial to Booking Info.xlsx": "excel",
    "PreTrial Disposition Reason.xlsx": "excel",
    "Events.xlsx": "excel",
    "SentencingDataPre2013.xlsx": "excel",
    "SentencingDataPost2013.xlsx": "excel",
    "revocationV2.xlsx": "excel",
}


OUTCOME_KEYWORDS = [
    "bond",
    "release",
    "detention",
    "jail",
    "custody",
    "conviction",
    "convicted",
    "disposition",
    "sentence",
    "sentencing",
    "revocation",
    "violent",
    "crime",
    "fta",
    "failure",
    "warrant",
    "dismiss",
    "guilty",
    "plea",
]


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def normalize_key(series: pd.Series) -> pd.Series:
    """
    Convert ID columns to comparable string keys.
    """

    return (
        series
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


def get_complete_key_sets(df: pd.DataFrame) -> dict[str, set[str]]:
    """
    Extract key sets from complete_defendants.
    """

    key_sets = {}

    possible_keys = [
        "pretrial_id",
        "defendant_booking_id",
        "person_mni",
        "PK_BKG_NO",
    ]

    for col in possible_keys:
        if col in df.columns:
            key_sets[col] = set(normalize_key(df[col]))

    return key_sets


def read_columns_csv(file_name: str) -> list[str]:
    """
    Read CSV column names.
    """

    path = RAW_DATA_DIR / file_name
    return pd.read_csv(path, nrows=5, low_memory=False).columns.tolist()


def read_columns_excel(file_name: str) -> dict[str, list[str]]:
    """
    Read Excel sheet names and column names.
    """

    path = RAW_DATA_DIR / file_name
    workbook = pd.ExcelFile(path)

    sheet_columns = {}

    for sheet in workbook.sheet_names:
        sample = pd.read_excel(path, sheet_name=sheet, nrows=5)
        sheet_columns[sheet] = sample.columns.tolist()

    return sheet_columns


def find_candidate_outcome_columns(columns: list[str]) -> list[str]:
    """
    Find columns whose names suggest possible outcome variables.
    """

    candidates = []

    for col in columns:
        lower_col = str(col).lower()

        if any(keyword in lower_col for keyword in OUTCOME_KEYWORDS):
            candidates.append(col)

    return candidates


def compute_overlap(
    complete_keys: dict[str, set[str]],
    raw_values: pd.Series,
) -> list[dict]:
    """
    Compare one raw key column to all complete-defendant key columns.
    """

    raw_set = set(normalize_key(raw_values))

    rows = []

    for complete_key_name, complete_set in complete_keys.items():
        shared = complete_set & raw_set

        rows.append(
            {
                "complete_key": complete_key_name,
                "complete_unique": len(complete_set),
                "raw_unique": len(raw_set),
                "shared_unique": len(shared),
                "complete_overlap_pct": (
                    round(len(shared) / len(complete_set) * 100, 2)
                    if complete_set else 0
                ),
                "raw_overlap_pct": (
                    round(len(shared) / len(raw_set) * 100, 2)
                    if raw_set else 0
                ),
            }
        )

    return rows


# ---------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------

def run():
    print("Loading complete defendants...")

    complete_df = pd.read_csv(
        COMPLETE_DEFENDANTS_PATH,
        low_memory=False,
    )

    print(
        f"Complete defendants: {len(complete_df):,} rows × "
        f"{len(complete_df.columns)} columns"
    )

    complete_keys = get_complete_key_sets(complete_df)

    column_inventory_rows = []
    candidate_outcome_rows = []
    overlap_rows = []

    for file_name, file_type in RAW_FILES.items():

        print(f"\nAuditing {file_name}...")

        path = RAW_DATA_DIR / file_name

        if not path.exists():
            print(f"  Missing file: {path}")
            continue

        if file_type == "csv":

            columns = read_columns_csv(file_name)

            column_inventory_rows.append(
                {
                    "file": file_name,
                    "sheet": None,
                    "n_columns": len(columns),
                    "columns": columns,
                }
            )

            candidate_cols = find_candidate_outcome_columns(columns)

            for col in candidate_cols:
                candidate_outcome_rows.append(
                    {
                        "file": file_name,
                        "sheet": None,
                        "candidate_outcome_column": col,
                    }
                )

            # Check overlap for all columns that look like IDs.
            id_like_cols = [
                col for col in columns
                if any(
                    key in str(col).lower()
                    for key in ["id", "mni", "booking", "case"]
                )
            ]

            for key_col in id_like_cols:
                try:
                    raw_key_df = pd.read_csv(
                        path,
                        usecols=[key_col],
                        low_memory=False,
                    )

                    overlaps = compute_overlap(
                        complete_keys,
                        raw_key_df[key_col],
                    )

                    for row in overlaps:
                        row.update(
                            {
                                "raw_file": file_name,
                                "raw_sheet": None,
                                "raw_key": key_col,
                            }
                        )

                        overlap_rows.append(row)

                except Exception as exc:
                    print(f"  Could not test key {key_col}: {exc}")

        elif file_type == "excel":

            workbook = pd.ExcelFile(path)

            for sheet in workbook.sheet_names:

                sample = pd.read_excel(
                    path,
                    sheet_name=sheet,
                    nrows=5,
                )

                columns = sample.columns.tolist()

                column_inventory_rows.append(
                    {
                        "file": file_name,
                        "sheet": sheet,
                        "n_columns": len(columns),
                        "columns": columns,
                    }
                )

                candidate_cols = find_candidate_outcome_columns(columns)

                for col in candidate_cols:
                    candidate_outcome_rows.append(
                        {
                            "file": file_name,
                            "sheet": sheet,
                            "candidate_outcome_column": col,
                        }
                    )

                id_like_cols = [
                    col for col in columns
                    if any(
                        key in str(col).lower()
                        for key in ["id", "mni", "booking", "bkg", "case", "mast"]
                    )
                ]

                for key_col in id_like_cols:
                    try:
                        raw_key_df = pd.read_excel(
                            path,
                            sheet_name=sheet,
                            usecols=[key_col],
                        )

                        overlaps = compute_overlap(
                            complete_keys,
                            raw_key_df[key_col],
                        )

                        for row in overlaps:
                            row.update(
                                {
                                    "raw_file": file_name,
                                    "raw_sheet": sheet,
                                    "raw_key": key_col,
                                }
                            )

                            overlap_rows.append(row)

                    except Exception as exc:
                        print(f"  Could not test key {key_col}: {exc}")

    column_inventory_df = pd.DataFrame(column_inventory_rows)
    candidate_outcome_df = pd.DataFrame(candidate_outcome_rows)
    overlap_df = pd.DataFrame(overlap_rows)

    column_inventory_df.to_csv(
        OUTPUT_DIR / "outcome_file_column_inventory.csv",
        index=False,
    )

    candidate_outcome_df.to_csv(
        OUTPUT_DIR / "candidate_outcome_columns.csv",
        index=False,
    )

    overlap_df.to_csv(
        OUTPUT_DIR / "outcome_key_overlap.csv",
        index=False,
    )

    print("\nSaved outcome_file_column_inventory.csv")
    print("Saved candidate_outcome_columns.csv")
    print("Saved outcome_key_overlap.csv")

    print("\n=== Candidate Outcome Columns ===")
    print(candidate_outcome_df.to_string(index=False))

    print("\n=== Top Key Overlaps ===")
    if not overlap_df.empty:
        print(
            overlap_df.sort_values(
                "shared_unique",
                ascending=False,
            )
            .head(25)
            .to_string(index=False)
        )

    return (
        column_inventory_df,
        candidate_outcome_df,
        overlap_df,
    )


if __name__ == "__main__":
    run()