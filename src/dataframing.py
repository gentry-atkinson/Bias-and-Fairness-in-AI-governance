"""
dataframing.py
--------------
Builds and saves the two analysis-ready dataframes for the Travis County
criminal justice dataset:

  1. Pretrial-level dataframe (one row per PA_MAST_NO)
     → data/interim/travis_county_pretrial_analysis_df.csv

  2. Booking-level dataframe (one row per BookingNumber)
     → data/interim/travis_county_booking_analysis_df.csv

Run from the project root:
    python src/dataframing.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd

from data_loading import PROJECT_ROOT, RAW_DATA_DIR

INTERIM_DIR = PROJECT_ROOT / "data" / "interim"

# ---------------------------------------------------------------------------
# Column selections
# ---------------------------------------------------------------------------

PRETRIAL_DEFENDANT_COLS = [
    "PA_MAST_NO", "PA_BKG_NO", "BJ_BK_DATE", "PA_PTS_RISK", "PB_MNI",
    "PB_SEX", "PB_RAC", "PB_DOB", "PB_CITY", "PB_ST", "PB_ZIP", "PC_ETHNIC",
]

PRETRIAL_CHARGE_COLS = [
    "PA_MAST_NO", "PK_BKG_NO", "BJ_BK_DATE", "PK_BND_GRT", "PK_BND_AMT",
    "PK_BND_TYP", "PK_BND_STS", "PK_CHARGE", "PK_CHG_LIT", "PK_LVL", "JUDGE",
]

BOOKING_COLS = [
    "bookingID", "BookingNumber", "mni", "PersonID", "bookingdate", "ReleaseDate",
    "ArrestingAgencyID", "HighestBookingCharge", "HighestBookingCount", "BookingChargeID",
    "ChargeCode", "ChargeDescription", "ChargeClassID", "EligibleforBail", "BailTypeID",
    "BailAmount", "ReleaseReasonID",
]

PERSON_COLS = [
    "PersonID", "MNI", "DateofBirth", "GenderID", "RaceID", "EthnicityID", "CitizenshipID",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_blank_strings(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df[columns].copy()
    for col in columns:
        if out[col].dtype == object:
            out[col] = out[col].replace(r"^\s*$", np.nan, regex=True)
    return out


def _normalize_booking_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64").astype("string")


# ---------------------------------------------------------------------------
# Pretrial-level dataframe
# ---------------------------------------------------------------------------

def build_pretrial_df() -> pd.DataFrame:
    """One row per pretrial record (PA_MAST_NO)."""
    defendants = pd.read_excel(
        RAW_DATA_DIR / "PreTrial Defendants.xlsx",
        sheet_name="Sheet1",
        usecols=PRETRIAL_DEFENDANT_COLS,
    )
    charges = pd.read_csv(
        RAW_DATA_DIR / "PreTrial Charge-Interview.csv",
        usecols=PRETRIAL_CHARGE_COLS,
        low_memory=False,
    )

    defendants_unique = (
        _clean_blank_strings(defendants, PRETRIAL_DEFENDANT_COLS)
        .sort_values("PA_MAST_NO")
        .groupby("PA_MAST_NO", as_index=False)
        .first()
    )
    charges_unique = (
        _clean_blank_strings(charges, PRETRIAL_CHARGE_COLS)
        .sort_values("PA_MAST_NO")
        .groupby("PA_MAST_NO", as_index=False)
        .first()
    )

    df = defendants_unique.merge(charges_unique, on="PA_MAST_NO", how="left", suffixes=("_def", "_chg"))

    df["booking_date"] = pd.to_datetime(
        df["BJ_BK_DATE_def"].combine_first(df["BJ_BK_DATE_chg"]), errors="coerce"
    )
    df["dob"] = pd.to_datetime(df["PB_DOB"], errors="coerce")
    df["age_at_booking"] = ((df["booking_date"] - df["dob"]).dt.days / 365.25).round(1)
    df.loc[(df["age_at_booking"] < 0) | (df["age_at_booking"] > 100), "age_at_booking"] = np.nan
    df["age_group"] = pd.cut(
        df["age_at_booking"],
        bins=[0, 24, 34, 44, 54, 64, 100],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        include_lowest=True,
    ).astype("string")

    df["PA_PTS_RISK_num"] = pd.to_numeric(df["PA_PTS_RISK"], errors="coerce")
    df["PK_BND_AMT_num"] = pd.to_numeric(df["PK_BND_AMT"], errors="coerce")
    df["bond_granted_flag"] = df["PK_BND_GRT"].astype(str).str.upper().map({"Y": 1, "N": 0})

    required = [
        "PA_MAST_NO", "booking_date", "PB_SEX", "PB_RAC", "PC_ETHNIC", "PB_ZIP",
        "age_at_booking", "age_group", "PA_PTS_RISK_num", "PK_BND_GRT", "bond_granted_flag",
        "PK_BND_AMT_num", "PK_BND_TYP", "PK_BND_STS", "PK_CHARGE", "PK_LVL", "JUDGE",
    ]

    analysis_ready = (
        df[required]
        .copy()
        .rename(columns={
            "PA_MAST_NO": "pretrial_id",
            "PB_SEX": "sex",
            "PB_RAC": "race",
            "PC_ETHNIC": "ethnicity",
            "PB_ZIP": "zip_code",
            "PA_PTS_RISK_num": "risk_score",
            "PK_BND_GRT": "bond_granted_raw",
            "PK_BND_AMT_num": "bond_amount",
            "PK_BND_TYP": "bond_type",
            "PK_BND_STS": "bond_status",
            "PK_CHARGE": "charge_code",
            "PK_LVL": "charge_level",
            "JUDGE": "judge",
        })
    )
    analysis_ready["booking_date"] = pd.to_datetime(analysis_ready["booking_date"], errors="coerce")
    analysis_ready["age_group"] = analysis_ready["age_group"].astype("string")

    return analysis_ready, df   # also return the full joined df for booking use


# ---------------------------------------------------------------------------
# Booking-level dataframe
# ---------------------------------------------------------------------------

def build_booking_df(pretrial_joined_df: pd.DataFrame) -> pd.DataFrame:
    """One row per BookingNumber, merged with person demographics and pretrial summary."""
    booking_2010 = pd.read_csv(RAW_DATA_DIR / "Booking2010_2012v3.csv", usecols=BOOKING_COLS, low_memory=False)
    booking_2013 = pd.read_csv(RAW_DATA_DIR / "Booking2013_2016v3.csv", usecols=BOOKING_COLS, low_memory=False)
    all_bookings = pd.concat([booking_2010, booking_2013], ignore_index=True)

    person_df = pd.read_excel(
        RAW_DATA_DIR / "PersonData.xlsx",
        sheet_name="PersonData",
        usecols=PERSON_COLS,
    ).rename(columns={
        "PersonID": "person_id", "MNI": "person_mni", "DateofBirth": "date_of_birth",
        "GenderID": "gender_id", "RaceID": "race_id", "EthnicityID": "ethnicity_id",
        "CitizenshipID": "citizenship_id",
    })

    all_bookings["booking_number_norm"] = _normalize_booking_number(all_bookings["BookingNumber"])
    all_bookings["bookingdate"] = pd.to_datetime(all_bookings["bookingdate"], errors="coerce")
    all_bookings["ReleaseDate"] = pd.to_datetime(all_bookings["ReleaseDate"], errors="coerce")

    booking_base = (
        all_bookings.sort_values(["booking_number_norm", "bookingdate"])
        .groupby("booking_number_norm", as_index=False)
        .agg(
            booking_row_count=("bookingID", "size"),
            booking_id=("bookingID", "first"),
            booking_number=("BookingNumber", "first"),
            person_id=("PersonID", "first"),
            mni=("mni", "first"),
            booking_date=("bookingdate", "first"),
            release_date=("ReleaseDate", "first"),
            arresting_agency_id=("ArrestingAgencyID", "first"),
            highest_booking_charge=("HighestBookingCharge", "first"),
            highest_booking_count=("HighestBookingCount", "max"),
            charge_row_count=("BookingChargeID", "count"),
            unique_charge_codes=("ChargeCode", "nunique"),
            primary_charge_code=("ChargeCode", "first"),
            primary_charge_description=("ChargeDescription", "first"),
            primary_charge_class_id=("ChargeClassID", "first"),
            eligible_for_bail=("EligibleforBail", "max"),
            bail_type_id=("BailTypeID", "first"),
            bail_amount_max=("BailAmount", "max"),
            release_reason_id=("ReleaseReasonID", "first"),
        )
    )

    booking_base["person_id"] = pd.to_numeric(booking_base["person_id"], errors="coerce")
    person_df["person_id"] = pd.to_numeric(person_df["person_id"], errors="coerce")

    # Pretrial summary per booking
    pt = pretrial_joined_df.copy()
    pt["booking_number_norm"] = _normalize_booking_number(
        pt["PA_BKG_NO"].combine_first(pt["PK_BKG_NO"])
    )
    pretrial_summary = (
        pt.dropna(subset=["booking_number_norm"])
        .groupby("booking_number_norm", as_index=False)
        .agg(
            linked_pretrial_records=("PA_MAST_NO", "size"),
            mean_pretrial_risk_score=("PA_PTS_RISK_num", "mean"),
            pretrial_bond_grant_rate=("bond_granted_flag", "mean"),
        )
    )

    result = booking_base.merge(person_df, on="person_id", how="left")
    result = result.merge(pretrial_summary, on="booking_number_norm", how="left")
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    print("Building pretrial-level dataframe...")
    pretrial_df, pretrial_joined = build_pretrial_df()
    pretrial_path = INTERIM_DIR / "travis_county_pretrial_analysis_df.csv"
    pretrial_df.to_csv(pretrial_path, index=False)
    print(f"  Saved {pretrial_df.shape[0]:,} rows × {pretrial_df.shape[1]} cols → {pretrial_path}")

    print("Building booking-level dataframe...")
    booking_df = build_booking_df(pretrial_joined)
    booking_path = INTERIM_DIR / "travis_county_booking_analysis_df.csv"
    booking_df.to_csv(booking_path, index=False)
    print(f"  Saved {booking_df.shape[0]:,} rows × {booking_df.shape[1]} cols → {booking_path}")
