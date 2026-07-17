"""
Summary of High-Risk vs. Low-Risk defendants.

Creates:

outputs/
    high_low_risk_summary.csv
    high_low_risk_by_race.csv
    high_low_risk_by_sex.csv
    high_low_risk_by_age.csv

figures/
    high_low_risk_distribution.png
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import clean_race_labels


# -----------------------------------------------------
# Paths
# -----------------------------------------------------

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


# -----------------------------------------------------
# Configuration
# -----------------------------------------------------

HIGH_RISK_THRESHOLD = 6


# -----------------------------------------------------
# Load Data
# -----------------------------------------------------

def load_data():

    print(f"Loading {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    df = clean_race_labels(df)

    print(f"Loaded {len(df):,} rows")

    return df


# -----------------------------------------------------
# Create Risk Groups
# -----------------------------------------------------

def create_risk_groups(df):

    df = df[df["risk_score"].notna()].copy()

    df["risk_group"] = np.where(
        df["risk_score"] >= HIGH_RISK_THRESHOLD,
        "High Risk",
        "Low Risk",
    )

    return df


# -----------------------------------------------------
# Overall Summary
# -----------------------------------------------------

def summarize_risk_groups(df):

    summary = (
        df.groupby("risk_group")
        .size()
        .reset_index(name="count")
    )

    summary["percent"] = (
        summary["count"]
        / summary["count"].sum()
        * 100
    ).round(2)

    return summary


# -----------------------------------------------------
# Demographic Breakdown
# -----------------------------------------------------

def summarize_by_group(df, group_col):

    summary = (
        df.groupby(["risk_group", group_col])
        .size()
        .reset_index(name="count")
    )

    summary["percent"] = (
        summary.groupby("risk_group")["count"]
        .transform(lambda x: x / x.sum() * 100)
        .round(2)
    )

    return summary


# -----------------------------------------------------
# Plot
# -----------------------------------------------------

def plot_risk_groups(summary):

    fig, ax = plt.subplots(figsize=(6,5))

    bars = ax.bar(
        summary["risk_group"],
        summary["percent"],
    )

    ax.set_ylabel("Percent of Defendants")
    ax.set_xlabel("")
    ax.set_title(
        "High-Risk vs. Low-Risk Population"
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(axis="y", alpha=0.25)

    for bar, pct in zip(bars, summary["percent"]):

        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{pct:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )
        
        

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR / "high_low_risk_distribution.png",
        dpi=300,
    )

    plt.close()
    
    
def plot_stacked_bar(summary, group_col):
        
    """
    Plot a 100% stacked bar chart showing the demographic
    composition of the High-Risk and Low-Risk groups.
    """

    pivot = (
        summary.pivot(
            index="risk_group",
            columns=group_col,
            values="percent",
        )
        .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(8,6))

    pivot.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.65,
    )
    
    for container in ax.containers:

        labels = []

        for value in container.datavalues:

            if value < 3:
                labels.append("")
            else:
                labels.append(f"{value:.1f}%")

        ax.bar_label(
            container,
            labels=labels,
            label_type="center",
            fontsize=9,
    )

    ax.set_ylabel("Percent of Risk Group")
    ax.set_xlabel("")
    ax.set_ylim(0,100)

    ax.set_title(
        f"{group_col.replace('_',' ').title()} Distribution\nWithin High- and Low-Risk Groups"
    )

    ax.legend(
        title=group_col.replace("_"," ").title(),
        bbox_to_anchor=(1.02,1),
        loc="upper left",
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(axis="y", alpha=0.25)

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR /
        f"high_low_risk_{group_col}.png",
        dpi=300,
    )

    plt.close()


# -----------------------------------------------------
# Main
# -----------------------------------------------------

def run():

    df = load_data()

    df = create_risk_groups(df)

    overall = summarize_risk_groups(df)

    race = summarize_by_group(df, "race")

    sex = summarize_by_group(df, "sex")

    age = summarize_by_group(df, "age_group")

    print("\nOverall")
    print(overall)

    print("\nRace")
    print(race)

    print("\nSex")
    print(sex)

    print("\nAge")
    print(age)

    overall.to_csv(
        OUTPUT_DIR / "high_low_risk_summary.csv",
        index=False,
    )

    race.to_csv(
        OUTPUT_DIR / "high_low_risk_by_race.csv",
        index=False,
    )

    sex.to_csv(
        OUTPUT_DIR / "high_low_risk_by_sex.csv",
        index=False,
    )

    age.to_csv(
        OUTPUT_DIR / "high_low_risk_by_age.csv",
        index=False,
    )

    plot_risk_groups(overall)
    
    plot_stacked_bar(race, "race")
    plot_stacked_bar(sex, "sex")
    plot_stacked_bar(age, "age_group")

    print("\nSaved high_low_risk_summary.csv")
    print("Saved high_low_risk_by_race.csv")
    print("Saved high_low_risk_by_sex.csv")
    print("Saved high_low_risk_by_age.csv")
    print("Saved high_low_risk_distribution.png")

    return overall, race, sex, age


if __name__ == "__main__":

    run()