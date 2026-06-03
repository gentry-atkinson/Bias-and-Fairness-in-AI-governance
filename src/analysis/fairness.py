"""Basic fairness metric helpers."""


def rate_by_group(frame, group_column, outcome_column):
    """Compute the mean outcome rate by group."""

    return frame.groupby(group_column, dropna=False)[outcome_column].mean()