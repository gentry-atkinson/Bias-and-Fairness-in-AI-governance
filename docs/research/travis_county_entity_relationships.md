# Travis County Data Relationship Map

This is a week 1 relationship map based on the observed schemas and measured identifier overlap across the core Travis County files. It is still exploratory, but it is more concrete than a header-only hypothesis list.

## Primary entity anchors

### Person

- strongest identifiers: `PersonID`, `MNI` or `mni`
- primary files: `PersonData.xlsx`, booking extracts, `CaseData_v2.csv`
- likely role: `PersonData.xlsx` is the clearest demographic anchor and the best place to attach protected-attribute fields to downstream case and booking records

### Booking

- strongest identifiers: `BookingNumber`, `bookingID`, `BookingChargeID`
- primary files: `Booking2010_2012v3.csv`, `Booking2013_2016v3.csv`
- likely role: booking records appear to be the operational hub connecting jail intake, booking charges, pretrial records, and case references

### Case

- strongest identifiers: `CaseID`, `OriginalBookingNumber`, `AssociatedBookingNumber`, `CaseChargeID`
- primary files: `CaseData_v2.csv`, `CaseIDtoBookingChargeIDUPDATED.xlsx`, sentencing workbooks, `revocationV2.xlsx`
- likely role: case records appear to be the main court-process and outcome table

### Pretrial

- strongest identifiers: `PA_MAST_NO`, booking-number variants, court-case-number style fields
- primary files: `PreTrial Charge-Interview.csv`, `PreTrial Defendants.xlsx`, `PreTrial to Booking Info.xlsx`, `PreTrial TCUD-ODAR Events.xlsx`, `PreTrial Disposition Reason.xlsx`
- likely role: pretrial appears to be a connected subgraph that can join into bookings directly and into cases indirectly

### Charge and offense classification

- strongest identifiers: `BookingChargeID`, `CaseChargeID`, `ChargeCode`, `PK_CHARGE`
- primary files: booking extracts, `CaseData_v2.csv`, `CaseIDtoBookingChargeIDUPDATED.xlsx`, `chargecode_description.dta`, violent-charge lookup workbook
- likely role: row-level charge bridges should rely on booking or case charge IDs, while `ChargeCode` is better treated as an offense classification variable

## Measured relationship evidence

### Person-level joins

- `CaseData_v2.csv` aligns very strongly to `PersonData.xlsx`: case `PersonID` overlaps essentially all person-table `PersonID` values, and case `MNI` shows the same pattern.
- booking records also align strongly to `PersonData.xlsx`, but they cover a broader person universe than the person workbook alone.
- `PreTrial Defendants.xlsx` overlaps strongly with `PersonData.xlsx` through `PB_MNI`, making it a plausible route from pretrial records to person-level demographics.

### Booking-centered joins

- pretrial booking identifiers are the strongest observed joins into bookings.
- `BH_BKG_NO` in `PreTrial to Booking Info.xlsx`, `PK_BKG_NO` in `PreTrial Charge-Interview.csv`, and `PA_BKG_NO` in `PreTrial Defendants.xlsx` each overlap almost perfectly with booking `BookingNumber`.
- case booking references are also strong: both `OriginalBookingNumber` and `AssociatedBookingNumber` in `CaseData_v2.csv` match most booking numbers, though not every case maps back to a booking in the extracts.

### Case-centered joins

- `CaseID` is the best downstream key.
- `CaseIDtoBookingChargeIDUPDATED.xlsx` overlaps most case IDs found in `CaseData_v2.csv`, making it a practical bridge from booking charge rows to court case rows.
- sentencing workbooks reuse `CaseID` and overlap almost entirely with the case table, so they look like broad downstream extensions of the court-processing path.
- `revocationV2.xlsx` also uses `CaseID`, but it covers a narrower subset of cases.

### Charge-level joins

- `CaseIDtoBookingChargeIDUPDATED.xlsx` overlaps almost fully with booking `BookingChargeID`, which is the strongest observed row-level bridge between booking-side and case-side charge records.
- `revocationV2.xlsx` reuses `CaseChargeID` and overlaps a meaningful but narrower subset of case charges.
- `ChargeCode` is shared across booking and case data, and `PK_CHARGE` in pretrial overlaps strongly with booking `ChargeCode`, which supports offense-type harmonization and lookup enrichment.

### Pretrial internal joins

- `PA_MAST_NO` is the main internal pretrial key.
- it overlaps almost perfectly across `PreTrial Charge-Interview.csv`, `PreTrial Defendants.xlsx`, and `PreTrial to Booking Info.xlsx`.
- `PreTrial TCUD-ODAR Events.xlsx` covers a smaller subset of the same `PA_MAST_NO` universe, which suggests it is an event table attached to pretrial records rather than a parallel master table.
- `PK_CNTY_NO` in `PreTrial Charge-Interview.csv` and `BH_C_CASE` in `PreTrial to Booking Info.xlsx` overlap strongly, which suggests these are court-case-number style fields that may help route pretrial activity back into court records.

## Likely cardinalities

The observed files do not look one-row-per-entity.

- one person likely has many bookings
- one booking likely has many booking-charge rows
- one case likely has many case-charge or attorney-status rows
- one `PA_MAST_NO` likely has multiple pretrial-related rows across interviews, defendants, bridge records, and event files
- one case can link to multiple booking charges through `CaseIDtoBookingChargeIDUPDATED.xlsx`

## Practical linkage strategy

For week 1 analysis, the safest staged join path is:

1. use `PersonData.xlsx` as the demographic anchor through `PersonID` or `MNI`
2. join bookings through `BookingNumber` and booking-side charge rows through `BookingChargeID`
3. bridge bookings to cases through `CaseIDtoBookingChargeIDUPDATED.xlsx` plus case booking-number references where needed
4. attach pretrial records through `PA_MAST_NO` internally and booking-number fields externally
5. attach sentencing and revocation outcomes on `CaseID`
6. enrich offense classes through `ChargeCode` lookups, not as a primary row key

## Recommended working tables

- `persons`
- `bookings`
- `booking_charges`
- `cases`
- `case_booking_charge_bridge`
- `pretrial_master`
- `pretrial_events`
- `sentencing_outcomes`
- `revocation_outcomes`
- `charge_lookups`