"""
connect_case_outcomes.py
------------------------

Connect preliminary case/disposition outcome variables from CaseData_v2.csv
to the complete-defendants dataset.

Important:
This script does NOT define conviction yet.
Most CaseData outcome fields are coded numeric IDs, so this script only creates
preliminary outcome indicators such as:
- has_case_record
- case_count
- has_disposition
- has_sentence
- has_plea
- has_verdict

Run from project root:
    python src/connect_case_outcomes.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
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

CASE_DATA_PATH = RAW_DATA_DIR / "CaseData_v2.csv"

OUTPUT_PATH = (
    INTERIM_DATA_DIR
    / "travis_county_complete_defendants_with_case_outcomes.csv"
)

MERGE_REPORT_PATH = OUTPUT_DIR / "case_outcome_merge_report.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------

CASE_COLUMNS = [
    "CaseID",
    "CaseChargeID",
    "PersonID",
    "MNI",
    "OriginalBookingNumber",
    "AssociatedBookingNumber",
    "ChargeCode",

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


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def normalize_key(series: pd.Series) -> pd.Series:
    """
    Normalize ID-like columns so merge keys match across files.
    """

    return (
        series
        .astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


def parse_dates(df: pd.DataFrame, date_cols: list[str]) -> pd.DataFrame:
    """
    Parse date columns safely.
    """

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                errors="coerce",
            )

    return df


def first_nonnull(series: pd.Series):
    """
    Return the first non-null value in a series.
    """

    nonnull = series.dropna()

    if nonnull.empty:
        return np.nan

    return nonnull.iloc[0]


def build_case_outcome_summary(case_df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse CaseData_v2 to one row per OriginalBookingNumber.

    This prevents row duplication when merging to complete defendants.
    """

    case_df = case_df.copy()

    case_df["case_join_booking_id"] = normalize_key(
        case_df["OriginalBookingNumber"]
    )

    case_df = case_df[
        case_df["case_join_booking_id"].notna()
    ].copy()

    date_cols = [
        "OriginalDispositionDate",
        "OriginalDispositionPleaDate",
        "OriginalDispositionVerdictDate",
        "LatestDispositionDate",
        "DispositionDate",
    ]

    case_df = parse_dates(
        case_df,
        date_cols,
    )

    # Indicator columns before aggregation.
    case_df["has_disposition"] = (
        case_df["DispositionID"].notna()
        | case_df["OriginalDispositionID"].notna()
        | case_df["LatestDispositionID"].notna()
    )

    case_df["has_sentence"] = (
        case_df["OriginalSentenceID"].notna()
        | case_df["LatestSentenceID"].notna()
    )

    case_df["has_plea"] = (
        case_df["OriginalDispositionPleaID"].notna()
    )

    case_df["has_verdict"] = (
        case_df["OriginalDispositionVerdictID"].notna()
    )

    # Sort so first_nonnull pulls from the latest known disposition row first.
    case_df = case_df.sort_values(
        by=[
            "case_join_booking_id",
            "DispositionDate",
            "OriginalDispositionDate",
            "LatestDispositionDate",
        ],
        ascending=[
            True,
            False,
            False,
            False,
        ],
    )

    grouped = (
        case_df
        .groupby("case_join_booking_id", dropna=False)
        .agg(
            case_count=("CaseID", "count"),
            unique_case_count=("CaseID", pd.Series.nunique),
            unique_case_charge_count=("CaseChargeID", pd.Series.nunique),

            has_case_record=("CaseID", lambda x: True),
            has_disposition=("has_disposition", "max"),
            has_sentence=("has_sentence", "max"),
            has_plea=("has_plea", "max"),
            has_verdict=("has_verdict", "max"),

            first_disposition_date=("DispositionDate", "min"),
            latest_disposition_date=("DispositionDate", "max"),
            first_original_disposition_date=("OriginalDispositionDate", "min"),
            latest_original_disposition_date=("OriginalDispositionDate", "max"),

            disposition_id=("DispositionID", first_nonnull),
            disposition_event_id=("DispositionEventID", first_nonnull),
            disposition_type_id=("DispositionTypeID", first_nonnull),
            disposition_method_id=("DispositionMethodID", first_nonnull),

            original_disposition_id=("OriginalDispositionID", first_nonnull),
            original_disposition_event=("OriginalDispositionEvent", first_nonnull),
            original_disposition_method_id=("OriginalDispositionMethodID", first_nonnull),
            original_disposition_plea_id=("OriginalDispositionPleaID", first_nonnull),
            original_disposition_verdict_id=("OriginalDispositionVerdictID", first_nonnull),
            original_sentence_id=("OriginalSentenceID", first_nonnull),

            latest_disposition_id=("LatestDispositionID", first_nonnull),
            latest_disposition_method_id=("LatestDispositionMethodID", first_nonnull),
            latest_sentence_id=("LatestSentenceID", first_nonnull),

            calendar_days_filing_to_disposition=(
                "CalendarDaysFilingtoDisposition",
                "max",
            ),
            time_to_disposition=(
                "TimetoDisposition",
                "max",
            ),
        )
        .reset_index()
    )

    return grouped


def build_merge_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a simple merge/coverage report.
    """

    total = len(df)

    rows = []

    for col in [
        "has_case_record",
        "has_disposition",
        "has_sentence",
        "has_plea",
        "has_verdict",
    ]:
        if col not in df.columns:
            continue

        count = int(df[col].fillna(False).sum())

        rows.append(
            {
                "metric": col,
                "count": count,
                "rate": round(count / total, 4),
                "total_rows": total,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Main
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

    print("Loading CaseData_v2.csv...")

    case_df = pd.read_csv(
        CASE_DATA_PATH,
        usecols=lambda col: col in CASE_COLUMNS,
        low_memory=False,
    )

    print(
        f"CaseData_v2: {len(case_df):,} rows × "
        f"{len(case_df.columns)} columns"
    )

    print("Building case outcome summary by OriginalBookingNumber...")

    case_summary = build_case_outcome_summary(
        case_df,
    )

    print(
        f"Case outcome summary: {len(case_summary):,} booking-level rows"
    )

    complete_df["case_join_booking_id"] = normalize_key(
        complete_df["defendant_booking_id"]
    )

    merged = complete_df.merge(
        case_summary,
        on="case_join_booking_id",
        how="left",
        validate="many_to_one",
    )

    # Fill missing boolean outcome indicators.
    for col in [
        "has_case_record",
        "has_disposition",
        "has_sentence",
        "has_plea",
        "has_verdict",
    ]:
        merged[col] = merged[col].fillna(False).astype(bool)

    merge_report = build_merge_report(
        merged,
    )

    merged.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    merge_report.to_csv(
        MERGE_REPORT_PATH,
        index=False,
    )

    print(f"\nSaved merged dataset → {OUTPUT_PATH}")
    print(f"Saved merge report → {MERGE_REPORT_PATH}")

    print("\n=== Case Outcome Merge Report ===")
    print(
        merge_report.to_string(index=False)
    )

    return merged, merge_report


if __name__ == "__main__":
    run()