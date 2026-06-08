# Travis County EDA Walkthrough Script

## Important files to mention

- `notebooks/travis_county_eda.ipynb`: the main exploration notebook and the best place to walk through what was completed
- `docs/data/travis_county_data_inventory.md`: full inventory of all raw files, workbook sheets, column names, and previews
- `docs/data/travis_county_entity_relationships.md`: working relationship map across person, booking, case, pretrial, charge, sentencing, and revocation data
- `docs/data/data_dictionary.md`: grouped feature inventory with demographics, geography, charges, risk, process, and outcomes
- `docs/research/proxy_variable_notes.md`: first-pass audit of direct sensitive fields and likely proxy variables
- `reports/tables/travis_county_basic_eda/`: saved EDA summary tables for shapes, dtypes, missingness, numeric summaries, and categorical counts
- `reports/figures/travis_county_basic_eda/`: basic EDA figures
- `reports/figures/travis_county_grouped_viz/`: grouped exploratory figures for demographics, risk scores, missingness, and bond outcomes

## Short meeting script

I want to walk you through the Travis County exploratory notebook and the main documentation I built around it. The notebook is `notebooks/travis_county_eda.ipynb`, and it now acts as the main week 1 workspace for inventorying the files, identifying relationships, grouping features, and producing initial exploratory outputs.

I start the notebook by setting up the project root, locating the raw data folder, and listing the highest-priority core files. From there, I build an inventory of the raw files and preview the schemas of the core CSVs. The goal of that first section is to understand what is actually present before making assumptions about modeling or fairness analysis.

The next important notebook section is the priority workbook inspection. In that part I look closely at `PersonData.xlsx`, `PreTrial to Booking Info.xlsx`, and `CaseIDtoBookingChargeIDUPDATED.xlsx`. These are important because they clarify how demographic information, pretrial records, and booking or case records may connect. `PersonData.xlsx` is especially important because it contains the clearest direct demographic fields.

After that, the notebook moves into the relationship map. This is where I document the likely entity structure of the data. The working picture is that the data behaves like a pipeline rather than one flat table. `PersonData.xlsx` is the person anchor through `PersonID` and `MNI`. The booking CSVs are the operational hub through `BookingNumber`, `bookingID`, and `BookingChargeID`. `CaseData_v2.csv` is the main case table through `CaseID`. The pretrial files connect strongly to booking records through booking-number variants and internally through `PA_MAST_NO`. Sentencing and revocation appear to extend the case pathway.

I then added a measured relationship section so this is not only a header-based guess. In that part of the notebook I compute actual identifier overlap across the main files. The strongest links are between pretrial booking identifiers and booking `BookingNumber`, and between the booking charge IDs and the case bridge workbook. That gives us more confidence about which joins are safe to use first.

The next major notebook section is the feature inventory. I grouped variables into categories that matter for fairness work: demographics, geography, legal history, current charge, risk-related variables, court decisions, judge or court-process variables, and outcomes. I also separated out fields whose meanings are still unclear because many of the columns are coded IDs or abbreviated institutional fields.

After that, I added feature role tagging. This section labels key columns as identifiers, sensitive features, proxies, decisions, outcomes, process variables, or candidate predictors. This matters because a fairness project cannot treat every available variable as an acceptable model input. For example, race, ethnicity, sex, and date of birth should be treated as sensitive. ZIP code and arresting agency are likely proxies. Bond recommendation and bond grant fields are decisions or outcomes, not neutral predictors.

The notebook then runs a basic EDA pipeline across the major datasets. That code loads the main CSV and Excel files, computes shapes, data types, missing values, duplicate rows, numeric summary statistics, and categorical value counts, and saves those tables into `reports/tables/travis_county_basic_eda/`. This gives a reusable data-quality snapshot outside the notebook itself.

I also added a candidate modeling feature section that separates baseline candidate predictors from proxy-risk fields and sensitive attributes. The goal there is to make it easier to say which variables might be reasonable in a first-pass model and which ones should be excluded or only used for auditing.

The last major notebook pieces are the visualization sections. One section reads the saved EDA tables and makes general plots like rows by dataset and missingness by dataset. The grouped visual exploration section builds a pretrial-focused analysis frame and plots missingness, demographic distributions, pretrial risk scores, bond outcome distributions, and group-level comparisons of bond grant rates by race, gender, age group, and ZIP code. Those figures are saved to `reports/figures/travis_county_grouped_viz/`.

## What I would emphasize in conversation

- The biggest accomplishment this week is that the dataset is now documented well enough to talk about structure rather than just raw files.
- The clearest demographic anchor is `PersonData.xlsx`, but the clearest branch for early fairness exploration is the pretrial branch because it combines demographics, a risk-like score, and a near-term institutional outcome.
- The data contains direct sensitive attributes and many likely proxies, so fairness concerns are already visible even before formal modeling begins.
- Some of the strongest blockers are still interpretability blockers: many fields are coded IDs, and several process fields are heavily missing.
- The notebook is now not just exploratory; it also produces reusable tables and figures that can support the next phase.

## Suggested closing for the meeting

My recommendation for the next phase is to define one concrete target outcome, resolve the most important coded fields, and build a first-pass joined analysis table centered on the clearest branch of the data. Right now, the pretrial branch looks like the best place to start because it is the most interpretable link between demographics, risk-related information, and institutional outcomes.
