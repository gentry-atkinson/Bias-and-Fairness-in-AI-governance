# Proxy Variable Analysis Report

## Methodology

Association strength between each feature and each protected attribute was measured using the appropriate statistical test:

| Feature type | Protected type | Test | Effect size |
|---|---|---|---|
| Categorical | Categorical | Chi-Square | Cramer's V |
| Numeric | Categorical | Kruskal-Wallis | Eta-squared |
| Numeric | Numeric | Spearman | \|rho\| |

Effect sizes range from 0 (no association) to 1 (perfect association).

---

## Strongest Associations (Top 20)

|   rank | feature           | protected_attribute   | test_name   |   statistic |   p_value |   effect_size | effect_size_label   |   n_observations | notes    |
|-------:|:------------------|:----------------------|:------------|------------:|----------:|--------------:|:--------------------|-----------------:|:---------|
|      1 | charge_code       | sex                   | Chi-Square  |   17587.9   |         0 |        0.2667 | Cramer's V          |           234049 | dof=938  |
|      2 | charge_code       | ethnicity             | Chi-Square  |   16935.6   |         0 |        0.1794 | Cramer's V          |           234045 | dof=1870 |
|      3 | charge_code       | race                  | Chi-Square  |   27538.8   |         0 |        0.1594 | Cramer's V          |           234049 | dof=3752 |
|      4 | bond_status       | sex                   | Chi-Square  |    2073.43  |         0 |        0.1584 | Cramer's V          |            81037 | dof=41   |
|      5 | bond_granted_raw  | sex                   | Chi-Square  |    3873.58  |         0 |        0.1413 | Cramer's V          |           194061 | dof=1    |
|      6 | bond_granted_flag | sex                   | Chi-Square  |    3873.58  |         0 |        0.1413 | Cramer's V          |           194061 | dof=1    |
|      7 | bond_status       | ethnicity             | Chi-Square  |    1816.07  |         0 |        0.1035 | Cramer's V          |            81004 | dof=82   |
|      8 | charge_level      | sex                   | Chi-Square  |    2240.9   |         0 |        0.0972 | Cramer's V          |           234049 | dof=29   |
|      9 | risk_score        | race                  | Chi-Square  |    3106.27  |         0 |        0.094  | Cramer's V          |            86849 | dof=36   |
|     10 | bond_granted_flag | race                  | Chi-Square  |    1427.53  |         0 |        0.0856 | Cramer's V          |           194061 | dof=4    |
|     11 | bond_granted_raw  | race                  | Chi-Square  |    1427.53  |         0 |        0.0856 | Cramer's V          |           194061 | dof=4    |
|     12 | age_group         | ethnicity             | Chi-Square  |    3162.42  |         0 |        0.082  | Cramer's V          |           234174 | dof=10   |
|     13 | charge_level      | ethnicity             | Chi-Square  |    3074.72  |         0 |        0.0803 | Cramer's V          |           234045 | dof=58   |
|     14 | risk_score        | ethnicity             | Chi-Square  |     762.395 |         0 |        0.0655 | Cramer's V          |            86847 | dof=18   |
|     15 | judge             | sex                   | Chi-Square  |     585.088 |         0 |        0.0645 | Cramer's V          |           120418 | dof=84   |
|     16 | judge             | ethnicity             | Chi-Square  |    1056.65  |         0 |        0.0607 | Cramer's V          |           120403 | dof=168  |
|     17 | bond_status       | race                  | Chi-Square  |    1349.49  |         0 |        0.0605 | Cramer's V          |            81037 | dof=164  |
|     18 | risk_score        | sex                   | Chi-Square  |     252.898 |         0 |        0.053  | Cramer's V          |            86849 | dof=9    |
|     19 | charge_level      | race                  | Chi-Square  |    2681.95  |         0 |        0.0524 | Cramer's V          |           234049 | dof=116  |
|     20 | judge             | race                  | Chi-Square  |    1601.51  |         0 |        0.0513 | Cramer's V          |           120418 | dof=336  |

---

## KL Divergence — Distribution Shift Across Race Groups

KL divergence measures how different the distribution of a numeric feature is between two racial groups.  0 = identical distributions; larger = more different.

| feature        | group_a   | group_b   |   kl_divergence |
|:---------------|:----------|:----------|----------------:|
| age_at_booking | I         | U         |          2.733  |
| age_at_booking | B         | I         |          2.6743 |
| age_at_booking | A         | I         |          2.6658 |
| age_at_booking | A         | U         |          1.6599 |
| bond_amount    | I         | U         |          1.6397 |
| age_at_booking | W         | I         |          1.339  |
| age_at_booking | B         | U         |          0.9168 |
| age_at_booking | W         | U         |          0.6665 |
| bond_amount    | A         | I         |          0.5004 |
| bond_amount    | A         | U         |          0.4772 |
| bond_amount    | B         | I         |          0.2771 |
| bond_amount    | W         | I         |          0.1114 |
| bond_amount    | B         | U         |          0.057  |
| zip_code       | I         | U         |          0.0436 |
| bond_amount    | W         | U         |          0.0366 |
| bond_amount    | B         | A         |          0.0363 |
| age_at_booking | W         | A         |          0.0282 |
| bond_amount    | W         | A         |          0.027  |
| age_at_booking | B         | A         |          0.0257 |
| zip_code       | A         | U         |          0.018  |

---

## Potential Proxy Variables

Features with effect size ≥ 0.10 and p-value < 0.05 are flagged as potential proxy variables:

|   rank | feature           | protected_attribute   | test_name   |   effect_size |   p_value |
|-------:|:------------------|:----------------------|:------------|--------------:|----------:|
|      1 | charge_code       | sex                   | Chi-Square  |        0.2667 |         0 |
|      2 | charge_code       | ethnicity             | Chi-Square  |        0.1794 |         0 |
|      3 | charge_code       | race                  | Chi-Square  |        0.1594 |         0 |
|      4 | bond_status       | sex                   | Chi-Square  |        0.1584 |         0 |
|      5 | bond_granted_raw  | sex                   | Chi-Square  |        0.1413 |         0 |
|      6 | bond_granted_flag | sex                   | Chi-Square  |        0.1413 |         0 |
|      7 | bond_status       | ethnicity             | Chi-Square  |        0.1035 |         0 |