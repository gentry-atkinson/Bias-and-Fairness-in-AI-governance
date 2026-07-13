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

