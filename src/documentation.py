"""
documentation.py
----------------
Feature inventory and role-tagging tables for the Travis County dataset.

Produces three structured DataFrames:
  - feature_inventory_df  : grouped list of all variables by analysis category
  - feature_role_df       : column-level role tags (identifier / sensitive / proxy / etc.)
  - unclear_fields_df     : fields whose semantics need domain confirmation

Run from the project root:
    python src/documentation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from dataloader import PROJECT_ROOT

OUTPUT_DIR = PROJECT_ROOT / "reports" / "tables"

# ---------------------------------------------------------------------------
# Feature inventory (by category)
# ---------------------------------------------------------------------------

FEATURE_INVENTORY_ROWS: list[dict] = [
    {"category": "demographics", "columns": "PersonID, MNI, DateofBirth, GenderID, RaceID, EthnicityID, CitizenshipID", "source_files": "PersonData.xlsx", "notes": "Best person-level demographic anchor; several fields are coded."},
    {"category": "demographics", "columns": "PB_MNI, PB_SEX, PB_RAC, PB_DOB, PC_ETHNIC", "source_files": "PreTrial Defendants.xlsx", "notes": "Defendant-level demographic fields; some values are abbreviated or coded."},
    {"category": "geography", "columns": "PB_CITY, PB_ST, PB_ZIP", "source_files": "PreTrial Defendants.xlsx", "notes": "Most direct residence-style geography fields in the current files."},
    {"category": "geography", "columns": "ArrestingAgencyID, DivisionID, AssignedCourtID, OriginalDispositionCourtID, LatestDispositonCourtID, CourtJudgeIdentifier", "source_files": "booking extracts; CaseData_v2.csv; revocationV2.xlsx; Events.xlsx", "notes": "Institutional geography or assignment rather than home geography."},
    {"category": "legal_history", "columns": "bookingID, BookingNumber, ChargeCount, HighestBookingCharge, HighestBookingCount, OpenCharge", "source_files": "Booking2010_2012v3.csv; Booking2013_2016v3.csv", "notes": "Booking-side history and repeated charge context."},
    {"category": "legal_history", "columns": "CriminalDefendantID, CriminalDefendantHistoryID, EarliestKnownChargeID, HighestLevelChargeCount, HighestLevelDispositionCount, ReindictRefile", "source_files": "CaseData_v2.csv; revocationV2.xlsx", "notes": "Likely accumulated case or defendant history fields."},
    {"category": "current_charge", "columns": "BookingChargeID, ChargeCode, ChargeDescription, ChargeClassID, chargedate, chargetime", "source_files": "booking extracts", "notes": "Booking-side charge detail."},
    {"category": "current_charge", "columns": "CaseChargeID, CountNumber, ChargeCode, CurrentChargeStateID, ChargeReducedEnhanced", "source_files": "CaseData_v2.csv; revocationV2.xlsx", "notes": "Case-side charge detail."},
    {"category": "current_charge", "columns": "PK_CHARGE, PK_CHG_LIT, PK_LVL, PK_CHG_DT, PK_SEQ_No", "source_files": "PreTrial Charge-Interview.csv", "notes": "Pretrial-side charge description and offense level."},
    {"category": "risk_assessment", "columns": "PA_PTS_RISK", "source_files": "PreTrial Defendants.xlsx", "notes": "Most explicit risk score field in the current data."},
    {"category": "risk_assessment", "columns": "PI_SCORE, PI_EVENT, PI_EVT_DISP", "source_files": "PreTrial TCUD-ODAR Events.xlsx", "notes": "Program-linked score and event outcome fields."},
    {"category": "risk_assessment", "columns": "PK_BND_REC, PK_ATY_REC, PK_ATY_BND, OFF_REC, INT_OFF", "source_files": "PreTrial Charge-Interview.csv", "notes": "Recommendation or interview-process fields; exact semantics need confirmation."},
    {"category": "court_decision", "columns": "PK_BND_GRT, PK_GRNT_DT, PK_BND_AMT, PK_BND_TYP, PK_BND_STS", "source_files": "PreTrial Charge-Interview.csv", "notes": "Pretrial bond decision variables."},
    {"category": "court_decision", "columns": "DispositionID, DispositionDate, DispositionTypeID, DispositionMethodID, OriginalDispositionID, OriginalDispositionDate, LatestDispositionID, LatestDispositionDate", "source_files": "CaseData_v2.csv; revocationV2.xlsx", "notes": "Case decision and disposition variables."},
    {"category": "court_decision", "columns": "SentenceTypeID, ReceivableTypeID, AgencyID, SentenceUOMID, SentenceQuantity, SentenceOther, SentenceEffectiveDt, SentenceConcurrencyFlag", "source_files": "SentencingDataPre2013.xlsx; SentencingDataPost2013.xlsx", "notes": "Sentencing structure and punishment variables."},
    {"category": "judge_court_process", "columns": "JUDGE, AssignedCourtID, OriginalDispositionCourtID, LatestDispositonCourtID, CourtTypeID, CaseTypeID, CaseStatusID, CaseStateID", "source_files": "PreTrial Charge-Interview.csv; CaseData_v2.csv; revocationV2.xlsx", "notes": "Judge routing, court assignment, and process-state fields."},
    {"category": "judge_court_process", "columns": "PartyAttorneyID, PartyIDRepresenting, attorneyID, AttorneySBN, AttorneyCounselTypeID, AttorneyCaseStatusID, AttorneyStatusDateTime", "source_files": "CaseData_v2.csv; revocationV2.xlsx", "notes": "Attorney assignment and representation process."},
    {"category": "judge_court_process", "columns": "BH_C_CASE, BH_CRT_DATE, BH_CRT_TIME, BH_CRT_EVT, BH_WAR_NO", "source_files": "PreTrial to Booking Info.xlsx", "notes": "Booking-to-court bridge and scheduling fields."},
    {"category": "outcome_variables", "columns": "ReleaseDate, ReleaseTime, ReleaseReasonID, TimeBookingtoRelease, EligibleforBail, BailAmount, BailTypeID, MagistrationDate", "source_files": "booking extracts", "notes": "Booking-stage release and bail outcomes."},
    {"category": "outcome_variables", "columns": "DispositionID, DispositionDate, DispositionTypeID, CalendarDaysFilingtoDisposition, TimetoDisposition, InactivityDays, AgeofCase", "source_files": "CaseData_v2.csv; revocationV2.xlsx", "notes": "Case outcome and case timing measures."},
    {"category": "outcome_variables", "columns": "PL_BND_DISP, PL_DISP_RSN, EventResultID, AssociatedCaseStatusID", "source_files": "PreTrial Disposition Reason.xlsx; Events.xlsx", "notes": "Pretrial and event-level disposition outcomes."},
]

# ---------------------------------------------------------------------------
# Feature role tags
# ---------------------------------------------------------------------------

FEATURE_ROLE_ROWS: list[dict] = [
    {"column": "PersonID", "role": "identifier", "source": "PersonData.xlsx; booking; case", "reason": "person-level linkage key"},
    {"column": "MNI", "role": "identifier", "source": "PersonData.xlsx; case; events", "reason": "cross-file person linkage key"},
    {"column": "BookingNumber", "role": "identifier", "source": "booking extracts", "reason": "best booking-level linkage key"},
    {"column": "bookingID", "role": "identifier", "source": "booking extracts", "reason": "booking record identifier"},
    {"column": "BookingChargeID", "role": "identifier", "source": "booking extracts; case bridge", "reason": "booking-charge linkage key"},
    {"column": "CaseID", "role": "identifier", "source": "CaseData_v2.csv; sentencing; revocation", "reason": "best case-level linkage key"},
    {"column": "CaseChargeID", "role": "identifier", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "case-charge linkage key"},
    {"column": "PA_MAST_NO", "role": "identifier", "source": "pretrial files", "reason": "best internal pretrial linkage key"},
    {"column": "DateofBirth", "role": "sensitive", "source": "PersonData.xlsx", "reason": "direct age-related protected attribute input"},
    {"column": "GenderID", "role": "sensitive", "source": "PersonData.xlsx", "reason": "protected attribute"},
    {"column": "RaceID", "role": "sensitive", "source": "PersonData.xlsx", "reason": "protected attribute"},
    {"column": "EthnicityID", "role": "sensitive", "source": "PersonData.xlsx", "reason": "protected attribute"},
    {"column": "CitizenshipID", "role": "sensitive", "source": "PersonData.xlsx", "reason": "sensitive status field"},
    {"column": "PB_SEX", "role": "sensitive", "source": "PreTrial Defendants.xlsx", "reason": "sex field in abbreviated form"},
    {"column": "PB_RAC", "role": "sensitive", "source": "PreTrial Defendants.xlsx", "reason": "race field in abbreviated form"},
    {"column": "PC_ETHNIC", "role": "sensitive", "source": "PreTrial Defendants.xlsx", "reason": "ethnicity field in abbreviated form"},
    {"column": "PB_CITY", "role": "proxy", "source": "PreTrial Defendants.xlsx", "reason": "geography can proxy race and class"},
    {"column": "PB_ST", "role": "proxy", "source": "PreTrial Defendants.xlsx", "reason": "geography can proxy demographic composition"},
    {"column": "PB_ZIP", "role": "proxy", "source": "PreTrial Defendants.xlsx", "reason": "zip code is a strong socioeconomic proxy"},
    {"column": "ArrestingAgencyID", "role": "proxy", "source": "booking extracts", "reason": "institutional and geographic proxy for enforcement patterns"},
    {"column": "ChargeCode", "role": "candidate_predictor", "source": "booking; case; pretrial", "reason": "offense type is substantively important but should be interpreted carefully"},
    {"column": "ChargeDescription", "role": "candidate_predictor", "source": "booking extracts", "reason": "human-readable offense detail"},
    {"column": "ChargeClassID", "role": "candidate_predictor", "source": "booking extracts", "reason": "charge severity proxy once decoded"},
    {"column": "PK_LVL", "role": "candidate_predictor", "source": "PreTrial Charge-Interview.csv", "reason": "pretrial offense-level field"},
    {"column": "HighestBookingCharge", "role": "candidate_predictor", "source": "booking extracts", "reason": "booking-side severity indicator"},
    {"column": "ChargeCount", "role": "candidate_predictor", "source": "booking extracts", "reason": "current booking complexity"},
    {"column": "PA_PTS_RISK", "role": "candidate_predictor", "source": "PreTrial Defendants.xlsx", "reason": "explicit risk score, but should be assessed for bias"},
    {"column": "PI_SCORE", "role": "candidate_predictor", "source": "PreTrial TCUD-ODAR Events.xlsx", "reason": "program score that may be analytically useful with caution"},
    {"column": "PK_BND_REC", "role": "decision", "source": "PreTrial Charge-Interview.csv", "reason": "bond recommendation is an institutional decision input"},
    {"column": "PK_ATY_REC", "role": "decision", "source": "PreTrial Charge-Interview.csv", "reason": "attorney recommendation field"},
    {"column": "OFF_REC", "role": "decision", "source": "PreTrial Charge-Interview.csv", "reason": "officer recommendation field"},
    {"column": "PK_BND_GRT", "role": "outcome", "source": "PreTrial Charge-Interview.csv", "reason": "bond grant is a judicial outcome"},
    {"column": "PK_BND_AMT", "role": "outcome", "source": "PreTrial Charge-Interview.csv", "reason": "bond amount is a direct pretrial decision outcome"},
    {"column": "DispositionID", "role": "outcome", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "final case disposition"},
    {"column": "DispositionDate", "role": "outcome", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "timing of case outcome"},
    {"column": "SentenceQuantity", "role": "outcome", "source": "sentencing workbooks", "reason": "downstream punishment quantity"},
    {"column": "SentenceEffectiveDt", "role": "outcome", "source": "sentencing workbooks", "reason": "effective date of sentence"},
    {"column": "ReleaseReasonID", "role": "outcome", "source": "booking extracts", "reason": "booking-stage release outcome code"},
    {"column": "TimeBookingtoRelease", "role": "outcome", "source": "booking extracts", "reason": "booking-stage timing outcome"},
    {"column": "AssignedCourtID", "role": "process", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "court routing variable"},
    {"column": "JUDGE", "role": "process", "source": "PreTrial Charge-Interview.csv", "reason": "judge assignment/process variable"},
    {"column": "AttorneyCounselTypeID", "role": "process", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "representation process field"},
    {"column": "AttorneyCaseStatusID", "role": "process", "source": "CaseData_v2.csv; revocationV2.xlsx", "reason": "attorney process status field"},
]

# ---------------------------------------------------------------------------
# Unclear / needs-lookup fields
# ---------------------------------------------------------------------------

UNCLEAR_FIELD_ROWS: list[dict] = [
    {"group": "booking", "field": "CustodyStatusID", "reason": "coded custody status without visible lookup"},
    {"group": "booking", "field": "CustodyTypeID", "reason": "coded custody type without visible lookup"},
    {"group": "booking", "field": "ReleaseReasonID", "reason": "coded release reason"},
    {"group": "booking", "field": "ChargeDispositionTypeID", "reason": "coded charge disposition type"},
    {"group": "booking", "field": "BookingAuthorityID", "reason": "authority code needs lookup"},
    {"group": "case_revocation", "field": "CaseTypeID", "reason": "coded case type"},
    {"group": "case_revocation", "field": "CaseStatusID", "reason": "coded case status"},
    {"group": "case_revocation", "field": "CaseStateID", "reason": "coded case state"},
    {"group": "case_revocation", "field": "CurrentChargeStateID", "reason": "charge state meaning needs definition"},
    {"group": "case_revocation", "field": "ChargeReducedEnhanced", "reason": "label suggests legal transformation but coding is unclear"},
    {"group": "case_revocation", "field": "OriginalDispositionPleaID", "reason": "coded plea identifier"},
    {"group": "case_revocation", "field": "OriginalDispositionTrialTypeID", "reason": "coded trial type"},
    {"group": "case_revocation", "field": "OriginalDispositionVerdictID", "reason": "coded verdict identifier"},
    {"group": "case_revocation", "field": "DispositionMethodID", "reason": "coded disposition method"},
    {"group": "pretrial", "field": "INT_OFF", "reason": "abbreviated interview field"},
    {"group": "pretrial", "field": "OFF_REC", "reason": "abbreviated recommendation field"},
    {"group": "pretrial", "field": "PK_ATY_REC", "reason": "abbreviated attorney recommendation field"},
    {"group": "pretrial", "field": "PK_ATY_BND", "reason": "meaning unclear without pretrial codebook"},
    {"group": "pretrial", "field": "PK_BNDRSN_1", "reason": "bond reason code"},
    {"group": "pretrial", "field": "PK_BND_CND1", "reason": "bond condition code"},
    {"group": "pretrial", "field": "PK_BND_CD1", "reason": "bond code field"},
    {"group": "pretrial", "field": "PTS_OFF", "reason": "risk-assessment support field needs definition"},
    {"group": "pretrial", "field": "PL_MOT_RSN1", "reason": "motion reason code"},
    {"group": "pretrial", "field": "PI_EVT_DISP", "reason": "event disposition code requires program context"},
    {"group": "events_sentencing", "field": "EventCodeID", "reason": "coded event identifier"},
    {"group": "events_sentencing", "field": "EventCategoryID", "reason": "coded event category"},
    {"group": "events_sentencing", "field": "CourtJudgeIdentifier", "reason": "judge identifier format is not yet decoded"},
    {"group": "events_sentencing", "field": "SentenceTypeID", "reason": "coded sentence type"},
    {"group": "events_sentencing", "field": "ReceivableTypeID", "reason": "coded receivable type"},
    {"group": "events_sentencing", "field": "SentenceUOMID", "reason": "coded sentence unit"},
]

# ---------------------------------------------------------------------------
# DataFrame builders
# ---------------------------------------------------------------------------

def build_feature_inventory() -> pd.DataFrame:
    return (
        pd.DataFrame(FEATURE_INVENTORY_ROWS)
        .sort_values(["category", "source_files"])
        .reset_index(drop=True)
    )


def build_feature_role_df() -> pd.DataFrame:
    return (
        pd.DataFrame(FEATURE_ROLE_ROWS)
        .sort_values(["role", "column"])
        .reset_index(drop=True)
    )


def build_unclear_fields_df() -> pd.DataFrame:
    return (
        pd.DataFrame(UNCLEAR_FIELD_ROWS)
        .sort_values(["group", "field"])
        .reset_index(drop=True)
    )


def build_candidate_modeling_features(feature_role_df: pd.DataFrame) -> pd.DataFrame:
    role_map = {
        "candidate_predictor": "consider_for_baseline_model",
        "proxy": "review_for_proxy_risk_before_use",
        "sensitive": "exclude_from_default_model_use_for_fairness_audit",
    }
    df = feature_role_df[feature_role_df["role"].isin(role_map)].copy()
    df["modeling_recommendation"] = df["role"].map(role_map)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    feature_inventory_df = build_feature_inventory()
    feature_role_df = build_feature_role_df()
    unclear_fields_df = build_unclear_fields_df()
    candidate_df = build_candidate_modeling_features(feature_role_df)

    feature_inventory_df.to_csv(OUTPUT_DIR / "feature_inventory.csv", index=False)
    feature_role_df.to_csv(OUTPUT_DIR / "feature_roles.csv", index=False)
    unclear_fields_df.to_csv(OUTPUT_DIR / "unclear_fields.csv", index=False)
    candidate_df.to_csv(OUTPUT_DIR / "candidate_modeling_features.csv", index=False)

    print("Feature inventory:")
    print(feature_inventory_df.groupby("category").size().to_string())
    print()
    print("Feature role counts:")
    print(feature_role_df.groupby("role").size().to_string())
    print()
    print(f"Tables saved → {OUTPUT_DIR}")
