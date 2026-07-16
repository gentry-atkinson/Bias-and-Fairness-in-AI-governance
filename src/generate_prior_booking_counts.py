from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BOOKINGS_2010_2012 = PROJECT_ROOT / "data/raw/Booking2010_2012v3.csv"
BOOKINGS_2013_2016 = PROJECT_ROOT / "data/raw/Booking2013_2016v3.csv"

OUTPUT = (
    PROJECT_ROOT
    / "data/interim/prior_booking_counts_by_defendant.csv"
)


def main():

    df_2010_2012 = pd.read_csv(
        BOOKINGS_2010_2012,
        low_memory=False,
    )

    df_2013_2016 = pd.read_csv(
        BOOKINGS_2013_2016,
        low_memory=False,
    )

    df = pd.concat(
        [df_2010_2012, df_2013_2016],
        ignore_index=True,
    )

    df = (
        df[
            [
                "mni",
                "BookingNumber",
                "bookingdate",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    df["bookingdate"] = pd.to_datetime(df["bookingdate"])

    df = df.sort_values(
        ["mni", "bookingdate"]
    )

    df["prior_booking_count"] = (
        df.groupby("mni").cumcount()
    )

    df["three_or_more_prior_bookings"] = (
        df["prior_booking_count"] >= 3
    )

    summary = (
        df.groupby("mni", as_index=False)
        .agg(
            prior_booking_count=(
                "prior_booking_count",
                "max",
            ),
            three_or_more_prior_bookings=(
                "three_or_more_prior_bookings",
                "max",
            ),
        )
    )

    summary = summary.rename(columns={"mni": "person_mni"})

    summary.to_csv(
        OUTPUT,
        index=False,
    )

    print(summary.head())
    print(f"\nSaved to: {OUTPUT}")


if __name__ == "__main__":
    main()