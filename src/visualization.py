"""
visualization.py
----------------
All matplotlib visualizations for the Travis County EDA:
  - Dataset size and missingness overview (from EDA summary tables)
  - Demographic distributions (race, gender, age, ZIP)
  - Risk score distribution
  - Bond outcome distributions
  - Group-level bond grant rate comparisons

Loads from saved interim CSV; run dataframing.py first if needed.

Run from the project root:
    python src/visualization.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import pandas as pd

from dataloader import PROJECT_ROOT

EDA_TABLE_DIR = PROJECT_ROOT / "reports" / "tables" / "travis_county_basic_eda"
EDA_FIG_DIR = PROJECT_ROOT / "reports" / "figures" / "travis_county_basic_eda"
GROUPED_FIG_DIR = PROJECT_ROOT / "reports" / "figures" / "travis_county_grouped_viz"
INTERIM_DATA_PATH = PROJECT_ROOT / "data" / "interim" / "travis_county_pretrial_analysis_df.csv"

# ---------------------------------------------------------------------------
# EDA overview plots (from saved summary tables)
# ---------------------------------------------------------------------------

def plot_eda_overviews() -> None:
    """Rows by dataset, missing by dataset, top missingness columns, top cat counts."""
    EDA_FIG_DIR.mkdir(parents=True, exist_ok=True)

    overview = pd.read_csv(EDA_TABLE_DIR / "dataset_overview.csv")
    missing = pd.read_csv(EDA_TABLE_DIR / "missing_values.csv")
    cat_counts = pd.read_csv(EDA_TABLE_DIR / "categorical_value_counts_top10.csv")

    missing_by_ds = missing.groupby("dataset", as_index=False)["missing_count"].sum().sort_values("missing_count", ascending=False)
    top_missing_cols = missing.sort_values(["missing_pct", "missing_count"], ascending=[False, False]).head(15)
    top_cat = cat_counts.groupby(["dataset", "column"], as_index=False)["count"].max().sort_values("count", ascending=False).head(15)

    # Rows by dataset
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(overview["dataset"], overview["rows"], color="#4C78A8")
    ax.set_title("Rows by Dataset")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Rows")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(EDA_FIG_DIR / "rows_by_dataset.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Missing by dataset
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(missing_by_ds["dataset"], missing_by_ds["missing_count"], color="#F58518")
    ax.set_title("Total Missing Values by Dataset")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Missing values")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(EDA_FIG_DIR / "missing_values_by_dataset.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Top missingness columns
    labels = top_missing_cols["dataset"] + " | " + top_missing_cols["column"]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(labels, top_missing_cols["missing_pct"], color="#E45756")
    ax.set_title("Top Missingness Rates")
    ax.set_xlabel("Missing percent")
    fig.tight_layout()
    fig.savefig(EDA_FIG_DIR / "top_missingness_columns.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Top categorical value counts
    labels = top_cat["dataset"] + " | " + top_cat["column"]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(labels, top_cat["count"], color="#72B7B2")
    ax.set_title("Largest Top Category Counts")
    ax.set_xlabel("Count of most frequent value")
    fig.tight_layout()
    fig.savefig(EDA_FIG_DIR / "top_categorical_value_counts.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"EDA overview figures saved → {EDA_FIG_DIR}")


# ---------------------------------------------------------------------------
# Grouped / demographic plots (from analysis-ready CSV)
# ---------------------------------------------------------------------------

def _load_analysis_df() -> pd.DataFrame:
    df = pd.read_csv(INTERIM_DATA_PATH, low_memory=False)
    df["race_display"] = df["race"].fillna("<MISSING>").astype(str)
    df["gender_display"] = df["sex"].fillna("<MISSING>").astype(str)
    df["zip_display"] = df["zip_code"].fillna("<MISSING>").astype(str)
    df["PA_PTS_RISK_num"] = pd.to_numeric(df["risk_score"], errors="coerce")
    df["PK_BND_AMT_num"] = pd.to_numeric(df["bond_amount"], errors="coerce")
    # age_group may already be in CSV; recompute if absent
    if "age_group" not in df.columns:
        df["age_group"] = pd.cut(
            df["age_at_booking"],
            bins=[0, 24, 34, 44, 54, 64, 100],
            labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
            include_lowest=True,
        ).astype("string")
    return df


def plot_key_field_missingness(df: pd.DataFrame) -> None:
    GROUPED_FIG_DIR.mkdir(parents=True, exist_ok=True)
    cols = [
        "sex", "race", "age_at_booking", "zip_code", "ethnicity", "risk_score",
        "bond_granted_raw", "bond_amount", "bond_type", "bond_status", "charge_code", "judge",
        "bond_granted_flag",
    ]
    missing_pct = [df[c].isna().mean() * 100 for c in cols if c in df.columns]
    present_cols = [c for c in cols if c in df.columns]

    plot_df = pd.DataFrame({"column": present_cols, "missing_pct": missing_pct}).sort_values("missing_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_df["column"], plot_df["missing_pct"], color="#E45756")
    ax.set_title("Missingness in Key Pretrial Analysis Fields")
    ax.set_xlabel("Missing percent")
    fig.tight_layout()
    fig.savefig(GROUPED_FIG_DIR / "key_field_missingness.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_demographic_distributions(df: pd.DataFrame) -> None:
    GROUPED_FIG_DIR.mkdir(parents=True, exist_ok=True)
    race_counts = df["race_display"].value_counts().head(10)
    gender_counts = df["gender_display"].value_counts().head(10)
    age_labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+", "nan"]
    age_counts = df["age_group"].astype(str).value_counts().reindex(age_labels, fill_value=0)
    zip_counts = df.loc[df["zip_display"] != "<MISSING>", "zip_display"].value_counts().head(10).sort_values()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].bar(race_counts.index.astype(str), race_counts.values, color="#4C78A8")
    axes[0, 0].set_title("Race Distribution")
    axes[0, 0].tick_params(axis="x", rotation=45)

    axes[0, 1].bar(gender_counts.index.astype(str), gender_counts.values, color="#F58518")
    axes[0, 1].set_title("Gender Distribution")
    axes[0, 1].tick_params(axis="x", rotation=45)

    axes[1, 0].bar(age_counts.index.astype(str), age_counts.values, color="#54A24B")
    axes[1, 0].set_title("Age Group Distribution")
    axes[1, 0].tick_params(axis="x", rotation=45)

    axes[1, 1].barh(zip_counts.index.astype(str), zip_counts.values, color="#B279A2")
    axes[1, 1].set_title("Top ZIP Code Counts")

    fig.suptitle("Key Demographic Distributions", fontsize=14)
    fig.tight_layout()
    fig.savefig(GROUPED_FIG_DIR / "demographic_distributions.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Risk score
    risk_counts = df["PA_PTS_RISK_num"].dropna().round().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(risk_counts.index.astype(str), risk_counts.values, color="#72B7B2")
    ax.set_title("Pretrial Risk Score Distribution")
    ax.set_xlabel("Risk score")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(GROUPED_FIG_DIR / "risk_score_distribution.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_outcome_distributions(df: pd.DataFrame) -> None:
    GROUPED_FIG_DIR.mkdir(parents=True, exist_ok=True)
    bond_grant_counts = df["bond_granted_raw"].fillna("<MISSING>").astype(str).str.upper().value_counts()
    p99 = df["PK_BND_AMT_num"].quantile(0.99)
    bond_amount_vals = df.loc[df["PK_BND_AMT_num"].between(0, p99, inclusive="both"), "PK_BND_AMT_num"].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].bar(bond_grant_counts.index.astype(str), bond_grant_counts.values, color="#ECA82C")
    axes[0].set_title("Bond Grant Outcomes")
    axes[0].set_xlabel("bond_granted_raw")

    axes[1].hist(bond_amount_vals, bins=30, color="#4C9F70", edgecolor="white")
    axes[1].set_title("Bond Amount Distribution (Trimmed at 99th pct)")
    axes[1].set_xlabel("Bond amount")
    axes[1].set_ylabel("Count")

    fig.tight_layout()
    fig.savefig(GROUPED_FIG_DIR / "outcome_distributions.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_group_level_comparisons(df: pd.DataFrame) -> None:
    GROUPED_FIG_DIR.mkdir(parents=True, exist_ok=True)

    race_grant = df.groupby("race_display", as_index=False)["bond_granted_flag"].mean().dropna().sort_values("bond_granted_flag", ascending=False).head(10)
    gender_grant = df.groupby("gender_display", as_index=False)["bond_granted_flag"].mean().dropna().sort_values("bond_granted_flag", ascending=False)
    age_grant = df.groupby("age_group", observed=False, as_index=False)["bond_granted_flag"].mean().dropna()
    zip_filtered = df[df["zip_display"] != "<MISSING>"].copy()
    zip_grant = (
        zip_filtered.groupby("zip_display", as_index=False)
        .agg(record_count=("pretrial_id", "size"), bond_granted_rate=("bond_granted_flag", "mean"))
        .query("record_count >= 100")
        .sort_values("bond_granted_rate", ascending=False)
        .head(10)
    )

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].bar(race_grant["race_display"].astype(str), race_grant["bond_granted_flag"], color="#4C78A8")
    axes[0, 0].set_title("Bond Grant Rate by Race")
    axes[0, 0].tick_params(axis="x", rotation=45)
    axes[0, 0].set_ylim(0, 1)

    axes[0, 1].bar(gender_grant["gender_display"].astype(str), gender_grant["bond_granted_flag"], color="#F58518")
    axes[0, 1].set_title("Bond Grant Rate by Gender")
    axes[0, 1].tick_params(axis="x", rotation=45)
    axes[0, 1].set_ylim(0, 1)

    axes[1, 0].bar(age_grant["age_group"].astype(str), age_grant["bond_granted_flag"], color="#54A24B")
    axes[1, 0].set_title("Bond Grant Rate by Age Group")
    axes[1, 0].tick_params(axis="x", rotation=45)
    axes[1, 0].set_ylim(0, 1)

    axes[1, 1].barh(zip_grant["zip_display"].astype(str), zip_grant["bond_granted_rate"], color="#B279A2")
    axes[1, 1].set_title("Bond Grant Rate by ZIP (>=100 records)")
    axes[1, 1].set_xlim(0, 1)

    fig.suptitle("Group-Level Outcome Comparisons", fontsize=14)
    fig.tight_layout()
    fig.savefig(GROUPED_FIG_DIR / "group_level_bond_grant_comparisons.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Grouped visualization figures saved → {GROUPED_FIG_DIR}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # EDA overview plots require the EDA summary tables to exist
    if (EDA_TABLE_DIR / "dataset_overview.csv").exists():
        print("Plotting EDA overview figures...")
        plot_eda_overviews()
    else:
        print("EDA summary tables not found — run src/eda.py first to generate them.")

    print("Loading analysis-ready dataframe for grouped visualizations...")
    df = _load_analysis_df()

    plot_key_field_missingness(df)
    plot_demographic_distributions(df)
    plot_outcome_distributions(df)
    plot_group_level_comparisons(df)
    print("All visualization figures complete.")
