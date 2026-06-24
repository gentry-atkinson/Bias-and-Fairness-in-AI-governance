"""
dataloader.py

Central dataloader for the Travis County pretrial risk assessment project.

What this file is doing:
1. Load raw Travis County files.
2. Build an analysis-ready pretrial dataframe.
3. Build a complete-defendants dataframe for fairness analysis and regression modeling.
4. Save basic completeness reports so missingness is visible.

Primary outputs:
- data/interim/travis_county_pretrial_analysis_df.csv
- data/interim/travis_county_complete_defendants_df.csv
- outputs/completeness_report.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE_REGISTRY = {
    # Core pretrial files
    "pretrial_defendants": {
        "filename": "PreTrial Defendants.xlsx",
        "type": "excel",
        "status": "used",
        "description": "Defendant demographics, booking date, risk score, MNI, ZIP/city/state",
    },
    "pretrial_charge_interview": {
        "filename": "PreTrial Charge-Interview.csv",
        "type": "csv",
        "status": "used",
        "description": "Interview, recommendation, bond, charge, and judge variables",
    },
    "pretrial_tcud_odar": {
        "filename": "PreTrial TCUD-ODAR Events.xlsx",
        "type": "excel",
        "status": "used",
        "description": "TCUD/ODAR score and event variables",
    },

    # Pretrial bridge/outcome support files
    "pretrial_disposition_reason": {
        "filename": "PreTrial Disposition Reason.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Disposition reason file; not yet merged",
    },
    "pretrial_to_booking": {
        "filename": "PreTrial to Booking Info.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Bridge between pretrial and booking records",
    },

    # Booking and court-system files
    "booking_2010_2012": {
        "filename": "Booking2010_2012v3.csv",
        "type": "csv",
        "status": "pending",
        "description": "Booking records before 2013",
    },
    "booking_2013_2016": {
        "filename": "Booking2013_2016v3.csv",
        "type": "csv",
        "status": "pending",
        "description": "Booking records after 2013",
    },
    "case_data": {
        "filename": "CaseData_v2.csv",
        "type": "csv",
        "status": "pending",
        "description": "Court case data; likely needed for outcomes",
    },
    "person_data": {
        "filename": "PersonData.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Person-level identifiers and demographics",
    },

    # Outcome/event files
    "events": {
        "filename": "Events.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Event records; may be needed for pretrial crime or court events",
    },
    "mental_health_events": {
        "filename": "Mental Health Flag Events.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Mental health flag event data",
    },
    "revocation": {
        "filename": "revocationV2.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Revocation outcome data",
    },
    "sentencing_pre_2013": {
        "filename": "SentencingDataPre2013.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Sentencing outcomes before 2013",
    },
    "sentencing_post_2013": {
        "filename": "SentencingDataPost2013.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Sentencing outcomes after 2013",
    },

    # Lookup/bridge files
    "case_booking_charge_bridge": {
        "filename": "CaseIDtoBookingChargeIDUPDATED.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Bridge between case IDs and booking charge IDs",
    },
    "charge_code_description": {
        "filename": "chargecode_description.dta",
        "type": "stata",
        "status": "pending",
        "description": "Charge code lookup/description file",
    },
    "violent_charge_codes": {
        "filename": "171017_CCHCodes_Violent marked by Slayton.xlsx",
        "type": "excel",
        "status": "pending",
        "description": "Charge code violence classification lookup",
    },
}


# ---------------------------------------------------------------------
# Raw file names
# ---------------------------------------------------------------------

PRETRIAL_DEFENDANTS_FILE = "PreTrial Defendants.xlsx"
PRETRIAL_CHARGE_INTERVIEW_FILE = "PreTrial Charge-Interview.csv"
PRETRIAL_TCUD_FILE = "PreTrial TCUD-ODAR Events.xlsx"
PRETRIAL_DISPOSITION_FILE = "PreTrial Disposition Reason.xlsx"
PRETRIAL_TO_BOOKING_FILE = "PreTrial to Booking Info.xlsx"

BOOKING_2010_2012_FILE = "Booking2010_2012v3.csv"
BOOKING_2013_2016_FILE = "Booking2013_2016v3.csv"
CASE_DATA_FILE = "CaseData_v2.csv"
PERSON_DATA_FILE = "PersonData.xlsx"


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------


def read_csv_file(filename: str, **kwargs) -> pd.DataFrame:
    """Read a CSV file from data/raw."""
    path = RAW_DATA_DIR / filename
    print(f"Loading CSV: {path}")
    return pd.read_csv(path, low_memory=False, **kwargs)


def read_excel_file(filename: str, sheet_name=0, **kwargs) -> pd.DataFrame:
    """Read an Excel file from data/raw."""
    path = RAW_DATA_DIR / filename
    print(f"Loading Excel: {path}")
    return pd.read_excel(path, sheet_name=sheet_name, **kwargs)


def clean_blank_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Replace empty strings and whitespace-only strings with NaN."""
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == "object" or str(df[col].dtype) == "string":
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    return df


def normalize_zip(series: pd.Series) -> pd.Series:
    """
    Convert ZIP codes to clean categorical strings.

    ZIP codes should not be treated as numeric values.
    """
    return (
        series
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )


def safe_datetime(series: pd.Series) -> pd.Series:
    """Convert a column to datetime, coercing errors to NaT."""
    return pd.to_datetime(series, errors="coerce")


def safe_numeric(series: pd.Series) -> pd.Series:
    """Convert a column to numeric, coercing errors to NaN."""
    return pd.to_numeric(series, errors="coerce")


def first_nonnull(series: pd.Series):
    """Return the first non-null value from a group."""
    nonnull = series.dropna()
    if len(nonnull) == 0:
        return np.nan
    return nonnull.iloc[0]


def existing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return columns that actually exist in a dataframe."""
    return [col for col in columns if col in df.columns]


# ---------------------------------------------------------------------
# Load raw datasets
# ---------------------------------------------------------------------

def load_pretrial_defendants() -> pd.DataFrame:
    """Load defendant-level pretrial data."""
    df = read_excel_file(PRETRIAL_DEFENDANTS_FILE)
    df = clean_blank_strings(df)
    return df


def load_pretrial_charge_interview() -> pd.DataFrame:
    """Load pretrial charge/interview data."""
    df = read_csv_file(PRETRIAL_CHARGE_INTERVIEW_FILE)
    df = clean_blank_strings(df)
    return df


def load_tcud_events() -> pd.DataFrame:
    """Load TCUD/ODAR event data."""
    df = read_excel_file(PRETRIAL_TCUD_FILE)
    df = clean_blank_strings(df)
    return df


def load_disposition_reason() -> pd.DataFrame:
    """Load pretrial disposition reason data."""
    df = read_excel_file(PRETRIAL_DISPOSITION_FILE)
    df = clean_blank_strings(df)
    return df


def load_pretrial_to_booking() -> pd.DataFrame:
    """Load pretrial-to-booking bridge file."""
    df = read_excel_file(PRETRIAL_TO_BOOKING_FILE)
    df = clean_blank_strings(df)
    return df


# ---------------------------------------------------------------------
# Build pretrial dataframe
# ---------------------------------------------------------------------

def build_pretrial_records_df() -> pd.DataFrame:
    """
    Build one row per pretrial record using PA_MAST_NO.

    This dataframe is intentionally broad. It keeps demographics,
    risk scores, interview variables, recommendations, charge variables,
    bond variables, and judge information.
    """

    defendants = load_pretrial_defendants()
    charges = load_pretrial_charge_interview()
    tcud = load_tcud_events()

    # -------------------------------------------------------------
    # Standardize defendant-level fields
    # -------------------------------------------------------------

    if "BJ_BK_DATE" in defendants.columns:
        defendants["booking_date"] = safe_datetime(defendants["BJ_BK_DATE"])
    else:
        defendants["booking_date"] = pd.NaT

    if "PB_DOB" in defendants.columns:
        defendants["date_of_birth"] = safe_datetime(defendants["PB_DOB"])
    else:
        defendants["date_of_birth"] = pd.NaT

    defendants["age_at_booking"] = (
        (defendants["booking_date"] - defendants["date_of_birth"])
        .dt.days
        .div(365.25)
    )

    if "PA_PTS_RISK" in defendants.columns:
        defendants["risk_score"] = safe_numeric(defendants["PA_PTS_RISK"])

    if "PB_ZIP" in defendants.columns:
        defendants["zip_code"] = normalize_zip(defendants["PB_ZIP"])

    defendant_keep = existing_columns(
        defendants,
        [
            "PA_MAST_NO",
            "PA_BKG_NO",
            "PB_MNI",
            "booking_date",
            "PB_SEX",
            "PB_RAC",
            "PC_ETHNIC",
            "PB_CITY",
            "PB_ST",
            "zip_code",
            "age_at_booking",
            "risk_score",
        ],
    )

    print("Deduplicating defendant records...")

    defendants_unique = (
        defendants[defendant_keep]
        .sort_values("PA_MAST_NO")
        .drop_duplicates(subset=["PA_MAST_NO"], keep="first")
        .copy()
    )

    print(f"Defendant records: {len(defendants_unique):,}")

    # -------------------------------------------------------------
    # Charge/interview/recommendation/bond fields
    # -------------------------------------------------------------

    if "PK_BND_AMT" in charges.columns:
        charges["bond_amount"] = safe_numeric(charges["PK_BND_AMT"])

    charge_keep = existing_columns(
        charges,
        [
            "PA_MAST_NO",
            "PK_BKG_NO",
            "BJ_BK_DATE",

            # interview / recommendation fields
            "INT_OFF",
            "OFF_REC",
            "PK_ATY_REC",
            "PK_ATY_BND",
            "PK_BND_REC",

            # bond fields
            "PK_BND_GRT",
            "PK_BND_TYP",
            "PK_BND_STS",

            # charge fields
            "PK_CHARGE",
            "PK_CHG_LIT",
            "PK_LVL",

            # judge
            "JUDGE",
        ],
    )

    print("Deduplicating charge/interview records...")

    charges_unique = (
        charges[charge_keep]
        .sort_values("PA_MAST_NO")
        .drop_duplicates(subset=["PA_MAST_NO"], keep="first")
        .copy()
    )

    # Keep the maximum bond amount separately, because one pretrial record
    # may have multiple charge rows with different bond amounts.
    if "bond_amount" in charges.columns:
        bond_amount_max = (
            charges
            .groupby("PA_MAST_NO", as_index=False)["bond_amount"]
            .max()
            .rename(columns={"bond_amount": "bond_amount_max"})
        )

        charges_unique = charges_unique.merge(
            bond_amount_max,
            on="PA_MAST_NO",
            how="left",
        )

    print(f"Charge/interview records: {len(charges_unique):,}")

    charge_counts = (
        charges
        .groupby("PA_MAST_NO")
        .agg(
            pretrial_charge_rows=("PA_MAST_NO", "size"),
            unique_pretrial_charges=("PK_CHARGE", "nunique")
            if "PK_CHARGE" in charges.columns
            else ("PA_MAST_NO", "size"),
        )
        .reset_index()
    )

    charges_unique = charges_unique.merge(
        charge_counts,
        on="PA_MAST_NO",
        how="left",
    )

    # -------------------------------------------------------------
    # TCUD/ODAR events
    # -------------------------------------------------------------

    tcud_keep = existing_columns(
        tcud,
        [
            "PA_MAST_NO",
            "PI_SCORE",
            "PI_EVENT",
            "PI_EVT_DISP",
        ],
    )

    if "PI_SCORE" in tcud.columns:
        tcud["PI_SCORE"] = safe_numeric(tcud["PI_SCORE"])

    if len(tcud_keep) > 1: ###
        
        print("Deduplicating TCUD/ODAR records...")

        tcud_unique = (
            tcud[tcud_keep]
            .sort_values("PA_MAST_NO")
            .drop_duplicates(subset=["PA_MAST_NO"], keep="first")
            .copy()
        )

        if "PI_SCORE" in tcud.columns:
            tcud_score_max = (
                tcud
                .groupby("PA_MAST_NO", as_index=False)["PI_SCORE"]
                .max()
                .rename(columns={"PI_SCORE": "PI_SCORE_MAX"})
            )

            tcud_unique = tcud_unique.merge(
                tcud_score_max,
                on="PA_MAST_NO",
                how="left",
            )

        print(f"TCUD/ODAR records: {len(tcud_unique):,}")
        
        ###


        tcud_counts = (
            tcud
            .groupby("PA_MAST_NO")
            .size()
            .reset_index(name="tcud_event_count")
        )

        tcud_unique = tcud_unique.merge(
            tcud_counts,
            on="PA_MAST_NO",
            how="left",
        )
    else:
        tcud_unique = pd.DataFrame(columns=["PA_MAST_NO"])

    # -------------------------------------------------------------
    # Merge files
    # -------------------------------------------------------------

    df = defendants_unique.merge(
        charges_unique,
        on="PA_MAST_NO",
        how="left",
    )

    df = df.merge(
        tcud_unique,
        on="PA_MAST_NO",
        how="left",
    )

    # -------------------------------------------------------------
    # Derived variables
    # -------------------------------------------------------------

    if "PK_BND_GRT" in df.columns:
        df["bond_granted_flag"] = (
            df["PK_BND_GRT"]
            .astype("string")
            .str.upper()
            .isin(["Y", "YES", "1", "TRUE"])
        )

    df["age_group"] = pd.cut(
        df["age_at_booking"],
        bins=[0, 25, 35, 50, 120],
        labels=["18-25", "26-35", "36-50", "50+"],
    )

    # -------------------------------------------------------------
    # Rename columns to analysis names
    # -------------------------------------------------------------

    df = df.rename(
        columns={
            "PA_MAST_NO": "pretrial_id",
            "PA_BKG_NO": "defendant_booking_id",
            "PB_MNI": "person_mni",

            "PB_SEX": "sex",
            "PB_RAC": "race",
            "PC_ETHNIC": "ethnicity",
            "PB_CITY": "city",
            "PB_ST": "state",

            "INT_OFF": "interview_officer",
            "OFF_REC": "officer_recommendation",
            "PK_ATY_REC": "attorney_recommendation",
            "PK_ATY_BND": "attorney_bond",
            "PK_BND_REC": "bond_recommendation",

            "PK_BND_GRT": "bond_granted_raw",
            "PK_BND_TYP": "bond_type",
            "PK_BND_STS": "bond_status",
            "bond_amount_max": "bond_amount",

            "PK_CHARGE": "charge_code",
            "PK_CHG_LIT": "charge_description",
            "PK_LVL": "charge_level",

            "JUDGE": "judge",

            "PI_SCORE": "tcud_score",
            "PI_EVENT": "tcud_event",
            "PI_EVT_DISP": "tcud_event_disposition",
            "PI_SCORE_MAX": "tcud_score_max"
        }
    )

    return df


# ---------------------------------------------------------------------
# Build complete defendants dataframe
# ---------------------------------------------------------------------

def build_complete_defendants_df(
    df: pd.DataFrame,
    require_outcome: bool = False,
) -> pd.DataFrame:
    """
    Build the current complete-defendants dataset.

    Current definition:
    A complete defendant has the minimum fields needed for
    risk-score fairness analysis:

    - pretrial_id
    - race
    - sex
    - age_at_booking
    - risk_score
    - booking_date

    If require_outcome=True, this function also requires
    bond_granted_flag as the currently available outcome/decision.
    """

    required_cols = [
        "pretrial_id",
        "race",
        "sex",
        "age_at_booking",
        "risk_score",
        "booking_date",
    ]

    if require_outcome and "bond_granted_flag" in df.columns:
        required_cols.append("bond_granted_flag")

    available_required_cols = existing_columns(df, required_cols)

    complete_df = df.dropna(
        subset=available_required_cols
    ).copy()

    complete_df["has_complete_core_fields"] = True

    return complete_df


# ---------------------------------------------------------------------
# Completeness report
# ---------------------------------------------------------------------

def build_completeness_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create column-level missingness report.
    """

    report = pd.DataFrame(
        {
            "column": df.columns,
            "non_missing_count": df.notna().sum().values,
            "missing_count": df.isna().sum().values,
            "missing_rate": df.isna().mean().values,
            "dtype": [str(df[col].dtype) for col in df.columns],
        }
    )

    report["missing_rate"] = report["missing_rate"].round(4)

    return report.sort_values(
        by="missing_rate",
        ascending=False,
    )


def build_key_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize major identifiers in the analysis dataframe.
    """

    possible_keys = [
        "pretrial_id",
        "person_mni",
        "defendant_booking_id",
    ]

    rows = []

    for key in possible_keys:
        if key in df.columns:
            rows.append(
                {
                    "key": key,
                    "non_missing": df[key].notna().sum(),
                    "unique_values": df[key].nunique(dropna=True),
                    "duplicate_rows": df[key].duplicated().sum(),
                }
            )

    return pd.DataFrame(rows)


def build_raw_file_inventory() -> pd.DataFrame:
    """
    Create an inventory of all raw files available to the project.
    This documents which files are currently used and which are pending.
    """

    rows = []

    for dataset_name, info in RAW_FILE_REGISTRY.items():
        path = RAW_DATA_DIR / info["filename"]

        rows.append(
            {
                "dataset_name": dataset_name,
                "filename": info["filename"],
                "file_type": info["type"],
                "status": info["status"],
                "exists": path.exists(),
                "description": info["description"],
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Run full build
# ---------------------------------------------------------------------

def run():
    
    print("\nSaving raw file inventory...")

    inventory = build_raw_file_inventory()
    inventory.to_csv(
        OUTPUT_DIR / "raw_file_inventory.csv",
        index=False,
    )
    print("Saved outputs/raw_file_inventory.csv")
    
    
    print("\nBuilding pretrial analysis dataframe...")

    pretrial_df = build_pretrial_records_df()

    pretrial_path = (
        INTERIM_DATA_DIR
        / "travis_county_pretrial_analysis_df.csv"
    )

    pretrial_df.to_csv(pretrial_path, index=False)

    print(
        f"Saved pretrial dataframe: {pretrial_path}"
    )

    print(
        f"Rows: {len(pretrial_df):,} | Columns: {len(pretrial_df.columns):,}"
    )

    print("\nBuilding complete defendants dataframe...")

    complete_df = build_complete_defendants_df(
        pretrial_df,
        require_outcome=False,
    )

    complete_path = (
        INTERIM_DATA_DIR
        / "travis_county_complete_defendants_df.csv"
    )

    complete_df.to_csv(complete_path, index=False)

    print(
        f"Saved complete defendants dataframe: {complete_path}"
    )

    print(
        f"Rows: {len(complete_df):,} | Columns: {len(complete_df.columns):,}"
    )

    print("\nSaving completeness report...")

    completeness_report = build_completeness_report(pretrial_df)

    completeness_report.to_csv(
        OUTPUT_DIR / "completeness_report.csv",
        index=False,
    )

    print("Saved outputs/completeness_report.csv")

    print("\nSaving key summary...")

    key_summary = build_key_summary(pretrial_df)

    key_summary.to_csv(
        OUTPUT_DIR / "key_summary.csv",
        index=False,
    )

    print("Saved outputs/key_summary.csv")
    

    return pretrial_df, complete_df


if __name__ == "__main__":
    pretrial_df, complete_df = run()