## Bias and Fairness in AI Governance

This repository supports an eight-week summer research project on bias and fairness in criminal risk assessment systems, starting with exploratory analysis of the Travis County dataset.

## Current Focus

- inventory the Travis County files and reverse-engineer table relationships
- identify candidate proxy variables that may encode protected attributes indirectly
- establish a reusable workflow for exploratory analysis and fairness evaluation

## Week 1 Workspace

- dataset exploration script: `src/analysis/travis_county_week1_eda.py`
- data inventory: `docs/data/travis_county_data_inventory.md`
- proxy variable notes: `docs/research/proxy_variable_notes.md`
- week 1 summary: `docs/research/week_01_summary.md`

## Working Conventions

- source data stays in `data/raw/`
- reusable analysis code goes in `src/`
- exploratory notes and research writeups live in `docs/`
- PDFs and private literature collections stay outside GitHub
