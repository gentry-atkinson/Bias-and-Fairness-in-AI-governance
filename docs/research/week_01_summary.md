# Friday Research Update

## What I analyzed

This week I completed a first-pass exploratory analysis of the Travis County criminal-justice dataset. The main tasks were to inventory the raw files, identify how the files connect, group available features into analysis categories, flag likely proxy variables, and build reusable EDA outputs and visualizations in the notebook and reports folders.

## What files exist

The `data/raw` folder currently contains 18 source files.

- core operational CSVs: `Booking2010_2012v3.csv`, `Booking2013_2016v3.csv`, `CaseData_v2.csv`, `PreTrial Charge-Interview.csv`
- person and bridge workbooks: `PersonData.xlsx`, `PreTrial to Booking Info.xlsx`, `CaseIDtoBookingChargeIDUPDATED.xlsx`
- pretrial supporting workbooks: `PreTrial Defendants.xlsx`, `PreTrial Disposition Reason.xlsx`, `PreTrial TCUD-ODAR Events.xlsx`, `PreTrial Charge-Interview.xlsx`
- event and downstream outcome workbooks: `Events.xlsx`, `Mental Health Flag Events.xlsx`, `SentencingDataPre2013.xlsx`, `SentencingDataPost2013.xlsx`, `revocationV2.xlsx`
- lookup files: `chargecode_description.dta`, `171017_CCHCodes_Violent marked by Slayton.xlsx`

I documented the file inventory in `docs/data/travis_county_data_inventory.md`.

## How the files may relate

The files appear to form a linked justice-process pipeline rather than one flat table.

- person layer: `PersonData.xlsx` is the clearest demographic anchor through `PersonID` and `MNI`
- booking layer: the booking CSVs are the operational hub through `BookingNumber`, `bookingID`, and `BookingChargeID`
- case layer: `CaseData_v2.csv` is the main case-outcome table through `CaseID`, with booking references in `OriginalBookingNumber` and `AssociatedBookingNumber`
- pretrial layer: `PA_MAST_NO` ties together the pretrial files, while `PK_BKG_NO`, `PA_BKG_NO`, and `BH_BKG_NO` connect pretrial records back to booking numbers
- bridge layer: `CaseIDtoBookingChargeIDUPDATED.xlsx` is the clearest direct bridge between booking-side charge rows and case rows
- downstream outcomes: sentencing and revocation files appear to extend the case pathway through `CaseID`

Measured overlap checks support these relationships strongly, especially for booking-number matches across pretrial files and for `BookingChargeID` overlap between the booking extracts and the case bridge workbook.

## Important features identified so far

The most useful feature groups at this stage are:

- demographics: `DateofBirth`, `GenderID`, `RaceID`, `EthnicityID`, `CitizenshipID`, plus defendant-level fields such as `PB_SEX`, `PB_RAC`, and `PC_ETHNIC`
- geography: `PB_CITY`, `PB_ST`, `PB_ZIP`, and institutional location or assignment fields such as `ArrestingAgencyID` and court identifiers
- current charge and severity: `ChargeCode`, `ChargeDescription`, `ChargeClassID`, `CaseChargeID`, `PK_CHARGE`, `PK_CHG_LIT`, `PK_LVL`
- risk or recommendation features: `PA_PTS_RISK`, `PI_SCORE`, `PK_BND_REC`, `PK_ATY_REC`, `OFF_REC`
- court decision and process variables: bond grant and amount fields, case disposition fields, sentence fields, judge identifiers, and attorney-assignment fields
- outcomes: release fields, bond grant and bond amount, case dispositions, sentence quantities, and some event-level disposition fields

I documented these in `docs/data/data_dictionary.md` and added notebook sections that tag features as identifiers, sensitive fields, proxies, decisions, outcomes, or candidate predictors.

## Potential proxy variables

Several fields are likely to act as proxies for protected attributes or prior institutional judgment.

- geographic proxies: `PB_ZIP`, `PB_CITY`, `PB_ST`
- institutional proxies: `ArrestingAgencyID`, `AssignedCourtID`, `OriginalDispositionCourtID`, `LatestDispositonCourtID`, `JailChargeCourt`
- process-history proxies: prior event tables, revocation records, mental-health event flags, and booking-history fields
- decision-derived proxies: `BailAmount`, `BailTypeID`, bond recommendation fields, judge identifiers, officer identifiers, and attorney-assignment fields

These are documented in `docs/research/proxy_variable_notes.md`.

## Initial bias and fairness concerns

The current data raises several early fairness concerns.

- direct protected attributes are present and linkable into operational records through person identifiers
- many operational variables appear to encode prior human or institutional decisions rather than neutral facts
- geographic and agency fields could proxy race, class, or neighborhood-level enforcement patterns
- charge and event-history fields may reflect cumulative surveillance or enforcement disparities rather than only legal seriousness
- some high-missingness fields and coded-ID fields may introduce misleading structure if used without validation or lookup tables

At this point, I would not treat recommendation fields, judicial outcome fields, or coded operational history variables as default predictors in a fairness experiment.

## Current blockers

- many important fields are coded IDs and still need lookup tables or domain interpretation
- some columns are effectively all missing, especially several late-phase case-process fields
- the strongest joined exploratory plots currently rely on the pretrial subset because it has the clearest combination of demographics, risk, and outcome variables in one branch
- we still need a clear target definition for any fairness metric or predictive modeling setup

## Visualizations completed

I generated and saved reusable EDA outputs and figures.

- summary tables: `reports/tables/travis_county_basic_eda/`
- general EDA figures: `reports/figures/travis_county_basic_eda/`
- grouped exploration figures: `reports/figures/travis_county_grouped_viz/`

Current plots include:

- rows by dataset
- total missing values by dataset
- top missingness-rate columns
- largest top-category counts
- key-field missingness in the pretrial analysis subset
- demographic distributions for race, gender, age group, and ZIP code
- pretrial risk score distribution
- bond-grant and bond-amount outcome distributions
- group-level bond-grant comparisons by race, gender, age group, and ZIP code

## Recommended next steps

1. Build a first-pass analysis table anchored on the pretrial branch and booking bridge, with one row per `PA_MAST_NO` or booking record.
2. Resolve the most important coded fields first, especially charge severity, case status, disposition, sentence, and pretrial decision codes.
3. Define one concrete fairness outcome for the next phase, such as bond grant, bond amount, or a case-disposition target.
4. Separate variables into `allowed predictors`, `sensitive audit fields`, `proxy-risk fields`, `decision variables`, and `outcomes` before any modeling begins.
5. Expand visual comparisons to include confidence intervals or sample-size thresholds once the modeling target is fixed.