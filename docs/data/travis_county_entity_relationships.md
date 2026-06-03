# Travis County Entity Relationship Notes

This is a week 1 working map of the likely entities in the Travis County data. It is a hypothesis document for exploration, not a finalized schema.

## Working entity map

### Person

- likely identifiers: `PersonID`, `mni`, `MNI`
- likely source files: booking extracts, case extract, `PersonData.xlsx`
- research importance: may contain the clearest route to direct demographic variables and protected attributes

### Booking

- likely identifiers: `bookingID`, `BookingNumber`, possibly `PK_BKG_NO`
- likely source files: `Booking2010_2012v3.csv`, `Booking2013_2016v3.csv`, `PreTrial to Booking Info.xlsx`
- research importance: booking records appear to be the operational bridge between jail, charges, and pretrial processing

### Charge

- likely identifiers: `BookingChargeID`, `CaseChargeID`, `ChargeCode`
- likely source files: booking extracts, case extract, `chargecode_description.dta`, violent-charge lookup workbook
- research importance: charge severity and offense type are important features but may also embed enforcement disparities

### Case

- likely identifiers: `CaseID`, `AssociatedBookingNumber`, `OriginalBookingNumber`
- likely source files: `CaseData_v2.csv`, `CaseIDtoBookingChargeIDUPDATED.xlsx`
- research importance: case records carry dispositions, attorney assignments, and court-processing outcomes

### Pretrial interview

- likely identifiers: `PA_MAST_NO`, `PK_BKG_NO`, `PK_CHARGE`
- likely source files: `PreTrial Charge-Interview.csv`, `PreTrial Charge-Interview.xlsx`, `PreTrial Defendants.xlsx`
- research importance: likely contains bond recommendations, grants, and operational decision points relevant to fairness analysis

### Sentencing and downstream outcomes

- likely identifiers: case- or person-level fields to be confirmed
- likely source files: `SentencingDataPre2013.xlsx`, `SentencingDataPost2013.xlsx`, `revocationV2.xlsx`
- research importance: these files may support longer-horizon outcome definitions if linkages can be confirmed

## Likely relationship hypotheses

1. One person can have many bookings.
2. One booking can have many booking-charge rows.
3. One case can involve many case-charge rows.
4. Booking and case records may connect through booking number bridge tables rather than a single stable key inside every table.
5. Pretrial interview records likely connect to bookings first, then cases indirectly.

## Priority bridge tables to inspect

1. `PreTrial to Booking Info.xlsx`
2. `CaseIDtoBookingChargeIDUPDATED.xlsx`
3. `PersonData.xlsx`

## Week 1 validation tasks

1. Confirm whether `mni` and `MNI` are the same concept across files.
2. Check whether `PK_BKG_NO` matches `BookingNumber` exactly or requires formatting cleanup.
3. Identify whether `CaseChargeID` and `BookingChargeID` map one-to-one, one-to-many, or many-to-many.
4. Verify whether demographic variables live only in `PersonData.xlsx` or also appear elsewhere.

## Minimal target data structure

For an initial research-ready structure, aim to model the data as linked tables:

- `persons`
- `bookings`
- `booking_charges`
- `cases`
- `case_charges`
- `pretrial_interviews`
- `sentencing_outcomes`
- `lookups`

This is simple enough for week 1 EDA and flexible enough for later fairness experiments.