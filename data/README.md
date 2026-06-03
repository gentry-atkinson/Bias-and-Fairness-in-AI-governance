# Data Layout

Use this directory to separate original source material from derived analysis assets.

## Subdirectories

- `raw/`: immutable source exports such as booking, case, sentencing, and pretrial tables
- `external/`: codebooks, charge descriptions, lookup tables, or labeling references
- `interim/`: temporary joins, filtered extracts, and quality-check tables
- `processed/`: final analysis-ready datasets used by notebooks or models

## Rules

- do not edit files in `raw/` after adding them
- document source, date, and meaning of each table in `docs/data/data_dictionary.md`
- write reproducible transforms in `src/data/` instead of manual notebook-only edits