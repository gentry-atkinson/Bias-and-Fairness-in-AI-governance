"""
outcome_fairness_visualization.py
---------------------------------

Create grouped bar charts for preliminary outcome/disposition fairness.

Inputs:
- outputs/outcome_fairness_summary.csv
- outputs/outcome_disparity_table.csv

Outputs:
- figures/outcome_rates_race.png
- figures/outcome_rates_gender.png
- figures/outcome_rates_age.png
- figures/outcome_disparity_race.png
- figures/outcome_disparity_gender.png
- figures/outcome_disparity_age.png
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SUMMARY_PATH = PROJECT_ROOT / "outputs" / "outcome_fairness_summary.csv"
DISPARITY_PATH = PROJECT_ROOT / "outputs" / "outcome_disparity_table.csv"
FIGURE_DIR = PROJECT_ROOT / "figures"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

PROTECTED_GROUP_COLUMNS = {
    "race": "race",
    "gender": "sex",
    "age": "age_group",
}

GROUP_ORDERS = {
    "race": ["A", "B", "I", "U", "W"],
    "gender": ["F", "M"],
    "age": ["18-25", "26-35", "36-50", "50+"],
}

OUTCOME_ORDER = [
    "has_case_record",
    "has_disposition",
    "has_sentence",
    "has_plea",
    "has_verdict",
]

OUTCOME_LABELS = {
    "has_case_record": "Case Record",
    "has_disposition": "Disposition",
    "has_sentence": "Sentence",
    "has_plea": "Plea",
    "has_verdict": "Verdict",
}


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def prepare_rate_pivot(summary_df, protected_attribute):
    group_col = PROTECTED_GROUP_COLUMNS[protected_attribute]

    subset = summary_df[
        summary_df["protected_attribute"] == protected_attribute
    ].copy()

    subset[group_col] = pd.Categorical(
        subset[group_col],
        categories=GROUP_ORDERS[protected_attribute],
        ordered=True,
    )

    pivot = subset.pivot(
        index=group_col,
        columns="outcome",
        values="outcome_rate",
    )

    pivot = pivot.reindex(GROUP_ORDERS[protected_attribute])

    available_cols = [col for col in OUTCOME_ORDER if col in pivot.columns]
    pivot = pivot[available_cols]

    return pivot


def prepare_disparity_pivot(disparity_df, protected_attribute):
    group_col = PROTECTED_GROUP_COLUMNS[protected_attribute]

    subset = disparity_df[
        disparity_df["protected_attribute"] == protected_attribute
    ].copy()

    subset[group_col] = pd.Categorical(
        subset[group_col],
        categories=GROUP_ORDERS[protected_attribute],
        ordered=True,
    )

    pivot = subset.pivot(
        index=group_col,
        columns="outcome",
        values="rate_ratio_to_reference",
    )

    pivot = pivot.reindex(GROUP_ORDERS[protected_attribute])

    available_cols = [col for col in OUTCOME_ORDER if col in pivot.columns]
    pivot = pivot[available_cols]

    return pivot


def plot_grouped_bars(pivot_df, title, ylabel, output_path):
    x = np.arange(len(pivot_df.index))
    n_series = len(pivot_df.columns)
    width = 0.15

    plt.figure(figsize=(12, 6))

    for i, col in enumerate(pivot_df.columns):
        offset = (i - (n_series - 1) / 2) * width
        plt.bar(
            x + offset,
            pivot_df[col].values,
            width=width,
            label=OUTCOME_LABELS.get(col, col),
        )

    plt.xticks(x, pivot_df.index.astype(str))
    plt.ylim(0, max(1.0, float(pivot_df.max().max()) + 0.1))
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def run():
    print(f"Loading {SUMMARY_PATH}")
    summary_df = pd.read_csv(SUMMARY_PATH)

    print(f"Loading {DISPARITY_PATH}")
    disparity_df = pd.read_csv(DISPARITY_PATH)

    # --------------------------------------------------------------
    # Outcome rate charts
    # --------------------------------------------------------------

    for protected_attribute in ["race", "gender", "age"]:
        rate_pivot = prepare_rate_pivot(summary_df, protected_attribute)

        plot_grouped_bars(
            rate_pivot,
            title=f"Preliminary Outcome Rates by {protected_attribute.title()}",
            ylabel="Outcome Rate",
            output_path=FIGURE_DIR / f"outcome_rates_{protected_attribute}.png",
        )

    # --------------------------------------------------------------
    # Disparity ratio charts
    # --------------------------------------------------------------

    for protected_attribute in ["race", "gender", "age"]:
        disparity_pivot = prepare_disparity_pivot(disparity_df, protected_attribute)

        plot_grouped_bars(
            disparity_pivot,
            title=f"Outcome Rate Ratios by {protected_attribute.title()}",
            ylabel="Rate Ratio to Reference Group",
            output_path=FIGURE_DIR / f"outcome_disparity_{protected_attribute}.png",
        )

    print("\nSaved:")
    print(" - figures/outcome_rates_race.png")
    print(" - figures/outcome_rates_gender.png")
    print(" - figures/outcome_rates_age.png")
    print(" - figures/outcome_disparity_race.png")
    print(" - figures/outcome_disparity_gender.png")
    print(" - figures/outcome_disparity_age.png")


if __name__ == "__main__":
    run()