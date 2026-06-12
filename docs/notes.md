# Proxy Variable Analysis — Research Notes

Week 2 | Travis County Pretrial Dataset  
Branch: `khadeja/proxy-variable-analysis`

---

## Method

Every feature in the dataset was tested against three protected attributes:
- **Race** (`race` column)
- **Gender** (`sex` column)
- **Age** (`age_at_booking` column)

Statistical tests were selected based on variable types:

| Feature type | Protected type | Test | Effect size reported |
|---|---|---|---|
| Categorical | Categorical | Chi-Square | Cramer's V |
| Numeric | Categorical | Kruskal-Wallis | Eta-squared |
| Categorical | Numeric | Kruskal-Wallis | Eta-squared |
| Numeric | Numeric | Spearman | \|rho\| |

Effect sizes are on a 0–1 scale. With n=234k, nearly every p-value is 0 — **effect size is the meaningful metric here, not p-value.**

---

## Full Results

See `outputs/proxy_associations.csv` for the complete ranked table.

---

## Preliminary Findings

### Strongest Race Associations

| Rank | Feature | Effect Size | Test |
|---|---|---|---|
| 1 | `ethnicity` | 0.290 | Cramer's V |
| 2 | `zip_code` | 0.205 | Cramer's V |
| 3 | `charge_code` | 0.159 | Cramer's V |
| 4 | `risk_score` | 0.094 | Cramer's V |
| 5 | `bond_granted_flag` | 0.086 | Cramer's V |
| 6 | `bond_status` | 0.061 | Cramer's V |
| 7 | `charge_level` | 0.052 | Cramer's V |
| 8 | `judge` | 0.051 | Cramer's V |

### Strongest Gender Associations

| Rank | Feature | Effect Size | Test |
|---|---|---|---|
| 1 | `charge_code` | 0.267 | Cramer's V |
| 2 | `bond_status` | 0.158 | Cramer's V |
| 3 | `bond_granted_raw` / `bond_granted_flag` | 0.141 | Cramer's V |
| 4 | `charge_level` | 0.097 | Cramer's V |
| 5 | `risk_score` | 0.053 | Cramer's V |

### Strongest Age Associations

| Rank | Feature | Effect Size | Test |
|---|---|---|---|
| 1 | `charge_code` | 0.111 | Eta-squared |
| 2 | `risk_score` | 0.058 | Eta-squared |
| 3 | `zip_code` | 0.022 | Eta-squared |
| 4 | `bond_granted_flag` | 0.020 | Eta-squared |
| 5 | `bond_amount` | 0.041 | Spearman \|rho\| |

---

## Observations

### 1. Ethnicity is a near-proxy for race (V = 0.290)

The `ethnicity` column has the strongest association with `race` in the entire dataset. This is expected — both columns describe the same underlying characteristic from different classification systems. **If a model uses `ethnicity` but not `race`, it has effectively used race anyway.**

### 2. ZIP code is a strong race proxy (V = 0.205)

After fixing the data type (zip codes are categorical, not numeric quantities), ZIP code emerged as the second-strongest race association. This is a well-documented phenomenon in criminal justice research — residential segregation means geography encodes race. A model using ZIP code as an input would indirectly encode race.

### 3. Charge code is the most broadly associated feature

`charge_code` is strongly associated with all three protected attributes:
- Gender: V = 0.267
- Race: V = 0.159
- Age: eta² = 0.111

This likely reflects real disparities in policing and charging practices rather than a simple proxy relationship. **Charge code should be flagged for both proxy analysis and disparate impact analysis.**

### 4. The risk score is associated with race and age

`risk_score` (the pretrial risk tool output) shows meaningful association with race (V = 0.094) and age (eta² = 0.058). This is the most consequential finding: the score used to inform pretrial decisions is not race-neutral. This is consistent with published critiques of pretrial risk tools (e.g., ProPublica's COMPAS analysis).

### 5. Bond outcomes vary by gender more than by race

Bond-related outcomes (`bond_granted_flag`, `bond_status`) show stronger associations with gender than with race. This is worth investigating further — it may reflect charge-type differences between male and female defendants, or it may indicate gender-based judicial discretion.

### 6. Bond amount is weakly associated with protected attributes

`bond_amount` (continuous) shows very small effect sizes across all three protected attributes. However, the distributions are highly skewed and many values are $0 (no-bond releases), which may be masking real disparities at specific charge levels.

---

## Data Note: ZIP Code Type Bug

The original analysis (in `correlation_analysis.py`) incorrectly treated `zip_code` as a numeric variable because it was stored as a float in the CSV. This produced Eta-squared = 0.0009 (essentially zero association with race).

After casting ZIP codes to string in `proxy_analysis.py`, the correct Chi-Square test gives Cramer's V = 0.205 — a moderate association. **The original result was a measurement artifact, not a real finding.**

---

## Questions for Professor

1. Should `ethnicity` be treated as a protected attribute alongside `race`, or as a proxy for race?
2. Is the `risk_score` association with race a primary finding or out of scope for this week?
3. Should we report effect sizes for outcome variables (`bond_granted`, `bond_amount`) separately from input/candidate-predictor variables?
4. For the KL divergence stretch goal — which group comparisons are most relevant (e.g., Black vs. White defendants specifically, or all pairs)?

---

## Next Steps

- Visualize distributions of `charge_code` and `zip_code` by race group
- Investigate whether `risk_score` ↔ race association persists after controlling for charge type
- Check if the `judge` association with race reflects courthouse/jurisdictional differences or individual judge behavior
