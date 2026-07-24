## Bias and Fairness in AI Governance

## Overview

This repository contains the code, analyses, and documentation developed during a ten-week undergraduate research project investigating bias and fairness in the Travis County pretrial risk assessment system.

The goal of this project was to examine whether pretrial risk scores and downstream court outcomes differed across protected demographic groups, including race, sex, and age. The project combines data integration, exploratory data analysis, statistical testing, fairness metrics, and visualization to produce a reproducible fairness audit of the Travis County criminal justice dataset.

Although the original objective included developing predictive machine learning models, a substantial portion of the research focused on understanding, integrating, and documenting the Travis County datasets. Because many variables lacked complete documentation or an official codebook, significant effort was devoted to data linkage, feature engineering, and fairness analysis. These efforts established a well-documented, analysis-ready dataset that provides a strong foundation for future machine learning research.

---

# Getting Started

1. Place all required raw datasets inside `data/raw/`.
2. Run `dataloader.py` to construct the integrated analysis dataset.
3. Run the remaining analysis scripts as needed:
   - `population_summary.py`
   - `proxy_analysis.py`
   - `fairness_analysis.py`
   - `outcome_fairness_analysis.py`
   - `statistical_analysis.py`
4. Generated tables will be saved in `outputs/`, and figures will be saved in `figures/`.

# Research Objectives

The project focused on the following objectives:

- Build an integrated defendant-level dataset by linking multiple Travis County criminal justice datasets.
- Identify reliable join keys across booking, pretrial, court, and sentencing records.
- Investigate potential proxy variables for protected demographic attributes.
- Evaluate fairness across race, sex, and age using descriptive and inferential statistics.
- Assess disparities in downstream court outcomes, including case records, dispositions, pleas, verdicts, and sentencing.
- Produce publication-quality tables and visualizations summarizing the findings.

---

# Repository Structure

```
Bias-and-Fairness-in-AI-governance/

├── archives/
│   Exploratory analyses and development scripts
│
├── data/
│   ├── raw/
│   └── interim/
│
├── docs/
│   Project documentation
│
├── figures/
│   Publication-quality figures
│
├── outputs/
│   Generated CSV summaries and statistical outputs
│
├── src/
│   Primary analysis scripts
│
├── README.md
└── LICENSE
```

---

# Main Analysis Pipeline

The primary analysis scripts are located in the `src/` directory.

| Script | Purpose |
|----------|---------|
| `dataloader.py` | Builds the integrated analysis dataset by merging multiple Travis County datasets. |
| `connect_case_outcomes.py` | Links downstream court outcomes to the complete defendant dataset. |
| `proxy_analysis.py` | Evaluates whether non-protected variables act as proxies for protected attributes. |
| `fairness_analysis.py` | Computes fairness metrics and demographic risk score summaries. |
| `population_summary.py` | Summarizes the demographic composition of the defendant population. |
| `outcome_fairness_analysis.py` | Evaluates fairness across downstream court outcomes. |
| `statistical_analysis.py` | Performs descriptive statistics and inferential statistical tests. |
| `generate_mental_health_features.py` | Creates defendant-level mental health features. |
| `generate_prior_booking_counts.py` | Computes prior booking history features. |
| `utils.py` | Shared utility functions used across analysis scripts. |

---

# Data Sources

The analyses integrate information from several Travis County datasets, including:

- Booking records
- Pretrial defendant records
- Pretrial charge and interview records
- Court case data
- Sentencing records
- Revocation records
- Mental health flag events
- TCUD-ODAR event records

These datasets are merged into a unified defendant-level dataset that serves as the foundation for all analyses.

---

# Methods

The project applies several statistical and fairness analysis techniques, including:

- Exploratory Data Analysis (EDA)
- Data linkage and entity resolution
- Proxy variable analysis
- Descriptive statistics
- Kruskal-Wallis tests
- Mann-Whitney U tests
- Chi-square tests
- Effect size calculations
- Statistical parity analysis
- Demographic disparity analysis
- Publication-quality data visualization

---

# Key Findings

The primary findings of this research include:

- The defendant population consisted primarily of White defendants (75.4%) and Black defendants (23.2%).
- Black defendants received the highest average pretrial risk scores among the evaluated racial groups.
- Younger defendants tended to receive higher average risk scores than older defendants.
- Male defendants received slightly higher average risk scores than female defendants.
- Statistically significant differences in risk scores were identified across race, sex, and age groups.
- Although statistically significant differences were observed, calculated effect sizes were generally small, indicating that demographic characteristics explained only a limited portion of the variation in assigned risk scores.
- Significant demographic differences were also identified across several downstream court outcomes, with the strongest associations occurring for plea and verdict outcomes.

---

# Outputs

Generated outputs are saved in the following directories:

- `outputs/`
    - Statistical summary tables
    - Fairness metrics
    - Population summaries
    - Descriptive statistics

- `figures/`
    - Publication-quality visualizations
    - Population summaries
    - Fairness figures
    - Outcome visualizations

---

# Archive

The `archives/` directory contains exploratory analyses, data audits, and development scripts created during the early stages of the project. These scripts document the process used to understand, clean, and integrate the Travis County datasets but are not required to reproduce the final fairness analyses.


---

# Future Work

This project established a comprehensive data integration and fairness evaluation framework for the Travis County pretrial dataset. Several opportunities remain for future research:

- Develop predictive machine learning models using the integrated defendant-level dataset created during this project.
- Investigate feature importance and model interpretability to better understand the factors influencing predicted risk scores.
- Evaluate algorithmic fairness metrics for trained machine learning models and compare them with the fairness characteristics observed in the existing Travis County risk assessment process.
- Incorporate additional engineered features, including mental health indicators and prior booking history, into predictive models.
- Expand fairness analyses using additional definitions of fairness, such as equalized odds, predictive parity, and calibration.
- Compare fairness outcomes across multiple jurisdictions or additional criminal justice datasets.
- If a comprehensive codebook or documentation for the Travis County datasets becomes available, revisit the coded variables (e.g., disposition, event, plea, and verdict codes) to create more informative features for predictive modeling and improve model interpretability.

---

# Acknowledgements

This research was completed as part of an undergraduate summer research project in Artificial Intelligence and Data Science at St. Edward's University.

The project was conducted under the mentorship of **Dr. Gentry Atkinson**, whose guidance and feedback were instrumental throughout the research process.

The Travis County criminal justice datasets used in this project were provided through a collaboration with **Texas A&M University**, enabling the data integration, fairness analyses, and statistical evaluations presented in this repository.