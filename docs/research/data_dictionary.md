# Travis County Feature Inventory

This feature inventory groups the main Travis County variables into analysis-oriented categories rather than listing every field alphabetically. It is intended to support feature selection for fairness analysis, not to serve as a final codebook.

## Scope and interpretation

- Focus: main person, booking, case, pretrial, event, sentencing, and revocation files used in week 1 EDA.
- Grouping rule: columns are grouped by likely analytic meaning, even when the raw files use different naming conventions.
- Caveat: many fields are coded IDs without attached lookup tables in the current workspace. Those are flagged as unclear or partially unclear.

## Category inventory

### Demographics

These are the clearest person-level or defendant-level descriptive features.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Demographics | `PersonID`, `MNI`, `DateofBirth`, `GenderID`, `RaceID`, `EthnicityID`, `CitizenshipID` | `PersonData.xlsx` | strongest person-level demographic anchor; `GenderID`, `RaceID`, `EthnicityID`, and `CitizenshipID` appear coded |
| Demographics | `PersonID`, `mni` | `Booking2010_2012v3.csv`, `Booking2013_2016v3.csv` | identifiers only, not direct demographic descriptors |
| Demographics | `PersonID`, `MNI` | `CaseData_v2.csv`, `revocationV2.xlsx` | identifiers only, useful for linking to person table |
| Demographics | `PB_MNI`, `PB_SEX`, `PB_RAC`, `PB_DOB`, `PC_ETHNIC` | `PreTrial Defendants.xlsx` | defendant-level demographic fields; `PB_SEX`, `PB_RAC`, and `PC_ETHNIC` use coded or abbreviated values |

### Geography

These are the clearest location or residence features currently visible in the file set.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Geography | `PB_CITY`, `PB_ST`, `PB_ZIP` | `PreTrial Defendants.xlsx` | most direct residence-style geography fields in the current inventory |
| Geography | `ArrestingAgencyID` | booking extracts | not residence geography; may still proxy location or agency jurisdiction, but requires lookup |
| Geography | `DivisionID`, `AssignedCourtID`, `OriginalDispositionCourtID`, `LatestDispositonCourtID`, `CourtJudgeIdentifier` | `CaseData_v2.csv`, `revocationV2.xlsx`, `Events.xlsx` | institutional geography or court assignment rather than home geography |

### Legal history and prior system contact

These features look like prior involvement, charge history, or accumulated process history rather than the current single decision point.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Legal history | `bookingID`, `BookingNumber`, `ChargeCount`, `HighestBookingCharge`, `HighestBookingCount`, `OpenCharge` | booking extracts | describe booking and booking-charge history within each record |
| Legal history | `CriminalDefendantID`, `CriminalDefendantHistoryID`, `EarliestKnownChargeID`, `HighestLevelChargeCount`, `HighestLevelDispositionCount`, `ReindictRefile` | `CaseData_v2.csv`, `revocationV2.xlsx` | likely prior or accumulated history indicators; `ReindictRefile` meaning needs validation |
| Legal history | `Event`, `EventDescription`, `EventDate`, `EventCode`, `EventCategoryID`, `EventResultID` | `Mental Health Flag Events.xlsx`, `Events.xlsx` | useful for past system contact or event-history reconstruction |
| Legal history | `OriginalBookingNumber`, `AssociatedBookingNumber`, `AssociatedBookingDate`, `BookingDate`, `OffenseDate` | `CaseData_v2.csv`, `revocationV2.xlsx` | can help reconstruct prior sequence of contact but may also describe the current case chain |

### Current charge and offense severity

These are the clearest variables describing the booked or filed offense currently attached to the row.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Current charge | `BookingChargeID`, `ChargeCode`, `ChargeDescription`, `ChargeClassID`, `chargedate`, `chargetime` | booking extracts | booking-side charge detail; `ChargeClassID` requires decoding |
| Current charge | `CaseChargeID`, `CountNumber`, `ChargeCode`, `CurrentChargeStateID`, `ChargeReducedEnhanced` | `CaseData_v2.csv`, `revocationV2.xlsx` | case-side charge detail; `CurrentChargeStateID` and `ChargeReducedEnhanced` need definition checks |
| Current charge | `PK_CHARGE`, `PK_CHG_LIT`, `PK_LVL`, `PK_CHG_DT`, `PK_SEQ_No` | `PreTrial Charge-Interview.csv`, `PreTrial Charge-Interview.xlsx` | pretrial-side charge text and level; `PK_LVL` likely offense level |
| Current charge | `BH_CHG_DATE`, `BH_JCHG_NO` | `PreTrial to Booking Info.xlsx` | charge date and jail-charge-number style bridge fields |
| Current charge | `Code`, `Offense`, `Citation`, `Statute`, `L/D`, `Violent` | violent-charge lookup workbook | lookup or enrichment variables rather than person-case features |
| Current charge | `chargecode`, `chargecode_numeric`, `chargecode_description` | `chargecode_description.dta` | charge lookup table |

### Risk assessment score and need indicators

These are the clearest candidate risk, screening, or recommendation features.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Risk assessment | `PA_PTS_RISK` | `PreTrial Defendants.xlsx` | strongest explicit risk score field in the current data |
| Risk assessment | `PI_SCORE` | `PreTrial TCUD-ODAR Events.xlsx` | score tied to TCUD or ODAR event records; requires program-context interpretation |
| Risk assessment | `PK_BND_REC`, `PK_ATY_REC`, `PK_ATY_BND`, `OFF_REC`, `INT_OFF` | `PreTrial Charge-Interview.csv`, `PreTrial Charge-Interview.xlsx` | recommendation or assessment-process fields; exact semantics for some columns remain unclear |
| Risk assessment | `Mental Health Flag` style event indicators through `Event` and `EventDescription` | `Mental Health Flag Events.xlsx` | can proxy need, diagnosis, or service contact; should be handled carefully in fairness analysis |

### Court decision and judicial action

These are the clearest variables capturing recommendations, grants, dispositions, sentencing, or other formal decisions.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Court decision | `PK_BND_GRT`, `PK_GRNT_DT`, `PK_BND_AMT`, `PK_BND_TYP`, `PK_BND_STS` | `PreTrial Charge-Interview.csv`, `PreTrial Charge-Interview.xlsx` | pretrial bond decision variables |
| Court decision | `DispositionID`, `DispositionDate`, `DispositionTypeID`, `DispositionMethodID`, `OriginalDispositionID`, `OriginalDispositionDate`, `OriginalDispositionMethodID`, `LatestDispositionID`, `LatestDispositionDate`, `LatestDispositionMethodID` | `CaseData_v2.csv`, `revocationV2.xlsx` | most direct case outcome and decision variables; many are coded |
| Court decision | `OriginalDispositionPleaID`, `OriginalDispositionTrialTypeID`, `OriginalDispositionVerdictID`, `OriginalSentenceID`, `LatestSentenceID` | `CaseData_v2.csv`, `revocationV2.xlsx` | plea, trial, verdict, and sentence-related decision fields |
| Court decision | `PL_BND_DISP`, `PL_DISP_RSN` | `PreTrial Disposition Reason.xlsx` | pretrial bond-disposition and reason fields; coding needs lookup |
| Court decision | `SentenceTypeID`, `ReceivableTypeID`, `AgencyID`, `SentenceUOMID`, `SentenceQuantity`, `SentenceOther`, `SentenceEffectiveDt`, `SentenceConcurrencyFlag` | sentencing workbooks | sentence structure and punishment details |

### Judge and court process

These variables describe assignment, scheduling, attorney status, event processing, or judge routing.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Judge and court process | `JUDGE` | `PreTrial Charge-Interview.csv`, `PreTrial Charge-Interview.xlsx` | direct judge identifier |
| Judge and court process | `AssignedCourtID`, `OriginalDispositionCourtID`, `LatestDispositonCourtID`, `CourtTypeID`, `CaseTypeID`, `CaseStatusID`, `CaseStateID`, `StatusDate`, `CaseInitiationDate`, `DateCaseEntered`, `ActivationDate`, `ActivationEventID`, `ActivationTypeID`, `casephaseID`, `CasePhaseCode` | `CaseData_v2.csv`, `revocationV2.xlsx` | process-state and court-routing fields, many coded |
| Judge and court process | `PartyAttorneyID`, `PartyIDRepresenting`, `attorneyID`, `AttorneySBN`, `AttorneyCounselTypeID`, `AttorneyCaseStatusID`, `AttorneyStatusDateTime`, `CurrentAttorneyFlag`, `AttorneyStartDate`, `AttorneyEndDate`, `CurrentLeadAttorneyFlag` | `CaseData_v2.csv`, `revocationV2.xlsx` | attorney assignment and representation process |
| Judge and court process | `BH_C_CASE`, `BH_CRT_DATE`, `BH_CRT_TIME`, `BH_CRT_EVT`, `BH_WAR_NO` | `PreTrial to Booking Info.xlsx` | booking-to-court bridge and scheduling fields |
| Judge and court process | `EventID`, `EventDate`, `EventDateSeq`, `EventCodeID`, `EventResultID`, `AssociatedCountNo`, `EventCode`, `EventDescription`, `AssociatedCaseStatusID`, `CourtJudgeIdentifier` | `Events.xlsx` | event log for court-process reconstruction |

### Outcome variables

These are the clearest end-state or downstream variables for fairness or performance outcomes.

| Category | Columns | Source files | Notes |
| --- | --- | --- | --- |
| Outcome variables | `ReleaseDate`, `ReleaseTime`, `ReleaseReasonID`, `TimeBookingtoRelease`, `EligibleforBail`, `BailAmount`, `BailTypeID`, `MagistrationDate` | booking extracts | release and bail outcomes at the booking stage |
| Outcome variables | `DispositionID`, `DispositionDate`, `DispositionTypeID`, `CalendarDaysFilingtoDisposition`, `TimetoDisposition`, `InactivityDays`, `AgeofCase` | `CaseData_v2.csv`, `revocationV2.xlsx` | case completion timing and outcome measures |
| Outcome variables | `SentenceQuantity`, `SentenceEffectiveDt`, `SentenceConcurrencyFlag`, `SentenceOther` | sentencing workbooks | downstream sentencing outcomes |
| Outcome variables | `PL_BND_DISP`, `PL_DISP_RSN` | `PreTrial Disposition Reason.xlsx` | pretrial disposition outcomes |
| Outcome variables | `PI_EVT_DISP` | `PreTrial TCUD-ODAR Events.xlsx` | event-level program outcome or completion status |
| Outcome variables | `EventResultID`, `AssociatedCaseStatusID` | `Events.xlsx` | event-level process outcomes, but coding requires lookup |

## High-priority unclear or partially unclear fields

These columns either use abbreviations without a visible codebook, encode institutional categories through numeric IDs, or need domain confirmation before modeling.

### Booking files

- `CustodyStatusID`
- `CustodyTypeID`
- `ReleaseReasonID`
- `ArrestingAgencyID`
- `INSHold`
- `FederalHold`
- `StateHold`
- `TDC_BWHold`
- `OtherHold`
- `ActiveWrit`
- `ChargeClassID`
- `ChargeDispositionTypeID`
- `BookingAuthorityID`
- `ChargeStatusID`
- `JailChargeCourt`

### Case and revocation files

- `DivisionID`
- `CourtTypeID`
- `CaseTypeID`
- `CaseStatusID`
- `CaseStateID`
- `ReindictRefile`
- `CaseStateIssue`
- `LatestCasePhaseID`
- `LatestAgeofPendingComplaint`
- `JailCaseTypeID`
- `CurrentChargeStateID`
- `ChargeReducedEnhanced`
- `OriginalDispositionPleaID`
- `OriginalDispositionTrialTypeID`
- `OriginalDispositionVerdictID`
- `OriginalDispositionMethodID`
- `OriginalDispositionID`
- `OriginalDispositionEvent`
- `OriginalSentenceID`
- `LatestDispositionMethodID`
- `LatestDispositionID`
- `LatestSentenceID`
- `ActivationEventID`
- `ActivationTypeID`
- `casephaseID`
- `UnabletoCalcAgeInactivity`
- `DispositionMethodID`
- `AttorneyCounselTypeID`
- `AttorneyCaseStatusID`

### Pretrial files

- `INT_OFF`
- `OFF_REC`
- `PK_ATY_REC`
- `PK_ATY_BND`
- `PK_BND_STS`
- `PK_INT_TYPE`
- `PK_BNDRSN_1`, `PK_BNDRSN_2`, `PK_BNDRSN_3`
- `PK_BND_CND1` through `PK_BND_CND6`
- `PK_BND_CD1` through `PK_BND_CD6`
- `PTS_OFF`
- `PL_MOT_RSN1`
- `PL_BND_DISP`
- `PL_DISP_RSN`
- `PI_EVENT`
- `PI_EVT_DISP`

### Event and sentencing files

- `EventCodeID`
- `EventResultID`
- `EventCodeID.1`
- `DivisionID.1`
- `EventCategoryID`
- `AssociatedCaseStatusID`
- `CourtJudgeIdentifier`
- `SentenceTypeID`
- `ReceivableTypeID`
- `AgencyID`
- `SentenceUOMID`

## Recommended use in fairness analysis

- treat demographics and geography as sensitive or proxy-sensitive features, not default predictors
- treat bond recommendation, bond grant, attorney recommendation, event dispositions, and sentencing variables as decision or outcome variables, not neutral inputs
- use coded-ID fields only after finding a lookup or validating them with domain context
- keep a separate list of unresolved fields while modeling so unclear institutional codes are not silently misused