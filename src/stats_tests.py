"""
stats_tests.py
--------------
Statistical tests for measuring association between features and protected
attributes in the Travis County pretrial dataset.

Supported test pairs
--------------------
| Feature type  | Protected type | Test               | Effect size   |
|---------------|----------------|--------------------|---------------|
| categorical   | categorical    | Chi-Square         | Cramer's V    |
| numeric       | categorical    | Kruskal-Wallis     | Eta-squared   |
| categorical   | numeric        | Kruskal-Wallis     | Eta-squared   |
| numeric       | numeric        | Spearman           | |rho|          |

Kruskal-Wallis is preferred over one-way ANOVA because the data are rarely
normally distributed in criminal justice datasets.
"""

from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

class TestResult(NamedTuple):
    feature: str
    protected_attribute: str
    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    effect_size_label: str
    n_observations: int
    notes: str


# ---------------------------------------------------------------------------
# Helper: Cramer's V
# ---------------------------------------------------------------------------

def cramers_v(chi2: float, n: int, r: int, k: int) -> float:
    """Compute Cramer's V from chi-square statistics.

    Parameters
    ----------
    chi2:  Chi-square statistic.
    n:     Total number of observations.
    r:     Number of rows in contingency table.
    k:     Number of columns in contingency table.
    """
    if n == 0 or min(r, k) <= 1:
        return 0.0
    phi2 = chi2 / n
    phi2_corr = max(0.0, phi2 - ((r - 1) * (k - 1)) / (n - 1))
    r_corr = r - (r - 1) ** 2 / (n - 1)
    k_corr = k - (k - 1) ** 2 / (n - 1)
    denom = min(k_corr - 1, r_corr - 1)
    if denom <= 0:
        return 0.0
    return math.sqrt(phi2_corr / denom)


# ---------------------------------------------------------------------------
# Helper: Eta-squared from Kruskal-Wallis
# ---------------------------------------------------------------------------

def kruskal_eta_squared(h_stat: float, n: int, k: int) -> float:
    """Compute eta-squared effect size from Kruskal-Wallis H statistic.

    Formula: η² = (H - k + 1) / (n - k)
    """
    denom = n - k
    if denom <= 0:
        return 0.0
    return max(0.0, (h_stat - k + 1) / denom)


# ---------------------------------------------------------------------------
# Core test dispatch
# ---------------------------------------------------------------------------

def test_categorical_vs_categorical(
    feature_series: pd.Series,
    protected_series: pd.Series,
    feature_name: str,
    protected_name: str,
) -> TestResult:
    """Chi-Square test + Cramer's V for two categorical variables."""
    combined = pd.DataFrame({
        "feature": feature_series,
        "protected": protected_series,
    }).dropna()

    n = len(combined)
    if n < 5:
        return TestResult(
            feature=feature_name,
            protected_attribute=protected_name,
            test_name="Chi-Square",
            statistic=float("nan"),
            p_value=float("nan"),
            effect_size=float("nan"),
            effect_size_label="Cramer's V",
            n_observations=n,
            notes="Too few observations after dropping NaN.",
        )

    contingency = pd.crosstab(combined["feature"], combined["protected"])
    chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
    r, k = contingency.shape
    v = cramers_v(chi2, n, r, k)

    return TestResult(
        feature=feature_name,
        protected_attribute=protected_name,
        test_name="Chi-Square",
        statistic=round(chi2, 4),
        p_value=round(p_val, 6),
        effect_size=round(v, 4),
        effect_size_label="Cramer's V",
        n_observations=n,
        notes=f"dof={dof}",
    )


def test_numeric_vs_categorical(
    numeric_series: pd.Series,
    categorical_series: pd.Series,
    numeric_name: str,
    categorical_name: str,
) -> TestResult:
    """Kruskal-Wallis test + eta-squared for numeric feature vs categorical protected attr."""
    combined = pd.DataFrame({
        "numeric": numeric_series,
        "categorical": categorical_series,
    }).dropna()

    n = len(combined)
    groups = [
        grp["numeric"].values
        for _, grp in combined.groupby("categorical")
        if len(grp) >= 1
    ]
    k = len(groups)

    if k < 2 or n < 5:
        return TestResult(
            feature=numeric_name,
            protected_attribute=categorical_name,
            test_name="Kruskal-Wallis",
            statistic=float("nan"),
            p_value=float("nan"),
            effect_size=float("nan"),
            effect_size_label="Eta-squared",
            n_observations=n,
            notes="Fewer than 2 groups or too few observations after dropping NaN.",
        )

    h_stat, p_val = stats.kruskal(*groups)
    eta2 = kruskal_eta_squared(h_stat, n, k)

    return TestResult(
        feature=numeric_name,
        protected_attribute=categorical_name,
        test_name="Kruskal-Wallis",
        statistic=round(h_stat, 4),
        p_value=round(p_val, 6),
        effect_size=round(eta2, 4),
        effect_size_label="Eta-squared",
        n_observations=n,
        notes=f"k={k} groups",
    )


def test_numeric_vs_numeric(
    feature_series: pd.Series,
    protected_series: pd.Series,
    feature_name: str,
    protected_name: str,
) -> TestResult:
    """Spearman correlation for two numeric variables."""
    combined = pd.DataFrame({
        "feature": feature_series,
        "protected": protected_series,
    }).dropna()

    n = len(combined)
    if n < 5:
        return TestResult(
            feature=feature_name,
            protected_attribute=protected_name,
            test_name="Spearman",
            statistic=float("nan"),
            p_value=float("nan"),
            effect_size=float("nan"),
            effect_size_label="|rho|",
            n_observations=n,
            notes="Too few observations after dropping NaN.",
        )

    rho, p_val = stats.spearmanr(combined["feature"], combined["protected"])

    return TestResult(
        feature=feature_name,
        protected_attribute=protected_name,
        test_name="Spearman",
        statistic=round(rho, 4),
        p_value=round(p_val, 6),
        effect_size=round(abs(rho), 4),
        effect_size_label="|rho|",
        n_observations=n,
        notes="",
    )


# ---------------------------------------------------------------------------
# KL Divergence (stretch goal)
# ---------------------------------------------------------------------------

def kl_divergence_for_groups(
    numeric_series: pd.Series,
    group_series: pd.Series,
    group_a: str,
    group_b: str,
    n_bins: int = 30,
) -> float:
    """Compute KL divergence between two group distributions of a numeric variable.

    Uses histogram binning to estimate probability distributions.
    Returns KL( P_a || P_b ).

    Parameters
    ----------
    numeric_series:  Continuous feature values.
    group_series:    Categorical group labels (e.g. race).
    group_a:         Label for the reference group (P).
    group_b:         Label for the comparison group (Q).
    n_bins:          Number of histogram bins.
    """
    combined = pd.DataFrame({"val": numeric_series, "grp": group_series}).dropna()
    vals_a = combined.loc[combined["grp"] == group_a, "val"].values
    vals_b = combined.loc[combined["grp"] == group_b, "val"].values

    if len(vals_a) < 5 or len(vals_b) < 5:
        return float("nan")

    global_min = min(vals_a.min(), vals_b.min())
    global_max = max(vals_a.max(), vals_b.max())
    bins = np.linspace(global_min, global_max, n_bins + 1)

    hist_a, _ = np.histogram(vals_a, bins=bins, density=False)
    hist_b, _ = np.histogram(vals_b, bins=bins, density=False)

    # Add small epsilon to avoid log(0)
    eps = 1e-10
    p = hist_a.astype(float) + eps
    q = hist_b.astype(float) + eps
    p /= p.sum()
    q /= q.sum()

    return float(stats.entropy(p, q))
