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
    / "travis_county_pretrial_analysis_df.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"

OUTPUT_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

RISK_SCORE_COL = "risk_score"

PROTECTED_ATTRIBUTES = [
    "race",
    "gender",
    "age_group",
]

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

