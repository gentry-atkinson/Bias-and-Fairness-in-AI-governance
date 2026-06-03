# Week 1 Summary

## Research context

Khadeja is leading data exploration for an eight-week summer research project on bias and fairness in criminal risk assessment AI systems, starting with the Travis County dataset.

## Meeting outcomes

- weekly cadence is Monday planning, Wednesday check-in and pivot, Friday results presentation
- literature review should prioritize IEEE and ACM sources and avoid long law-review papers
- fairness definitions should be mathematical and computable, not only conceptual
- code should be developed in feature branches and merged after Friday review
- papers and PDFs stay in private Google Drive rather than this public repository

## Khadeja week 1 responsibilities

- inspect all Travis County files and reverse-engineer file relationships
- identify the features available across the dataset
- document candidate proxy variables such as geographic or institutional identifiers
- start exploratory analysis and simple visual checks where useful
- organize the data into a workable research structure

## What is now in the repo

- a raw-data inventory and schema preview script in `src/analysis/travis_county_week1_eda.py`
- a starting file inventory in `docs/data/travis_county_data_inventory.md`
- a proxy-variable audit note in `docs/research/proxy_variable_notes.md`
- this week 1 summary for tracking immediate goals and constraints

## Week 1 recommended deliverables for Friday

1. a cleaned inventory of all dataset files and workbook purposes
2. a draft entity-relationship map across person, booking, case, pretrial, and sentencing data
3. a first-pass list of direct sensitive attributes and likely proxies
4. a short presentation of initial findings, ambiguities, and next steps

## Open questions

- which workbook contains the clearest demographic variables?
- what is the exact bridge between pretrial records and booking or case records?
- which files are lookup tables versus event-level data?
- which fairness metrics will be feasible once a modeling target is defined?