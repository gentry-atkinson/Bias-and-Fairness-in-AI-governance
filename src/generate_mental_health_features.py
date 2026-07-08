from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT = PROJECT_ROOT / "data/raw/Mental Health Flag Events.xlsx"
OUTPUT = PROJECT_ROOT / "data/interim/mental_health_features.csv"


def main():

    df = pd.read_excel(INPUT)

    summary = (
        df.groupby("MNI", as_index=False)
        .agg(
            mental_health_event_count=("Event", "count"),
        )
    )

    summary["has_mental_health_flag"] = 1

    summary = summary.rename(columns={"MNI": "person_mni"})

    summary = summary[
        [
            "person_mni",
            "has_mental_health_flag",
            "mental_health_event_count",
        ]
    ]

    summary.to_csv(OUTPUT, index=False)

    print(summary.head())
    print()
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()