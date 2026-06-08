"""Cleaning and linkage entry points."""


def standardize_column_names(frame):
    """Normalize a tabular object's column names to lowercase snake case."""

    frame = frame.copy()
    frame.columns = (
        frame.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    return frame