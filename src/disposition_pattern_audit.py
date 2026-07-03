"""
disposition_pattern_audit.py
----------------------------

Audit whether disposition codes are associated with sentence, plea,
or verdict fields.

This does NOT fully decode disposition codes, but it helps identify
which codes are likely related to conviction/sentencing outcomes.

Run from project root:
    python src/disposition_pattern_audit.py
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CASE_PATH = RAW_DATA_DIR / "CaseData_v2.csv"


USECOLS = [
    "CaseID",
    "OriginalBookingNumber",
    "OriginalDispositionID",
    "LatestDispositionID",
    "DispositionID",
    "DispositionTypeID",
    "DispositionMethodID",
    "OriginalDispositionPleaID",
    "OriginalDispositionVerdictID",
    "OriginalSentenceID",
    "LatestSentenceID",
    "DispositionDate",
    "OriginalDispositionDate",
    "LatestDispositionDate",
]


CODE_COLUMNS = [
    "OriginalDispositionID",
    "LatestDispositionID",
    "DispositionID",
    "DispositionTypeID",
    "DispositionMethodID",
]


def summarize_by_code(df, code_col):
    temp = df.copy()

    temp["has_sentence"] = (
        temp["OriginalSentenceID"].notna()
        | temp["LatestSentenceID"].notna()
    )

    temp["has_plea"] = temp["OriginalDispositionPleaID"].notna()

    temp["has_verdict"] = temp["OriginalDispositionVerdictID"].notna()

    temp["has_disposition_date"] = (
        temp["DispositionDate"].notna()
        | temp["OriginalDispositionDate"].notna()
        | temp["LatestDispositionDate"].notna()
    )

    summary = (
        temp
        .groupby(code_col, dropna=False)
        .agg(
            n_cases=("CaseID", "count"),
            has_sentence_rate=("has_sentence", "mean"),
            has_plea_rate=("has_plea", "mean"),
            has_verdict_rate=("has_verdict", "mean"),
            has_disposition_date_rate=("has_disposition_date", "mean"),
            unique_cases=("CaseID", "nunique"),
            unique_bookings=("OriginalBookingNumber", "nunique"),
        )
        .reset_index()
        .sort_values("n_cases", ascending=False)
    )

    summary.insert(0, "code_column", code_col)

    return summary


def run():
    print("Loading CaseData_v2.csv...")

    df = pd.read_csv(
        CASE_PATH,
        usecols=lambda col: col in USECOLS,
        low_memory=False,
    )

    print(f"Loaded {len(df):,} rows × {len(df.columns)} columns")

    all_summaries = []

    for code_col in CODE_COLUMNS:
        if code_col not in df.columns:
            print(f"Skipping missing column: {code_col}")
            continue

        print(f"Summarizing {code_col}...")

        summary = summarize_by_code(df, code_col)
        all_summaries.append(summary)

        output_path = OUTPUT_DIR / f"{code_col}_pattern_summary.csv"
        summary.to_csv(output_path, index=False)

        print(f"Saved {output_path}")

    combined = pd.concat(all_summaries, ignore_index=True)

    combined_path = OUTPUT_DIR / "disposition_code_pattern_summary.csv"
    combined.to_csv(combined_path, index=False)

    print("\nSaved combined summary:")
    print(combined_path)

    print("\n=== Top disposition code patterns ===")
    print(
        combined
        .sort_values(["code_column", "n_cases"], ascending=[True, False])
        .groupby("code_column")
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    run()