# Travis County Data Inventory

This is the week 1 starting inventory for the re-added Travis County files. It is intentionally lightweight and should be refined as relationships and field meanings become clearer.

## Core linking hypotheses

- `PersonID` and `MNI` appear in the booking and case extracts and are likely person-level linkage keys.
- `bookingID` and `BookingNumber` appear in booking extracts; `AssociatedBookingNumber` appears in case data.
- `CaseID` is the obvious case-level key in the case extract.
- `PK_BKG_NO` in the pretrial charge-interview file is a likely booking-number style linkage field.
- workbook files probably contain additional lookup tables or relationship bridges that need manual inspection.

## File inventory

| File | Format | Preliminary role | Likely unit | Initial linkage clues | Week 1 status |
| --- | --- | --- | --- | --- | --- |
| `Booking2010_2012v3.csv` | CSV | booking and charge history, 2010-2012 | booking-charge record | `bookingID`, `BookingNumber`, `mni`, `PersonID`, `BookingChargeID`, `ChargeCode` | header inspected |
| `Booking2013_2016v3.csv` | CSV | booking and charge history, 2013-2016 | booking-charge record | `bookingID`, `BookingNumber`, `mni`, `PersonID`, `BookingChargeID`, `ChargeCode` | header inspected |
| `CaseData_v2.csv` | CSV | case processing and dispositions | case-charge-attorney record | `CaseID`, `PersonID`, `MNI`, `OriginalBookingNumber`, `AssociatedBookingNumber`, `CaseChargeID` | header inspected |
| `PreTrial Charge-Interview.csv` | CSV | pretrial interview and bond information | pretrial charge or interview record | `PA_MAST_NO`, `PK_BKG_NO`, `PK_CHARGE`, `PK_CNTY_NO` | header inspected |
| `PreTrial Charge-Interview.xlsx` | XLSX | possible spreadsheet version of pretrial interview data | unknown | compare against CSV version | inspect sheets |
| `PersonData.xlsx` | XLSX | person-level attributes | likely person record | likely person identifiers such as `PersonID` or `MNI` | inspect sheets |
| `Events.xlsx` | XLSX | event history | event record | unknown until workbook inspection | inspect sheets |
| `Mental Health Flag Events.xlsx` | XLSX | mental-health-related events | event record | likely person or case linkage | inspect sheets |
| `PreTrial Defendants.xlsx` | XLSX | defendant-level pretrial data | defendant record | likely pretrial master or booking linkage | inspect sheets |
| `PreTrial Disposition Reason.xlsx` | XLSX | disposition lookup or event data | unknown | unknown until workbook inspection | inspect sheets |
| `PreTrial TCUD-ODAR Events.xlsx` | XLSX | pretrial event history | event record | likely pretrial or booking linkage | inspect sheets |
| `PreTrial to Booking Info.xlsx` | XLSX | bridge between pretrial and booking systems | mapping table | likely booking number and pretrial identifiers | high-priority inspect |
| `CaseIDtoBookingChargeIDUPDATED.xlsx` | XLSX | bridge between case and booking charge records | mapping table | `CaseID`, `BookingChargeID` likely present | high-priority inspect |
| `SentencingDataPre2013.xlsx` | XLSX | sentencing outcomes before 2013 | sentence or case record | likely case or person linkage | inspect sheets |
| `SentencingDataPost2013.xlsx` | XLSX | sentencing outcomes after 2013 | sentence or case record | likely case or person linkage | inspect sheets |
| `revocationV2.xlsx` | XLSX | revocation outcomes or events | revocation record | likely case, booking, or person linkage | inspect sheets |
| `chargecode_description.dta` | DTA | charge code lookup | charge code lookup row | likely `ChargeCode` mapping | inspect variables |
| `171017_CCHCodes_Violent marked by Slayton.xlsx` | XLSX | violent-offense reference list | charge code lookup row | likely charge code mapping | inspect sheets |

## Observed headers from core CSVs

### Booking extracts

Observed fields include booking identifiers, custody status, hold flags, booking and release timestamps, charge metadata, bail fields, and court-related fields.

### Case extract

Observed fields include case identifiers, court and case status fields, person linkage fields, booking references, charge and disposition fields, attorney assignment fields, and court assignment fields.

### Pretrial interview extract

Observed fields include booking number, charge date, interview officer, bond recommendation, bond grant, attorney-related indicators, county number, bond amount, bond type, status, judge, reasons, conditions, and codes.

## Week 1 priorities

1. Open the bridge workbooks first: `PreTrial to Booking Info.xlsx` and `CaseIDtoBookingChargeIDUPDATED.xlsx`.
2. Inspect `PersonData.xlsx` for direct demographics and sensitive attributes.
3. Compare the CSV and XLSX versions of pretrial interview data to avoid duplicate workflows.
4. Build a minimal entity map: person, booking, charge, case, pretrial interview, disposition, sentencing.