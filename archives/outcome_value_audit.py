"""
outcome_value_audit.py
----------------------

Inspect possible outcome variables in CaseData_v2.csv.

This script does not merge outcomes yet.
It prints value counts and missingness for disposition-related columns
so we can decide which columns can be used as outcomes.

Run from project root:
    python src/outcome_value_audit.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CASE_DATA_PATH = RAW_DATA_DIR / "CaseData_v2.csv"


CANDIDATE_OUTCOME_COLUMNS = [
    "JailCaseTypeID",
    "HighestLevelDispositionCount",
    "OriginalDispositionPleaID",
    "OriginalDispositionPleaDate",
    "OriginalDispositionTrialTypeID",
    "OriginalDispositionVerdictID",
    "OriginalDispositionVerdictDate",
    "OriginalDispositionMethodID",
    "OriginalDispositionID",
    "OriginalDispositionDate",
    "OriginalDispositionEvent",
    "OriginalSentenceID",
    "LatestDispositionMethodID",
    "LatestDispositionID",
    "LatestDispositionDate",
    "LatestSentenceID",
    "DispositionID",
    "DispositionDate",
    "DispositionEventID",
    "DispositionTypeID",
    "DispositionMethodID",
    "CalendarDaysFilingtoDisposition",
    "TimetoDisposition",
]


JOIN_COLUMNS = [
    "OriginalBookingNumber",
    "AssociatedBookingNumber",
    "MNI",
    "PersonID",
    "CaseID",
    "CaseChargeID",
    "ChargeCode",
]


def run():
    print("Loading CaseData_v2.csv...")

    usecols = list(
        set(CANDIDATE_OUTCOME_COLUMNS + JOIN_COLUMNS)
    )

    df = pd.read_csv(
        CASE_DATA_PATH,
        usecols=lambda col: col in usecols,
        low_memory=False,
    )

    print(
        f"Loaded CaseData_v2.csv: {len(df):,} rows × "
        f"{len(df.columns)} columns"
    )

    summary_rows = []

    value_count_tables = []

    for col in CANDIDATE_OUTCOME_COLUMNS:

        if col not in df.columns:
            continue

        non_missing = df[col].notna().sum()
        missing = df[col].isna().sum()
        unique = df[col].nunique(dropna=True)

        summary_rows.append(
            {
                "column": col,
                "non_missing": non_missing,
                "missing": missing,
                "missing_rate": round(missing / len(df), 4),
                "unique_values": unique,
            }
        )

        counts = (
            df[col]
            .value_counts(dropna=False)
            .head(25)
            .reset_index()
        )

        counts.columns = [
            "value",
            "count",
        ]

        counts["column"] = col

        value_count_tables.append(counts)

        print(f"\n=== {col} ===")
        print(
            counts[
                ["column", "value", "count"]
            ].to_string(index=False)
        )

    summary_df = pd.DataFrame(summary_rows)

    value_counts_df = pd.concat(
        value_count_tables,
        ignore_index=True,
    )

    summary_df.to_csv(
        OUTPUT_DIR / "case_outcome_column_summary.csv",
        index=False,
    )

    value_counts_df.to_csv(
        OUTPUT_DIR / "case_outcome_value_counts.csv",
        index=False,
    )

    print("\nSaved case_outcome_column_summary.csv")
    print("Saved case_outcome_value_counts.csv")

    return summary_df, value_counts_df


if __name__ == "__main__":
    run()