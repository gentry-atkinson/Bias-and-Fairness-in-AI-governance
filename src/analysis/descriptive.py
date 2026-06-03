"""Descriptive summary helpers."""


def missingness_summary(frame):
    """Return a simple missingness summary by column."""

    return (
        frame.isna()
        .mean()
        .sort_values(ascending=False)
        .rename("missing_rate")
        .to_frame()
    )