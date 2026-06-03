"""Validation helpers for source and derived tables."""


def require_columns(frame, required_columns):
    """Raise an error when expected columns are missing."""

    missing_columns = sorted(set(required_columns) - set(frame.columns))
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_list}")