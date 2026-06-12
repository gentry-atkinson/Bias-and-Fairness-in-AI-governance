"""
correlation_analysis.py
-----------------------
Generalized pipeline that tests every non-protected feature against every
protected attribute and produces a ranked proxy variable table.

Usage (from project root)
--------------------------
    python src/correlation_analysis.py
        --data   data/interim/travis_county_pretrial_analysis_df.csv
        --output outputs/correlation_tables/proxy_variable_results.csv
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from feature_utils import (
    PROTECTED_ATTRIBUTES,
    build_feature_type_map,
    get_analysis_features,
)
from stats_tests import (
    TestResult,
    kl_divergence_for_groups,
    test_categorical_vs_categorical,
    test_numeric_vs_categorical,
    test_numeric_vs_numeric,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Single-pair dispatcher
# ---------------------------------------------------------------------------

def analyze_feature_against_protected(
    df: pd.DataFrame,
    feature: str,
    protected: str,
    feature_type_map: dict[str, str],
) -> TestResult:
    """Auto-detect types and dispatch to the correct statistical test.

    Parameters
    ----------
    df:               Analysis dataframe.
    feature:          Column name for the candidate proxy feature.
    protected:        Column name for the protected attribute.
    feature_type_map: Pre-built mapping of column → type.

    Returns
    -------
    TestResult named-tuple.
    """
    feat_type = feature_type_map.get(feature, "categorical")
    prot_type = feature_type_map.get(protected, "categorical")

    if feat_type == "categorical" and prot_type == "categorical":
        return test_categorical_vs_categorical(
            df[feature], df[protected], feature, protected
        )
    elif feat_type == "numeric" and prot_type == "categorical":
        return test_numeric_vs_categorical(
            df[feature], df[protected], feature, protected
        )
    elif feat_type == "categorical" and prot_type == "numeric":
        # Treat protected as the grouping variable by swapping
        return test_numeric_vs_categorical(
            df[protected], df[feature], protected, feature
        )._replace(feature=feature, protected_attribute=protected)
    else:
        return test_numeric_vs_numeric(
            df[feature], df[protected], feature, protected
        )


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def run_proxy_analysis(
    df: pd.DataFrame,
    protected_attributes: list[str] | None = None,
    include_age: bool = False,
) -> pd.DataFrame:
    """Run association tests for every feature × every protected attribute.

    Parameters
    ----------
    df:                   Analysis dataframe.
    protected_attributes: Columns to treat as protected (defaults to
                          ``PROTECTED_ATTRIBUTES``).
    include_age:          Whether to add ``age_at_booking`` to protected attrs.

    Returns
    -------
    DataFrame sorted by effect size (descending) with columns:
        feature, protected_attribute, test_name, effect_size,
        effect_size_label, p_value, statistic, n_observations, notes
    """
    protected = list(protected_attributes or PROTECTED_ATTRIBUTES)
    if include_age and "age_at_booking" in df.columns and "age_at_booking" not in protected:
        protected.append("age_at_booking")

    # Only keep protected columns that actually exist in the dataframe
    protected = [p for p in protected if p in df.columns]

    feature_type_map = build_feature_type_map(df)
    analysis_features = get_analysis_features(df, protected=protected)

    logger.info(
        "Protected attributes: %s", protected
    )
    logger.info(
        "Features to test: %d columns", len(analysis_features)
    )

    results: list[TestResult] = []
    for prot in protected:
        for feat in analysis_features:
            if feat == prot:
                continue
            try:
                result = analyze_feature_against_protected(
                    df, feat, prot, feature_type_map
                )
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping %s vs %s: %s", feat, prot, exc)

    result_df = pd.DataFrame(results, columns=TestResult._fields)
    result_df = result_df.sort_values("effect_size", ascending=False).reset_index(drop=True)
    result_df.insert(0, "rank", result_df.index + 1)
    return result_df


# ---------------------------------------------------------------------------
# KL Divergence table
# ---------------------------------------------------------------------------

def run_kl_divergence_analysis(
    df: pd.DataFrame,
    group_column: str = "race",
    numeric_features: list[str] | None = None,
) -> pd.DataFrame:
    """Compute KL divergence for numeric features across race groups.

    Compares each unique group pair: all combinations of
    (group_a, group_b) where group_a != group_b.

    Parameters
    ----------
    df:               Analysis dataframe.
    group_column:     Categorical column to use for grouping (default: race).
    numeric_features: List of numeric column names to analyse.

    Returns
    -------
    DataFrame with columns: feature, group_a, group_b, kl_divergence
    sorted by kl_divergence descending.
    """
    feature_type_map = build_feature_type_map(df)

    if numeric_features is None:
        numeric_features = [
            col for col, t in feature_type_map.items()
            if t == "numeric" and col != group_column
        ]

    groups = df[group_column].dropna().unique().tolist()
    rows = []

    for feat in numeric_features:
        for i, ga in enumerate(groups):
            for gb in groups[i + 1:]:
                kl = kl_divergence_for_groups(
                    df[feat], df[group_column], ga, gb
                )
                rows.append({
                    "feature": feat,
                    "group_a": ga,
                    "group_b": gb,
                    "kl_divergence": round(kl, 4) if not pd.isna(kl) else float("nan"),
                })

    kl_df = pd.DataFrame(rows)
    if not kl_df.empty:
        kl_df = kl_df.sort_values("kl_divergence", ascending=False).reset_index(drop=True)
    return kl_df


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def generate_markdown_report(
    proxy_df: pd.DataFrame,
    kl_df: pd.DataFrame,
    output_path: Path,
    top_n: int = 20,
) -> None:
    """Write a Markdown proxy variable report.

    Parameters
    ----------
    proxy_df:    Full proxy variable results dataframe.
    kl_df:       KL divergence results dataframe.
    output_path: File path to write the report.
    top_n:       Number of top associations to include in the report.
    """
    top = proxy_df.head(top_n)

    lines = [
        "# Proxy Variable Analysis Report",
        "",
        "## Methodology",
        "",
        "Association strength between each feature and each protected attribute "
        "was measured using the appropriate statistical test:",
        "",
        "| Feature type | Protected type | Test | Effect size |",
        "|---|---|---|---|",
        "| Categorical | Categorical | Chi-Square | Cramer's V |",
        "| Numeric | Categorical | Kruskal-Wallis | Eta-squared |",
        "| Numeric | Numeric | Spearman | \\|rho\\| |",
        "",
        "Effect sizes range from 0 (no association) to 1 (perfect association).",
        "",
        "---",
        "",
        "## Strongest Associations (Top " + str(top_n) + ")",
        "",
        top.to_markdown(index=False),
        "",
        "---",
        "",
        "## KL Divergence — Distribution Shift Across Race Groups",
        "",
        "KL divergence measures how different the distribution of a numeric "
        "feature is between two racial groups.  "
        "0 = identical distributions; larger = more different.",
        "",
    ]

    if not kl_df.empty:
        lines.append(kl_df.head(top_n).to_markdown(index=False))
    else:
        lines.append("_No numeric features available for KL divergence analysis._")

    lines += [
        "",
        "---",
        "",
        "## Potential Proxy Variables",
        "",
        "Features with effect size ≥ 0.10 and p-value < 0.05 are flagged as "
        "potential proxy variables:",
        "",
    ]

    flagged = proxy_df[
        (proxy_df["effect_size"] >= 0.10) & (proxy_df["p_value"] < 0.05)
    ][["rank", "feature", "protected_attribute", "test_name", "effect_size", "p_value"]]

    if not flagged.empty:
        lines.append(flagged.to_markdown(index=False))
    else:
        lines.append("_No features met the proxy flagging threshold._")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Report written → %s", output_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run proxy variable analysis on the Travis County pretrial dataset."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/interim/travis_county_pretrial_analysis_df.csv"),
        help="Path to the analysis CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/correlation_tables"),
        help="Directory for output CSV and Markdown files.",
    )
    parser.add_argument(
        "--include-age",
        action="store_true",
        default=False,
        help="Include age_at_booking as a protected attribute.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    logger.info("Loading data from %s", args.data)
    df = pd.read_csv(args.data, low_memory=False)
    logger.info("Loaded %d rows × %d columns", *df.shape)

    # ---- Proxy variable association table --------------------------------
    proxy_df = run_proxy_analysis(df, include_age=args.include_age)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    proxy_csv = args.output_dir / "proxy_variable_results.csv"
    proxy_df.to_csv(proxy_csv, index=False)
    logger.info("Results saved → %s", proxy_csv)

    # ---- KL divergence table ---------------------------------------------
    kl_df = run_kl_divergence_analysis(df, group_column="race")
    if not kl_df.empty:
        kl_csv = args.output_dir / "kl_divergence_race.csv"
        kl_df.to_csv(kl_csv, index=False)
        logger.info("KL divergence saved → %s", kl_csv)

    # ---- Markdown report -------------------------------------------------
    report_path = args.output_dir.parent / "proxy_variable_report.md"
    generate_markdown_report(proxy_df, kl_df, report_path)

    # ---- Console summary -------------------------------------------------
    print("\n=== Top 15 Proxy Variable Candidates ===\n")
    print(
        proxy_df.head(15)[
            ["rank", "feature", "protected_attribute", "test_name", "effect_size", "p_value"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
