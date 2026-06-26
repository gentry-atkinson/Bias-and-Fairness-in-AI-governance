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

def add_bar_labels(ax, bars, fmt="{:.3f}", pad=0.01):
    """
    Add value labels above bars.
    """
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + pad,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=10,
        )

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

def plot_single_outcome_rate(
    summary_df,
    protected_attribute,
    outcome,
    title,
    output_path,
):
    """
    Plot one outcome rate by one protected attribute.

    This creates a cleaner, more focused chart than showing
    all outcomes at once.
    """

    group_col = PROTECTED_GROUP_COLUMNS[protected_attribute]

    subset = summary_df[
        (summary_df["protected_attribute"] == protected_attribute)
        & (summary_df["outcome"] == outcome)
    ].copy()

    subset[group_col] = pd.Categorical(
        subset[group_col],
        categories=GROUP_ORDERS[protected_attribute],
        ordered=True,
    )

    subset = subset.sort_values(group_col)

    x = subset[group_col].astype(str)
    y = subset["outcome_rate"].values

    fig, ax = plt.subplots(figsize=(8, 4.8))

    bars = ax.bar(x, y)

    # Keep baseline at 0, but reduce wasted white space
    y_max = max(y) if len(y) > 0 else 1
    upper = max(0.1, y_max * 1.20)
    ax.set_ylim(0, upper)

    ax.set_ylabel("Outcome Rate")
    ax.set_xlabel(protected_attribute.title())
    ax.set_title(title)

    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    # Clean up chart appearance
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add labels above bars
    add_bar_labels(ax, bars, fmt="{:.3f}", pad=upper * 0.02)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    

def plot_single_outcome_ratio(
    disparity_df,
    protected_attribute,
    outcome,
    title,
    output_path,
):
    """
    Plot one outcome rate ratio by protected group.

    A horizontal line at 1.0 marks the reference group.
    """


    group_col = PROTECTED_GROUP_COLUMNS[protected_attribute]

    subset = disparity_df[
        (disparity_df["protected_attribute"] == protected_attribute)
        & (disparity_df["outcome"] == outcome)
    ].copy()

    subset[group_col] = pd.Categorical(
        subset[group_col],
        categories=GROUP_ORDERS[protected_attribute],
        ordered=True,
    )

    subset = subset.sort_values(group_col)

    x = subset[group_col].astype(str)
    y = subset["rate_ratio_to_reference"].values

    fig, ax = plt.subplots(figsize=(8, 4.8))

    bars = ax.bar(x, y)

    # Keep baseline at 0, but reduce white space
    y_max = max(y) if len(y) > 0 else 1
    upper = max(1.1, y_max * 1.15)
    ax.set_ylim(0, upper)

    ax.axhline(
        y=1.0,
        linestyle="--",
        linewidth=1,
    )

    ax.set_ylabel("Rate Ratio to Reference Group")
    ax.set_xlabel(protected_attribute.title())
    ax.set_title(title)

    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    add_bar_labels(ax, bars, fmt="{:.3f}", pad=upper * 0.02)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    
def plot_outcome_heatmap(
    summary_df,
    protected_attribute,
    title,
    output_path,
):
    """
    Heatmap of outcome rates for all outcomes within one protected attribute.
    """

    group_col = PROTECTED_GROUP_COLUMNS[protected_attribute]

    outcome_order = [
        "has_case_record",
        "has_disposition",
        "has_sentence",
        "has_plea",
        "has_verdict",
    ]

    outcome_labels = {
        "has_case_record": "Case Record",
        "has_disposition": "Disposition",
        "has_sentence": "Sentence",
        "has_plea": "Plea",
        "has_verdict": "Verdict",
    }

    subset = summary_df[
        summary_df["protected_attribute"] == protected_attribute
    ].copy()

    pivot = subset.pivot(
        index=group_col,
        columns="outcome",
        values="outcome_rate",
    )

    pivot = pivot.reindex(index=GROUP_ORDERS[protected_attribute])
    pivot = pivot[outcome_order]
    pivot.columns = [outcome_labels[col] for col in pivot.columns]

    fig, ax = plt.subplots(figsize=(8, 4.8))

    im = ax.imshow(pivot.values, aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(x) for x in pivot.index])

    ax.set_xlabel("Outcome")
    ax.set_ylabel(protected_attribute.title())
    ax.set_title(title)

    # Annotate each cell
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iloc[i, j]
            ax.text(
                j,
                i,
                f"{value:.3f}",
                ha="center",
                va="center",
                fontsize=9,
            )

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Outcome Rate")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
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


    # --------------------------------------------------------------
    # Focused charts for strongest preliminary disparities
    # --------------------------------------------------------------

    focused_charts = [
        {
            "protected_attribute": "race",
            "outcome": "has_verdict",
            "rate_title": "Group B has the highest verdict record rate among race groups",
            "ratio_title": "Verdict record rate ratio is highest for group B",
            "rate_file": "focused_verdict_rate_by_race.png",
            "ratio_file": "focused_verdict_ratio_by_race.png",
        },
        {
            "protected_attribute": "gender",
            "outcome": "has_verdict",
            "rate_title": "Males have a higher verdict record rate than females",
            "ratio_title": "Male verdict record rate is about 1.6 times the female rate",
            "rate_file": "focused_verdict_rate_by_gender.png",
            "ratio_file": "focused_verdict_ratio_by_gender.png",
        },
        {
            "protected_attribute": "age",
            "outcome": "has_verdict",
            "rate_title": "Verdict record rates increase with age",
            "ratio_title": "Older age groups have higher verdict record rate ratios",
            "rate_file": "focused_verdict_rate_by_age.png",
            "ratio_file": "focused_verdict_ratio_by_age.png",
        },
        {
            "protected_attribute": "gender",
            "outcome": "has_plea",
            "rate_title": "Males have a higher plea record rate than females",
            "ratio_title": "Male plea record rate is higher than the female reference group",
            "rate_file": "focused_plea_rate_by_gender.png",
            "ratio_file": "focused_plea_ratio_by_gender.png",
        },
        {
            "protected_attribute": "age",
            "outcome": "has_plea",
            "rate_title": "Plea record rates increase across age groups",
            "ratio_title": "Older age groups have higher plea record rate ratios",
            "rate_file": "focused_plea_rate_by_age.png",
            "ratio_file": "focused_plea_ratio_by_age.png",
        },
    ]

    for chart in focused_charts:
        plot_single_outcome_rate(
            summary_df,
            protected_attribute=chart["protected_attribute"],
            outcome=chart["outcome"],
            title=chart["rate_title"],
            output_path=FIGURE_DIR / chart["rate_file"],
        )

        plot_single_outcome_ratio(
            disparity_df,
            protected_attribute=chart["protected_attribute"],
            outcome=chart["outcome"],
            title=chart["ratio_title"],
            output_path=FIGURE_DIR / chart["ratio_file"],
        )
        
    #--------------------------------------------------------------    
    # Heatmaps showing all outcomes at once
    #--------------------------------------------------------------
    
    plot_outcome_heatmap(
        summary_df,
        protected_attribute="race",
        title="Outcome rates across all outcomes by race",
        output_path=FIGURE_DIR / "heatmap_outcome_rates_race.png",
    )

    plot_outcome_heatmap(
        summary_df,
        protected_attribute="gender",
        title="Outcome rates across all outcomes by gender",
        output_path=FIGURE_DIR / "heatmap_outcome_rates_gender.png",
    )

    plot_outcome_heatmap(
        summary_df,
        protected_attribute="age",
        title="Outcome rates across all outcomes by age",
        output_path=FIGURE_DIR / "heatmap_outcome_rates_age.png",
    )

if __name__ == "__main__":
    run()