"""Feature engineering entry points for analysis-ready tables."""


def add_missing_indicator(frame, column_name):
    """Add a simple missingness flag for a named column."""

    frame = frame.copy()
    frame[f"{column_name}_is_missing"] = frame[column_name].isna()
    return frame