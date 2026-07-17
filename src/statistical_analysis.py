"""
statistical_analysis.py
-----------------------

Statistical analysis for the Travis County
pretrial fairness audit.

This script generates:

• Descriptive statistics
• Risk score association tests
• Outcome association tests

This script performs hypothesis testing for differences
across protected groups.

Tests performed
---------------
Risk Score
    - Race -> Kruskal-Wallis
    - Age  -> Kruskal-Wallis
    - Sex  -> Mann-Whitney U

Categorical Outcomes
    - Chi-square tests
    - Cramer's V effect size

Outputs
-------
outputs/risk_score_association_summary.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import (
    chi2_contingency,
    kruskal,
    mannwhitneyu,
)

from utils import clean_race_labels
# ----------------------------------------------------
# Paths
# ----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "travis_county_complete_defendants_with_case_outcomes.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

RISK_SCORE = "risk_score"

# PROTECTED_ATTRIBUTES = {
#     "race": "race",
#     "sex": "sex",
#     "age": "age_group",
# }

OUTCOME_COLUMNS = [
    "has_case_record",
    "has_disposition",
    "has_sentence",
    "has_plea",
    "has_verdict",
]

def create_age_groups(df):

    if "age_group" not in df.columns:

        df["age_group"] = pd.cut(
            df["age_at_booking"],
            bins=[0,25,35,50,120],
            labels=[
                "18-25",
                "26-35",
                "36-50",
                "50+",
            ],
        )

    return df

def cramers_v(table):

    chi2, _, _, _ = chi2_contingency(table)

    n = table.sum().sum()

    r, c = table.shape

    return np.sqrt(
        chi2 /
        (
            n *
            (min(r - 1, c - 1))
        )
    )
    
    
def kruskal_test(
    df,
    outcome,
    group,
):

    subset = df[
        [outcome, group]
    ].dropna()

    groups = [

        values[outcome].values

        for _, values

        in subset.groupby(group)

    ]

    stat, p = kruskal(*groups)

    return stat, p


def mann_whitney_test(
    df,
    outcome,
    group,
):

    subset = df[
        [outcome, group]
    ].dropna()

    levels = subset[group].unique()

    if len(levels) != 2:
        return np.nan, np.nan

    g1 = subset[
        subset[group] == levels[0]
    ][outcome]

    g2 = subset[
        subset[group] == levels[1]
    ][outcome]

    stat, p = mannwhitneyu(
        g1,
        g2,
        alternative="two-sided",
    )

    return stat, p


def descriptive_statistics(df, group):

    summary = (
        df.groupby(group)[RISK_SCORE]
        .agg(
            Count="count",
            Mean="mean",
            Median="median",
            Std="std",
            Minimum="min",
            Maximum="max",
        )
        .round(3)
        .reset_index()
    )

    summary.insert(
        0,
        "Protected Attribute",
        group,
    )

    return summary

def chi_square_test(
    df,
    outcome,
    group,
):
    """
    Chi-square test of independence between
    a protected attribute and a binary outcome.
    """

    subset = df[
        [outcome, group]
    ].dropna()

    table = pd.crosstab(
        subset[group],
        subset[outcome],
    )

    chi2, p, dof, _ = chi2_contingency(table)

    effect = cramers_v(table)

    return (
        chi2,
        p,
        dof,
        effect,
    )


def run():

    print(
        f"Loading {DATA_PATH}"
    )

    df = pd.read_csv(
        DATA_PATH,
        low_memory=False,
    )

    df = create_age_groups(df)
    
    df = clean_race_labels(df)

    results = []
    
    
    race_summary = descriptive_statistics(
        df,
        "race",
    )

    sex_summary = descriptive_statistics(
        df,
        "sex",
    )

    age_summary = descriptive_statistics(
        df,
        "age_group",
    )

    descriptive = pd.concat(
        [
            race_summary,
            sex_summary,
            age_summary,
        ],
        ignore_index=True,
    )

    descriptive.to_csv(
        OUTPUT_DIR
        / "descriptive_statistics.csv",
        index=False,
    )

    # ------------------------------
    # Risk score association tests
    # ------------------------------

    stat, p = kruskal_test(
        df,
        RISK_SCORE,
        "race",
    )

    results.append({
        "Outcome":"risk_score",
        "Protected Attribute":"race",
        "Test":"Kruskal-Wallis",
        "Statistic":stat,
        "P-value":p,
        "Effect Size":np.nan,
    })

    stat, p = kruskal_test(
        df,
        RISK_SCORE,
        "age_group",
    )

    results.append({
        "Outcome":"risk_score",
        "Protected Attribute":"age_group",
        "Test":"Kruskal-Wallis",
        "Statistic":stat,
        "P-value":p,
        "Effect Size":np.nan,
    })

    stat, p = mann_whitney_test(
        df,
        RISK_SCORE,
        "sex",
    )

    results.append({
        "Outcome":"risk_score",
        "Protected Attribute":"sex",
        "Test":"Mann-Whitney U",
        "Statistic":stat,
        "P-value":p,
        "Effect Size":np.nan,
    })

    for outcome in OUTCOME_COLUMNS:

        for group in [
            "race",
            "sex",
            "age_group",
        ]:

            chi2, p, dof, effect = chi_square_test(
                df,
                outcome,
                group,
            )

            results.append({

                "Outcome": outcome,

                "Protected Attribute": group,

                "Test":"Chi-square",

                "Statistic":chi2,

                "P-value":p,

                "Degrees Freedom":dof,

                "Effect Size":effect,

            })

    association_summary = pd.DataFrame(results)

    association_summary.to_csv(

        OUTPUT_DIR
        / "risk_score_association_summary.csv",

        index=False,

    )

    print(association_summary.to_string(index=False))

    print("\nSaved risk_score_association_summary.csv")
    print("Saved descriptive_statistics.csv")

    return association_summary


if __name__ == "__main__":

    run()