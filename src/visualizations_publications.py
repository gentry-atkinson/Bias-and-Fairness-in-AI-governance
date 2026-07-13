"""
Publication-quality visualizations for the Travis County
Pretrial Fairness Analysis.

Outputs
-------
figures/publication/
    risk_score_boxplot_race.png
    risk_score_boxplot_sex.png
    risk_score_boxplot_age.png
    mean_risk_scores.png
    outcome_heatmap.png
    effect_sizes.png
    significance_matrix.png
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats

# -----------------------------------------------------
# Paths
# -----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_with_case_outcomes.csv"
)

STATS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "inferential_statistics.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "figures"
    / "publication"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# -----------------------------------------------------
# Configuration
# -----------------------------------------------------

RISK_SCORE = "risk_score"

PROTECTED_ATTRIBUTES = {
    "Race": "race",
    "Sex": "sex",
    "Age": "age_group",
}

OUTCOME_COLUMNS = [
    "has_case_record",
    "has_disposition",
    "has_sentence",
    "has_plea",
    "has_verdict",
]

def add_value_labels(ax, decimals=2):
    """
    Place labels on top of every bar.
    """

    for container in ax.containers:

        ax.bar_label(
            container,
            fmt=f"%.{decimals}f",
            fontsize=9,
            padding=3,
        )
        
        
        
def standardize_axes(ax):
    """
    Publication styling.
    """

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    ax.set_axisbelow(True)
    
    
    
def save_figure(filename):
    """
    Save figure consistently.
    """

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / filename,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()
    
    
def load_data():

    print(f"Loading {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print(
        f"Loaded {len(df):,} rows × {len(df.columns)} columns"
    )

    return df


def load_statistics():

    stats_df = pd.read_csv(STATS_PATH)

    return stats_df




## Outcome Heatmap

def plot_outcome_heatmap(df):
    """
    Heatmap of outcome rates across protected groups.
    """

    records = []

    protected = {
        "Race": "race",
        "Sex": "sex",
        "Age": "age_group",
    }

    for group_name, column in protected.items():

        for outcome in OUTCOME_COLUMNS:

            rates = (
                df.groupby(column)[outcome]
                .mean()
                .reset_index()
            )

            for _, row in rates.iterrows():

                records.append({
                    "Protected Group": group_name,
                    "Category": row[column],
                    "Outcome": outcome.replace("has_", "").replace("_", " ").title(),
                    "Rate": row[outcome],
                })

    heat = pd.DataFrame(records)

    for group in heat["Protected Group"].unique():

        subset = heat[heat["Protected Group"] == group]

        pivot = subset.pivot(
            index="Category",
            columns="Outcome",
            values="Rate",
        )

        fig, ax = plt.subplots(figsize=(8,4))

        im = ax.imshow(
            pivot.values,
            aspect="auto",
        )

        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels(
            pivot.columns,
            rotation=30,
            ha="right",
        )

        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels(pivot.index)

        plt.colorbar(im)

        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):

                ax.text(
                    j,
                    i,
                    f"{pivot.iloc[i,j]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=9,
                )

        ax.set_title(f"{group} Outcome Rates")

        save_figure(
            f"{group.lower()}_outcome_heatmap.png"
        )
        
        
        
## Mean Risk Scores Bar Chart

def plot_mean_risk_scores(df):

    for label, column in PROTECTED_ATTRIBUTES.items():

        summary = (
            df.groupby(column)[RISK_SCORE]
            .mean()
            .sort_values()
        )

        fig, ax = plt.subplots(figsize=(7,4))

        bars = ax.bar(
            summary.index.astype(str),
            summary.values,
        )

        ax.set_ylabel("Average Risk Score")
        ax.set_xlabel(label)

        ax.set_title(
            f"Average Risk Score by {label}"
        )

        add_value_labels(ax, 2)

        standardize_axes(ax)

        save_figure(
            f"mean_risk_score_{column}.png"
        )
        
        
        
def plot_mean_risk_scores(df):

    for label, column in PROTECTED_ATTRIBUTES.items():

        summary = (
            df.groupby(column)[RISK_SCORE]
            .mean()
            .sort_values()
        )

        fig, ax = plt.subplots(figsize=(7,4))

        bars = ax.bar(
            summary.index.astype(str),
            summary.values,
        )

        ax.set_ylabel("Average Risk Score")
        ax.set_xlabel(label)

        ax.set_title(
            f"Average Risk Score by {label}"
        )

        add_value_labels(ax, 2)

        standardize_axes(ax)

        save_figure(
            f"mean_risk_score_{column}.png"
        )
        
        
## Effect Sizes Plot
        
def plot_effect_sizes(stats_df):

    effects = stats_df[
        stats_df["Effect Size"].notna()
    ].copy()

    effects = effects.sort_values(
        "Effect Size",
        ascending=False,
    )

    labels = (
        effects["Outcome"]
        + "\n"
        + effects["Protected Attribute"]
    )

    fig, ax = plt.subplots(figsize=(10,6))

    ax.barh(
        labels,
        effects["Effect Size"],
    )

    ax.set_xlabel("Cramer's V")

    ax.set_title(
        "Association Strength Between Protected Attributes and Outcomes"
    )

    standardize_axes(ax)

    save_figure("effect_sizes.png")
    
    
def run():

    df = load_data()

    stats_df = load_statistics()

    plot_mean_risk_scores(df)

    plot_outcome_heatmap(df)

    plot_effect_sizes(stats_df)

    print("\nFinished creating publication figures.")
    
    
    
    
    
if __name__ == "__main__":
    run()