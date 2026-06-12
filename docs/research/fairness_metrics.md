# Fairness Metrics

Document the disparity metrics and subgroup comparisons used in the project.

## Candidate metrics

- group-wise base rates
- detention or release disparities
- failure-to-appear disparities
- false positive and false negative rates
- calibration by subgroup
- exposure to harsher outcomes conditional on case attributes

## Notes to record

- mathematical definition of each metric
- why the metric is appropriate for the research question
- known caveats for observational criminal justice data
- subgroup definitions and sample-size thresholds

## Demographic Parity
- Definition: Positive prediction rates should be equal across groups.
- Formula: P(Ŷ=1|A=a) = P(Ŷ=1|A=b)
- Input: Predictions and group labels.
- Output: Difference in positive prediction rates.
- Caveat: Ignores actual outcomes.

## Equal Opportunity
- Definition: True positive rates should be equal across groups.
- Formula: P(Ŷ=1|Y=1,A=a) = P(Ŷ=1|Y=1,A=b)
- Input: Predictions, true labels, group labels.
- Output: Difference in TPR.
- Caveat: Ignores false positives.

## Equalized Odds
- Definition: TPR and FPR should both be equal across groups.
- Input: Predictions, true labels, group labels.
- Output: Combined TPR/FPR disparity.
- Caveat: Difficult to satisfy simultaneously with calibration
- Formula: P(Ŷ=1|Y=1,A=a) = P(Ŷ=1|Y=1,A=b)
           P(Ŷ=1|Y=0,A=a) = P(Ŷ=1|Y=0,A=b)

## Predictive Parity
- Definition: Precision should be equal across groups.
- Output: Difference in PPV.
- Caveat: Often conflicts with Equalized Odds
- Formula: P(Y=1|Ŷ=1,A=a) = P(Y=1|Ŷ=1,A=b)

## Calibration
- Definition: Equal risk scores should imply equal outcome probabilities across groups.
- Caveat: Often incompatible with other fairness criteria.