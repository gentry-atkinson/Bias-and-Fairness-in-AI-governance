# Travis County Data Inventory

This inventory was generated from files currently present in data/raw.

## Coverage check

- Scope: all .csv, .xlsx, and .dta files in data/raw.
- For workbook files, sheet names are listed and each sheet is documented separately.
- Preview tables show up to the first 3 rows and first 8 columns to keep the document readable.

## Files

### 171017_CCHCodes_Violent marked by Slayton.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet1 |

#### Sheet: Sheet1

| Field | Value |
| --- | --- |
| Rows | 2112 |
| Columns | 6 |
| Column names | Code, Offense, Citation, Statute, L/D, Violent |

Preview:

| Code | Offense | Citation | Statute | L/D | Violent |
| --- | --- | --- | --- | --- | --- |
| 9990030 | MURDER | 19.02(c) | PC | F1 | Y |
| 9990021 | MURDER UNDER INFLUENCE OF SUDDEN PASSION | 19.02(d) | PC | F2 | Y |
| 9990020 | CAPITAL MURDER OF A PEACE OFFICER OR FIREMAN | 19.03(a)(1) | PC | FX | Y |

### Booking2010_2012v3.csv

| Field | Value |
| --- | --- |
| File type | CSV |
| Rows | 289061 |
| Columns | 43 |
| Sheet names | Not applicable |
| Column names | bookingID, BookingNumber, mni, PersonID, jailID, CustodyStatusID, CustodyTypeID, bookingdate, bookingtime, ReleaseDate, ReleaseTime, ReleaseReasonID, HighestBookingCharge, HighestBookingCount, ArrestDate, ArrestTime, ArrestingAgencyID, INSHold, FederalHold, StateHold, TDC_BWHold, OtherHold, ActiveWrit, AgeofBooking, TimeBookingtoRelease, BookingChargeID, ChargeCount, ChargeCode, ChargeDescription, ChargeClassID, chargedate, chargetime, ChargeDispositionTypeID, ChargeDispositionDate, ChargeSentenceDate, BookingAuthorityID, ChargeStatusID, OpenCharge, EligibleforBail, BailTypeID, BailAmount, MagistrationDate, JailChargeCourt |

Preview:

| bookingID | BookingNumber | mni | PersonID | jailID | CustodyStatusID | CustodyTypeID | bookingdate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 733938 | 1107309.0 | 1661970.0 | 390093.0 | P00244116 | 2.0 | 1.0 | 2/13/2011 |
| 853303 | 1107310.0 | 8925245.0 | 462723.0 | P00295851 | 2.0 | 1.0 | 2/13/2011 |
| 650752 | 1107312.0 | 1399408.0 | 352407.0 | P00295852 | 2.0 | 1.0 | 2/13/2011 |

### Booking2013_2016v3.csv

| Field | Value |
| --- | --- |
| File type | CSV |
| Rows | 289869 |
| Columns | 43 |
| Sheet names | Not applicable |
| Column names | bookingID, BookingNumber, mni, PersonID, jailID, CustodyStatusID, CustodyTypeID, bookingdate, bookingtime, ReleaseDate, ReleaseTime, ReleaseReasonID, HighestBookingCharge, HighestBookingCount, ArrestDate, ArrestTime, ArrestingAgencyID, INSHold, FederalHold, StateHold, TDC_BWHold, OtherHold, ActiveWrit, AgeofBooking, TimeBookingtoRelease, BookingChargeID, ChargeCount, ChargeCode, ChargeDescription, ChargeClassID, chargedate, chargetime, ChargeDispositionTypeID, ChargeDispositionDate, ChargeSentenceDate, BookingAuthorityID, ChargeStatusID, OpenCharge, EligibleforBail, BailTypeID, BailAmount, MagistrationDate, JailChargeCourt |

Preview:

| bookingID | BookingNumber | mni | PersonID | jailID | CustodyStatusID | CustodyTypeID | bookingdate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 800433 | 1402848.0 | 1865202.0 | 431547.0 | P00327853 | 2.0 | 1.0 | 1/21/2014 |
| 762445 | 1402850.0 | 1760191.0 | 407743.0 | P00288801 | 2.0 | 1.0 | 1/21/2014 |
| 762445 | 1402850.0 | 1760191.0 | 407743.0 | P00288801 | 2.0 | 1.0 | 1/21/2014 |

### CaseData_v2.csv

| Field | Value |
| --- | --- |
| File type | CSV |
| Rows | 271699 |
| Columns | 81 |
| Sheet names | Not applicable |
| Column names | CaseID, DivisionID, CourtTypeID, CaseTypeID, CaseStatusID, StatusDate, CaseStateID, SealedFlag, RestrictedFlag, CaseInitiationDate, DateCaseEntered, ReindictRefile, CaseStateIssue, LatestCasePhaseID, LatestAgeofPendingComplaint, CriminalDefendantID, PartyID, PersonID, MNI, OriginalBookingNumber, BookingDate, IndictFilingDate, CalendarDaysBookingtoIndictFiling, JailCaseTypeID, HighestLevelChargeCount, HighestLevelDispositionCount, CaseChargeID, CountNumber, ChargeCode, CsMgmtChargeID, CurrentChargeStateID, ChargeReducedEnhanced, OriginalDispositionPleaID, OriginalDispositionPleaDate, OriginalDispositionTrialTypeID, OriginalDispositionVerdictID, OriginalDispositionVerdictDate, OriginalDispositionMethodID, OriginalDispositionID, OriginalDispositionDate, OriginalDispositionEvent, OriginalSentenceID, LatestDispositionMethodID, LatestDispositionID, LatestDispositionDate, LatestSentenceID, EarliestKnownChargeID, OffenseDate, CriminalDefendantHistoryID, ActivationDate, ActivationEventID, ActivationTypeID, AssociatedBookingNumber, AssociatedBookingDate, InactivityDays, CalendarDaysFilingtoCurrent, AgeofCase, DispositionID, DispositionDate, DispositionEventID, DispositionTypeID, CalendarDaysFilingtoDisposition, TimetoDisposition, casephaseID, CasePhaseCode, UnabletoCalcAgeInactivity, DispositionMethodID, PartyAttorneyID, PartyIDRepresenting, attorneyID, AttorneySBN, AttorneyCounselTypeID, AttorneyCaseStatusID, AttorneyStatusDateTime, CurrentAttorneyFlag, AttorneyStartDate, AttorneyEndDate, CurrentLeadAttorneyFlag, AssignedCourtID, OriginalDispositionCourtID, LatestDispositonCourtID |

Preview:

| CaseID | DivisionID | CourtTypeID | CaseTypeID | CaseStatusID | StatusDate | CaseStateID | SealedFlag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1381881 | 2 | 1 | 203.0 | 142 | 11/18/2010 | 3 | 0 |
| 1398852 | 2 | 1 | 195.0 | 142 | 10/2/2013 | 3 | 0 |
| 1437533 | 2 | 1 | 203.0 | 142 | 10/2/2012 | 3 | 0 |

### CaseIDtoBookingChargeIDUPDATED.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet2, Sheet3 |

#### Sheet: Sheet2

| Field | Value |
| --- | --- |
| Rows | 579075 |
| Columns | 2 |
| Column names | BookingChargeID, CaseID |

Preview:

| BookingChargeID | CaseID |
| --- | --- |
| 1276847.0 | 408393.0 |
| 1265925.0 | 408402.0 |
| 1512394.0 | 408402.0 |

#### Sheet: Sheet3

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

### chargecode_description.dta

| Field | Value |
| --- | --- |
| File type | Stata .dta |
| Rows | 7041 |
| Columns | 3 |
| Sheet names | Not applicable |
| Column names | chargecode, chargecode_numeric, chargecode_description |

Preview:

| chargecode | chargecode_numeric | chargecode_description |
| --- | --- | --- |
| /09996000 |  | AIDING SUICIDE |
| /13130100 |  | ASSAULT |
| /13130300 |  | ASSAULT WITH THREAT AND INJURY |

### Events.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Events |

#### Sheet: Events

| Field | Value |
| --- | --- |
| Rows | 52853 |
| Columns | 16 |
| Column names | EventID, CaseID, PartyID, EventDate, EventDateSeq, EventCodeID, EventResultID, AssociatedCountNo, DivisionID, EventCodeID.1, DivisionID.1, EventCode, EventDescription, EventCategoryID, AssociatedCaseStatusID, CourtJudgeIdentifier |

Preview:

| EventID | CaseID | PartyID | EventDate | EventDateSeq | EventCodeID | EventResultID | AssociatedCountNo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 63624446 | 336.0 | 49083.0 | 1992-07-30 00:00:00 | 1.0 | 114.0 |  |  |
| 63640376 | 695.0 |  | 2010-08-03 00:00:00 | 2.0 | 190.0 | 9.0 |  |
| 63999086 | 3852.0 |  | 2013-04-23 00:00:00 | 2.0 | 190.0 | 9.0 |  |

### Mental Health Flag Events.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet1, Sheet2, Sheet3 |

#### Sheet: Sheet1

| Field | Value |
| --- | --- |
| Rows | 94336 |
| Columns | 7 |
| Column names | BookingNumber, MNI, BookingDate, Event, EventDescription, EventEntryDate, EventEntryTime |

Preview:

| BookingNumber | MNI | BookingDate | Event | EventDescription | EventEntryDate | EventEntryTime |
| --- | --- | --- | --- | --- | --- | --- |
| 1000033 | 1716091 | 2010-01-01 00:00:00 | PSY | PSY - Seen and Eval per Counselor | 2010-01-01 00:00:00 | 1317 |
| 1000070 | 713247 | 2010-01-01 00:00:00 | PSY | PSY - Seen and Eval per Counselor | 2010-01-02 00:00:00 | 1315 |
| 1000070 | 713247 | 2010-01-01 00:00:00 | PP | PP - MHMR Priority Population | 2010-01-02 00:00:00 | 1315 |

#### Sheet: Sheet2

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

#### Sheet: Sheet3

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

### PersonData.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | PersonData |

#### Sheet: PersonData

| Field | Value |
| --- | --- |
| Rows | 123571 |
| Columns | 7 |
| Column names | PersonID, MNI, DateofBirth, GenderID, RaceID, EthnicityID, CitizenshipID |

Preview:

| PersonID | MNI | DateofBirth | GenderID | RaceID | EthnicityID | CitizenshipID |
| --- | --- | --- | --- | --- | --- | --- |
| 69724 | 1172445.0 | 1984-06-19 00:00:00 | 1.0 | 7.0 |  | 1.0 |
| 135247 | 782761.0 | 1974-09-15 00:00:00 | 1.0 | 7.0 | 1.0 | 1.0 |
| 135253 | 782777.0 | 1977-02-22 00:00:00 | 2.0 | 7.0 |  | 1.0 |

### PreTrial Charge-Interview.csv

| Field | Value |
| --- | --- |
| File type | CSV |
| Rows | 397886 |
| Columns | 37 |
| Sheet names | Not applicable |
| Column names | PA_MAST_NO, PK_BKG_NO, BJ_BK_DATE, PK_CHG_DT, INT_OFF, OFF_REC, PK_BND_REC, PK_BND_GRT, PK_GRNT_DT, PK_ATY_REC, PK_ATY_BND, PK_CNTY_NO, PK_BND_AMT, PK_BND_TYP, PK_BND_STS, PK_SEQ_No, PK_CHARGE, PK_CHG_LIT, PK_LVL, PK_INT_DT, PK_INT_TYPE, JUDGE, PK_BNDRSN_1, PK_BNDRSN_2, PK_BNDRSN_3, PK_BND_CND1, PK_BND_CND2, PK_BND_CND3, PK_BND_CND4, PK_BND_CND5, PK_BND_CND6, PK_BND_CD1, PK_BND_CD2, PK_BND_CD3, PK_BND_CD4, PK_BND_CD5, PK_BND_CD6 |

Preview:

| PA_MAST_NO | PK_BKG_NO | BJ_BK_DATE | PK_CHG_DT | INT_OFF | OFF_REC | PK_BND_REC | PK_BND_GRT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT10000003 | 1000003 | 1/1/2010 | 1/1/2010 | P031 | P031 | Y | Y |
| PT10000002 | 1000003 | 1/1/2010 | 1/1/2010 |  |  |  |  |
| PT10000005 | 1000008 | 1/1/2010 | 1/1/2010 |  |  |  |  |

### PreTrial Charge-Interview.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Charges |

#### Sheet: Charges

| Field | Value |
| --- | --- |
| Rows | 397886 |
| Columns | 37 |
| Column names | PA_MAST_NO, PK_BKG_NO, BJ_BK_DATE, PK_CHG_DT, INT_OFF, OFF_REC, PK_BND_REC, PK_BND_GRT, PK_GRNT_DT, PK_ATY_REC, PK_ATY_BND, PK_CNTY_NO, PK_BND_AMT, PK_BND_TYP, PK_BND_STS, PK_SEQ_No, PK_CHARGE, PK_CHG_LIT, PK_LVL, PK_INT_DT, PK_INT_TYPE, JUDGE, PK_BNDRSN_1, PK_BNDRSN_2, PK_BNDRSN_3, PK_BND_CND1, PK_BND_CND2, PK_BND_CND3, PK_BND_CND4, PK_BND_CND5, PK_BND_CND6, PK_BND_CD1, PK_BND_CD2, PK_BND_CD3, PK_BND_CD4, PK_BND_CD5, PK_BND_CD6 |

Preview:

| PA_MAST_NO | PK_BKG_NO | BJ_BK_DATE | PK_CHG_DT | INT_OFF | OFF_REC | PK_BND_REC | PK_BND_GRT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT10000003 | 1000003 | 2010-01-01 00:00:00 | 2010-01-01 00:00:00 | P031 | P031 | Y | Y |
| PT10000002 | 1000003 | 2010-01-01 00:00:00 | 2010-01-01 00:00:00 |  |  |  |  |
| PT10000005 | 1000008 | 2010-01-01 00:00:00 | 2010-01-01 00:00:00 |  |  |  |  |

### PreTrial Defendants.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet1, Sheet2, Sheet3 |

#### Sheet: Sheet1

| Field | Value |
| --- | --- |
| Rows | 238567 |
| Columns | 13 |
| Column names | PA_MAST_NO, PA_BKG_NO, BJ_BK_DATE, PA_PTS_RISK, PTS_OFF, PB_MNI, PB_SEX, PB_RAC, PB_DOB, PB_CITY, PB_ST, PB_ZIP, PC_ETHNIC |

Preview:

| PA_MAST_NO | PA_BKG_NO | BJ_BK_DATE | PA_PTS_RISK | PTS_OFF | PB_MNI | PB_SEX | PB_RAC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT10000002 | 1000003 | 2010-01-01 00:00:00 |  |  | 1717266 | M | W |
| PT10000003 | 1000003 | 2010-01-01 00:00:00 | 2 | P071 | 1717266 | M | W |
| PT10000005 | 1000008 | 2010-01-01 00:00:00 |  |  | 1717269 | M | W |

#### Sheet: Sheet2

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

#### Sheet: Sheet3

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

### PreTrial Disposition Reason.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet1, Sheet2, Sheet3 |

#### Sheet: Sheet1

| Field | Value |
| --- | --- |
| Rows | 48793 |
| Columns | 8 |
| Column names | PA_MAST_NO, PA_BKG_NO, BJ_BK_DATE, PK_SEQ_NO, PL_MOT_RSN1, PL_BND_CASE, PL_BND_DISP, PL_DISP_RSN |

Preview:

| PA_MAST_NO | PA_BKG_NO | BJ_BK_DATE | PK_SEQ_NO | PL_MOT_RSN1 | PL_BND_CASE | PL_BND_DISP | PL_DISP_RSN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT10000028 | 1000048 | 2010-01-01 00:00:00 | 1 | REARR | C1CR07223838 | 2.0 | 5 |
| PT10000028 | 1000048 | 2010-01-01 00:00:00 | 2 | REARR | C1CR07223838 | 2.0 | 5 |
| PT10000028 | 1000048 | 2010-01-01 00:00:00 | 1 | REARR | C1CR09213661 | 2.0 | 5 |

#### Sheet: Sheet2

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

#### Sheet: Sheet3

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

### PreTrial TCUD-ODAR Events.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Sheet1, Sheet2, Sheet3 |

#### Sheet: Sheet1

| Field | Value |
| --- | --- |
| Rows | 77345 |
| Columns | 6 |
| Column names | PA_MAST_NO, PA_BKG_NO, BJ_BK_DATE, PI_EVENT, PI_EVT_DISP, PI_SCORE |

Preview:

| PA_MAST_NO | PA_BKG_NO | BJ_BK_DATE | PI_EVENT | PI_EVT_DISP | PI_SCORE |
| --- | --- | --- | --- | --- | --- |
| PT10018573 | 1029325 | 2010-06-21 00:00:00 | TCUD30 | COMPLETE | 1.0 |
| PT10032707 | 1051396 | 2010-10-22 00:00:00 | TCUD30 | COMPLETE | 0.0 |
| PT11024290 | 1137284 | 2011-08-12 00:00:00 | TCUD30 | COMPLETE | 9.0 |

#### Sheet: Sheet2

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

#### Sheet: Sheet3

| Field | Value |
| --- | --- |
| Rows | 0 |
| Columns | 0 |
| Column names |  |

Preview:

_No data rows available._

### PreTrial to Booking Info.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | Booking |

#### Sheet: Booking

| Field | Value |
| --- | --- |
| Rows | 429635 |
| Columns | 11 |
| Column names | PA_MAST_NO, BH_BKG_NO, BJ_BK_DATE, BH_WAR_NO, BH_C_CASE, BH_BAIL_AMT, BH_CHG_DATE, BH_JCHG_NO, BH_CRT_DATE, BH_CRT_TIME, BH_CRT_EVT |

Preview:

| PA_MAST_NO | BH_BKG_NO | BJ_BK_DATE | BH_WAR_NO | BH_C_CASE | BH_BAIL_AMT | BH_CHG_DATE | BH_JCHG_NO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PT10000002 | 1000003 | 2010-01-01 00:00:00 |  | C1CR10200039 | 5000.0 | 2010-01-01 00:00:00 | 1 |
| PT10000003 | 1000003 | 2010-01-01 00:00:00 |  | C1CR10200039 | 5000.0 | 2010-01-01 00:00:00 | 1 |
| PT10000005 | 1000008 | 2010-01-01 00:00:00 |  |  | 0.0 | 2010-01-01 00:00:00 | 2 |

### revocationV2.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | revocation |

#### Sheet: revocation

| Field | Value |
| --- | --- |
| Rows | 19258 |
| Columns | 81 |
| Column names | CaseID, DivisionID, CourtTypeID, CaseTypeID, CaseStatusID, StatusDate, CaseStateID, SealedFlag, RestrictedFlag, CaseInitiationDate, DateCaseEntered, ReindictRefile, CaseStateIssue, LatestCasePhaseID, LatestAgeofPendingComplaint, CriminalDefendantID, PartyID, PersonID, MNI, OriginalBookingNumber, BookingDate, IndictFilingDate, CalendarDaysBookingtoIndictFiling, JailCaseTypeID, HighestLevelChargeCount, HighestLevelDispositionCount, CaseChargeID, CountNumber, ChargeCode, CsMgmtChargeID, CurrentChargeStateID, ChargeReducedEnhanced, OriginalDispositionPleaID, OriginalDispositionPleaDate, OriginalDispositionTrialTypeID, OriginalDispositionVerdictID, OriginalDispositionVerdictDate, OriginalDispositionMethodID, OriginalDispositionID, OriginalDispositionDate, OriginalDispositionEvent, OriginalSentenceID, LatestDispositionMethodID, LatestDispositionID, LatestDispositionDate, LatestSentenceID, EarliestKnownChargeID, OffenseDate, CriminalDefendantHistoryID, ActivationDate, ActivationEventID, ActivationTypeID, AssociatedBookingNumber, AssociatedBookingDate, InactivityDays, CalendarDaysFilingtoCurrent, AgeofCase, DispositionID, DispositionDate, DispositionEventID, DispositionTypeID, CalendarDaysFilingtoDisposition, TimetoDisposition, casephaseID, CasePhaseCode, UnabletoCalcAgeInactivity, DispositionMethodID, PartyAttorneyID, PartyIDRepresenting, attorneyID, AttorneySBN, AttorneyCounselTypeID, AttorneyCaseStatusID, AttorneyStatusDateTime, CurrentAttorneyFlag, AttorneyStartDate, AttorneyEndDate, CurrentLeadAttorneyFlag, AssignedCourtID, OriginalDispositionCourtID, LatestDispositonCourtID |

Preview:

| CaseID | DivisionID | CourtTypeID | CaseTypeID | CaseStatusID | StatusDate | CaseStateID | SealedFlag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1595 | 1.0 | 1.0 | 80.0 | 62.0 | 2016-03-01 00:00:00 | 3.0 | 0.0 |
| 1595 | 1.0 | 1.0 | 80.0 | 62.0 | 2016-03-01 00:00:00 | 3.0 | 0.0 |
| 2437 | 1.0 | 1.0 | 80.0 | 62.0 | 2014-09-19 00:00:00 | 3.0 | 0.0 |

### SentencingDataPost2013.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | SentencingDataPost2013 |

#### Sheet: SentencingDataPost2013

| Field | Value |
| --- | --- |
| Rows | 84209 |
| Columns | 14 |
| Column names | CriminalSentencingID, CaseID, PartyID, CountNumber, Sequence, SentenceTypeID, ReceivableTypeID, AgencyID, SentenceUOMID, SentenceQuantity, SentenceOther, SentenceEffectiveDt, SentenceConcurrencyFlag, DivisionID |

Preview:

| CriminalSentencingID | CaseID | PartyID | CountNumber | Sequence | SentenceTypeID | ReceivableTypeID | AgencyID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2484 | 354133.0 | 1160079.0 | 1.0 | 2.0 | 2.0 | 190.0 | 227.0 |
| 624828 | 352173.0 | 1152957.0 | 1.0 | 1.0 | 1.0 | 319.0 | 872.0 |
| 627370 | 418075.0 | 1351074.0 | 1.0 | 2.0 | 1.0 | 319.0 | 847.0 |

### SentencingDataPre2013.xlsx

| Field | Value |
| --- | --- |
| File type | Excel workbook |
| Sheet names | SentencingDataPre2013 |

#### Sheet: SentencingDataPre2013

| Field | Value |
| --- | --- |
| Rows | 63122 |
| Columns | 14 |
| Column names | CriminalSentencingID, CaseID, PartyID, CountNumber, Sequence, SentenceTypeID, ReceivableTypeID, AgencyID, SentenceUOMID, SentenceQuantity, SentenceOther, SentenceEffectiveDt, SentenceConcurrencyFlag, DivisionID |

Preview:

| CriminalSentencingID | CaseID | PartyID | CountNumber | Sequence | SentenceTypeID | ReceivableTypeID | AgencyID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2237 | 371529.0 | 1212773.0 | 1.0 | 1.0 | 2.0 | 384.0 | 227.0 |
| 3055 | 32004.0 | 69659.0 | 1.0 | 2.0 | 2.0 | 190.0 | 227.0 |
| 528696 | 943597.0 | 1843597.0 | 1.0 | 1.0 | 1.0 | 613.0 | 1519.0 |

