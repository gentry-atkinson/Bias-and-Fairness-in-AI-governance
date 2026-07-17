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

import pandas as pd
import matplotlib.pyplot as plt

from utils import clean_race_labels



from fairness_metrics import (
    group_base_rate,
    harsher_outcome_disparity,
)

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

HIGH_RISK_THRESHOLD = 6

# Additional thresholds for sensitivity analysis.
# This helps us see whether group disparities depend on the cutoff.
HIGH_RISK_THRESHOLDS = [4, 5, 6, 7]

# Reference groups for disparity comparisons.
# These are temporary and should be confirmed with the professor.
REFERENCE_GROUPS = {
    "race": "White",
    "sex": "F",
    "age_group": "18-25",
}


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
        df.groupby(group_col, observed=False)[RISK_SCORE_COL]
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
    Statistical parity difference for every pair of groups.
    """

    groups = sorted(df[group_col].dropna().unique())

    rows = []

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            g1 = groups[i]
            g2 = groups[j]

            subset = df[df[group_col].isin([g1, g2])]

            disparity = group_base_rate(
                subset["high_risk"].to_numpy(),
                subset[group_col].to_numpy(),
            )

            rows.append(
                {
                    group_col: f"{g1} vs {g2}",
                    "statistical_parity_difference": round(disparity, 4),
                }
            )

    return pd.DataFrame(rows)

def mean_score_disparity(df, group_col):
    """
    Difference in mean risk score between every pair of groups.
    """

    groups = sorted(df[group_col].dropna().unique())

    rows = []

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            g1 = groups[i]
            g2 = groups[j]

            subset = df[df[group_col].isin([g1, g2])]

            disparity = harsher_outcome_disparity(
                subset[RISK_SCORE_COL].to_numpy(),
                subset[group_col].to_numpy(),
            )

            rows.append(
                {
                    group_col: f"{g1} vs {g2}",
                    "mean_score_difference": round(disparity, 4),
                }
            )

    return pd.DataFrame(rows)

def threshold_sensitivity(df, group_col):
    """
    Compute high-risk rates by group across multiple thresholds.

    This shows whether statistical parity results depend on
    the chosen high-risk cutoff.
    """

    rows = []

    for threshold in HIGH_RISK_THRESHOLDS:

        temp = df.copy()

        temp["high_risk_at_threshold"] = (
            temp[RISK_SCORE_COL] >= threshold
        )

        rates = (
            temp.groupby(group_col)["high_risk_at_threshold"]
            .mean()
            .reset_index()
        )

        rates["threshold"] = threshold

        rates.rename(
            columns={
                "high_risk_at_threshold": "high_risk_rate"
            },
            inplace=True,
        )

        rows.append(rates)

    result = pd.concat(
        rows,
        ignore_index=True,
    )

    result["high_risk_rate"] = (
        result["high_risk_rate"]
        .round(4)
    )

    return result


def build_disparity_table(df, group_col):
    """
    Build a group-level disparity table.

    Compares each group to a reference group using:
    - mean risk score difference
    - high-risk rate difference
    - high-risk rate ratio
    """

    summary = summarize_scores(
        df,
        group_col,
    )

    parity = statistical_parity(
        df,
        group_col,
    )

    table = summary.merge(
        parity,
        on=group_col,
        how="left",
    )

    reference_group = REFERENCE_GROUPS.get(group_col)

    if reference_group is None:
        table["reference_group"] = np.nan
        table["mean_score_difference_from_reference"] = np.nan
        table["high_risk_rate_difference_from_reference"] = np.nan
        table["high_risk_rate_ratio_to_reference"] = np.nan
        return table

    reference_row = table[
        table[group_col] == reference_group
    ]

    if reference_row.empty:
        table["reference_group"] = reference_group
        table["mean_score_difference_from_reference"] = np.nan
        table["high_risk_rate_difference_from_reference"] = np.nan
        table["high_risk_rate_ratio_to_reference"] = np.nan
        return table

    reference_mean = reference_row["mean"].iloc[0]
    reference_rate = reference_row["high_risk_rate"].iloc[0]

    table["reference_group"] = reference_group

    table["mean_score_difference_from_reference"] = (
        table["mean"] - reference_mean
    ).round(3)

    table["high_risk_rate_difference_from_reference"] = (
        table["high_risk_rate"] - reference_rate
    ).round(4)

    if reference_rate == 0:
        table["high_risk_rate_ratio_to_reference"] = np.nan
    else:
        table["high_risk_rate_ratio_to_reference"] = (
            table["high_risk_rate"] / reference_rate
        ).round(3)

    return table

#plots

def get_group_order(group_col):
    """
    Define a clean display order for groups.
    """
    orders = {
        "race": [
            "Asian",
            "Black",
            "American Indian / Alaska Native",
            "Unknown",
            "White",
        ],
        "sex": ["F", "M"],
        "age_group": ["18-25", "26-35", "36-50", "50+"],
    }
    return orders.get(group_col, None)

def add_bar_labels(ax, bars, decimals=3):
    """
    Add numeric labels above bars.
    """
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.{decimals}f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
        
def plot_mean_risk_scores(summary_df, group_col):
    """
    Bar chart of mean risk score by group.
    """
    plot_df = summary_df.copy()

    order = get_group_order(group_col)
    if order is not None:
        plot_df[group_col] = pd.Categorical(
            plot_df[group_col],
            categories=order,
            ordered=True,
        )
        plot_df = plot_df.sort_values(group_col)

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        plot_df[group_col].astype(str),
        plot_df["mean"],
    )

    ax.set_title(f"Average Risk Score by {group_col}")
    ax.set_xlabel(group_col.replace("_", " ").title())
    ax.set_ylabel("Mean Risk Score")
    ax.set_ylim(0, max(plot_df["mean"]) * 1.15)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    add_bar_labels(ax, bars, decimals=3)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"mean_risk_score_{group_col}.png", dpi=300)
    plt.close()
    
    
def plot_high_risk_rate(parity_df, group_col):
    """
    Bar chart of high-risk rate by group.
    """
    plot_df = parity_df.copy()

    order = get_group_order(group_col)
    if order is not None:
        plot_df[group_col] = pd.Categorical(
            plot_df[group_col],
            categories=order,
            ordered=True,
        )
        plot_df = plot_df.sort_values(group_col)

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        plot_df[group_col].astype(str),
        plot_df["high_risk_rate"],
    )

    ax.set_title(f"High-Risk Rate by {group_col} (threshold = {HIGH_RISK_THRESHOLD})")
    ax.set_xlabel(group_col.replace("_", " ").title())
    ax.set_ylabel("High-Risk Rate")
    ax.set_ylim(0, max(plot_df["high_risk_rate"]) * 1.20 + 0.01)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    add_bar_labels(ax, bars, decimals=4)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"high_risk_rate_{group_col}.png", dpi=300)
    plt.close()
    
def plot_threshold_sensitivity(threshold_df, group_col):
    """
    Line chart showing how high-risk rates change across thresholds.
    """
    plot_df = threshold_df.copy()

    order = get_group_order(group_col)
    groups = order if order is not None else sorted(plot_df[group_col].dropna().unique())

    fig, ax = plt.subplots(figsize=(8, 5))

    for group in groups:
        subset = plot_df[plot_df[group_col] == group].sort_values("threshold")
        ax.plot(
            subset["threshold"],
            subset["high_risk_rate"],
            marker="o",
            label=str(group),
        )

    ax.set_title(f"Threshold Sensitivity by {group_col}")
    ax.set_xlabel("High-Risk Threshold")
    ax.set_ylabel("High-Risk Rate")
    ax.set_xticks(HIGH_RISK_THRESHOLDS)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(title=group_col, frameon=False)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"threshold_sensitivity_{group_col}.png", dpi=300)
    plt.close()

def plot_risk_boxplot(df, group_col):
    """
    Boxplot of risk score distributions by group.
    """
    order = get_group_order(group_col)
    if order is None:
        order = sorted(df[group_col].dropna().unique())

    data = [
        df.loc[df[group_col] == group, RISK_SCORE_COL].dropna()
        for group in order
    ]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.boxplot(
        data,
        labels=[str(group) for group in order],
        patch_artist=False,
    )

    ax.set_title(f"Risk Score Distribution by {group_col}")
    ax.set_xlabel(group_col.replace("_", " ").title())
    ax.set_ylabel("Risk Score")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(FIGURE_DIR / f"risk_boxplot_{group_col}.png", dpi=300)
    plt.close()


# def plot_risk_distribution(df, group_col):
#     """
#     Plot risk score distributions.
#     """

#     plt.figure(figsize=(10, 6))

#     for group in sorted(df[group_col].dropna().unique()):

#         subset = df[
#             df[group_col] == group
#         ]

#         plt.hist(
#             subset[RISK_SCORE_COL],
#             bins=10,
#             alpha=0.5,
#             density=True,
#             label=str(group),
#         )

#     plt.xlabel("Risk Score")
#     plt.ylabel("Density")
#     plt.title(
#         f"Risk Score Distribution by {group_col}"
#     )
#     plt.legend()

#     plt.tight_layout()

#     plt.savefig(
#         FIGURE_DIR /
#         f"risk_distribution_{group_col}.png"
#     )

#     plt.close()


# ------------------------------------------------------------------
# Main Analysis
# ------------------------------------------------------------------

def run():

    df = pd.read_csv(DATA_PATH)
    
    df = clean_race_labels(df)
    

    print(
        f"Loaded {len(df):,} rows × "
        f"{len(df.columns)} columns"
    )
    
    '''
    print("\n=== Columns in Complete Defendants Dataset ===")
    print(df.columns.tolist())
    '''

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
    threshold_tables = []
    disparity_tables = []

    score_disparity_tables = []

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
        
        threshold_table = threshold_sensitivity(
            fairness_df,
            column,
        )

        disparity_table = build_disparity_table(
            fairness_df,
            column,
        )

        score_disparity = mean_score_disparity(
        fairness_df,
        column,
    )

        print("\nMean Score Disparity")
        print(score_disparity)

        print("\nRisk Scores")
        print(summary)

        print("\nStatistical Parity")
        print(parity)
        
        print("\nThreshold Sensitivity")
        print(threshold_table)

        print("\nDisparity Table")
        print(disparity_table)

        summary["protected_attribute"] = column

        parity["protected_attribute"] = column
        
        threshold_table["protected_attribute"] = column
        
        disparity_table["protected_attribute"] = column

        summary_tables.append(summary)
        parity_tables.append(parity)
        threshold_tables.append(threshold_table)
        disparity_tables.append(disparity_table)

        score_disparity["protected_attribute"] = column
        score_disparity_tables.append(score_disparity)

        plot_risk_distribution(
            fairness_df,
            column,
    )
        plot_mean_risk_scores(summary, column)

        plot_high_risk_rate(parity, column)

        plot_threshold_sensitivity(threshold_table, column)

        plot_risk_boxplot(fairness_df, column)

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
    
    threshold_sensitivity_df = pd.concat(
        threshold_tables,
        ignore_index=True,
    )

    disparity_df = pd.concat(
        disparity_tables,
        ignore_index=True,
    )

    mean_score_disparity_df = pd.concat(
        score_disparity_tables,
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

    mean_score_disparity_df.to_csv(
    OUTPUT_DIR /
    "mean_score_disparity.csv",
    index=False,
    )

    print(
        "\nSaved fairness_summary.csv"
    
    threshold_sensitivity_df.to_csv(
        OUTPUT_DIR / "threshold_sensitivity.csv",
        index=False,
    )

    disparity_df.to_csv(
        OUTPUT_DIR / "fairness_disparity_table.csv",
        index=False,
    )

    print(
    "Saved mean_score_disparity.csv"
    )

    print(
        "Saved risk distribution figures"
    )
    print("\nSaved fairness_summary.csv")
    print("Saved statistical_parity.csv")
    print("Saved threshold_sensitivity.csv")
    print("Saved fairness_disparity_table.csv")
    print("Saved figures figures")

    return (
        fairness_summary,
        statistical_parity_df,
        mean_score_disparity_df,
        threshold_sensitivity_df,
        disparity_df,
    )

# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":

    fairness_summary, parity, mean_score_disparity = run()

