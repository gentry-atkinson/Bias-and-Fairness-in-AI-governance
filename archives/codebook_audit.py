"""
codebook_audit.py
-----------------

Search raw Travis County files for possible codebooks, lookup tables,
description columns, and outcome/disposition mappings.

Goal:
Find whether any raw file can decode coded fields such as:
- DispositionID
- DispositionTypeID
- DispositionMethodID
- OriginalDispositionEvent
- SentenceID
- VerdictID
- PleaID

Run from project root:
    python src/codebook_audit.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Files to inspect
# ---------------------------------------------------------------------

RAW_FILES = [
    "PreTrial Disposition Reason.xlsx",
    "PreTrial TCUD-ODAR Events.xlsx",
    "PreTrial to Booking Info.xlsx",
    "revocationV2.xlsx",
    "SentencingDataPost2013.xlsx",
    "SentencingDataPre2013.xlsx",
    "171017_CCHCodes_Violent marked by Slayton.xlsx",
    "Booking2010_2012v3.csv",
    "Booking2013_2016v3.csv",
    "CaseData_v2.csv",
    "CaseIDtoBookingChargeIDUPDATED.xlsx",
    "chargecode_description.dta",
    "Events.xlsx",
    "Mental Health Flag Events.xlsx",
    "PersonData.xlsx",
    "PreTrial Charge-Interview.csv",
    "PreTrial Charge-Interview.xlsx",
    "PreTrial Defendants.xlsx",
]


LOOKUP_KEYWORDS = [
    "description",
    "desc",
    "reason",
    "type",
    "method",
    "event",
    "status",
    "code",
    "id",
    "disposition",
    "sentence",
    "sentencing",
    "verdict",
    "plea",
    "charge",
    "violent",
    "outcome",
    "result",
    "decision",
    "bond",
    "release",
    "detention",
    "revocation",
]


TARGET_CODE_COLUMNS = [
    "DispositionID",
    "DispositionTypeID",
    "DispositionMethodID",
    "DispositionEventID",
    "OriginalDispositionID",
    "OriginalDispositionEvent",
    "OriginalDispositionMethodID",
    "OriginalDispositionPleaID",
    "OriginalDispositionVerdictID",
    "OriginalSentenceID",
    "LatestDispositionID",
    "LatestDispositionMethodID",
    "LatestSentenceID",
    "SentenceTypeID",
    "SentenceUOMID",
    "JailCaseTypeID",
]


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def safe_read_csv(path: Path, nrows=None, usecols=None) -> pd.DataFrame:
    return pd.read_csv(
        path,
        nrows=nrows,
        usecols=usecols,
        low_memory=False,
    )


def safe_read_excel(path: Path, sheet_name, nrows=None, usecols=None) -> pd.DataFrame:
    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        nrows=nrows,
        usecols=usecols,
    )


def read_dta(path: Path, nrows=None) -> pd.DataFrame:
    df = pd.read_stata(path)

    if nrows is not None:
        df = df.head(nrows)

    return df


def is_lookup_like(df: pd.DataFrame) -> bool:
    """
    A loose heuristic for lookup/codebook-like tables.

    Lookup tables often have:
    - not too many rows
    - an ID/code column
    - a description/reason/name column
    """

    cols = [str(c).lower() for c in df.columns]

    has_id_or_code = any(
        ("id" in c or "code" in c) for c in cols
    )

    has_desc = any(
        (
            "desc" in c
            or "description" in c
            or "reason" in c
            or "name" in c
            or "type" in c
            or "method" in c
        )
        for c in cols
    )

    return has_id_or_code and has_desc and len(df) <= 50000


def keyword_columns(columns: list[str]) -> list[str]:
    matches = []

    for col in columns:
        col_lower = str(col).lower()

        if any(keyword in col_lower for keyword in LOOKUP_KEYWORDS):
            matches.append(col)

    return matches


def target_columns_present(columns: list[str]) -> list[str]:
    present = []

    lower_to_original = {
        str(col).lower(): col
        for col in columns
    }

    for target in TARGET_CODE_COLUMNS:
        if target.lower() in lower_to_original:
            present.append(lower_to_original[target.lower()])

    return present


def value_counts_for_targets(
    df: pd.DataFrame,
    file_name: str,
    sheet_name,
) -> list[dict]:
    rows = []

    for col in target_columns_present(df.columns):

        counts = (
            df[col]
            .value_counts(dropna=False)
            .head(30)
        )

        for value, count in counts.items():
            rows.append(
                {
                    "file": file_name,
                    "sheet": sheet_name,
                    "column": col,
                    "value": value,
                    "count": count,
                }
            )

    return rows


def inspect_dataframe(
    df: pd.DataFrame,
    file_name: str,
    sheet_name,
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Return:
    1. sheet inventory rows
    2. candidate codebook rows
    3. target value-count rows
    """

    columns = list(df.columns)

    inventory_row = {
        "file": file_name,
        "sheet": sheet_name,
        "n_rows_sample_or_full": len(df),
        "n_columns": len(columns),
        "columns": columns,
        "target_code_columns_present": target_columns_present(columns),
        "keyword_columns": keyword_columns(columns),
        "is_lookup_like": is_lookup_like(df),
    }

    candidate_rows = []

    if inventory_row["keyword_columns"] or inventory_row["is_lookup_like"]:
        candidate_rows.append(
            {
                "file": file_name,
                "sheet": sheet_name,
                "is_lookup_like": inventory_row["is_lookup_like"],
                "target_code_columns_present": inventory_row[
                    "target_code_columns_present"
                ],
                "keyword_columns": inventory_row["keyword_columns"],
                "n_rows_sample_or_full": len(df),
                "n_columns": len(columns),
            }
        )

    value_count_rows = value_counts_for_targets(
        df,
        file_name,
        sheet_name,
    )

    return [inventory_row], candidate_rows, value_count_rows


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def run():
    inventory_rows = []
    candidate_rows = []
    value_count_rows = []

    for file_name in RAW_FILES:

        path = RAW_DATA_DIR / file_name

        print(f"\nInspecting {file_name}...")

        if not path.exists():
            print(f"  Missing: {path}")
            continue

        suffix = path.suffix.lower()

        try:
            if suffix == ".csv":

                # Read only sample first for inventory.
                sample_df = safe_read_csv(path, nrows=5000)

                inv, cand, counts = inspect_dataframe(
                    sample_df,
                    file_name,
                    sheet_name=None,
                )

                inventory_rows.extend(inv)
                candidate_rows.extend(cand)

                # For target value counts, read only relevant target columns from full CSV.
                target_cols = target_columns_present(sample_df.columns)

                if target_cols:
                    full_target_df = safe_read_csv(
                        path,
                        usecols=target_cols,
                    )

                    value_count_rows.extend(
                        value_counts_for_targets(
                            full_target_df,
                            file_name,
                            sheet_name=None,
                        )
                    )

            elif suffix in [".xlsx", ".xls"]:

                workbook = pd.ExcelFile(path)

                for sheet in workbook.sheet_names:

                    print(f"  Sheet: {sheet}")

                    sample_df = safe_read_excel(
                        path,
                        sheet_name=sheet,
                        nrows=5000,
                    )

                    inv, cand, counts = inspect_dataframe(
                        sample_df,
                        file_name,
                        sheet_name=sheet,
                    )

                    inventory_rows.extend(inv)
                    candidate_rows.extend(cand)

                    target_cols = target_columns_present(sample_df.columns)

                    if target_cols:
                        full_target_df = safe_read_excel(
                            path,
                            sheet_name=sheet,
                            usecols=target_cols,
                        )

                        value_count_rows.extend(
                            value_counts_for_targets(
                                full_target_df,
                                file_name,
                                sheet_name=sheet,
                            )
                        )

            elif suffix == ".dta":

                df = read_dta(path)

                inv, cand, counts = inspect_dataframe(
                    df,
                    file_name,
                    sheet_name=None,
                )

                inventory_rows.extend(inv)
                candidate_rows.extend(cand)
                value_count_rows.extend(counts)

            else:
                print(f"  Skipping unsupported file type: {suffix}")

        except Exception as exc:
            print(f"  ERROR reading {file_name}: {exc}")

    inventory_df = pd.DataFrame(inventory_rows)
    candidate_df = pd.DataFrame(candidate_rows)
    value_counts_df = pd.DataFrame(value_count_rows)

    inventory_path = OUTPUT_DIR / "raw_codebook_sheet_inventory.csv"
    candidate_path = OUTPUT_DIR / "candidate_codebook_tables.csv"
    value_counts_path = OUTPUT_DIR / "target_code_value_counts.csv"

    inventory_df.to_csv(
        inventory_path,
        index=False,
    )

    candidate_df.to_csv(
        candidate_path,
        index=False,
    )

    value_counts_df.to_csv(
        value_counts_path,
        index=False,
    )

    print("\nSaved:")
    print(inventory_path)
    print(candidate_path)
    print(value_counts_path)

    print("\n=== Candidate Codebook / Lookup Tables ===")
    if candidate_df.empty:
        print("No candidate lookup/codebook tables found.")
    else:
        print(
            candidate_df[
                [
                    "file",
                    "sheet",
                    "is_lookup_like",
                    "target_code_columns_present",
                    "keyword_columns",
                    "n_rows_sample_or_full",
                    "n_columns",
                ]
            ].to_string(index=False)
        )

    print("\n=== Target Code Columns Found ===")
    if inventory_df.empty:
        print("No inventory generated.")
    else:
        target_hits = inventory_df[
            inventory_df["target_code_columns_present"].astype(str) != "[]"
        ]

        if target_hits.empty:
            print("No target code columns found.")
        else:
            print(
                target_hits[
                    [
                        "file",
                        "sheet",
                        "target_code_columns_present",
                        "keyword_columns",
                    ]
                ].to_string(index=False)
            )

    return inventory_df, candidate_df, value_counts_df


if __name__ == "__main__":
    run()