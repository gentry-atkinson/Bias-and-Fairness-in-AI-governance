"""
outcome_fairness_analysis.py
----------------------------

Preliminary outcome/disposition fairness analysis.

This script analyzes preliminary case/disposition outcome indicators
after connecting CaseData_v2.csv to the complete-defendants dataset.

Important:
These are NOT final conviction or recidivism labels.
The indicators only show whether case/disposition/sentence/plea/verdict
records exist for each defendant.

Run from project root:
    python src/outcome_fairness_analysis.py

Outputs:
- outputs/outcome_fairness_summary.csv
- outputs/outcome_disparity_table.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_with_case_outcomes.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROTECTED_ATTRIBUTES = {
    "race": "race",
    "gender": "sex",
    "age": "age_group",
}

OUTCOME_COLUMNS = [
    "has_case_record",
    "has_disposition",
    "has_sentence",
    "has_plea",
    "has_verdict",
]

REFERENCE_GROUPS = {
    "race": "W",
    "sex": "F",
    "age_group": "18-25",
}


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def create_age_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create age buckets if age_group is missing.
    """

    if "age_group" not in df.columns:
        df["age_group"] = pd.cut(
            df["age_at_booking"],
            bins=[0, 25, 35, 50, 120],
            labels=[
                "18-25",
                "26-35",
                "36-50",
                "50+",
            ],
        )

    return df


def ensure_boolean_columns(
    df: pd.DataFrame,
    outcome_cols: list[str],
) -> pd.DataFrame:
    """
    Convert outcome indicator columns to boolean values.
    """

    for col in outcome_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna(False)
                .astype(bool)
            )

    return df


def summarize_outcome_rates(
    df: pd.DataFrame,
    group_col: str,
    outcome_cols: list[str],
) -> pd.DataFrame:
    """
    Compute outcome rates by protected group.

    Each outcome rate is P(outcome=True | group).
    """

    rows = []

    for outcome_col in outcome_cols:

        if outcome_col not in df.columns:
            continue

        summary = (
            df.groupby(group_col)[outcome_col]
            .agg(
                count="count",
                outcome_count="sum",
                outcome_rate="mean",
            )
            .reset_index()
        )

        summary["outcome"] = outcome_col

        summary["outcome_rate"] = (
            summary["outcome_rate"]
            .round(4)
        )

        rows.append(summary)

    if not rows:
        return pd.DataFrame()

    return pd.concat(
        rows,
        ignore_index=True,
    )


def build_outcome_disparity_table(
    outcome_summary: pd.DataFrame,
    group_col: str,
) -> pd.DataFrame:
    """
    Compare each group's outcome rate to a reference group.
    """

    if outcome_summary.empty:
        return outcome_summary

    reference_group = REFERENCE_GROUPS.get(group_col)

    rows = []

    for outcome_name, subset in outcome_summary.groupby("outcome"):

        subset = subset.copy()

        reference_row = subset[
            subset[group_col] == reference_group
        ]

        if reference_row.empty:
            subset["reference_group"] = reference_group
            subset["rate_difference_from_reference"] = np.nan
            subset["rate_ratio_to_reference"] = np.nan
            rows.append(subset)
            continue

        reference_rate = reference_row["outcome_rate"].iloc[0]

        subset["reference_group"] = reference_group

        subset["rate_difference_from_reference"] = (
            subset["outcome_rate"] - reference_rate
        ).round(4)

        if reference_rate == 0:
            subset["rate_ratio_to_reference"] = np.nan
        else:
            subset["rate_ratio_to_reference"] = (
                subset["outcome_rate"] / reference_rate
            ).round(3)

        rows.append(subset)

    return pd.concat(
        rows,
        ignore_index=True,
    )


# ---------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------

def run():
    print(f"Loading {DATA_PATH}")

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False,
    )

    print(
        f"Loaded {len(df):,} rows × "
        f"{len(df.columns)} columns"
    )

    df = create_age_groups(df)

    df = ensure_boolean_columns(
        df,
        OUTCOME_COLUMNS,
    )

    available_outcomes = [
        col for col in OUTCOME_COLUMNS
        if col in df.columns
    ]

    print("\nOutcome indicators analyzed:")
    print(available_outcomes)

    summary_tables = []
    disparity_tables = []

    for label, group_col in PROTECTED_ATTRIBUTES.items():

        if group_col not in df.columns:
            print(
                f"Skipping {label}: "
                f"column {group_col} not found"
            )
            continue

        print(f"\n=== {label.upper()} ({group_col}) ===")

        outcome_summary = summarize_outcome_rates(
            df,
            group_col,
            available_outcomes,
        )

        outcome_disparity = build_outcome_disparity_table(
            outcome_summary,
            group_col,
        )

        outcome_summary["protected_attribute"] = label
        outcome_disparity["protected_attribute"] = label

        summary_tables.append(outcome_summary)
        disparity_tables.append(outcome_disparity)

        print("\nOutcome Rates")
        print(
            outcome_summary.to_string(index=False)
        )

        print("\nOutcome Disparities")
        print(
            outcome_disparity.to_string(index=False)
        )

    outcome_fairness_summary = pd.concat(
        summary_tables,
        ignore_index=True,
    )

    outcome_disparity_table = pd.concat(
        disparity_tables,
        ignore_index=True,
    )

    outcome_fairness_summary.to_csv(
        OUTPUT_DIR / "outcome_fairness_summary.csv",
        index=False,
    )

    outcome_disparity_table.to_csv(
        OUTPUT_DIR / "outcome_disparity_table.csv",
        index=False,
    )

    print("\nSaved outcome_fairness_summary.csv")
    print("Saved outcome_disparity_table.csv")

    return (
        outcome_fairness_summary,
        outcome_disparity_table,
    )


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    run()