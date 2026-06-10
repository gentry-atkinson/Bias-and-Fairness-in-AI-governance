"""Fairness metric implementations."""

import numpy as np


def demographic_parity(y_pred, protected):
    """
    Difference in positive prediction rates between two groups.

    Returns:
        float
    """

    groups = np.unique(protected)

    if len(groups) != 2:
        raise ValueError("Exactly two groups are required.")

    rates = []

    for group in groups:
        mask = protected == group
        rates.append(np.mean(y_pred[mask]))

    return abs(rates[0] - rates[1])


def equal_opportunity(y_true, y_pred, protected):
    """
    Difference in true positive rates between two groups.

    Returns:
        float
    """

    groups = np.unique(protected)

    if len(groups) != 2:
        raise ValueError("Exactly two groups are required.")

    tprs = []

    for group in groups:
        mask = protected == group

        tp = np.sum((y_true == 1) & (y_pred == 1) & mask)
        fn = np.sum((y_true == 1) & (y_pred == 0) & mask)

        if tp + fn == 0:
            tprs.append(0.0)
        else:
            tprs.append(tp / (tp + fn))

    return abs(tprs[0] - tprs[1])

def false_positive_rate_difference(y_true, y_pred, protected):
    """
    Difference in false positive rates between two groups.
    """

    groups = np.unique(protected)

    if len(groups) != 2:
        raise ValueError("Exactly two groups are required.")

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
    Difference in false negative rates between two groups.
    """

    groups = np.unique(protected)

    if len(groups) != 2:
        raise ValueError("Exactly two groups are required.")

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