"""
inferential_statistics.py
-------------------------

Inferential statistical testing for the Travis County
pretrial fairness audit.

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
outputs/inferential_statistics.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import (
    chi2_contingency,
    kruskal,
    mannwhitneyu,
)

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

PROTECTED_ATTRIBUTES = {
    "race": "race",
    "sex": "sex",
    "age": "age_group",
}

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

