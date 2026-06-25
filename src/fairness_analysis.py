"""

Initial fairness analysis of Travis County risk scores.

Measures:
1. Average risk score by protected group
2. Statistical parity
3. Risk score distributions
4. Group summary tables

Outputs:
- fairness_summary.csv
- statistical_parity.csv
- figures/*.png

"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_df.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

RISK_SCORE_COL = "risk_score"

PROTECTED_ATTRIBUTES = {
    "race": "race",
    "gender": "sex",
    "age": "age_group",
}

HIGH_RISK_THRESHOLD = 7


# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def create_age_groups(df):
    """
    Create age buckets for fairness analysis.
    """

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


def summarize_scores(df, group_col):
    """
    Average risk score by group.
    """

    summary = (
        df.groupby(group_col)[RISK_SCORE_COL]
        .agg(
            count="count",
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
        )
        .round(3)
        .reset_index()
    )

    return summary


def statistical_parity(df, group_col):
    """
    P(high risk | group)

    Measures how often each group
    receives a high-risk label.
    """

    parity = (
        df.groupby(group_col)["high_risk"]
        .mean()
        .round(4)
        .reset_index()
    )

    parity.rename(
        columns={
            "high_risk": "high_risk_rate"
        },
        inplace=True,
    )

    return parity


def plot_risk_distribution(df, group_col):
    """
    Plot risk score distributions.
    """

    plt.figure(figsize=(10, 6))

    for group in sorted(df[group_col].dropna().unique()):

        subset = df[
            df[group_col] == group
        ]

        plt.hist(
            subset[RISK_SCORE_COL],
            bins=10,
            alpha=0.5,
            density=True,
            label=str(group),
        )

    plt.xlabel("Risk Score")
    plt.ylabel("Density")
    plt.title(
        f"Risk Score Distribution by {group_col}"
    )
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR /
        f"risk_distribution_{group_col}.png"
    )

    plt.close()


# ------------------------------------------------------------------
# Main Analysis
# ------------------------------------------------------------------

def run():

    df = pd.read_csv(DATA_PATH)

    print(
        f"Loaded {len(df):,} rows × "
        f"{len(df.columns)} columns"
    )
    
    ##
    print("\n=== Columns in Complete Defendants Dataset ===")
    print(df.columns.tolist())
    ##

    df = create_age_groups(df)

    fairness_df = df[
        df[RISK_SCORE_COL].notna()
    ].copy()

    fairness_df["high_risk"] = (
        fairness_df[RISK_SCORE_COL] >= HIGH_RISK_THRESHOLD
    )

    print(
        f"Using {len(fairness_df):,} records "
        f"with observed risk scores"
    )


    # ------------------------------------------
    # Overall score summary
    # ------------------------------------------
    
    overall = (
        fairness_df[RISK_SCORE_COL]
        .describe()
        .round(3)
    )

    print("\n=== Overall Risk Score Summary ===")
    print(overall)

    # ------------------------------------------
    # Group summaries
    # ------------------------------------------

    summary_tables = []

    parity_tables = []

    for label, column in PROTECTED_ATTRIBUTES.items():
        
        print(
            f"\n=== {column.upper()} ==="
        )

        summary = summarize_scores(
            fairness_df,
            column,
        )

        parity = statistical_parity(
            fairness_df,
            column,
        )   

        print("\nRisk Scores")
        print(summary)

        print("\nStatistical Parity")
        print(parity)

        summary["protected_attribute"] = column

        parity["protected_attribute"] = column

        summary_tables.append(summary)

        parity_tables.append(parity)

        plot_risk_distribution(
            fairness_df,
            column,
        )

    # ------------------------------------------
    # Save outputs
    # ------------------------------------------

    fairness_summary = pd.concat(
        summary_tables,
        ignore_index=True,
    )

    statistical_parity_df = pd.concat(
        parity_tables,
        ignore_index=True,
    )

    fairness_summary.to_csv(
        OUTPUT_DIR /
        "fairness_summary.csv",
        index=False,
    )

    statistical_parity_df.to_csv(
        OUTPUT_DIR /
        "statistical_parity.csv",
        index=False,
    )

    print(
        "\nSaved fairness_summary.csv"
    )

    print(
        "Saved statistical_parity.csv"
    )

    print(
        "Saved risk distribution figures"
    )

    return (
        fairness_summary,
        statistical_parity_df,
    )


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":

    fairness_summary, parity = run()

