import pandas as pd

RACE_MAP = {
    "W": "White",
    "B": "Black",
    "A": "Asian",
    "I": "American Indian / Alaska Native",
    "U": "Unknown"
}

def clean_race_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace abbreviated race codes with descriptive labels.
    """

    df = df.copy()

    df["race"] = (
        df["race"]
        .replace(RACE_MAP)
        .fillna("Unknown")
    )

    return df