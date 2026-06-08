# Proxy Variable Notes

These notes are a week 1 audit list for variables that may act as proxies for protected attributes in criminal justice data. They are hypotheses for review, not conclusions.

## Why this matters

The project focus is not only whether explicit race or gender fields exist, but also whether seemingly neutral variables can encode protected-group information indirectly and affect downstream decisions or model behavior.

## Audit categories

### Direct or near-direct sensitive attributes

- any explicit race, ethnicity, sex, gender, nationality, or age fields found in `PersonData.xlsx` or linked tables
- mental health flags if used in outcome prediction rather than descriptive context

### Likely proxy candidates already visible in the schema

- `ArrestingAgencyID`: may reflect geography, policing patterns, and neighborhood-level enforcement differences
- `AssignedCourtID`, `OriginalDispositionCourtID`, `LatestDispositonCourtID`, `JailChargeCourt`: court assignment can encode institutional variation tied to place and case mix
- `AttorneyCounselTypeID`, `CurrentAttorneyFlag`, lead-attorney indicators: defense representation patterns can correlate with socioeconomic status
- `BailTypeID`, `BailAmount`, bond recommendation and grant fields: these may reflect prior institutional judgments and resource constraints rather than underlying risk alone
- `ChargeCode`, `ChargeDescription`, `ChargeClassID`, `HighestBookingCharge`: legally relevant but also potentially entangled with historical enforcement disparities
- `BookingAuthorityID`, `CustodyStatusID`, `CustodyTypeID`, hold flags: may capture system processing decisions that differ by group
- judge and officer identifiers in the pretrial interview data: individual decision-makers may introduce structured variation
- event-history tables such as revocation, mental-health, or pretrial events: past system contact can function as a proxy for broader surveillance exposure

### Proxy candidates to confirm after workbook inspection

- zip code, address, precinct, neighborhood, or county subregion fields
- employment, education, or housing-status fields
- marital or family-status fields
- language or citizenship-related fields

## Week 1 audit questions

1. Which files contain direct demographic variables, and at what entity level?
2. Which identifiers let those fields flow into booking, case, and pretrial records?
3. Which operational variables represent prior human decisions rather than raw facts?
4. Which variables should be excluded, separately analyzed, or carefully justified in any fairness experiment?

## Immediate next actions

1. Inspect `PersonData.xlsx` first for direct protected attributes.
2. Review the bridge workbooks to see how demographic fields could propagate into modeling tables.
3. Tag each candidate variable as `direct`, `proxy`, `outcome`, `operational`, or `unclear` in the data dictionary.