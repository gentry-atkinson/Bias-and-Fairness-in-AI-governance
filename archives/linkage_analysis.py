"""
analysis.py
-----------
Linkage and entity-relationship analysis for the Travis County dataset.

Measures key overlap across join keys to verify which fields can
reliably connect persons, bookings, charges, cases, and pretrial records.

Run from the project root:
    python src/analysis.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from dataloader import PROJECT_ROOT, RAW_DATA_DIR

OUTPUT_DIR = PROJECT_ROOT / "reports" / "tables"

# ---------------------------------------------------------------------------
# Unique-value extractors
# ---------------------------------------------------------------------------

def unique_csv(file_name: str, column: str, chunk_size: int = 100_000) -> set[str]:
    """Return the set of non-null, stripped string values for *column* in a CSV."""
    values: set[str] = set()
    for chunk in pd.read_csv(
        RAW_DATA_DIR / file_name,
        usecols=[column],
        dtype={column: "string"},
        chunksize=chunk_size,
        low_memory=False,
    ):
        s = chunk[column].dropna().astype("string").str.strip()
        values.update(s[s != ""].tolist())
    return values


def unique_excel(file_name: str, sheet_name: str, column: str) -> set[str]:
    """Return the set of non-null, stripped string values for *column* in an Excel sheet."""
    df = pd.read_excel(
        RAW_DATA_DIR / file_name,
        sheet_name=sheet_name,
        usecols=[column],
        dtype={column: "string"},
    )
    s = df[column].dropna().astype("string").str.strip()
    return set(s[s != ""].tolist())


# ---------------------------------------------------------------------------
# Overlap summariser
# ---------------------------------------------------------------------------

def overlap_row(
    group: str,
    left_label: str,
    left: set[str],
    right_label: str,
    right: set[str],
) -> dict:
    shared = left & right
    return {
        "relationship_group": group,
        "left": left_label,
        "right": right_label,
        "left_unique": len(left),
        "right_unique": len(right),
        "shared_unique": len(shared),
        "left_overlap_pct": round(len(shared) / len(left) * 100, 2) if left else 0.0,
        "right_overlap_pct": round(len(shared) / len(right) * 100, 2) if right else 0.0,
    }


# ---------------------------------------------------------------------------
# Cardinality helpers
# ---------------------------------------------------------------------------

def _mean_rows_per_key_csv(file_name: str, key_col: str) -> float:
    df = pd.read_csv(RAW_DATA_DIR / file_name, usecols=[key_col], dtype="string", low_memory=False)
    return round(float(df.groupby(key_col).size().mean()), 2)


def _mean_rows_per_key_excel(file_name: str, sheet: str, key_col: str) -> float:
    df = pd.read_excel(RAW_DATA_DIR / file_name, sheet_name=sheet, usecols=[key_col], dtype="string")
    return round(float(df.groupby(key_col).size().mean()), 2)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_linkage_analysis() -> dict[str, pd.DataFrame]:
    """Compute overlap and cardinality tables for all key join paths."""
    print("Extracting unique key sets (this may take a minute)...")

    booking_person = unique_csv("Booking2010_2012v3.csv", "PersonID") | unique_csv("Booking2013_2016v3.csv", "PersonID")
    booking_mni = unique_csv("Booking2010_2012v3.csv", "mni") | unique_csv("Booking2013_2016v3.csv", "mni")
    booking_number = unique_csv("Booking2010_2012v3.csv", "BookingNumber") | unique_csv("Booking2013_2016v3.csv", "BookingNumber")
    booking_charge_id = unique_csv("Booking2010_2012v3.csv", "BookingChargeID") | unique_csv("Booking2013_2016v3.csv", "BookingChargeID")
    booking_charge_code = unique_csv("Booking2010_2012v3.csv", "ChargeCode") | unique_csv("Booking2013_2016v3.csv", "ChargeCode")

    case_person = unique_csv("CaseData_v2.csv", "PersonID")
    case_mni = unique_csv("CaseData_v2.csv", "MNI")
    case_assoc_booking = unique_csv("CaseData_v2.csv", "AssociatedBookingNumber")
    case_orig_booking = unique_csv("CaseData_v2.csv", "OriginalBookingNumber")
    case_id = unique_csv("CaseData_v2.csv", "CaseID")
    case_charge_id = unique_csv("CaseData_v2.csv", "CaseChargeID")
    case_charge_code = unique_csv("CaseData_v2.csv", "ChargeCode")

    person_person = unique_excel("PersonData.xlsx", "PersonData", "PersonID")
    person_mni = unique_excel("PersonData.xlsx", "PersonData", "MNI")

    pretrial_pa = unique_csv("PreTrial Charge-Interview.csv", "PA_MAST_NO")
    pretrial_booking = unique_csv("PreTrial Charge-Interview.csv", "PK_BKG_NO")
    pretrial_case_number = unique_csv("PreTrial Charge-Interview.csv", "PK_CNTY_NO")
    pretrial_charge_code = unique_csv("PreTrial Charge-Interview.csv", "PK_CHARGE")

    pretrial_def_pa = unique_excel("PreTrial Defendants.xlsx", "Sheet1", "PA_MAST_NO")
    pretrial_def_booking = unique_excel("PreTrial Defendants.xlsx", "Sheet1", "PA_BKG_NO")
    pretrial_def_mni = unique_excel("PreTrial Defendants.xlsx", "Sheet1", "PB_MNI")

    pretrial_bridge_pa = unique_excel("PreTrial to Booking Info.xlsx", "Booking", "PA_MAST_NO")
    pretrial_bridge_booking = unique_excel("PreTrial to Booking Info.xlsx", "Booking", "BH_BKG_NO")
    pretrial_bridge_case_number = unique_excel("PreTrial to Booking Info.xlsx", "Booking", "BH_C_CASE")

    tcud_pa = unique_excel("PreTrial TCUD-ODAR Events.xlsx", "Sheet1", "PA_MAST_NO")
    # bridge_case_id = unique_excel("CaseIDtoBookingChargeIDUPDATED.xlsx", "Sheet2", "CaseID")
    # bridge_booking_charge_id = unique_excel("CaseIDtoBookingChargeIDUPDATED.xlsx", "Sheet2", "BookingChargeID")
    sentencing_case_id = (
        unique_excel("SentencingDataPre2013.xlsx", "SentencingDataPre2013", "CaseID")
        | unique_excel("SentencingDataPost2013.xlsx", "SentencingDataPost2013", "CaseID")
    )
    revocation_case_id = unique_excel("revocationV2.xlsx", "revocation", "CaseID")
    revocation_case_charge_id = unique_excel("revocationV2.xlsx", "revocation", "CaseChargeID")

    print("Building overlap table...")
    relationship_rows = [
        overlap_row("person", "booking.PersonID", booking_person, "person.PersonID", person_person),
        overlap_row("person", "case.PersonID", case_person, "person.PersonID", person_person),
        overlap_row("person", "booking.mni", booking_mni, "person.MNI", person_mni),
        overlap_row("person", "case.MNI", case_mni, "person.MNI", person_mni),
        overlap_row("person", "pretrial_defendants.PB_MNI", pretrial_def_mni, "person.MNI", person_mni),
        overlap_row("booking", "case.AssociatedBookingNumber", case_assoc_booking, "booking.BookingNumber", booking_number),
        overlap_row("booking", "case.OriginalBookingNumber", case_orig_booking, "booking.BookingNumber", booking_number),
        overlap_row("booking", "pretrial_charge.PK_BKG_NO", pretrial_booking, "booking.BookingNumber", booking_number),
        overlap_row("booking", "pretrial_defendants.PA_BKG_NO", pretrial_def_booking, "booking.BookingNumber", booking_number),
        overlap_row("booking", "pretrial_bridge.BH_BKG_NO", pretrial_bridge_booking, "booking.BookingNumber", booking_number),
        # overlap_row("case", "case_bridge.CaseID", bridge_case_id, "case.CaseID", case_id),
        overlap_row("case", "sentencing.CaseID", sentencing_case_id, "case.CaseID", case_id),
        overlap_row("case", "revocation.CaseID", revocation_case_id, "case.CaseID", case_id),
        # overlap_row("charge", "case_bridge.BookingChargeID", bridge_booking_charge_id, "booking.BookingChargeID", booking_charge_id),
        overlap_row("charge", "revocation.CaseChargeID", revocation_case_charge_id, "case.CaseChargeID", case_charge_id),
        overlap_row("charge", "booking.ChargeCode", booking_charge_code, "case.ChargeCode", case_charge_code),
        overlap_row("charge", "pretrial_charge.PK_CHARGE", pretrial_charge_code, "booking.ChargeCode", booking_charge_code),
        overlap_row("pretrial", "pretrial_charge.PA_MAST_NO", pretrial_pa, "pretrial_defendants.PA_MAST_NO", pretrial_def_pa),
        overlap_row("pretrial", "pretrial_charge.PA_MAST_NO", pretrial_pa, "pretrial_bridge.PA_MAST_NO", pretrial_bridge_pa),
        overlap_row("pretrial", "pretrial_charge.PA_MAST_NO", pretrial_pa, "pretrial_tcud.PA_MAST_NO", tcud_pa),
        overlap_row("pretrial", "pretrial_charge.PK_CNTY_NO", pretrial_case_number, "pretrial_bridge.BH_C_CASE", pretrial_bridge_case_number),
    ]

    relationship_df = (
        pd.DataFrame(relationship_rows)
        .sort_values(["relationship_group", "shared_unique"], ascending=[True, False])
        .reset_index(drop=True)
    )

    print("Computing cardinality...")
    booking_concat = pd.concat([
        pd.read_csv(RAW_DATA_DIR / "Booking2010_2012v3.csv", usecols=["BookingNumber"], dtype="string", low_memory=False),
        pd.read_csv(RAW_DATA_DIR / "Booking2013_2016v3.csv", usecols=["BookingNumber"], dtype="string", low_memory=False),
    ], ignore_index=True)

    cardinality_df = pd.DataFrame([
        {"entity": "booking", "key": "BookingNumber", "mean_rows_per_key": round(float(booking_concat.groupby("BookingNumber").size().mean()), 2)},
        {"entity": "case", "key": "CaseID", "mean_rows_per_key": _mean_rows_per_key_csv("CaseData_v2.csv", "CaseID")},
        {"entity": "pretrial", "key": "PA_MAST_NO", "mean_rows_per_key": _mean_rows_per_key_csv("PreTrial Charge-Interview.csv", "PA_MAST_NO")},
        #{"entity": "case_bridge", "key": "CaseID", "mean_rows_per_key": _mean_rows_per_key_excel("CaseIDtoBookingChargeIDUPDATED.xlsx", "Sheet2", "CaseID")},
    ])

    return {"relationship_overlap": relationship_df, "cardinality": cardinality_df}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = run_linkage_analysis()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results["relationship_overlap"].to_csv(OUTPUT_DIR / "relationship_overlap.csv", index=False)
    results["cardinality"].to_csv(OUTPUT_DIR / "cardinality.csv", index=False)

    print("\n--- Relationship Overlap ---")
    print(results["relationship_overlap"].to_string(index=False))
    print("\n--- Cardinality ---")
    print(results["cardinality"].to_string(index=False))
    print(f"\nTables saved → {OUTPUT_DIR}")
