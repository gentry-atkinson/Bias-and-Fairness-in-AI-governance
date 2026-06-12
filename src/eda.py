"""
eda.py
------
Basic EDA pipeline for the Travis County criminal justice dataset.
Produces summary tables and saves them to reports/tables/travis_county_basic_eda/.

Run from the project root:
    python src/eda.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from data_loading import DATASET_SPECS, load_dataset, PROJECT_ROOT

OUTPUT_DIR = PROJECT_ROOT / "reports" / "tables" / "travis_county_basic_eda"

# ---------------------------------------------------------------------------
# Summary builders
# ---------------------------------------------------------------------------

def build_dataset_summary(name: str, df: pd.DataFrame) -> dict:
    dupes = int(df.duplicated().sum())
    return {
        "dataset": name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "duplicate_rows": dupes,
        "duplicate_pct": round(dupes / len(df) * 100, 2) if len(df) else 0.0,
        "numeric_columns": int(len(df.select_dtypes(include=["number"]).columns)),
        "categorical_columns": int(len(df.select_dtypes(include=["object", "string", "category", "bool"]).columns)),
    }


def build_dtype_summary(name: str, df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "dataset": name,
        "column": df.columns.astype(str),
        "dtype": df.dtypes.astype(str).values,
    })


def build_missing_summary(name: str, df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isna().sum()
    pct = (missing / len(df) * 100) if len(df) else 0
    result = pd.DataFrame({
        "dataset": name,
        "column": missing.index.astype(str),
        "missing_count": missing.values,
        "missing_pct": pct.values,
    })
    return result.sort_values(["missing_pct", "missing_count"], ascending=[False, False]).reset_index(drop=True)


def build_numeric_summary(name: str, df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame(columns=["dataset", "column", "count", "mean", "std", "min", "25%", "50%", "75%", "max"])
    summary = numeric_df.describe().T.reset_index().rename(columns={"index": "column"})
    summary.insert(0, "dataset", name)
    return summary


def build_categorical_value_counts(
    name: str,
    df: pd.DataFrame,
    max_columns: int = 12,
    top_n: int = 10,
) -> pd.DataFrame:
    cols = df.select_dtypes(include=["object", "string", "category", "bool"]).columns.tolist()[:max_columns]
    rows = []
    for col in cols:
        vc = df[col].fillna("<MISSING>").astype(str).value_counts(dropna=False).head(top_n)
        for val, cnt in vc.items():
            rows.append({"dataset": name, "column": col, "value": val, "count": int(cnt)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_eda(
    dataset_specs: list[dict] = DATASET_SPECS,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    """Run EDA over all dataset specs, save CSVs, and return the summary frames."""
    output_dir.mkdir(parents=True, exist_ok=True)

    overview_rows, dtype_frames, missing_frames, numeric_frames, cat_frames = [], [], [], [], []

    for spec in dataset_specs:
        name = spec["dataset"]
        print(f"  EDA: {name} ...")
        df = load_dataset(spec)

        overview_rows.append(build_dataset_summary(name, df))
        dtype_frames.append(build_dtype_summary(name, df))
        missing_frames.append(build_missing_summary(name, df))
        numeric_frames.append(build_numeric_summary(name, df))
        cat_frames.append(build_categorical_value_counts(name, df))

    results = {
        "dataset_overview": pd.DataFrame(overview_rows).sort_values("dataset").reset_index(drop=True),
        "column_dtypes": pd.concat(dtype_frames, ignore_index=True),
        "missing_values": pd.concat(missing_frames, ignore_index=True),
        "numeric_summary": pd.concat(numeric_frames, ignore_index=True),
        "categorical_value_counts": pd.concat(cat_frames, ignore_index=True),
    }

    for key, frame in results.items():
        path = output_dir / f"{key}.csv"
        frame.to_csv(path, index=False)
        print(f"  Saved → {path}")

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running basic EDA pipeline...")
    summaries = run_eda()

    print("\n--- Dataset Overview ---")
    print(summaries["dataset_overview"].to_string(index=False))

    print("\n--- Missing Values (totals by dataset) ---")
    totals = (
        summaries["missing_values"]
        .groupby("dataset", as_index=False)["missing_count"]
        .sum()
        .sort_values("missing_count", ascending=False)
    )
    print(totals.to_string(index=False))
