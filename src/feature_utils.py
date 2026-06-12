"""
feature_utils.py
----------------
Utilities for detecting feature types and categorizing columns in the
Travis County pretrial dataset for proxy variable analysis.
"""

from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Column roles defined from the data dictionary
# ---------------------------------------------------------------------------

PROTECTED_ATTRIBUTES: list[str] = ["race", "sex", "ethnicity"]

# age_at_booking is listed separately; include it when age bias is in scope
DEMOGRAPHIC_ATTRIBUTES: list[str] = ["age_at_booking", "age_group"]

# Columns that are identifiers or timestamps — skip these in analysis
SKIP_COLUMNS: set[str] = {"pretrial_id", "booking_date"}

# Categorical cardinality threshold: if a numeric column has ≤ this many
# unique values it is treated as categorical (e.g. binary flags).
CATEGORICAL_NUNIQUE_THRESHOLD: int = 10


def detect_feature_type(series: pd.Series) -> str:
    """Return ``"categorical"`` or ``"numeric"`` for a pandas Series.

    Rules:
    - Object / bool / category dtype → categorical
    - Numeric dtype with ≤ CATEGORICAL_NUNIQUE_THRESHOLD unique non-null
      values → categorical
    - All other numeric dtypes → numeric
    """
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_categorical_dtype(series) or pd.api.types.is_object_dtype(series):
        return "categorical"
    if pd.api.types.is_numeric_dtype(series):
        n_unique = series.nunique(dropna=True)
        if n_unique <= CATEGORICAL_NUNIQUE_THRESHOLD:
            return "categorical"
        return "numeric"
    # fallback
    return "categorical"


def build_feature_type_map(
    df: pd.DataFrame,
    skip: set[str] | None = None,
) -> dict[str, str]:
    """Return a mapping of column name → ``"categorical"`` | ``"numeric"``.

    Parameters
    ----------
    df:
        The analysis dataframe.
    skip:
        Additional column names to exclude (merged with ``SKIP_COLUMNS``).
    """
    excluded = SKIP_COLUMNS | (skip or set())
    return {
        col: detect_feature_type(df[col])
        for col in df.columns
        if col not in excluded
    }


def get_analysis_features(
    df: pd.DataFrame,
    protected: list[str] | None = None,
) -> list[str]:
    """Return all columns that are *not* protected attributes or skip columns.

    These are the candidate proxy / outcome features to test against each
    protected attribute.
    """
    protected_set = set(protected or PROTECTED_ATTRIBUTES)
    return [
        col for col in df.columns
        if col not in SKIP_COLUMNS and col not in protected_set
    ]
