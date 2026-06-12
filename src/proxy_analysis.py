"""
proxy_analysis.py
-----------------
Week 2 deliverable: proxy variable discovery for the Travis County
pretrial dataset.

Tests every feature against three protected attributes
(race, gender, age) using the statistically correct test for each
variable-type combination, then exports a ranked association table.

Run from the project root:
    python src/proxy_analysis.py

Output:
    outputs/proxy_associations.csv
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = _PROJECT_ROOT / "data/interim/travis_county_pretrial_analysis_df.csv"
OUTPUT_PATH = _PROJECT_ROOT / "outputs/proxy_associations.csv"

# Professor-specified protected attributes.
# Maps display name → column name in the dataframe.
PROTECTED_ATTRIBUTES: dict[str, str] = {
    "race":   "race",
    "gender": "sex",           # dataset column is 'sex'
    "age":    "age_at_booking", # dataset column is 'age_at_booking'
}

# Columns to skip entirely (identifiers, timestamps)
SKIP_COLUMNS: set[str] = {"pretrial_id", "booking_date", "age_group"}

# These should be forced to categorical regardless of dtype
# (zip codes are stored as floats but are not numeric quantities)
FORCE_CATEGORICAL: set[str] = {"zip_code"}

# ---------------------------------------------------------------------------
# Type detection
# ---------------------------------------------------------------------------

def detect_type(series: pd.Series, force_categorical: bool = False) -> str:
    """Return 'categorical' or 'numeric' for a pandas Series."""
    if force_categorical:
        return "categorical"
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        return "categorical"
    if pd.api.types.is_numeric_dtype(series):
        # Low-cardinality numeric → treat as categorical
        if series.nunique(dropna=True) <= 10:
            return "categorical"
        return "numeric"
    return "categorical"

# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def _cramers_v(chi2: float, n: int, r: int, k: int) -> float:
    """Bias-corrected Cramer's V."""
    if n == 0 or min(r, k) <= 1:
        return 0.0
    phi2 = chi2 / n
    phi2c = max(0.0, phi2 - (r - 1) * (k - 1) / (n - 1))
    rc = r - (r - 1) ** 2 / (n - 1)
    kc = k - (k - 1) ** 2 / (n - 1)
    denom = min(kc - 1, rc - 1)
    return 0.0 if denom <= 0 else (phi2c / denom) ** 0.5


def _kruskal_eta2(h: float, n: int, k: int) -> float:
    """Eta-squared from Kruskal-Wallis H."""
    denom = n - k
    return max(0.0, (h - k + 1) / denom) if denom > 0 else 0.0


def test_pair(
    df: pd.DataFrame,
    feature_col: str,
    protected_col: str,
    feature_type: str,
    protected_type: str,
    feature_label: str,
    protected_label: str,
) -> dict:
    """Run the appropriate test for one feature / protected-attribute pair."""

    base = {
        "feature": feature_label,
        "protected_attribute": protected_label,
        "n_observations": None,
        "test": None,
        "statistic": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_label": None,
    }

    pair = pd.DataFrame({"f": df[feature_col], "p": df[protected_col]}).dropna()
    n = len(pair)
    base["n_observations"] = n

    if n < 10:
        return {**base, "test": "skipped", "p_value": float("nan"),
                "effect_size": float("nan"), "effect_size_label": "n/a"}

    # ---- Categorical × Categorical → Chi-Square + Cramer's V -------------
    if feature_type == "categorical" and protected_type == "categorical":
        ct = pd.crosstab(pair["f"], pair["p"])
        chi2, p, _, _ = stats.chi2_contingency(ct)
        r, k = ct.shape
        v = _cramers_v(chi2, n, r, k)
        return {**base, "test": "Chi-Square", "statistic": round(chi2, 3),
                "p_value": round(p, 6), "effect_size": round(v, 4),
                "effect_size_label": "Cramer's V"}

    # ---- Numeric × Categorical → Kruskal-Wallis + Eta-squared ------------
    if feature_type == "numeric" and protected_type == "categorical":
        groups = [g["f"].values for _, g in pair.groupby("p") if len(g) >= 2]
        k = len(groups)
        if k < 2:
            return {**base, "test": "Kruskal-Wallis", "p_value": float("nan"),
                    "effect_size": float("nan"), "effect_size_label": "Eta-squared"}
        h, p = stats.kruskal(*groups)
        eta2 = _kruskal_eta2(h, n, k)
        return {**base, "test": "Kruskal-Wallis", "statistic": round(h, 3),
                "p_value": round(p, 6), "effect_size": round(eta2, 4),
                "effect_size_label": "Eta-squared"}

    # ---- Categorical × Numeric → Kruskal-Wallis (swap roles) -------------
    if feature_type == "categorical" and protected_type == "numeric":
        groups = [g["p"].values for _, g in pair.groupby("f") if len(g) >= 2]
        k = len(groups)
        if k < 2:
            return {**base, "test": "Kruskal-Wallis", "p_value": float("nan"),
                    "effect_size": float("nan"), "effect_size_label": "Eta-squared"}
        h, p = stats.kruskal(*groups)
        eta2 = _kruskal_eta2(h, n, k)
        return {**base, "test": "Kruskal-Wallis", "statistic": round(h, 3),
                "p_value": round(p, 6), "effect_size": round(eta2, 4),
                "effect_size_label": "Eta-squared"}

    # ---- Numeric × Numeric → Spearman ------------------------------------
    rho, p = stats.spearmanr(pair["f"], pair["p"])
    return {**base, "test": "Spearman", "statistic": round(rho, 4),
            "p_value": round(p, 6), "effect_size": round(abs(rho), 4),
            "effect_size_label": "|rho|"}

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(data_path: Path = DATA_PATH, output_path: Path = OUTPUT_PATH) -> pd.DataFrame:
    log.info("Loading %s", data_path)
    df = pd.read_csv(data_path, low_memory=False)
    log.info("Loaded %d rows × %d columns", *df.shape)

    # Force zip_code to string so it's treated categorically
    for col in FORCE_CATEGORICAL:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else float("nan"))

    protected_cols = set(PROTECTED_ATTRIBUTES.values())

    # All columns that are not protected, not identifiers/skipped
    feature_cols = [
        c for c in df.columns
        if c not in protected_cols and c not in SKIP_COLUMNS
    ]

    # Build type map
    type_map: dict[str, str] = {}
    for col in list(feature_cols) + list(protected_cols):
        if col in df.columns:
            type_map[col] = detect_type(df[col], force_categorical=(col in FORCE_CATEGORICAL))

    log.info("Features to test: %d", len(feature_cols))
    log.info("Protected attributes: %s", list(PROTECTED_ATTRIBUTES.keys()))

    rows = []
    for prot_label, prot_col in PROTECTED_ATTRIBUTES.items():
        if prot_col not in df.columns:
            log.warning("Protected column '%s' not found — skipping.", prot_col)
            continue
        for feat_col in feature_cols:
            try:
                row = test_pair(
                    df,
                    feature_col=feat_col,
                    protected_col=prot_col,
                    feature_type=type_map.get(feat_col, "categorical"),
                    protected_type=type_map.get(prot_col, "categorical"),
                    feature_label=feat_col,
                    protected_label=prot_label,
                )
                rows.append(row)
            except Exception as exc:
                log.warning("Skipped %s vs %s: %s", feat_col, prot_label, exc)

    results = pd.DataFrame(rows)
    results = results.sort_values("effect_size", ascending=False).reset_index(drop=True)
    results.insert(0, "rank", results.index + 1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    log.info("Saved → %s", output_path)

    # ---- KL Divergence across race groups --------------------------------
    run_kl_divergence(
        df,
        group_column="race",
        output_path=output_path.parent / "kl_divergence_race.csv",
    )

    # ---- Pandas Spearman correlation matrix ------------------------------
    spearman_df = run_spearman_corr(df, protected_cols=protected_cols)
    spearman_path = output_path.parent / "spearman_corr_protected.csv"
    spearman_df.to_csv(spearman_path)
    log.info("Spearman matrix saved → %s", spearman_path)

    return results


# ---------------------------------------------------------------------------
# Pandas built-in Spearman correlation
# ---------------------------------------------------------------------------

def run_spearman_corr(
    df: pd.DataFrame,
    protected_cols: set[str],
) -> pd.DataFrame:
    """Use pandas .corr(method='spearman') to compute a full correlation matrix.

    Why Spearman over Pearson or Kendall:
    - Pearson requires normally distributed continuous variables.
      Criminal justice data is skewed and contains many categorical variables.
    - Kendall is also rank-based and handles ties better, but is O(n²) —
      too slow for 234k rows.
    - Spearman is rank-based, handles non-normal and ordinal data, and runs
      efficiently at scale. It is the correct choice here.

    Categorical columns are label-encoded (integer codes) before computing
    correlations so that pandas can include them in the matrix.

    Returns the subset of the correlation matrix — columns are protected
    attributes, rows are all other features.
    """
    analysis_cols = [
        c for c in df.columns
        if c not in SKIP_COLUMNS
    ]
    df_enc = df[analysis_cols].copy()

    # Label-encode every object/categorical column
    for col in df_enc.columns:
        if pd.api.types.is_object_dtype(df_enc[col]) or pd.api.types.is_categorical_dtype(df_enc[col]):
            df_enc[col] = df_enc[col].astype("category").cat.codes.replace(-1, float("nan"))

    log.info("Computing Spearman correlation matrix (%d columns)...", len(df_enc.columns))
    corr_matrix = df_enc.corr(method="spearman")

    # Extract only the columns for protected attributes that exist
    prot_present = [c for c in protected_cols if c in corr_matrix.columns]
    subset = corr_matrix[prot_present].drop(index=prot_present, errors="ignore")

    # Rename protected columns to their display labels
    col_rename = {v: k for k, v in PROTECTED_ATTRIBUTES.items() if v in subset.columns}
    subset = subset.rename(columns=col_rename)

    return subset.sort_values(by=list(subset.columns)[0], key=abs, ascending=False)


# ---------------------------------------------------------------------------
# KL Divergence (checklist item 5)
# ---------------------------------------------------------------------------

def kl_divergence_for_groups(
    numeric_series: pd.Series,
    group_series: pd.Series,
    group_a: str,
    group_b: str,
    n_bins: int = 30,
) -> float:
    """Compute KL divergence between two groups' distributions of a numeric feature.

    Uses histogram binning to estimate probability distributions.
    Returns KL( P_a || P_b ).

    Interpretation:
        0   = identical distributions
        larger = more different (more distributional shift between groups)

    Parameters
    ----------
    numeric_series : Continuous feature values.
    group_series   : Categorical group labels (e.g. race).
    group_a        : Label for the reference group (P).
    group_b        : Label for the comparison group (Q).
    n_bins         : Number of histogram bins.
    """
    combined = pd.DataFrame({"val": numeric_series, "grp": group_series}).dropna()
    vals_a = combined.loc[combined["grp"] == group_a, "val"].values
    vals_b = combined.loc[combined["grp"] == group_b, "val"].values

    if len(vals_a) < 5 or len(vals_b) < 5:
        return float("nan")

    global_min = min(vals_a.min(), vals_b.min())
    global_max = max(vals_a.max(), vals_b.max())
    bins = np.linspace(global_min, global_max, n_bins + 1)

    eps = 1e-10
    p, _ = np.histogram(vals_a, bins=bins)
    q, _ = np.histogram(vals_b, bins=bins)
    p = p.astype(float) + eps
    q = q.astype(float) + eps
    p /= p.sum()
    q /= q.sum()

    return float(stats.entropy(p, q))


def run_kl_divergence(
    df: pd.DataFrame,
    group_column: str = "race",
    output_path: Path = _PROJECT_ROOT / "outputs/kl_divergence_race.csv",
) -> pd.DataFrame:
    """Compare numeric feature distributions across all pairs of race groups.

    For each numeric feature, computes KL divergence between every combination
    of group pairs (e.g. Black vs White, Black vs Hispanic, etc.).
    Results are sorted by KL divergence descending so the largest distributional
    shifts appear at the top.
    """
    numeric_features = [
        col for col in df.columns
        if col not in SKIP_COLUMNS
        and col not in set(PROTECTED_ATTRIBUTES.values())
        and col != group_column
        and detect_type(df[col]) == "numeric"
    ]

    groups = df[group_column].dropna().unique().tolist()
    rows = []
    for feat in numeric_features:
        for i, ga in enumerate(groups):
            for gb in groups[i + 1:]:
                kl = kl_divergence_for_groups(df[feat], df[group_column], ga, gb)
                rows.append({
                    "feature": feat,
                    "group_a": ga,
                    "group_b": gb,
                    "kl_divergence": round(kl, 4) if not pd.isna(kl) else float("nan"),
                })

    kl_df = pd.DataFrame(rows).sort_values("kl_divergence", ascending=False).reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    kl_df.to_csv(output_path, index=False)
    log.info("KL divergence saved → %s", output_path)
    return kl_df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = run()

    print("\n=== Top 20 Associations (ranked by effect size) ===\n")
    print(
        results.head(20)[
            ["rank", "feature", "protected_attribute", "test", "effect_size", "p_value"]
        ].to_string(index=False)
    )

    spearman_path = Path("outputs/proxy_associations.csv").parent / "spearman_corr_protected.csv"
    if spearman_path.exists():
        print("\n=== Spearman Correlations with Protected Attributes ===\n")
        print(pd.read_csv(spearman_path, index_col=0).round(4).to_string())
