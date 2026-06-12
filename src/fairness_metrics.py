"""Fairness metric implementations."""

import numpy as np


def _validate_two_groups(protected):
    groups = np.unique(protected)

    if len(groups) != 2:
        raise ValueError("Exactly two groups are required.")

    return groups


def group_base_rate(outcome, protected):
    """
    Difference in outcome rates between two groups.

    Example:
        bond granted rate by race
        detention rate by sex

    Returns:
        float
    """

    groups = _validate_two_groups(protected)

    rates = []

    for group in groups:
        mask = protected == group
        rates.append(np.mean(outcome[mask]))

    return abs(rates[0] - rates[1])


def detention_release_disparity(released, protected):
    """
    Difference in release rates between two groups.

    released:
        1 = released
        0 = detained

    Returns:
        float
    """

    return group_base_rate(released, protected)


def failure_to_appear_disparity(fta, protected):
    """
    Difference in failure-to-appear rates between groups.

    fta:
        1 = failed to appear
        0 = appeared

    Returns:
        float
    """

    return group_base_rate(fta, protected)


def false_positive_rate_difference(y_true, y_pred, protected):
    """
    Difference in false positive rates between groups.

    Returns:
        float
    """

    groups = _validate_two_groups(protected)

    fprs = []

    for group in groups:
        mask = protected == group

        fp = np.sum((y_true == 0) & (y_pred == 1) & mask)
        tn = np.sum((y_true == 0) & (y_pred == 0) & mask)

        if fp + tn == 0:
            fprs.append(0.0)
        else:
            fprs.append(fp / (fp + tn))

    return abs(fprs[0] - fprs[1])


def false_negative_rate_difference(y_true, y_pred, protected):
    """
    Difference in false negative rates between groups.

    Returns:
        float
    """

    groups = _validate_two_groups(protected)

    fnrs = []

    for group in groups:
        mask = protected == group

        fn = np.sum((y_true == 1) & (y_pred == 0) & mask)
        tp = np.sum((y_true == 1) & (y_pred == 1) & mask)

        if fn + tp == 0:
            fnrs.append(0.0)
        else:
            fnrs.append(fn / (fn + tp))

    return abs(fnrs[0] - fnrs[1])


def calibration_by_subgroup(scores, outcomes, protected):
    """
    Calibration difference between two groups.

    scores:
        risk scores

    outcomes:
        observed outcomes

    Returns:
        float
    """

    groups = _validate_two_groups(protected)

    calibration_errors = []

    for group in groups:
        mask = protected == group

        group_scores = scores[mask]
        group_outcomes = outcomes[mask]

        error = np.mean(np.abs(group_scores - group_outcomes))

        calibration_errors.append(error)

    return abs(calibration_errors[0] - calibration_errors[1])


def harsher_outcome_disparity(outcome_value, protected):
    """
    Difference in average punishment severity between groups.

    Examples:
        bond amount
        sentence length
        jail days

    Returns:
        float
    """

    groups = _validate_two_groups(protected)

    means = []

    for group in groups:
        mask = protected == group
        means.append(np.mean(outcome_value[mask]))

    return abs(means[0] - means[1])