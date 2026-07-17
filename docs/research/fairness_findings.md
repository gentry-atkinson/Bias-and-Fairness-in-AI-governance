# Initial Fairness Analysis Findings

## Objective

Evaluate whether ORAS risk scores differ across protected demographic groups in the Travis County pretrial dataset.

For this analysis, ORAS risk scores are treated as the outcome variable, following project guidance.

---

## Dataset

- Dataset: Travis County pretrial dataset
- Records analyzed: 85,459 defendants
- Outcome:
  - ORAS risk score
- Protected attributes:
  - Race
  - Sex
  - Age group (18–25, 26–35, 36–50, 50+)

---

## Methods

The initial fairness analysis includes:

1. Summary statistics by protected group
   - Count
   - Mean
   - Median
   - Standard deviation
   - Minimum
   - Maximum

2. Statistical parity
   - Comparison of the proportion of defendants classified as high risk
   - High-risk threshold: ORAS risk score ≥ 6

3. Mean score disparity
   - Absolute difference in average ORAS risk scores between demographic groups

4. Risk score distribution visualizations
   - Histograms generated for race, sex, and age groups

---

# Results

## Race

Mean ORAS risk scores:

| Group | Mean |
|------|------:|
| A | 1.873 |
| B | 3.053 |
| I | 2.312 |
| U | 1.954 |
| W | 2.412 |

Observations:

- Race shows the largest differences in average ORAS risk scores.
- The largest observed mean score disparity is between groups A and B (1.18 points).
- Groups I (n = 32) and U (n = 65) have very small sample sizes, so comparisons involving these groups should be interpreted cautiously.

---

## Sex

Mean ORAS risk scores:

| Group | Mean |
|------|------:|
| Female | 2.458 |
| Male | 2.587 |

Observations:

- Average ORAS risk scores differ only slightly between males and females.
- The observed mean score disparity is 0.1288 points.

---

## Age

Mean ORAS risk scores:

| Group | Mean |
|------|------:|
| 18–25 | 2.732 |
| 26–35 | 2.603 |
| 36–50 | 2.368 |
| 50+ | 2.181 |

Observations:

- Average ORAS risk scores decrease with increasing age.
- The largest observed difference is between defendants aged 18–25 and those aged 50+ (0.5507 points).

---

## Statistical Parity

Statistical parity differences were computed using the project high-risk threshold (risk score ≥ 6).

Observations:

- Statistical parity differences were generally small across race, sex, and age comparisons.
- Although average risk scores differ between demographic groups, the proportion of defendants classified as high risk varies less substantially.

---

# Preliminary Conclusions

Based on the current descriptive analysis:

- Race exhibits the largest differences in average assigned ORAS risk scores.
- Age also shows noticeable variation, with younger defendants receiving higher average scores.
- Sex differences are comparatively small.
- Differences in average scores are larger than differences observed using the statistical parity metric.

These findings describe observed differences in assigned risk scores and do not establish the cause of those differences.

---

# Limitations

Current limitations of this analysis include:

- ORAS risk scores are analyzed as the outcome rather than observed post-release outcomes.
- Small sample sizes for some race categories may reduce the stability of pairwise comparisons.
- This is an initial descriptive fairness analysis and should not be interpreted as evidence of causal bias.

