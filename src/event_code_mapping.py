"""
event_code_mapping_audit.py
---------------------------

Check whether CaseData disposition event codes can be decoded using Events.xlsx.

Run from project root:
    python src/event_code_mapping_audit.py
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CASE_PATH = RAW_DATA_DIR / "CaseData_v2.csv"
EVENTS_PATH = RAW_DATA_DIR / "Events.xlsx"


CASE_EVENT_COLUMNS = [
    "CaseID",
    "DispositionEventID",
    "OriginalDispositionEvent",
    "DispositionID",
    "OriginalDispositionID",
    "DispositionTypeID",
    "DispositionMethodID",
]

EVENT_COLUMNS = [
    "EventID",
    "CaseID",
    "PartyID",
    "EventDate",
    "EventCodeID",
    "EventResultID",
    "EventCode",
    "EventDescription",
    "EventCategoryID",
    "AssociatedCaseStatusID",
]


def normalize(series):
    return (
        series
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


def compute_overlap(left, right):
    left_set = set(normalize(left))
    right_set = set(normalize(right))

    shared = left_set & right_set

    return {
        "left_unique": len(left_set),
        "right_unique": len(right_set),
        "shared_unique": len(shared),
        "left_overlap_rate": round(len(shared) / len(left_set), 4)
        if left_set else 0,
        "right_overlap_rate": round(len(shared) / len(right_set), 4)
        if right_set else 0,
    }


def run():
    print("Loading CaseData_v2 event columns...")

    case_df = pd.read_csv(
        CASE_PATH,
        usecols=lambda col: col in CASE_EVENT_COLUMNS,
        low_memory=False,
    )

    print(
        f"CaseData: {len(case_df):,} rows × "
        f"{len(case_df.columns)} columns"
    )

    print("Loading Events.xlsx...")

    events_df = pd.read_excel(
        EVENTS_PATH,
        sheet_name="Events",
        usecols=lambda col: col in EVENT_COLUMNS,
    )

    print(
        f"Events: {len(events_df):,} rows × "
        f"{len(events_df.columns)} columns"
    )

    case_code_cols = [
        "DispositionEventID",
        "OriginalDispositionEvent",
        "DispositionID",
        "OriginalDispositionID",
        "DispositionTypeID",
        "DispositionMethodID",
    ]

    event_code_cols = [
        "EventID",
        "EventCodeID",
        "EventResultID",
        "EventCode",
        "EventCategoryID",
        "AssociatedCaseStatusID",
    ]

    overlap_rows = []

    for case_col in case_code_cols:
        if case_col not in case_df.columns:
            continue

        for event_col in event_code_cols:
            if event_col not in events_df.columns:
                continue

            overlap = compute_overlap(
                case_df[case_col],
                events_df[event_col],
            )

            overlap_rows.append(
                {
                    "case_column": case_col,
                    "events_column": event_col,
                    **overlap,
                }
            )

    overlap_df = pd.DataFrame(overlap_rows)

    overlap_df = overlap_df.sort_values(
        "shared_unique",
        ascending=False,
    )

    overlap_df.to_csv(
        OUTPUT_DIR / "case_event_code_overlap.csv",
        index=False,
    )

    print("\n=== Event Code Overlap ===")
    print(overlap_df.to_string(index=False))

    # Build possible readable mappings for strongest candidate columns.
    mapping_rows = []

    for event_col in event_code_cols:
        if event_col not in events_df.columns:
            continue

        if "EventDescription" not in events_df.columns:
            continue

        mapping = (
            events_df[[event_col, "EventDescription"]]
            .dropna()
            .drop_duplicates()
            .sort_values(event_col)
        )

        mapping["events_code_column"] = event_col

        mapping_rows.append(mapping)

    if mapping_rows:
        mapping_df = pd.concat(
            mapping_rows,
            ignore_index=True,
        )

        mapping_df.to_csv(
            OUTPUT_DIR / "event_code_description_candidates.csv",
            index=False,
        )

        print("\nSaved event_code_description_candidates.csv")

    print("\nSaved case_event_code_overlap.csv")

    return overlap_df


if __name__ == "__main__":
    run()